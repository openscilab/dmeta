# -*- coding: utf-8 -*-
"""DMeta functions."""
import os
import shutil
import zipfile
from PIL import Image
from art import tprint
from lxml import etree as lxml
from .errors import DMetaBaseError
from .util import get_file_format, extract, read_json
from .params import CORE_XML_MAP, APP_XML_MAP, OVERVIEW, DMETA_VERSION, \
    UPDATE_COMMAND_WITH_NO_CONFIG_FILE_ERROR, \
    SUPPORTED_MICROSOFT_FORMATS, SUPPORTED_FORMATS, \
    JPEG_MARKER_PREFIX, JPEG_SOI, JPEG_EOI, JPEG_SOS, JPEG_COM, \
    JPEG_APP_FIRST, JPEG_APP_LAST, JPEG_STANDALONE_MARKERS, \
    GIF_TRAILER, GIF_EXTENSION_INTRODUCER, GIF_IMAGE_DESCRIPTOR, \
    GIF_EXT_GRAPHIC_CONTROL, GIF_EXT_APPLICATION, \
    GIF_APP_EXT_NETSCAPE_IDENTIFIER, \
    MP3_ID3V2_MAGIC, MP3_ID3V1_MAGIC, MP3_ID3V1_SIZE, MP3_ID3V2_HEADER_SIZE, \
    MP3_ID3V2_FOOTER_FLAG, MP3_APE_MAGIC, MP3_APE_HEADER_SIZE, \
    MP3_APE_HAS_HEADER_FLAG, MP3_APE_IS_HEADER_FLAG, \
    MP3_LYRICS3V2_TAIL, MP3_LYRICS3V1_TAIL, MP3_LYRICS3V1_BEGIN, \
    FLAC_MAGIC, FLAC_BLOCK_HEADER_SIZE, FLAC_STREAMINFO_TYPE, FLAC_STREAMINFO_SIZE


def overwrite_metadata(
        xml_path,
        metadata=None,
        is_core=True):
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
        e_core = lxml.parse(xml_path)
        for xml_element in e_core.iter():
            for personal_field in xml_map if metadata is None else metadata:
                associated_xml_tag = xml_map[personal_field]
                if (associated_xml_tag in xml_element.tag):
                    xml_element.text = "" if metadata is None else metadata[personal_field]
        e_core.write(xml_path)


def clear(microsoft_file_name, in_place=False, verbose=False):
    """
    Clear all the editable metadata in the given Microsoft file.

    :param microsoft_file_name: name of Microsoft file
    :type microsoft_file_name: str
    :param in_place: the `in_place` flag applies the changes directly to the original file
    :type in_place: bool
    :param verbose: the `verbose` flag enables detailed output
    :type verbose: bool
    :return: None
    """
    microsoft_format = get_file_format(microsoft_file_name)
    if microsoft_format is None or microsoft_format not in SUPPORTED_MICROSOFT_FORMATS:
        return
    unzipped_dir, source_file = extract(microsoft_file_name)
    doc_props_dir = os.path.join(unzipped_dir, "docProps")
    core_xml_path = os.path.join(doc_props_dir, "core.xml")
    app_xml_path = os.path.join(doc_props_dir, "app.xml")

    def is_metadata_cleared(xml_path, is_core=True):
        if not os.path.exists(xml_path):
            return True
        tree = lxml.parse(xml_path)
        xml_map = CORE_XML_MAP if is_core else APP_XML_MAP
        for xml_element in tree.iter():
            for personal_field in xml_map:
                associated_xml_tag = xml_map[personal_field]
                if (associated_xml_tag in xml_element.tag):
                    if xml_element.text and xml_element.text.strip():
                        return False
        return True

    core_cleared = is_metadata_cleared(core_xml_path)
    app_cleared = is_metadata_cleared(app_xml_path, is_core=False)

    if core_cleared and app_cleared:
        if verbose:
            print(f"Metadata is already cleared for: {microsoft_file_name}")
        shutil.rmtree(unzipped_dir)
        return

    # Clear metadata if not already cleared
    overwrite_metadata(core_xml_path)
    overwrite_metadata(app_xml_path, is_core=False)

    modified = microsoft_file_name
    if not in_place:
        modified = microsoft_file_name[:microsoft_file_name.rfind('.')] + "_cleared" + "." + microsoft_format
    with zipfile.ZipFile(modified, "w", compression=zipfile.ZIP_DEFLATED) as file:
        for file_name in source_file.namelist():
            file.write(os.path.join(unzipped_dir, file_name), file_name)
        file.close()
    shutil.rmtree(unzipped_dir)

    if verbose:
        print(f"Cleared metadata for: {microsoft_file_name}")

    return modified


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
    counter = {
        fmt: 0 for fmt in SUPPORTED_FORMATS
    }

    for root, _, files in os.walk(path):
        for file in files:
            fmt = get_file_format(file)
            if fmt is None:
                continue
            clear_file(os.path.join(root, file), in_place, verbose)
            counter[fmt] += 1

    if verbose:
        for fmt in counter.keys():
            print("Metadata of {} files with the format of {} has been cleared.".format(counter[fmt], fmt))


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
    :return: None
    """
    config = read_json(config_file_name)
    personal_fields_core_xml = {k: config[k] for k in CORE_XML_MAP.keys() if k in config}
    personal_fields_app_xml = {k: config[k] for k in APP_XML_MAP.keys() if k in config}

    has_core_tags = len(personal_fields_core_xml) > 0
    has_app_tags = len(personal_fields_app_xml) > 0

    if not (has_core_tags or has_app_tags):
        print("There isn't any chosen personal field to remove.")
        return

    microsoft_format = get_file_format(microsoft_file_name)
    if microsoft_format is None or microsoft_format not in SUPPORTED_MICROSOFT_FORMATS:
        return

    unzipped_dir, source_file = extract(microsoft_file_name)
    doc_props_dir = os.path.join(unzipped_dir, "docProps")
    core_xml_path = os.path.join(doc_props_dir, "core.xml")
    app_xml_path = os.path.join(doc_props_dir, "app.xml")

    # Check if metadata is already up to date
    def is_metadata_up_to_date(xml_path, metadata, is_core=True):
        if not os.path.exists(xml_path):
            return False
        tree = lxml.parse(xml_path)
        xml_map = CORE_XML_MAP if is_core else APP_XML_MAP
        for xml_element in tree.iter():
            for personal_field in xml_map if metadata is None else metadata:
                associated_xml_tag = xml_map[personal_field]
                if (associated_xml_tag in xml_element.tag):
                    if xml_element.text != metadata[personal_field]:
                        return False
        return True

    core_up_to_date = is_metadata_up_to_date(core_xml_path, personal_fields_core_xml) if has_core_tags else True
    app_up_to_date = is_metadata_up_to_date(app_xml_path, personal_fields_app_xml) if has_app_tags else True

    if core_up_to_date and app_up_to_date:
        if verbose:
            print(f"Metadata is already up to date for: {microsoft_file_name}")
        shutil.rmtree(unzipped_dir)
        return

    # Update metadata if not already up to date
    if has_core_tags:
        overwrite_metadata(core_xml_path, personal_fields_core_xml)
    if has_app_tags:
        overwrite_metadata(app_xml_path, personal_fields_app_xml, is_core=False)

    modified = microsoft_file_name
    if not in_place:
        modified = microsoft_file_name[:microsoft_file_name.rfind('.')] + "_updated" + "." + microsoft_format
    with zipfile.ZipFile(modified, "w", compression=zipfile.ZIP_DEFLATED) as file:
        for file_name in source_file.namelist():
            file.write(os.path.join(unzipped_dir, file_name), file_name)
        file.close()
    shutil.rmtree(unzipped_dir)

    if verbose:
        print(f"Updated metadata for: {microsoft_file_name}")

    return modified


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
    counter = {
        format: 0 for format in SUPPORTED_MICROSOFT_FORMATS
    }

    for root, _, files in os.walk(path):
        for file in files:
            fmt = get_file_format(file)
            if fmt is None or fmt not in SUPPORTED_MICROSOFT_FORMATS:
                continue
            update(config_file_name, os.path.join(root, file), in_place, verbose)
            counter[fmt] += 1

    if verbose:
        for format in counter.keys():
            print("Metadata of {} files with the format of {} has been updated.".format(counter[format], format))


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
        clean_img = Image.new(img.mode, img.size)
        clean_img.putdata(list(img.getdata()))
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
    if not os.path.exists(jpeg_file_name) or not jpeg_file_name.lower().endswith((".jpg", ".jpeg")):
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
        payload = data[i:i + length]
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
        out += data[i:i + gct]
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
                out += data[i:i + 8]
                i += 8
            elif label == GIF_EXT_APPLICATION and i + 2 < n:
                ident_len = data[i + 2]
                ident = data[i + 3:i + 3 + ident_len]
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


def _id3_synchsafe_to_int(size_bytes):
    """
    Decode a 4-byte ID3v2 synchsafe integer.

    Per ID3v2.3 / ID3v2.4, each byte contributes 7 bits (MSB must be 0).
    """
    value = 0
    for byte in size_bytes:
        value = (value << 7) | (byte & 0x7F)
    return value


def _mp3_id3v2_len(data, offset=0):
    """
    Return byte length of an ID3v2 tag at offset, or 0 if absent/invalid.

    Layout (ID3v2.3 / ID3v2.4): "ID3" + version(2) + flags(1) + size(4 synchsafe)
    + frames; optional 10-byte footer when flags bit 0x10 is set (ID3v2.4).
    """
    if offset + MP3_ID3V2_HEADER_SIZE > len(data):
        return 0
    if data[offset:offset + 3] != MP3_ID3V2_MAGIC:
        return 0
    flags = data[offset + 5]
    body = _id3_synchsafe_to_int(data[offset + 6:offset + 10])
    footer = MP3_ID3V2_HEADER_SIZE if (flags & MP3_ID3V2_FOOTER_FLAG) else 0
    total = MP3_ID3V2_HEADER_SIZE + body + footer
    if offset + total > len(data):
        return 0
    return total


def _mp3_ape_tag_len_from_footer(data, footer_end):
    """
    Return (start, end) of an APEv2 tag ending at footer_end, or None.

    APEv2 preamble (32 bytes, "APETAGEX") appears as footer and optionally as
    header; size field counts items + footer, not a preceding header.
    """
    if footer_end < MP3_APE_HEADER_SIZE:
        return None
    footer = data[footer_end - MP3_APE_HEADER_SIZE:footer_end]
    if footer[:8] != MP3_APE_MAGIC:
        return None
    # size at bytes 12..15 little-endian: items + footer
    tag_size = int.from_bytes(footer[12:16], "little")
    flags = int.from_bytes(footer[20:24], "little")
    if flags & MP3_APE_IS_HEADER_FLAG:
        return None
    start = footer_end - tag_size
    if flags & MP3_APE_HAS_HEADER_FLAG:
        start -= MP3_APE_HEADER_SIZE
    if start < 0:
        return None
    return start, footer_end


def _mp3_strip_leading_tags(data):
    """Strip leading ID3v2 and APEv2 tags; return audio-start offset."""
    offset = 0
    id3_len = _mp3_id3v2_len(data, offset)
    if id3_len:
        offset += id3_len
    # Rare leading APEv2 (header preamble at start).
    if offset + MP3_APE_HEADER_SIZE <= len(data) and data[offset:offset + 8] == MP3_APE_MAGIC:
        header = data[offset:offset + MP3_APE_HEADER_SIZE]
        tag_size = int.from_bytes(header[12:16], "little")
        flags = int.from_bytes(header[20:24], "little")
        if flags & MP3_APE_IS_HEADER_FLAG:
            # header + items + footer; size is items + footer
            total = MP3_APE_HEADER_SIZE + tag_size
            if offset + total <= len(data):
                offset += total
    return offset


def _mp3_strip_trailing_tags(data):
    """
    Strip trailing ID3v1, Lyrics3, APEv2, and ID3v2 tags iteratively.

    Order follows common tag stacking (outermost at EOF): ID3v1, then Lyrics3 /
    APE / ID3v2.4 footer tags that may sit before it.
    """
    end = len(data)
    while end > 0:
        # ID3v1 (last 128 bytes, "TAG").
        if end >= MP3_ID3V1_SIZE and data[end - MP3_ID3V1_SIZE:end - MP3_ID3V1_SIZE + 3] == MP3_ID3V1_MAGIC:
            end -= MP3_ID3V1_SIZE
            continue
        # Lyrics3v2: 6-digit size + "LYRICS200" immediately before ID3v1 region.
        if end >= 15 and data[end - 9:end] == MP3_LYRICS3V2_TAIL:
            size_field = data[end - 15:end - 9]
            try:
                lyrics_size = int(size_field.decode("ascii"))
            except (ValueError, UnicodeDecodeError):
                break
            # size excludes the 6-digit field and "LYRICS200" (15 bytes total tail)
            start = end - 15 - lyrics_size
            if start >= 0 and data[start:start + 11] == MP3_LYRICS3V1_BEGIN:
                end = start
                continue
            break
        # Lyrics3v1: search backward for "LYRICSBEGIN" ... "LYRICSEND".
        if end >= 9 and data[end - 9:end] == MP3_LYRICS3V1_TAIL:
            begin = data.rfind(MP3_LYRICS3V1_BEGIN, 0, end - 9)
            if begin >= 0:
                end = begin
                continue
            break
        # APEv2 footer at end.
        ape = _mp3_ape_tag_len_from_footer(data, end)
        if ape is not None:
            end = ape[0]
            continue
        # ID3v2.4 tag with footer at EOF ("3DI" footer magic mirrors header).
        if end >= MP3_ID3V2_HEADER_SIZE and data[end - 10:end - 7] == b"3DI":
            body = _id3_synchsafe_to_int(data[end - 4:end])
            total = MP3_ID3V2_HEADER_SIZE + body + MP3_ID3V2_HEADER_SIZE
            start = end - total
            if start >= 0 and _mp3_id3v2_len(data, start) == total:
                end = start
                continue
        break
    return end


def clear_mp3_metadata(mp3_file_name, in_place=False, verbose=False):
    """
    Remove metadata tags from an MP3 file without re-encoding audio frames.

    Strips ID3v2 (ID3v2.3 / ID3v2.4), ID3v1 / ID3v1.1, APEv2, and Lyrics3 tags
    per those tag specifications; MPEG Audio frames are left untouched.

    :param mp3_file_name: path to original MP3 file
    :type mp3_file_name: str
    :param in_place: if True, overwrite the original file with cleaned version
    :type in_place: bool
    :param verbose: if True, print detailed output
    :type verbose: bool
    :return: path to cleaned MP3 file
    """
    if not os.path.exists(mp3_file_name) or not mp3_file_name.lower().endswith(".mp3"):
        return

    with open(mp3_file_name, "rb") as f:
        data = f.read()

    start = _mp3_strip_leading_tags(data)
    end = _mp3_strip_trailing_tags(data)
    if end < start:
        return
    cleaned = data[start:end]
    # Reject empty or non-audio payloads (MPEG frame sync is 0xFFE...).
    if not cleaned or cleaned[0] != 0xFF:
        return

    if in_place:
        output_path = mp3_file_name
    else:
        base, ext = os.path.splitext(mp3_file_name)
        output_path = base + "_cleaned" + ext

    with open(output_path, "wb") as f:
        f.write(cleaned)

    if verbose:
        action = "overwritten" if in_place else f"saved to {output_path}"
        print(f"Metadata cleared for: {mp3_file_name} ({action})")

    return output_path


def _flac_bytes_after_optional_id3(data):
    """
    Return a buffer starting at fLaC, stripping a leading ID3v2 tag if present.

    Some Windows tools prepend ID3v2 before the FLAC stream. Returns None if
    fLaC is missing or a non-ID3 prefix precedes it.
    """
    magic_at = data.find(FLAC_MAGIC)
    if magic_at < 0:
        return None
    if magic_at == 0:
        return data
    if _mp3_id3v2_len(data, 0) != magic_at:
        return None
    return data[magic_at:]


def _parse_flac_container(data):
    """
    Parse metadata blocks from a buffer that starts with fLaC.

    :return: (blocks, frames_offset) where blocks is [(block_type, payload), ...],
             or None if the container is invalid
    """
    if not data.startswith(FLAC_MAGIC):
        return None
    i = len(FLAC_MAGIC)
    n = len(data)
    blocks = []
    last = False
    while i + FLAC_BLOCK_HEADER_SIZE <= n and not last:
        header = data[i]
        last = bool(header & 0x80)
        block_type = header & 0x7F
        length = (data[i + 1] << 16) | (data[i + 2] << 8) | data[i + 3]
        i += FLAC_BLOCK_HEADER_SIZE
        if i + length > n:
            return None
        blocks.append((block_type, data[i:i + length]))
        i += length
    if not blocks:
        return None
    return blocks, i


def _mp3_has_sidecar_tags(mp3_file_name):
    """Return True if ID3 / APE / Lyrics3 regions exist outside MPEG frames."""
    if not os.path.exists(mp3_file_name):
        return False
    with open(mp3_file_name, "rb") as f:
        data = f.read()
    start = _mp3_strip_leading_tags(data)
    end = _mp3_strip_trailing_tags(data)
    return start > 0 or end < len(data)


def _flac_has_removable_metadata(flac_file_name):
    """
    Return True if removable FLAC metadata is present.

    Removable means a leading ID3v2 prefix and/or any metadata block other than
    a sole STREAMINFO (same rules as clear_flac_metadata).
    """
    if not os.path.exists(flac_file_name):
        return False
    with open(flac_file_name, "rb") as f:
        data = f.read()
    stripped = _flac_bytes_after_optional_id3(data)
    if stripped is None:
        return False
    if stripped is not data:
        return True
    parsed = _parse_flac_container(stripped)
    if parsed is None:
        return False
    blocks, _ = parsed
    types = [block_type for block_type, _ in blocks]
    return types != [FLAC_STREAMINFO_TYPE]


def has_audio_metadata(file_name):
    """
    Return True if removable MP3/FLAC metadata is present.

    Uses the same parsers as clear_mp3_metadata / clear_flac_metadata.
    """
    fmt = get_file_format(file_name)
    if fmt == "mp3":
        return _mp3_has_sidecar_tags(file_name)
    if fmt == "flac":
        return _flac_has_removable_metadata(file_name)
    return False


def clear_flac_metadata(flac_file_name, in_place=False, verbose=False):
    """
    Remove metadata blocks from a FLAC file without re-encoding audio frames.

    Per the FLAC format specification (https://xiph.org/flac/format.html), keeps
    only the mandatory STREAMINFO block and drops PADDING, APPLICATION,
    SEEKTABLE, VORBIS_COMMENT, CUESHEET, PICTURE, and any other metadata blocks.
    Also strips a leading ID3v2 tag if present (some Windows tools prepend one).
    Native FLAC frames after the metadata section are copied unchanged.

    :param flac_file_name: path to original FLAC file
    :type flac_file_name: str
    :param in_place: if True, overwrite the original file with cleaned version
    :type in_place: bool
    :param verbose: if True, print detailed output
    :type verbose: bool
    :return: path to cleaned FLAC file
    """
    if not os.path.exists(flac_file_name) or not flac_file_name.lower().endswith(".flac"):
        return

    with open(flac_file_name, "rb") as f:
        data = f.read()

    data = _flac_bytes_after_optional_id3(data)
    if data is None:
        return
    parsed = _parse_flac_container(data)
    if parsed is None:
        return
    blocks, frames_offset = parsed

    streaminfo = None
    for block_type, payload in blocks:
        if block_type != FLAC_STREAMINFO_TYPE:
            continue
        if len(payload) != FLAC_STREAMINFO_SIZE or streaminfo is not None:
            return
        streaminfo = payload
    if streaminfo is None:
        return

    # STREAMINFO only, marked as last metadata block (MSB of type byte set).
    out = bytearray(FLAC_MAGIC)
    out.append(0x80 | FLAC_STREAMINFO_TYPE)
    out.append((FLAC_STREAMINFO_SIZE >> 16) & 0xFF)
    out.append((FLAC_STREAMINFO_SIZE >> 8) & 0xFF)
    out.append(FLAC_STREAMINFO_SIZE & 0xFF)
    out += streaminfo
    out += data[frames_offset:]  # native FLAC audio frames

    if in_place:
        output_path = flac_file_name
    else:
        base, ext = os.path.splitext(flac_file_name)
        output_path = base + "_cleaned" + ext

    with open(output_path, "wb") as f:
        f.write(bytes(out))

    if verbose:
        action = "overwritten" if in_place else f"saved to {output_path}"
        print(f"Metadata cleared for: {flac_file_name} ({action})")

    return output_path


CLEAR_HANDLERS = {
    "docx": clear,
    "pptx": clear,
    "xlsx": clear,
    "png": clear_png_metadata,
    "jpg": clear_jpeg_metadata,
    "jpeg": clear_jpeg_metadata,
    "gif": clear_gif_metadata,
    "mp3": clear_mp3_metadata,
    "flac": clear_flac_metadata,
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


def extract_metadata(microsoft_file_name):
    """
    Extract all the editable metadata from the given Microsoft file.

    :param microsoft_file_name: name of Microsoft file
    :type microsoft_file_name: str
    :return: dict containing the extracted metadata
    """
    unzipped_dir, _ = extract(microsoft_file_name)
    doc_props_dir = os.path.join(unzipped_dir, "docProps")
    core_xml_path = os.path.join(doc_props_dir, "core.xml")
    app_xml_path = os.path.join(doc_props_dir, "app.xml")

    extracted_metadata = {}

    def _extract_metadata_from_xml(xml_path, xml_map):
        if os.path.exists(xml_path):
            tree = lxml.parse(xml_path)
            for xml_element in tree.iter():
                for personal_field, xml_tag in xml_map.items():
                    if xml_tag in xml_element.tag:
                        value = xml_element.text if xml_element.text else ""
                        extracted_metadata[personal_field] = value.strip()

    _extract_metadata_from_xml(core_xml_path, CORE_XML_MAP)
    _extract_metadata_from_xml(app_xml_path, APP_XML_MAP)

    # Clean up
    shutil.rmtree(unzipped_dir)
    return extracted_metadata


def dmeta_help():
    """
    Print DMeta details.

    :return: None
    """
    print(OVERVIEW)
    print("Repo : https://github.com/openscilab/dmeta")
    print("Webpage : https://openscilab.com")


def run_dmeta(args):
    """
    Run DMeta.

    :param args: input arguments
    :type args: argparse.Namespace
    :return: None
    """
    verbose = args.verbose
    if args.clear:
        clear_file(args.clear[0], args.inplace, verbose)
    elif args.clear_all:
        clear_all(args.inplace, verbose)
    elif args.update:
        if not args.config:
            raise DMetaBaseError(UPDATE_COMMAND_WITH_NO_CONFIG_FILE_ERROR)
        else:
            update(args.config[0], args.update[0], args.inplace, verbose)
    elif args.update_all:
        if not args.config:
            raise DMetaBaseError(UPDATE_COMMAND_WITH_NO_CONFIG_FILE_ERROR)
        else:
            update_all(args.config[0], args.inplace, verbose)
    else:
        tprint("DMeta")
        tprint("V:" + DMETA_VERSION)
        dmeta_help()
