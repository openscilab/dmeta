# -*- coding: utf-8 -*-
"""DMeta functions."""

import os
import shutil
import zipfile
from PIL import Image
import defusedxml.ElementTree as ET
from .util import get_file_format, extract, read_json
from .params import (
    CORE_XML_MAP,
    APP_XML_MAP,
    SUPPORTED_MICROSOFT_FORMATS,
    SUPPORTED_FORMATS,
    JPEG_MARKER_PREFIX,
    JPEG_SOI,
    JPEG_EOI,
    JPEG_SOS,
    JPEG_COM,
    JPEG_APP_FIRST,
    JPEG_APP_LAST,
    JPEG_STANDALONE_MARKERS,
    GIF_TRAILER,
    GIF_EXTENSION_INTRODUCER,
    GIF_IMAGE_DESCRIPTOR,
    GIF_EXT_GRAPHIC_CONTROL,
    GIF_EXT_APPLICATION,
    GIF_APP_EXT_NETSCAPE_IDENTIFIER,
)


def _output_path(source_file_path, in_place, suffix):
    """
    Determine the output path for a processed file.
    
    :param source_file_path: path to the source file
    :type source_file_path: str
    :param in_place: whether to modify the file in place
    :type in_place: bool
    :param suffix: suffix to add to the filename when not modifying in place
    :type suffix: str
    :return: path for the output file
    :rtype: str
    """
    if in_place:
        return source_file_path
    else:
        base, ext = os.path.splitext(source_file_path)
        return base + suffix + ext


def overwrite_metadata(xml_path, metadata=None, is_core=True):
    """
    Overwrite metadata in an XML file based on a predefined mapping.

    :param xml_path: path to the XML file to be updated
    :type xml_path: str
    :param metadata: a dictionary containing metadata to overwrite the XML elements with, or `None`
                     to reset
    :type metadata: dict
    :param is_core: a flag that indicates whether the given XML file is the core.xml file
    :type is_core: bool
    :return: None
    """
    xml_map = CORE_XML_MAP if is_core else APP_XML_MAP
    if os.path.exists(xml_path):
        # Parse XML file, make changes, and write back
        tree = ET.parse(xml_path)
        for xml_element in tree.iter():
            for personal_field in xml_map if metadata is None else metadata:
                associated_xml_tag = xml_map[personal_field]
                if associated_xml_tag in xml_element.tag:
                    xml_element.text = (
                        "" if metadata is None else metadata[personal_field]
                    )
        tree.write(xml_path)


def _cleanup_extracted(unzipped_dir, source_file, verbose):
    """Clean up extracted directory and close file handle."""
    # Ensure the source_file is closed before removing directory
    source_file.close()
    # On Windows, we may need to force garbage collection or add a small delay
    # to ensure file handles are fully released before removing the directory
    import gc

    gc.collect()  # Force garbage collection to release any remaining references
    try:
        shutil.rmtree(unzipped_dir)
    except PermissionError:
        # If we can't remove the directory immediately on Windows,
        # try again after a short delay
        import time

        time.sleep(0.1)
        try:
            shutil.rmtree(unzipped_dir)
        except PermissionError:
            # If it still fails, log the error but don't crash
            if verbose:
                print(
                    f"Warning: Could not remove temporary directory {unzipped_dir}, it may be cleaned up later"
                )


def _extract_and_prepare(source_file_path, verbose):
    """
    Extract the file and prepare the processing environment.
    
    :param source_file_path: path to the source file to process
    :type source_file_path: str
    :param verbose: whether to enable verbose output
    :type verbose: bool
    :return: tuple of (unzipped_dir, source_file, xml_paths_dict, microsoft_format)
    :rtype: tuple
    """
    # Validate format
    microsoft_format = get_file_format(source_file_path)
    if microsoft_format is None or microsoft_format not in SUPPORTED_MICROSOFT_FORMATS:
        return None, None, None, None

    # Extract the file
    unzipped_dir, source_file = extract(source_file_path)
    
    doc_props_dir = os.path.join(unzipped_dir, "docProps")
    core_xml_path = os.path.join(doc_props_dir, "core.xml")
    app_xml_path = os.path.join(doc_props_dir, "app.xml")
    
    xml_paths = {
        'core_xml_path': core_xml_path,
        'app_xml_path': app_xml_path
    }
    
    return unzipped_dir, source_file, xml_paths, microsoft_format


def _repack_and_cleanup(unzipped_dir, source_file, modified_path, verbose, process_type):
    """
    Repack the file into ZIP and perform cleanup.
    
    :param unzipped_dir: path to the unzipped directory
    :type unzipped_dir: str
    :param source_file: the opened source file object
    :type source_file: zipfile.ZipFile
    :param modified_path: path to the modified file to create
    :type modified_path: str
    :param verbose: whether to enable verbose output
    :type verbose: bool
    :param process_type: type of processing ('clear' or 'update')
    :type process_type: str
    :return: path to the modified file
    :rtype: str
    """
    # Re-zip the file
    with zipfile.ZipFile(modified_path, "w", compression=zipfile.ZIP_DEFLATED) as zip_file:
        for file_name in source_file.namelist():
            zip_file.write(os.path.join(unzipped_dir, file_name), file_name)

    if verbose:
        action = "cleared" if process_type == 'clear' else "updated"
        print(f"{action.capitalize()} metadata for: {modified_path}")

    return modified_path


def _process_metadata(source_file_path, in_place, verbose, process_type, **kwargs):
    """
    Shared function to process metadata in Microsoft files (clear/update)
    
    :param source_file_path: path to the source file to process
    :type source_file_path: str
    :param in_place: whether to modify the file in place
    :type in_place: bool
    :param verbose: whether to enable verbose output
    :type verbose: bool
    :param process_type: type of processing ('clear' or 'update')
    :type process_type: str
    :param kwargs: additional arguments for processing (e.g., new_metadata_dict for update)
    :return: path to the processed file or None if unsuccessful
    :rtype: str or None
    """
    # Extract and prepare
    unzipped_dir, source_file, xml_paths, microsoft_format = _extract_and_prepare(source_file_path, verbose)
    if xml_paths is None:
        return None
    
    core_xml_path = xml_paths['core_xml_path']
    app_xml_path = xml_paths['app_xml_path']

    try:
        # Define processing logic based on type
        if process_type == 'clear':
            # Define the clear-specific check function
            def is_metadata_cleared(xml_path, is_core=True):
                if not os.path.exists(xml_path):
                    return True
                tree = ET.parse(xml_path)
                xml_map = CORE_XML_MAP if is_core else APP_XML_MAP
                for xml_element in tree.iter():
                    for personal_field in xml_map:
                        associated_xml_tag = xml_map[personal_field]
                        if associated_xml_tag in xml_element.tag:
                            if xml_element.text and xml_element.text.strip():
                                return False
                return True

            # Check if metadata is already cleared
            core_cleared = is_metadata_cleared(core_xml_path)
            app_cleared = is_metadata_cleared(app_xml_path, is_core=False)

            if core_cleared and app_cleared:
                if verbose:
                    print(f"Metadata is already cleared for: {source_file_path}")
                return source_file_path  # Return the original file path when already cleared

            # Clear metadata if not already cleared
            overwrite_metadata(core_xml_path)
            overwrite_metadata(app_xml_path, is_core=False)

            # Determine output filename
            modified = _output_path(source_file_path, in_place, "_cleared")

        elif process_type == 'update':
            # Get the metadata from kwargs
            new_metadata_dict = kwargs.get('new_metadata_dict', {})
            personal_fields_core_xml = {
                k: new_metadata_dict[k] for k in CORE_XML_MAP.keys() if k in new_metadata_dict
            }
            personal_fields_app_xml = {k: new_metadata_dict[k] for k in APP_XML_MAP.keys() if k in new_metadata_dict}

            has_core_tags = len(personal_fields_core_xml) > 0
            has_app_tags = len(personal_fields_app_xml) > 0

            if not (has_core_tags or has_app_tags):
                print("There isn't any chosen personal field to remove.")
                return None

            # Define the update-specific check function
            def is_metadata_up_to_date(xml_path, metadata, is_core=True):
                if not os.path.exists(xml_path):
                    return False
                tree = ET.parse(xml_path)
                xml_map = CORE_XML_MAP if is_core else APP_XML_MAP
                for xml_element in tree.iter():
                    for personal_field in xml_map if metadata is None else metadata:
                        associated_xml_tag = xml_map[personal_field]
                        if associated_xml_tag in xml_element.tag:
                            if xml_element.text != metadata[personal_field]:
                                return False
                return True

            core_up_to_date = (
                is_metadata_up_to_date(core_xml_path, personal_fields_core_xml)
                if has_core_tags
                else True
            )
            app_up_to_date = (
                is_metadata_up_to_date(app_xml_path, personal_fields_app_xml)
                if has_app_tags
                else True
            )

            if core_up_to_date and app_up_to_date:
                if verbose:
                    print(f"Metadata is already up to date for: {source_file_path}")
                return source_file_path

            # Update metadata if not already up to date
            if has_core_tags:
                overwrite_metadata(core_xml_path, personal_fields_core_xml)
            if has_app_tags:
                overwrite_metadata(app_xml_path, personal_fields_app_xml, is_core=False)

            # Determine output filename
            modified = _output_path(source_file_path, in_place, "_updated")
        else:
            raise ValueError(f"Unknown process type: {process_type}")

        # Repack and cleanup
        result = _repack_and_cleanup(unzipped_dir, source_file, modified, verbose, process_type)
        return result

    finally:
        _cleanup_extracted(unzipped_dir, source_file, verbose)


def clear(microsoft_file_name, in_place=False, verbose=False):
    """
    Clear all the editable metadata in the given Microsoft file.

    :param microsoft_file_name: name of Microsoft file
    :type microsoft_file_name: str
    :param in_place: the `in_place` flag applies the changes directly to the original file
    :type in_place: bool
    :param verbose: the `verbose` flag enables detailed output
    :type verbose: bool
    :return: path to the cleared file if successful, None if format is unsupported,
             or original file path if metadata is already cleared
    :rtype: str or None
    """
    return _process_metadata(microsoft_file_name, in_place, verbose, 'clear')


def clear_all(in_place=False, verbose=False):
    """
    Clear all the editable metadata in any supported file in the current directory and its subdirectories.

    :param in_place: the `in_place` flag applies the changes directly to the original file
    :type in_place: bool
    :param verbose: the `verbose` flag enables detailed output
    :type verbose: bool
    :return: None
    """
    path = os.getcwd()
    counter = {fmt: 0 for fmt in SUPPORTED_FORMATS}

    for root, _, files in os.walk(path):
        for file in files:
            fmt = get_file_format(file)
            if fmt is None:
                continue
            clear_file(os.path.join(root, file), in_place, verbose)
            counter[fmt] += 1

    if verbose:
        for fmt in counter.keys():
            print(
                "Metadata of {} files with the format of {} has been cleared.".format(
                    counter[fmt], fmt
                )
            )


def update(config_file_name, microsoft_file_name, in_place=False, verbose=False):
    """
    Update all the editable metadata in the given Microsoft file according to the given config file.

    :param config_file_name: name of .json config file
    :type config_file_name: str
    :param microsoft_file_name: name of Microsoft file
    :type microsoft_file_name: str
    :param in_place: the `in_place` flag applies the changes directly to the original file
    :type in_place: bool
    :param verbose: the `verbose` flag enables detailed output
    :type verbose: bool
    :return: path to the updated file if successful, None if format is unsupported
    :rtype: str or None
    """
    config = read_json(config_file_name)
    return _process_metadata(microsoft_file_name, in_place, verbose, 'update', new_metadata_dict=config)


def update_all(config_file_name, in_place=False, verbose=False):
    """
    Update all the editable metadata in any Microsoft file in the current directory and its subdirectories according to the given config file.

    :param config_file_name: name of .json config file
    :type config_file_name: str
    :param in_place: the `in_place` flag applies the changes directly to the original file
    :type in_place: bool
    :param verbose: the `verbose` flag enables detailed output
    :type verbose: bool
    :return: None
    """
    path = os.getcwd()
    counter = {format: 0 for format in SUPPORTED_MICROSOFT_FORMATS}

    for root, _, files in os.walk(path):
        for file in files:
            fmt = get_file_format(file)
            if fmt is None or fmt not in SUPPORTED_MICROSOFT_FORMATS:
                continue
            update(config_file_name, os.path.join(root, file), in_place, verbose)
            counter[fmt] += 1

    if verbose:
        for format in counter.keys():
            print(
                "Metadata of {} files with the format of {} has been updated.".format(
                    counter[format], format
                )
            )


def clear_png_metadata(png_file_name, in_place=False, verbose=False):
    """
    Remove all metadata from a PNG file using Pillow.

    :param png_file_name: path to original PNG file
    :type png_file_name: str
    :param in_place: if True, overwrite the original file with cleaned version
    :type in_place: bool
    :param verbose: if True, print detailed output
    :type verbose: bool
    :return: path to cleaned PNG file
    """
    if not os.path.exists(png_file_name) or not png_file_name.lower().endswith(".png"):
        return

    if in_place:
        output_path = png_file_name
    else:
        base, ext = os.path.splitext(png_file_name)
        output_path = base + "_cleaned" + ext

    # Remove metadata
    with Image.open(png_file_name) as img:
        # Copy the image to strip all metadata while preserving pixel data,
        # palette (for "P" mode), and alpha channel (for "RGBA"/"LA" etc.).
        clean_img = img.copy()
        clean_img.save(output_path, format="PNG")

    if verbose:
        action = "overwritten" if in_place else f"saved to {output_path}"
        print(f"Metadata cleared for: {png_file_name} ({action})")

    return output_path


def clear_jpeg_metadata(jpeg_file_name, in_place=False, verbose=False):
    """
    Remove all metadata from a JPEG file without re-encoding pixel data.

    :param jpeg_file_name: path to original JPEG file
    :type jpeg_file_name: str
    :param in_place: if True, overwrite the original file with cleaned version
    :type in_place: bool
    :param verbose: if True, print detailed output
    :type verbose: bool
    :return: path to cleaned JPEG file
    """
    if not os.path.exists(jpeg_file_name) or not jpeg_file_name.lower().endswith(
        (".jpg", ".jpeg")
    ):
        return

    with open(jpeg_file_name, "rb") as f:
        data = f.read()
    soi = bytes([JPEG_MARKER_PREFIX, JPEG_SOI])
    if not data.startswith(soi):
        return

    # Walk JPEG segments per ITU-T T.81 and drop APPn + COM (metadata holders).
    out = bytearray(soi)
    i, n = 2, len(data)
    while i < n:
        while i < n and data[i] == JPEG_MARKER_PREFIX:
            i += 1
        if i >= n:
            break
        marker = data[i]
        i += 1
        if marker in JPEG_STANDALONE_MARKERS:
            out += bytes([JPEG_MARKER_PREFIX, marker])
            if marker == JPEG_EOI:
                break
            continue
        length = (data[i] << 8) | data[i + 1]
        payload = data[i : i + length]
        i += length
        if JPEG_APP_FIRST <= marker <= JPEG_APP_LAST or marker == JPEG_COM:
            continue
        out += bytes([JPEG_MARKER_PREFIX, marker]) + payload
        if marker == JPEG_SOS:
            out += data[i:]
            break

    if in_place:
        output_path = jpeg_file_name
    else:
        base, ext = os.path.splitext(jpeg_file_name)
        output_path = base + "_cleaned" + ext

    with open(output_path, "wb") as f:
        f.write(bytes(out))

    if verbose:
        action = "overwritten" if in_place else f"saved to {output_path}"
        print(f"Metadata cleared for: {jpeg_file_name} ({action})")

    return output_path


def clear_gif_metadata(gif_file_name, in_place=False, verbose=False):
    """
    Remove all metadata from a GIF file without re-encoding pixel data.

    Preserves per-frame Graphic Control and NETSCAPE2.0 loop blocks; removes
    Comment, Plain Text, and all other Application Extensions.

    :param gif_file_name: path to original GIF file
    :type gif_file_name: str
    :param in_place: if True, overwrite the original file with cleaned version
    :type in_place: bool
    :param verbose: if True, print detailed output
    :type verbose: bool
    :return: path to cleaned GIF file
    """
    if not os.path.exists(gif_file_name) or not gif_file_name.lower().endswith(".gif"):
        return

    with open(gif_file_name, "rb") as f:
        data = f.read()
    if not (data.startswith(b"GIF87a") or data.startswith(b"GIF89a")):
        return

    n = len(data)

    def skip_sub_blocks(start):
        j = start
        while j < n:
            size = data[j]
            j += 1
            if size == 0:
                return j
            j += size
        return j

    # Header + Logical Screen Descriptor + optional Global Color Table.
    out = bytearray(data[:13])
    packed = data[10]
    i = 13
    if packed & 0x80:
        gct = 3 * (1 << ((packed & 0x07) + 1))
        out += data[i : i + gct]
        i += gct

    # Walk data stream per GIF89a; drop metadata-bearing extensions only.
    while i < n:
        b = data[i]
        if b == GIF_TRAILER:
            out += bytes([GIF_TRAILER])
            break
        if b == GIF_EXTENSION_INTRODUCER and i + 1 < n:
            label = data[i + 1]
            if label == GIF_EXT_GRAPHIC_CONTROL:
                out += data[i : i + 8]
                i += 8
            elif label == GIF_EXT_APPLICATION and i + 2 < n:
                ident_len = data[i + 2]
                ident = data[i + 3 : i + 3 + ident_len]
                j = skip_sub_blocks(i + 3 + ident_len)
                if ident == GIF_APP_EXT_NETSCAPE_IDENTIFIER:
                    out += data[i:j]
                i = j
            else:
                # Comment, Plain Text, and any other extension carry metadata: drop.
                i = skip_sub_blocks(i + 2)
        elif b == GIF_IMAGE_DESCRIPTOR and i + 10 <= n:
            packed2 = data[i + 9]
            j = i + 10
            if packed2 & 0x80:
                j += 3 * (1 << ((packed2 & 0x07) + 1))
            j += 1  # LZW minimum code size
            j = skip_sub_blocks(j)
            out += data[i:j]
            i = j
        else:
            break

    if in_place:
        output_path = gif_file_name
    else:
        base, ext = os.path.splitext(gif_file_name)
        output_path = base + "_cleaned" + ext

    with open(output_path, "wb") as f:
        f.write(bytes(out))

    if verbose:
        action = "overwritten" if in_place else f"saved to {output_path}"
        print(f"Metadata cleared for: {gif_file_name} ({action})")

    return output_path


def extract_metadata(microsoft_file_name):
    """
    Extract metadata from the given Microsoft file.

    :param microsoft_file_name: name of Microsoft file
    :type microsoft_file_name: str
    :return: dictionary containing the metadata fields
    :rtype: dict
    """
    microsoft_format = get_file_format(microsoft_file_name)
    if microsoft_format is None or microsoft_format not in SUPPORTED_MICROSOFT_FORMATS:
        return {}

    unzipped_dir, source_file = extract(microsoft_file_name)

    try:
        doc_props_dir = os.path.join(unzipped_dir, "docProps")
        core_xml_path = os.path.join(doc_props_dir, "core.xml")
        app_xml_path = os.path.join(doc_props_dir, "app.xml")

        metadata = {}
        
        # Extract from core.xml
        if os.path.exists(core_xml_path):
            tree = ET.parse(core_xml_path)
            for xml_element in tree.iter():
                for personal_field, associated_xml_tag in CORE_XML_MAP.items():
                    if associated_xml_tag in xml_element.tag:
                        metadata[personal_field] = xml_element.text or ""
        
        # Extract from app.xml
        if os.path.exists(app_xml_path):
            tree = ET.parse(app_xml_path)
            for xml_element in tree.iter():
                for personal_field, associated_xml_tag in APP_XML_MAP.items():
                    if associated_xml_tag in xml_element.tag:
                        metadata[personal_field] = xml_element.text or ""

        return metadata
    finally:
        _cleanup_extracted(unzipped_dir, source_file, False)  # Using the existing cleanup function

CLEAR_HANDLERS = {
    "docx": clear,
    "pptx": clear,
    "xlsx": clear,
    "png": clear_png_metadata,
    "jpg": clear_jpeg_metadata,
    "jpeg": clear_jpeg_metadata,
    "gif": clear_gif_metadata,
}


def clear_file(file_name, in_place=False, verbose=False):
    """
    Clear all metadata from the given file based on its format.

    :param file_name: path to the file
    :type file_name: str
    :param in_place: applies changes directly to the original file
    :type in_place: bool
    :param verbose: enables detailed output
    :type verbose: bool
    :return: path to the cleared file, or None if format is unsupported
    :rtype: str or None
    """
    fmt = get_file_format(file_name)
    if fmt is None:
        return None
    handler = CLEAR_HANDLERS.get(fmt)
    if handler is None:
        return None
    return handler(file_name, in_place, verbose)