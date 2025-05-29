# -*- coding: utf-8 -*-
"""DMeta functions."""
import os
import shutil
import zipfile
from art import tprint
import defusedxml.lxml as lxml
from .errors import DMetaBaseError
from .util import get_microsoft_format, extract, read_json
from .params import CORE_XML_MAP, APP_XML_MAP, OVERVIEW, DMETA_VERSION, \
    UPDATE_COMMAND_WITH_NO_CONFIG_FILE_ERROR, SUPPORTED_MICROSOFT_FORMATS


def overwrite_metadata(
        xml_path,
        metadata=None,
        is_core=True):
    """
    Overwrite metadata in an XML file based on a predefined mapping.

    :param xml_path: path to the XML file to be updated
    :type xml_path: str
    :param metadata: a dictionary containing metadata to overwrite the XML elements with, or `None`
                     to reset
    :type metadata: dict
    :param is_core: a flag that indicates whether the given XML file is the core.xml file
    :type is_core: bool
    :return: None
    """
    xml_map = CORE_XML_MAP if is_core else APP_XML_MAP
    if os.path.exists(xml_path):
        e_core = lxml.parse(xml_path)
        for xml_element in e_core.iter():
            for personal_field in xml_map if metadata is None else metadata:
                associated_xml_tag = xml_map[personal_field]
                if (associated_xml_tag in xml_element.tag):
                    xml_element.text = "" if metadata is None else metadata[personal_field]
        e_core.write(xml_path)


def clear(microsoft_file_name, in_place=False, verbose=False):
    """
    Clear all the editable metadata in the given Microsoft file.

    :param microsoft_file_name: name of Microsoft file
    :type microsoft_file_name: str
    :param in_place: the `in_place` flag applies the changes directly to the original file
    :type in_place: bool
    :param verbose: the `verbose` flag enables detailed output
    :type verbose: bool
    :return: None
    """
    microsoft_format = get_microsoft_format(microsoft_file_name)
    if microsoft_format is None:
        return
    unzipped_dir, source_file = extract(microsoft_file_name)
    doc_props_dir = os.path.join(unzipped_dir, "docProps")
    core_xml_path = os.path.join(doc_props_dir, "core.xml")
    app_xml_path = os.path.join(doc_props_dir, "app.xml")

    def is_metadata_cleared(xml_path, is_core=True):
        if not os.path.exists(xml_path):
            return True
        tree = lxml.parse(xml_path)
        xml_map = CORE_XML_MAP if is_core else APP_XML_MAP
        for xml_element in tree.iter():
            for personal_field in xml_map:
                associated_xml_tag = xml_map[personal_field]
                if (associated_xml_tag in xml_element.tag):
                    if xml_element.text and xml_element.text.strip():
                        return False
        return True

    core_cleared = is_metadata_cleared(core_xml_path)
    app_cleared = is_metadata_cleared(app_xml_path, is_core=False)

    if core_cleared and app_cleared:
        if verbose:
            print(f"Metadata is already cleared for: {microsoft_file_name}")
        shutil.rmtree(unzipped_dir)
        return

    # Clear metadata if not already cleared
    overwrite_metadata(core_xml_path)
    overwrite_metadata(app_xml_path, is_core=False)

    modified = microsoft_file_name
    if not in_place:
        modified = microsoft_file_name[:microsoft_file_name.rfind('.')] + "_cleared" + "." + microsoft_format
    with zipfile.ZipFile(modified, "w") as file:
        for file_name in source_file.namelist():
            file.write(os.path.join(unzipped_dir, file_name), file_name)
        file.close()
    shutil.rmtree(unzipped_dir)

    if verbose:
        print(f"Cleared metadata for: {microsoft_file_name}")


def clear_all(in_place=False, verbose=False):
    """
    Clear all the editable metadata in any Microsoft file in the current directory and its subdirectories.

    :param in_place: the `in_place` flag applies the changes directly to the original file
    :type in_place: bool
    :param verbose: the `verbose` flag enables detailed output
    :type verbose: bool
    :return: None
    """
    path = os.getcwd()
    counter = {
        format: 0 for format in SUPPORTED_MICROSOFT_FORMATS
    }

    for root, _, files in os.walk(path):
        for file in files:
            format = get_microsoft_format(file)
            if format is None:
                continue
            clear(os.path.join(root, file), in_place, verbose)
            counter[format] += 1

    if verbose:
        for format in counter.keys():
            print("Metadata of {} files with the format of {} has been cleared.".format(counter[format], format))


def update(config_file_name, microsoft_file_name, in_place=False, verbose=False):
    """
    Update all the editable metadata in the given Microsoft file according to the given config file.

    :param config_file_name: name of .json config file
    :type config_file_name: str
    :param microsoft_file_name: name of Microsoft file
    :type microsoft_file_name: str
    :param in_place: the `in_place` flag applies the changes directly to the original file
    :type in_place: bool
    :param verbose: the `verbose` flag enables detailed output
    :type verbose: bool
    :return: None
    """
    config = read_json(config_file_name)
    personal_fields_core_xml = {e: v for e, v in CORE_XML_MAP.items() if e in config}
    personal_fields_app_xml = {e: v for e, v in APP_XML_MAP.items() if e in config}

    has_core_tags = len(personal_fields_core_xml) > 0
    has_app_tags = len(personal_fields_app_xml) > 0

    if not (has_core_tags or has_app_tags):
        print("There isn't any chosen personal field to remove.")
        return

    microsoft_format = get_microsoft_format(microsoft_file_name)
    if microsoft_format is None:
        return

    unzipped_dir, source_file = extract(microsoft_file_name)
    doc_props_dir = os.path.join(unzipped_dir, "docProps")
    core_xml_path = os.path.join(doc_props_dir, "core.xml")
    app_xml_path = os.path.join(doc_props_dir, "app.xml")

    # Check if metadata is already up to date
    def is_metadata_up_to_date(xml_path, metadata, is_core=True):
        if not os.path.exists(xml_path):
            return False
        tree = lxml.parse(xml_path)
        xml_map = CORE_XML_MAP if is_core else APP_XML_MAP
        for xml_element in tree.iter():
            for personal_field in xml_map if metadata is None else metadata:
                associated_xml_tag = xml_map[personal_field]
                if (associated_xml_tag in xml_element.tag):
                    if xml_element.text != metadata[personal_field]:
                        return False
        return True

    core_up_to_date = is_metadata_up_to_date(core_xml_path, personal_fields_core_xml) if has_core_tags else True
    app_up_to_date = is_metadata_up_to_date(app_xml_path, personal_fields_app_xml) if has_app_tags else True

    if core_up_to_date and app_up_to_date:
        if verbose:
            print(f"Metadata is already up to date for: {microsoft_file_name}")
        shutil.rmtree(unzipped_dir)
        return

    # Update metadata if not already up to date
    if has_core_tags:
        overwrite_metadata(core_xml_path, personal_fields_core_xml)
    if has_app_tags:
        overwrite_metadata(app_xml_path, personal_fields_app_xml, is_core=False)

    modified = microsoft_file_name
    if not in_place:
        modified = microsoft_file_name[:microsoft_file_name.rfind('.')] + "_updated" + "." + microsoft_format
    with zipfile.ZipFile(modified, "w") as file:
        for file_name in source_file.namelist():
            file.write(os.path.join(unzipped_dir, file_name), file_name)
        file.close()
    shutil.rmtree(unzipped_dir)

    if verbose:
        print(f"Updated metadata for: {microsoft_file_name}")


def update_all(config_file_name, in_place=False, verbose=False):
    """
    Update all the editable metadata in any Microsoft file in the current directory and its subdirectories according to the given config file.

    :param config_file_name: name of .json config file
    :type config_file_name: str
    :param in_place: the `in_place` flag applies the changes directly to the original file
    :type in_place: bool
    :param verbose: the `verbose` flag enables detailed output
    :type verbose: bool
    :return: None
    """
    path = os.getcwd()
    counter = {
        format: 0 for format in SUPPORTED_MICROSOFT_FORMATS
    }

    for root, _, files in os.walk(path):
        for file in files:
            try:
                format = get_microsoft_format(file)
                if format is None:
                    return
                update(config_file_name, os.path.join(root, file), in_place, verbose)
                counter[format] += 1
            except DMetaBaseError as e:
                e = e.__str__()
                if e == NOT_IMPLEMENTED_ERROR:
                    print("DMeta couldn't update the metadata of {} since {}".format(file, NOT_IMPLEMENTED_ERROR))
                if e == FILE_FORMAT_DOES_NOT_EXIST_ERROR:
                    print(
                        "Updating the metadata of {} failed because DMeta {}".format(
                            file, FILE_FORMAT_DOES_NOT_EXIST_ERROR))

    if verbose:
        for format in counter.keys():
            print("Metadata of {} files with the format of {} has been updated.".format(counter[format], format))


def dmeta_help():
    """
    Print DMeta details.

    :return: None
    """
    print(OVERVIEW)
    print("Repo : https://github.com/openscilab/dmeta")
    print("Webpage : https://openscilab.com")


def run_dmeta(args):
    """
    Run DMeta.

    :param args: input arguments
    :type args: argparse.Namespace
    :return: None
    """
    verbose = args.verbose
    if args.clear:
        clear(args.clear[0], args.inplace, verbose)
    elif args.clear_all:
        clear_all(args.inplace, verbose)
    elif args.update:
        if not args.config:
            raise DMetaBaseError(UPDATE_COMMAND_WITH_NO_CONFIG_FILE_ERROR)
        else:
            update(args.config[0], args.update[0], args.inplace, verbose)
    elif args.update_all:
        if not args.config:
            raise DMetaBaseError(UPDATE_COMMAND_WITH_NO_CONFIG_FILE_ERROR)
        else:
            update_all(args.config[0], args.inplace, verbose)
    else:
        tprint("DMeta")
        tprint("V:" + DMETA_VERSION)
        dmeta_help()
