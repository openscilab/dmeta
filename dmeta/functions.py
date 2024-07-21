# -*- coding: utf-8 -*-
"""DMeta functions."""
import os
import shutil
import zipfile
from art import tprint
from .util import get_microsoft_format, extract, read_json
import defusedxml.lxml as lxml


from .params import CORE_XML_MAP, APP_XML_MAP, OVERVIEW, DMETA_VERSION


def clear(microsoft_file_name):
    """
    Clear all the editable metadata in the given microsoft file.

    :param microsoft_file_name: name of microsoft file
    :type microsoft_file_name: str
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

    modified = microsoft_file_name[:microsoft_file_name.rfind('.')] + "_cleared"
    with zipfile.ZipFile(modified + "." + microsoft_format, "w") as file:
        for file_name in source_file.namelist():
            file.write(os.path.join(unzipped_dir, file_name), file_name)
        file.close()
    shutil.rmtree(unzipped_dir)


def clear_all():
    """
    Clear all the editable metadata in any microsoft file in the current directory.

    :return: None
    """
    path = os.getcwd()
    dir_list = os.listdir(path)
    microsoft_files = []
    for item in dir_list:
        if get_microsoft_format(item) is not None:
            microsoft_files.append(item)
    for microsoft_file in microsoft_files:
        clear(microsoft_file)


def update(config_file_name, microsoft_file_name):
    """
    Update all the editable metadata in the given microsoft file according to the given config file.

    :param config_file_name: name of .json config file
    :type config_file_name: str
    :param microsoft_file_name: name of microsoft file
    :type microsoft_file_name: str
    :return: None
    """
    config = read_json(config_file_name)
    personal_fields_core_xml = [e for e in CORE_XML_MAP.keys() if e in config]
    personal_fields_app_xml = [e for e in APP_XML_MAP.keys() if e in config]

    has_core_tags = len(personal_fields_core_xml) > 0
    has_app_tags = len(personal_fields_core_xml) > 0

    if not (has_core_tags or has_app_tags):
        print("There isn't any chosen personal field to remove")
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

    modified = microsoft_file_name[:microsoft_file_name.rfind('.')] + "_updated"
    with zipfile.ZipFile(modified + "." + microsoft_format, "w") as file:
        for file_name in source_file.namelist():
            file.write(os.path.join(unzipped_dir, file_name), file_name)
        file.close()
    shutil.rmtree(unzipped_dir)


def update_all(config_file_name):
    """
    Update all the editable metadata in any microsoft file in the current directory according to the given config file.

    :param config_file_name: name of .json config file
    :type config_file_name: str
    :return: None
    """
    path = os.getcwd()
    dir_list = os.listdir(path)
    microsoft_files = []
    for item in dir_list:
        if get_microsoft_format(item) is not None:
            microsoft_files.append(item)
    for microsoft_file in microsoft_files:
        update(config_file_name, microsoft_file)


def dmeta_help():
    """
    Print DMeta details.

    :return: None
    """
    print(OVERVIEW)
    print("Repo : https://github.com/openscilab/dmeta")
    print("Webpage : https://openscilab.com/")


def run_dmeta(args):
    """
    Run DMeta.

    :param args: input arguments
    :type args: argparse.Namespace
    :return: None
    """
    if args.clear:
        clear(args.clear[0])
    elif args.clear_all:
        clear_all()
    elif args.update:
        if not args.config:
            print("when using the `update` command, you should set the .json config file through the --config command")
        else:
            update(args.config[0], args.update[0])
    elif args.update_all:
        if not args.config:
            print("when using the `update-all` command, you should set the .json config file through the --config command")
        else:
            update_all(args.config[0])
    else:
        tprint("DMeta")
        tprint("V:" + DMETA_VERSION)
        dmeta_help()
