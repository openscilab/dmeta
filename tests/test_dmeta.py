# -*- coding: utf-8 -*-
"""DMeta test suite."""
import os
from PIL import Image
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from pypdf import PdfReader
from dmeta.functions import update, update_all, clear, clear_all
from dmeta.functions import clear_jpeg_metadata
from dmeta.functions import clear_png_metadata
from dmeta.functions import clear_gif_metadata
from dmeta.functions import clear_mp3_metadata
from dmeta.functions import clear_flac_metadata
from dmeta.functions import clear_pdf_metadata
from dmeta.functions import clear_file
from dmeta.functions import extract_metadata
from dmeta.functions import has_audio_metadata
from dmeta.functions import has_pdf_metadata


TESTS_DIR_PATH = os.path.join(os.getcwd(), "tests")


def _assert_audio_clear(path, clearer, in_place):
    """
    Assert audio metadata is present, clear it, then assert it is gone.

    :param path: path to the MP3 or FLAC file
    :type path: str
    :param clearer: clearance function to call
    :type clearer: callable
    :param in_place: if True, overwrite the file; otherwise write a cleaned copy
    :type in_place: bool
    :return: path to the cleared file
    """
    assert has_audio_metadata(path)
    if in_place:
        clearer(path, in_place=True, verbose=False)
        assert not has_audio_metadata(path)
        cleared = path
    else:
        output_path = clearer(path, in_place=False, verbose=False)
        assert has_audio_metadata(path)
        assert not has_audio_metadata(output_path)
        cleared = output_path
    if path.lower().endswith(".mp3"):
        assert list(MP3(cleared).keys()) == []
    else:
        flac = FLAC(cleared)
        assert dict(flac) == {}
        assert flac.pictures == []
    return cleared


def _assert_pdf_clear(path, clearer, in_place):
    """
    Assert PDF metadata is present, clear it, then assert it is gone.

    The Document Information values are captured from the untouched file and
    checked for byte-level absence in the result, proving a hard cleanup.

    :param path: path to the PDF file
    :type path: str
    :param clearer: clearance function to call
    :type clearer: callable
    :param in_place: if True, overwrite the file; otherwise write a cleaned copy
    :type in_place: bool
    :return: path to the cleared file
    """
    reader = PdfReader(path)
    secrets = [value.encode("utf-8", "ignore") for value in reader.metadata.values() if value]
    assert reader.xmp_metadata is not None
    assert has_pdf_metadata(path)
    if in_place:
        clearer(path, in_place=True, verbose=False)
        assert not has_pdf_metadata(path)
        cleared = path
    else:
        output_path = clearer(path, in_place=False, verbose=False)
        assert has_pdf_metadata(path)
        assert not has_pdf_metadata(output_path)
        cleared = output_path
    reader = PdfReader(cleared)
    assert reader.metadata is None
    assert reader.xmp_metadata is None
    assert len(reader.pages) >= 1
    raw = open(cleared, "rb").read()
    for secret in secrets:
        assert secret not in raw
    # Every XMP packet (document and page level) is physically erased.
    assert b"xmpmeta" not in raw
    assert b"<?xpacket" not in raw
    return cleared


def test1():
    """Clear a single .docx file [not inplace]."""
    microsoft_file_name = os.path.join(TESTS_DIR_PATH, "test_a.docx")
    output_path = clear(microsoft_file_name)
    for value in extract_metadata(output_path).values():
        assert value == ""


def test2():
    """Clear a single .pptx file [inplace]."""
    microsoft_file_name = os.path.join(TESTS_DIR_PATH, "test_a.pptx")
    _ = clear(microsoft_file_name, in_place=True)
    for value in extract_metadata(microsoft_file_name).values():
        assert value == ""


def test3():
    """Clear all existing supported files [not inplace]."""
    os.chdir(TESTS_DIR_PATH)
    clear_all()


def test4():
    """Clear all existing supported files [inplace]."""
    os.chdir(TESTS_DIR_PATH)
    clear_all(in_place=True)


def test5():
    """Update a single .docx file [not inplace]."""
    microsoft_file_name = os.path.join(TESTS_DIR_PATH, "test_a.docx")
    _author = extract_metadata(microsoft_file_name)["authors"]
    output_path = update(os.path.join(TESTS_DIR_PATH, "config.json"), microsoft_file_name, in_place=False)
    assert extract_metadata(microsoft_file_name)["authors"] == _author
    assert extract_metadata(output_path)["authors"] == "UPDATED-AUTHOR"


def test6():
    """Update a single .docx file [inplace]."""
    microsoft_file_name = os.path.join(TESTS_DIR_PATH, "test_a.docx")
    _ = update(os.path.join(TESTS_DIR_PATH, "config.json"), microsoft_file_name, in_place=True)
    assert extract_metadata(microsoft_file_name)["authors"] == "UPDATED-AUTHOR"


def test7():
    """Update all existing .docx files [not inplace]."""
    os.chdir(TESTS_DIR_PATH)
    update_all(os.path.join(TESTS_DIR_PATH, "config.json"))


def test8():
    """Update all existing .docx files [inplace]."""
    os.chdir(TESTS_DIR_PATH)
    update_all(os.path.join(TESTS_DIR_PATH, "config.json"), in_place=True)


def test9():
    """Clear the metadata of the .png file [inplace]."""
    png_file = os.path.join(TESTS_DIR_PATH, "test.png")
    clear_png_metadata(png_file, in_place=True, verbose=False)
    with Image.open(png_file) as img:
        assert img.info == {}


def test10():
    """Clear the metadata of the .png file [not inplace]."""
    png_file = os.path.join(TESTS_DIR_PATH, "test.png")
    output_path = clear_png_metadata(png_file, in_place=False, verbose=False)
    with Image.open(output_path) as img:
        assert img.info == {}


def test11():
    """Clear the metadata of the .jpg file [not inplace]."""
    jpeg_file = os.path.join(TESTS_DIR_PATH, "test.jpg")
    output_path = clear_jpeg_metadata(jpeg_file, in_place=False, verbose=False)
    with Image.open(output_path) as img:
        assert img.info == {}


def test12():
    """Clear the metadata of the .jpg file [inplace]."""
    jpeg_file = os.path.join(TESTS_DIR_PATH, "test.jpg")
    clear_jpeg_metadata(jpeg_file, in_place=True, verbose=False)
    with Image.open(jpeg_file) as img:
        assert img.info == {}


def test13():
    """Clear the metadata of the .gif file [not inplace]."""
    gif_file = os.path.join(TESTS_DIR_PATH, "test.gif")
    output_path = clear_gif_metadata(gif_file, in_place=False, verbose=False)
    with Image.open(output_path) as img:
        assert "comment" not in img.info


def test14():
    """Clear the metadata of the .gif file [inplace]."""
    gif_file = os.path.join(TESTS_DIR_PATH, "test.gif")
    clear_gif_metadata(gif_file, in_place=True, verbose=False)
    with Image.open(gif_file) as img:
        assert "comment" not in img.info


def test15(sample_file):
    """Clear the metadata of the .mp3 file [not inplace]."""
    _assert_audio_clear(sample_file("test.mp3"), clear_mp3_metadata, False)


def test16(sample_file):
    """Clear the metadata of the .mp3 file [inplace]."""
    _assert_audio_clear(sample_file("test.mp3"), clear_mp3_metadata, True)


def test17(sample_file):
    """Clear the metadata of the .flac file [not inplace]."""
    _assert_audio_clear(sample_file("test.flac"), clear_flac_metadata, False)


def test18(sample_file):
    """Clear the metadata of the .flac file [inplace]."""
    _assert_audio_clear(sample_file("test.flac"), clear_flac_metadata, True)


def test19(sample_file):
    """Clear_file routes mp3 and flac [not inplace]."""
    _assert_audio_clear(sample_file("test.mp3"), clear_file, False)
    _assert_audio_clear(sample_file("test.flac"), clear_file, False)


def test20(sample_file):
    """Clear the metadata of the .pdf file [not inplace]."""
    _assert_pdf_clear(sample_file("test.pdf"), clear_pdf_metadata, False)


def test21(sample_file):
    """Clear the metadata of the .pdf file [inplace]."""
    _assert_pdf_clear(sample_file("test.pdf"), clear_pdf_metadata, True)


def test22(sample_file):
    """Clear_file routes pdf [not inplace]."""
    _assert_pdf_clear(sample_file("test.pdf"), clear_file, False)
