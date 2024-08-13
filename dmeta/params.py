# -*- coding: utf-8 -*-
"""DMeta parameters and constants."""
DMETA_VERSION = "0.2"
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
    "lastSavedBy": "lastModifiedBy",
    "revisionNumber": "revision",
    "versionNumber": "version",

    # Content
    # we can't change "content type" field, it is automatically reset.
    "contentStatus": "contentStatus",
    "language": "language",
}
APP_XML_MAP = {
    # Origin
    # we can't change "Application" field, it becomes a corrupted file.
    "programName": "Application",
    "company": "Company",
    "manager": "Manager"
}
SUPPORTED_MICROSOFT_FORMATS = [
    "docx",
    "pptx",
    "xlsx"
]
NOT_IMPLEMENTED_ERROR = "The file format is not supported."
FILE_FORMAT_DOES_NOT_EXIST_ERROR = "Failed to detect the file format. Make sure associated file has a proper extension (.docx, .pptx, etc.)."
INVALID_CONFIG_FILE_NAME_ERROR = "Config file name is not a string."
CONFIG_FILE_DOES_NOT_EXIST_ERROR = "Given config file doesn't exist."
UPDATE_COMMAND_WITH_NO_CONFIG_FILE_ERROR = "No config file provided. Set the .json config file with --config command."
