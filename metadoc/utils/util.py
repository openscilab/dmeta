# -*- coding: utf-8 -*-
"""utility module."""
import os.path 
import shutil
import zipfile

def zip_and_extract(docx_file_name):

    if ".docx" in docx_file_name:
        source_file = zipfile.ZipFile(docx_file_name)
    else:
        source_file = zipfile.ZipFile(docx_file_name + ".docx")
    public_dir = os.getcwd() 
    unzipped_dir = os.path.join(public_dir, "unzipped_" + docx_file_name)
    shutil.rmtree(unzipped_dir, ignore_errors=True)
    os.mkdir(unzipped_dir)
    source_file.extractall(unzipped_dir)
    source_file.close()

    return unzipped_dir,source_file