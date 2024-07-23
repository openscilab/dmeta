# -*- coding: utf-8 -*-
"""DMeta parameters and constants."""
DMETA_VERSION = "0.1"
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
NOT_IMPLEMENTED_ERROR = "Removing the meta data of this format is not yet supported by DMeta."
FILE_FORMAT_DOES_NOT_EXIST_ERROR = "Given file name doesn't have a specific format at the end."
INVALID_CONFIG_FILE_NAME_ERROR = "Given config file name should be str not the other type."
CONFIG_FILE_DOES_NOT_EXIST_ERROR = "Given config file doesn't exist."
UPDATE_COMMAND_WITH_NO_CONFIG_FILE_ERROR = "when using the `update`/`update-all` command, you should set the .json config file through the --config command"
