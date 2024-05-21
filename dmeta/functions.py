# -*- coding: utf-8 -*-
"""DMeta functions."""
import os
import shutil
import zipfile
from .util import remove_format, extract_docx, extract_namespaces, read_json
import defusedxml.ElementTree as ET
from .params import CORE_XML_MAP, APP_XML_MAP, OVERVIEW


def clear(docx_file_name):
    """
    Clear all the editable metadata in the given .docx file.

    :param docx_file_name: name of .docx file
    :type docx_file_name: str
    :return: None
    """
    docx_file_name = remove_format(docx_file_name)
    unzipped_dir, source_file = extract_docx(docx_file_name)
    doc_props_dir = os.path.join(unzipped_dir, "docProps")
    core_xml_path = os.path.join(doc_props_dir, "core.xml")
    app_xml_path = os.path.join(doc_props_dir, "app.xml")

    e_core = ET.parse(core_xml_path)
    e_app = ET.parse(app_xml_path)

    for xml_element in e_core.iter():
        for personal_field in CORE_XML_MAP.keys():
            associated_xml_tag = CORE_XML_MAP[personal_field]
            if (associated_xml_tag in xml_element.tag):
                xml_element.text = ""
    e_core.write(core_xml_path, "utf-8", True, None, "xml")

    for xml_element in e_app.iter():
        for personal_field in APP_XML_MAP.keys():
            associated_xml_tag = APP_XML_MAP[personal_field]
            if (associated_xml_tag in xml_element.tag):
                xml_element.text = ""
    e_app.write(app_xml_path, "utf-8", True, None, "xml")

    modified_docx = docx_file_name + "_cleared"
    with zipfile.ZipFile(modified_docx + ".docx", "w") as docx:
        for file_name in source_file.namelist():
            docx.write(os.path.join(unzipped_dir, file_name), file_name)
        docx.close()
    shutil.rmtree(unzipped_dir)


def clear_all():
    """
    Clear all the editable metadata in any .docx file in the current directory.

    :return: None
    """
    path = os.getcwd()
    dir_list = os.listdir(path)
    docx_files = []
    for item in dir_list:
        if ".docx" in item:
            docx_files.append(item)
    for docx_file in docx_files:
        clear(docx_file)


def update(config_file_name, docx_file_name):
    """
    Update all the editable metadata in the given .docx file according to the given config file.

    :param config_file_name: name of .json config file
    :type config_file_name: str
    :param docx_file_name: name of .docx file
    :type docx_file_name: str
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

    docx_file_name = remove_format(docx_file_name)
    unzipped_dir, source_file = extract_docx(docx_file_name)
    doc_props_dir = os.path.join(unzipped_dir, "docProps")
    core_xml_path = os.path.join(doc_props_dir, "core.xml")
    app_xml_path = os.path.join(doc_props_dir, "app.xml")

    if has_core_tags:
        e_core = ET.parse(core_xml_path)
        for xml_element in e_core.iter():
            for personal_field in personal_fields_core_xml:
                associated_xml_tag = CORE_XML_MAP[personal_field]
                if (associated_xml_tag in xml_element.tag):
                    xml_element.text = config[personal_field]
        e_core.write(core_xml_path, "utf-8", True, None, "xml")

    if has_app_tags:
        e_app = ET.parse(app_xml_path)
        for xml_element in e_app.iter():
            for personal_field in personal_fields_app_xml:
                associated_xml_tag = APP_XML_MAP[personal_field]
                if (associated_xml_tag in xml_element.tag):
                    xml_element.text = config[personal_field]
        e_app.write(app_xml_path, "utf-8", True, None, "xml")

    modified_docx = docx_file_name + "_updated" 
    with zipfile.ZipFile(modified_docx + ".docx", "w") as docx:
        for filename in source_file.namelist():
            docx.write(os.path.join(unzipped_dir, filename), filename)
    shutil.rmtree(unzipped_dir)


def update_all(config_file_name):
    """
    Update all the editable metadata in any .docx file in the current directory according to the given config file.

    :param config_file_name: name of .json config file
    :type config_file_name: str
    :return: None
    """
    path = os.getcwd()
    dir_list = os.listdir(path)
    docx_files = []
    for item in dir_list:
        if ".docx" in item:
            docx_files.append(item)
    for docx_file in docx_files:
        update(config_file_name, docx_file)


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
