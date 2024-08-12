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
    UPDATE_COMMAND_WITH_NO_CONFIG_FILE_ERROR, SUPPORTED_MICROSOFT_FORMATS, \
    NOT_IMPLEMENTED_ERROR, FILE_FORMAT_DOES_NOT_EXIST_ERROR


def clear(microsoft_file_name, in_place=False):
    """
    Clear all the editable metadata in the given microsoft file.

    :param microsoft_file_name: name of microsoft file
    :type microsoft_file_name: str
    :param in_place: the `in_place` flag applies the changes directly to the original file
    :type in_place: bool
    :return: None
    """
    microsoft_format = get_microsoft_format(microsoft_file_name)
    unzipped_dir, source_file = extract(microsoft_file_name)
    doc_props_dir = os.path.join(unzipped_dir, "docProps")
    core_xml_path = os.path.join(doc_props_dir, "core.xml")
    app_xml_path = os.path.join(doc_props_dir, "app.xml")

    if os.path.exists(core_xml_path):
        e_core = lxml.parse(core_xml_path)
        for xml_element in e_core.iter():
            for personal_field in CORE_XML_MAP.values():
                if (personal_field in xml_element.tag):
                    xml_element.text = ""
        e_core.write(core_xml_path)

    if os.path.exists(app_xml_path):
        e_app = lxml.parse(app_xml_path)
        for xml_element in e_app.iter():
            for personal_field in APP_XML_MAP.values():
                if (personal_field in xml_element.tag):
                    xml_element.text = ""
        e_app.write(app_xml_path)

    
    modified = microsoft_file_name
    if not in_place:
        modified = microsoft_file_name[:microsoft_file_name.rfind('.')] + "_cleared" + "." + microsoft_format
    with zipfile.ZipFile(modified, "w") as file:
        for file_name in source_file.namelist():
            file.write(os.path.join(unzipped_dir, file_name), file_name)
        file.close()
    shutil.rmtree(unzipped_dir)


def clear_all(in_place=False):
    """
    Clear all the editable metadata in any microsoft file in the current directory.
    
    :param in_place: the `in_place` flag applies the changes directly to the original file
    :type in_place: bool
    :return: None
    """
    path = os.getcwd()
    dir_list = os.listdir(path)
    counter = {
        format: 0 for format in SUPPORTED_MICROSOFT_FORMATS
    }
    for file in dir_list:
        try:
            format = get_microsoft_format(file)
            clear(file, in_place)
            counter[format] += 1
        except DMetaBaseError as e:
            e = e.__str__()
            if e == NOT_IMPLEMENTED_ERROR:
                print("DMeta couldn't clear the metadata of {} since {}".format(file, NOT_IMPLEMENTED_ERROR))
            if e == FILE_FORMAT_DOES_NOT_EXIST_ERROR:
                print("Clearing the metadata of {} failed because DMeta {}".format(file, FILE_FORMAT_DOES_NOT_EXIST_ERROR))
    for format in counter.keys():
        print("Metadata of {} files with the format of {} has been cleared.".format(counter[format], format))


def update(config_file_name, microsoft_file_name, in_place=False):
    """
    Update all the editable metadata in the given microsoft file according to the given config file.

    :param config_file_name: name of .json config file
    :type config_file_name: str
    :param microsoft_file_name: name of microsoft file
    :type microsoft_file_name: str
    :param in_place: the `in_place` flag applies the changes directly to the original file
    :type in_place: bool
    :return: None
    """
    config = read_json(config_file_name)
    personal_fields_core_xml = [e for e in CORE_XML_MAP.keys() if e in config]
    personal_fields_app_xml = [e for e in APP_XML_MAP.keys() if e in config]

    has_core_tags = len(personal_fields_core_xml) > 0
    has_app_tags = len(personal_fields_core_xml) > 0

    if not (has_core_tags or has_app_tags):
        print("There isn't any chosen personal field to remove.")
        return

    microsoft_format = get_microsoft_format(microsoft_file_name)
    unzipped_dir, source_file = extract(microsoft_file_name)
    doc_props_dir = os.path.join(unzipped_dir, "docProps")
    core_xml_path = os.path.join(doc_props_dir, "core.xml")
    app_xml_path = os.path.join(doc_props_dir, "app.xml")

    if has_core_tags:
        if os.path.exists(core_xml_path):
            e_core = lxml.parse(core_xml_path)
            for xml_element in e_core.iter():
                for personal_field in personal_fields_core_xml:
                    associated_xml_tag = CORE_XML_MAP[personal_field]
                    if (associated_xml_tag in xml_element.tag):
                        xml_element.text = config[personal_field]
            e_core.write(core_xml_path)

    if has_app_tags:
        if os.path.exists(app_xml_path):
            e_app = lxml.parse(app_xml_path)
            for xml_element in e_app.iter():
                for personal_field in personal_fields_app_xml:
                    associated_xml_tag = APP_XML_MAP[personal_field]
                    if (associated_xml_tag in xml_element.tag):
                        xml_element.text = config[personal_field]
            e_app.write(app_xml_path)

    modified = microsoft_file_name
    if not in_place:
        modified = microsoft_file_name[:microsoft_file_name.rfind('.')] + "_updated" + "." + microsoft_format
    with zipfile.ZipFile(modified, "w") as file:
        for file_name in source_file.namelist():
            file.write(os.path.join(unzipped_dir, file_name), file_name)
        file.close()
    shutil.rmtree(unzipped_dir)


def update_all(config_file_name, in_place=False):
    """
    Update all the editable metadata in any microsoft file in the current directory according to the given config file.

    :param config_file_name: name of .json config file
    :type config_file_name: str
    :param in_place: the `in_place` flag applies the changes directly to the original file
    :type in_place: bool
    :return: None
    """
    path = os.getcwd()
    dir_list = os.listdir(path)
    counter = {
        format: 0 for format in SUPPORTED_MICROSOFT_FORMATS
    }
    for file in dir_list:
        try:
            format = get_microsoft_format(file)
            update(config_file_name, file, in_place)
            counter[format] += 1
        except DMetaBaseError as e:
            e = e.__str__()
            if e == NOT_IMPLEMENTED_ERROR:
                print("DMeta couldn't update the metadata of {} since {}".format(file, NOT_IMPLEMENTED_ERROR))
            if e == FILE_FORMAT_DOES_NOT_EXIST_ERROR:
                print("Updating the metadata of {} failed because DMeta {}".format(file, FILE_FORMAT_DOES_NOT_EXIST_ERROR))
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
    if args.clear:
        clear(args.clear[0], args.inplace)
    elif args.clear_all:
        clear_all(args.inplace)
    elif args.update:
        if not args.config:
            raise DMetaBaseError(UPDATE_COMMAND_WITH_NO_CONFIG_FILE_ERROR)
        else:
            update(args.config[0], args.update[0], args.inplace)
    elif args.update_all:
        if not args.config:
            raise DMetaBaseError(UPDATE_COMMAND_WITH_NO_CONFIG_FILE_ERROR)
        else:
            update_all(args.config[0], args.inplace)
    else:
        tprint("DMeta")
        tprint("V:" + DMETA_VERSION)
        dmeta_help()
