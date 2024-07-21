# -*- coding: utf-8 -*-
"""utility module."""
import os
import json
from shutil import rmtree
from zipfile import ZipFile
import defusedxml.ElementTree as ET


def extract_namespaces(xml_file_path):
    """
    Return used namespaces in the associated xml file.

    :param xml_file_path: path to the xml file
    :type xml_file_path: str
    :return: dict of namespaces[name: value]
    """
    namespaces = {}
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    # Extract namespaces from the root element
    for key, value in root.attrib.items():
        if key.startswith('xmlns:'):
            _, _, cropped_name = key.partition(':')
            namespaces[cropped_name] = value
        elif key == 'xmlns':
            namespaces['xmlns'] = value
    return namespaces


def remove_format(docx_file_name):
    """
    Remove the format from the end of the .docx file name.

    :param docx_file_name: name of .docx file
    :type docx_file_name: str
    :return: str (the .docx file name without format at the end)
    """
    last_dot_index = docx_file_name.rfind('.')
    if (last_dot_index != -1):
        docx_file_name = docx_file_name[:last_dot_index]
    return docx_file_name


def extract_docx(docx_file_name):
    """
    Zip and extract the .docx file.

    :param docx_file_name: name of .docx file
    :type docx_file_name: str
    :return: (str, ZipFile) as (unzipped directory, ZipFile instance to work with the extracted content)
    """
    docx_file_name = remove_format(docx_file_name)
    source_file = ZipFile(docx_file_name + ".docx")
    unzipped_dir = os.path.join(docx_file_name + "_unzipped")
    rmtree(unzipped_dir, ignore_errors=True)
    os.mkdir(unzipped_dir)
    source_file.extractall(unzipped_dir)
    return unzipped_dir, source_file


def read_json(config_file_name):
    """
    Read the config json file and return the python obj of it.

    :param config_file_name: name of .json file
    :type config_file_name: str
    :return: obj
    """
    if not isinstance(config_file_name, str):
        raise ("Given config file name should be str not the other type.")
    if ".json" not in config_file_name:
        config_file_name = config_file_name + ".json"
    if os.path.isfile(config_file_name):
        config_file = open(config_file_name)
        return json.load(config_file)
    else:
        raise ("Given config file doesn't exist.")
