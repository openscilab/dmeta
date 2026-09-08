import os
from PIL import Image
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.apev2 import APEv2, APENoHeaderError
from dmeta.functions import update, update_all, clear, clear_all
from dmeta.functions import clear_jpeg_metadata
from dmeta.functions import clear_png_metadata
from dmeta.functions import clear_gif_metadata
from dmeta.functions import clear_mp3_metadata
from dmeta.functions import clear_flac_metadata
from dmeta.functions import clear_file
from dmeta.functions import extract_metadata
from dmeta.functions import mp3_has_sidecar_tags
from dmeta.functions import flac_metadata_block_types
from dmeta.params import FLAC_STREAMINFO_TYPE
from dmeta.params import MP3_ID3V2_MAGIC


TESTS_DIR_PATH = os.path.join(os.getcwd(), "tests")


def test1():
    # clear a single .docx file [not inplace]
    microsoft_file_name = os.path.join(TESTS_DIR_PATH, "test_a.docx")
    output_path = clear(microsoft_file_name)
    for value in extract_metadata(output_path).values():
        assert value == ""


def test2():
    # clear a single .docx file [inplace]
    microsoft_file_name = os.path.join(TESTS_DIR_PATH, "test_a.pptx")
    _ = clear(microsoft_file_name, in_place=True)
    for value in extract_metadata(microsoft_file_name).values():
        assert value == ""


def test3():
    # clear all existing supported files [not inplace]
    os.chdir(TESTS_DIR_PATH)
    clear_all()


def test4():
    # clear all existing supported files [inplace]
    os.chdir(TESTS_DIR_PATH)
    clear_all(in_place=True)


def test5():
    # update a single .docx file [not inplace]
    microsoft_file_name = os.path.join(TESTS_DIR_PATH, "test_a.docx")
    _author = extract_metadata(microsoft_file_name)["authors"]
    output_path = update(os.path.join(TESTS_DIR_PATH, "config.json"), microsoft_file_name, in_place=False)
    assert extract_metadata(microsoft_file_name)["authors"] == _author
    assert extract_metadata(output_path)["authors"] == "UPDATED-AUTHOR"


def test6():
    # update a single .docx file [inplace]
    microsoft_file_name = os.path.join(TESTS_DIR_PATH, "test_a.docx")
    _ = update(os.path.join(TESTS_DIR_PATH, "config.json"), microsoft_file_name, in_place=True)
    assert extract_metadata(microsoft_file_name)["authors"] == "UPDATED-AUTHOR"


def test7():
    # update all existing .docx files [not inplace]
    os.chdir(TESTS_DIR_PATH)
    update_all(os.path.join(TESTS_DIR_PATH, "config.json"))


def test8():
    # update all existing .docx files [inplace]
    os.chdir(TESTS_DIR_PATH)
    update_all(os.path.join(TESTS_DIR_PATH, "config.json"), in_place=True)


def test9():
    # clear the metadata of the .png file [inplace]
    png_file = os.path.join(TESTS_DIR_PATH, "test.png")
    clear_png_metadata(png_file, in_place=True, verbose=False)
    with Image.open(png_file) as img:
        assert img.info == {}


def test10():
    # clear the metadata of the .png file [not inplace]
    png_file = os.path.join(TESTS_DIR_PATH, "test.png")
    output_path = clear_png_metadata(png_file, in_place=False, verbose=False)
    with Image.open(output_path) as img:
        assert img.info == {}


def test11():
    # clear the metadata of the .jpg file [not inplace]
    jpeg_file = os.path.join(TESTS_DIR_PATH, "test.jpg")
    output_path = clear_jpeg_metadata(jpeg_file, in_place=False, verbose=False)
    with Image.open(output_path) as img:
        assert img.info == {}


def test12():
    # clear the metadata of the .jpg file [inplace]
    jpeg_file = os.path.join(TESTS_DIR_PATH, "test.jpg")
    clear_jpeg_metadata(jpeg_file, in_place=True, verbose=False)
    with Image.open(jpeg_file) as img:
        assert img.info == {}


def test13():
    # clear the metadata of the .gif file [not inplace]
    gif_file = os.path.join(TESTS_DIR_PATH, "test.gif")
    output_path = clear_gif_metadata(gif_file, in_place=False, verbose=False)
    with Image.open(output_path) as img:
        assert "comment" not in img.info


def test14():
    # clear the metadata of the .gif file [inplace]
    gif_file = os.path.join(TESTS_DIR_PATH, "test.gif")
    clear_gif_metadata(gif_file, in_place=True, verbose=False)
    with Image.open(gif_file) as img:
        assert "comment" not in img.info


def test15():
    # clear the metadata of the .mp3 file [not inplace]
    mp3_file = os.path.join(TESTS_DIR_PATH, "test.mp3")
    output_path = clear_mp3_metadata(mp3_file, in_place=False, verbose=False)
    assert list(MP3(output_path).keys()) == []
    assert not mp3_has_sidecar_tags(output_path)
    try:
        APEv2(output_path)
        assert False, "APEv2 tag still present after clearance"
    except APENoHeaderError:
        pass


def test16():
    # clear the metadata of the .mp3 file [inplace]
    mp3_file = os.path.join(TESTS_DIR_PATH, "test.mp3")
    clear_mp3_metadata(mp3_file, in_place=True, verbose=False)
    assert list(MP3(mp3_file).keys()) == []
    assert not mp3_has_sidecar_tags(mp3_file)


def test17():
    # clear the metadata of the .flac file [not inplace]
    flac_file = os.path.join(TESTS_DIR_PATH, "test.flac")
    output_path = clear_flac_metadata(flac_file, in_place=False, verbose=False)
    flac = FLAC(output_path)
    assert dict(flac) == {}
    assert flac.pictures == []
    assert flac_metadata_block_types(output_path) == [FLAC_STREAMINFO_TYPE]


def test18():
    # clear the metadata of the .flac file [inplace]
    flac_file = os.path.join(TESTS_DIR_PATH, "test.flac")
    clear_flac_metadata(flac_file, in_place=True, verbose=False)
    flac = FLAC(flac_file)
    assert dict(flac) == {}
    assert flac.pictures == []
    assert flac_metadata_block_types(flac_file) == [FLAC_STREAMINFO_TYPE]


def test19():
    # clear_file routes mp3 and flac [not inplace]
    mp3_out = clear_file(os.path.join(TESTS_DIR_PATH, "test.mp3"), in_place=False, verbose=False)
    flac_out = clear_file(os.path.join(TESTS_DIR_PATH, "test.flac"), in_place=False, verbose=False)
    assert list(MP3(mp3_out).keys()) == []
    assert not mp3_has_sidecar_tags(mp3_out)
    assert dict(FLAC(flac_out)) == {}
    assert flac_metadata_block_types(flac_out) == [FLAC_STREAMINFO_TYPE]


def test20():
    # FLAC with leading ID3v2 (Windows/WMP style) still clears to STREAMINFO only
    flac_file = os.path.join(TESTS_DIR_PATH, "test.flac")
    with open(flac_file, "rb") as f:
        flac_bytes = f.read()
    # Empty ID3v2.3 header (same layout clear_flac / _mp3_id3v2_len accept).
    id3_prefix = MP3_ID3V2_MAGIC + b"\x03\x00\x00\x00\x00\x00\x00"
    prefixed = os.path.join(TESTS_DIR_PATH, "_prefixed.flac")
    with open(prefixed, "wb") as f:
        f.write(id3_prefix + flac_bytes)
    prefixed_out = clear_flac_metadata(prefixed, in_place=False, verbose=False)
    assert flac_metadata_block_types(prefixed_out) == [FLAC_STREAMINFO_TYPE]
    assert dict(FLAC(prefixed_out)) == {}
