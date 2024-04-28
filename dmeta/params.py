# -*- coding: utf-8 -*-
"""dmeta Parameters and constants."""
DMETA_VERSION = "0.1"
OVERVIEW = """
A Python library for removing personal metadata in Microsoft files(.docx, .pptx, .xlsx).

"""
CORE_XML_MAP = {
    #Description
    "title" : "title",
    "subject": "subject",
    "tags": "keywords",
    "categories": "category",
    "comments": "description",

    #Origin
    "authors": "creator",
    "lastSavedBy": "lastModifiedBy",
    "revisionNumber": "revision",
    "versionNumber": "version",

    #Content
    # we can't change "content type" field, it is automatically reset.
    "contentStatus": "contentStatus",
    "language": "language",
}
APP_XML_MAP = {
    #Origin 
    #we can't change "Application" field, it becomes a corrupted file.
    "programName": "Application",
    "company": "Company",
    "manager": "Manager"
}