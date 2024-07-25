# -*- coding: utf-8 -*-
"""utility module."""
import os
import json
from shutil import rmtree
from zipfile import ZipFile
import defusedxml.ElementTree as ET
from .params import SUPPORTED_MICROSOFT_FORMATS, NOT_IMPLEMENTED_ERROR, \
    FILE_FORMAT_DOES_NOT_EXIST_ERROR, INVALID_CONFIG_FILE_NAME_ERROR, CONFIG_FILE_DOES_NOT_EXIST_ERROR
from .errors import DMetaBaseError


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


def get_microsoft_format(file_name):
    """
    Extract format from the end of the given microsoft file name.

    :param file_name: name of the microsoft file name
    :type file_name: str
    :return: str
    """
    last_dot_index = file_name.rfind('.')
    if (last_dot_index == -1):
        raise DMetaBaseError(FILE_FORMAT_DOES_NOT_EXIST_ERROR)
    format = file_name[last_dot_index + 1:]
    if format not in SUPPORTED_MICROSOFT_FORMATS:
        raise DMetaBaseError(NOT_IMPLEMENTED_ERROR)
    return format


def extract(file_name):
    """
    Zip and extract the microsoft file.

    :param file_name: name of microsoft file
    :type file_name: str
    :return: (str, ZipFile) as (unzipped directory, ZipFile instance to work with the extracted content)
    """
    source_file = ZipFile(file_name)
    unzipped_dir = os.path.join(file_name[:file_name.rfind(".")] + "_unzipped")
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
        raise DMetaBaseError(INVALID_CONFIG_FILE_NAME_ERROR)
    if ".json" not in config_file_name:
        config_file_name = config_file_name + ".json"
    if os.path.isfile(config_file_name):
        config_file = open(config_file_name)
        return json.load(config_file)
    else:
        raise DMetaBaseError(CONFIG_FILE_DOES_NOT_EXIST_ERROR)
