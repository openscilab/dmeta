# -*- coding: utf-8 -*-
"""DMeta parameters and constants."""
DMETA_VERSION = "0.4"
OVERVIEW = """
A Python library for removing personal metadata in Microsoft files(.docx, .pptx, .xlsx).

"""
CORE_XML_MAP = {
    # Description
    "title": "title",
    "subject": "subject",
    "tags": "keywords",
    "categories": "category",
    "comments": "description",

    # Origin
    "authors": "creator",
    "last saved by": "lastModifiedBy",
    "revision number": "revision",
    "version number": "version",

    # Content
    # we can't change "content type" field, it is automatically reset.
    "content status": "contentStatus",
    "language": "language",
}
APP_XML_MAP = {
    # Origin
    # we can't change "Application" field, it becomes a corrupted file.
    "program name": "Application",
    "company": "Company",
    "manager": "Manager"
}
SUPPORTED_MICROSOFT_FORMATS = [
    "docx",
    "pptx",
    "xlsx"
]
INVALID_CONFIG_FILE_NAME_ERROR = "Config file name is not a string."
CONFIG_FILE_DOES_NOT_EXIST_ERROR = "Given config file doesn't exist."
UPDATE_COMMAND_WITH_NO_CONFIG_FILE_ERROR = "No config file provided. Set the .json config file with --config command."
CLI_MORE_INFO = "For more information, visit the DMeta README at https://github.com/openscilab/dmeta"
