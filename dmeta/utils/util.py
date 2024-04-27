# -*- coding: utf-8 -*-
"""utility module."""
import os
import json
from shutil import rmtree
from zipfile import ZipFile
import xml.dom.minidom as minidom


def extract_namespaces(xml_file_path):
    """
    Return used namespaces in the associated xml file.

    :param xml_file_path: path to the xml file
    :type xml_file_path: str
    :return: dict of namespaces[name: value]
    """
    namespaces = {}
    doc = minidom.parse(xml_file_path)
    root_child = doc.firstChild
    for namespace_name in root_child._attrs:
        xmlns, _, cropped_name = namespace_name.partition(":")
        if not xmlns == "xmlns":
            cropped_name = namespace_name
        namespaces[cropped_name] = root_child._attrs[namespace_name].value
    return namespaces
