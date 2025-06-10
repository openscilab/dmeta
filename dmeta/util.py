# -*- coding: utf-8 -*-
"""utility module."""
import os
import json
from shutil import rmtree
from zipfile import ZipFile
from .params import SUPPORTED_MICROSOFT_FORMATS, INVALID_CONFIG_FILE_NAME_ERROR, CONFIG_FILE_DOES_NOT_EXIST_ERROR
from .errors import DMetaBaseError


def get_microsoft_format(file_name):
    """
    Extract format from the end of the given microsoft file name.

    :param file_name: name of the microsoft file name
    :type file_name: str
    :return: str
    """
    if not isinstance(file_name, str):
        return None
    last_dot_index = file_name.rfind('.')
    if (last_dot_index == -1):
        return None
    format = file_name[last_dot_index + 1:]
    if format not in SUPPORTED_MICROSOFT_FORMATS:
        return None
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
