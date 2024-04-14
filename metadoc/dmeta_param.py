# -*- coding: utf-8 -*-
"""Dmeta Parameters and constants."""
DMETA_VERSION = "0.1"

PERSONAL_FIELDS_CORE_XML_CORRESPONDENCES = {
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

PERSONAL_FIELDS_APP_XML_CORRESPONDENCES = {
    #Origin 
    #we can't change "Application" field, it becomes a corrupted file.
    "programName": "Application",
    "company": "Company",
    "manager": "Manager"
}