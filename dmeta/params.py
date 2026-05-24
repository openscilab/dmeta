# -*- coding: utf-8 -*-
"""DMeta parameters and constants."""
DMETA_VERSION = "0.5"
OVERVIEW = """
A Python library for removing personal metadata in Microsoft files(.docx, .pptx, .xlsx) and image files(.png, .jpg, .jpeg, .gif).

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
SUPPORTED_IMAGE_FORMATS = [
    "png",
    "jpg",
    "jpeg",
    "gif"
]
SUPPORTED_FORMATS = SUPPORTED_MICROSOFT_FORMATS + SUPPORTED_IMAGE_FORMATS
# JPEG marker codes per ITU-T T.81.
JPEG_MARKER_PREFIX = 0xFF
JPEG_SOI = 0xD8                                                 # Start Of Image
JPEG_EOI = 0xD9                                                 # End Of Image
JPEG_SOS = 0xDA                                                 # Start Of Scan
JPEG_COM = 0xFE                                                 # Comment
JPEG_APP_FIRST, JPEG_APP_LAST = 0xE0, 0xEF                      # APP0..APP15
JPEG_STANDALONE_MARKERS = frozenset({0x00, 0x01, JPEG_SOI, JPEG_EOI} | set(range(0xD0, 0xD8)))

# GIF block markers per GIF89a specification.
GIF_TRAILER = 0x3B
GIF_EXTENSION_INTRODUCER = 0x21
GIF_IMAGE_DESCRIPTOR = 0x2C
GIF_EXT_GRAPHIC_CONTROL = 0xF9                                  # per-frame timing (kept)
GIF_EXT_APPLICATION = 0xFF
GIF_APP_EXT_NETSCAPE_IDENTIFIER = b"NETSCAPE2.0"                # animation loop (kept)
INVALID_CONFIG_FILE_NAME_ERROR = "Config file name is not a string."
CONFIG_FILE_DOES_NOT_EXIST_ERROR = "Given config file doesn't exist."
UPDATE_COMMAND_WITH_NO_CONFIG_FILE_ERROR = "No config file provided. Set the .json config file with --config command."
CLI_MORE_INFO = "For more information, visit the DMeta README at https://github.com/openscilab/dmeta"
