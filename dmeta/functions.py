# -*- coding: utf-8 -*-
"""Dmeta Functions."""
import os
import shutil
import zipfile
from .util import remove_format, extract_docx, extract_namespaces, read_json 
import xml.etree.ElementTree as ET
from .params import PERSONAL_FIELDS_CORE_XML_CORRESPONDENCES, PERSONAL_FIELDS_APP_XML_CORRESPONDENCES

def clear(docx_file_name):
    """
    Clear all the editable metadata in the given .docx file.

    :param docx_file_name: name of .docx file
    :type docx_file_name: str
    :return: None
    """
    docx_file_name = remove_format(docx_file_name)
    unzipped_dir, source_file = extract_docx(docx_file_name)
    doc_props_dir = os.path.join(unzipped_dir,"docProps")
    core_xml_path = os.path.join(doc_props_dir,"core.xml")
    app_xml_path = os.path.join(doc_props_dir,"app.xml")

    core_xml_ns = extract_namespaces(core_xml_path)
    app_xml_ns = extract_namespaces(app_xml_path)
    
    for key, value in core_xml_ns.items():
        ET.register_namespace(key,value)

    for key, value in app_xml_ns.items():
        ET.register_namespace(key,value)

    e_core = ET.parse(core_xml_path)
    e_app = ET.parse(app_xml_path)

    for xml_element in e_core.iter():
        for personal_field in PERSONAL_FIELDS_CORE_XML_CORRESPONDENCES.keys():
            associated_xml_tag = PERSONAL_FIELDS_CORE_XML_CORRESPONDENCES[personal_field]
            if(associated_xml_tag in xml_element.tag):
                xml_element.text = ""
    e_core.write(core_xml_path,"utf-8", True, None, "xml")

    for xml_element in e_app.iter():
        for personal_field in PERSONAL_FIELDS_APP_XML_CORRESPONDENCES.keys():
            associated_xml_tag = PERSONAL_FIELDS_APP_XML_CORRESPONDENCES[personal_field]
            if(associated_xml_tag in xml_element.tag):
                xml_element.text = ""
    e_app.write(app_xml_path,"utf-8", True, None, "xml")
    
    modified_docx = "cleared_" + docx_file_name
    with zipfile.ZipFile(modified_docx + ".docx", "w") as docx:
        for file_name in source_file.namelist():
            docx.write(os.path.join(unzipped_dir, file_name), file_name)
        docx.close()
    shutil.rmtree(unzipped_dir)
