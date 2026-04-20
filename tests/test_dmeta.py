import os
from PIL import Image
from dmeta.functions import update, update_all, clear, clear_all
from dmeta.functions import clear_jpeg_metadata
from dmeta.functions import clear_png_metadata
from dmeta.functions import clear_gif_metadata
from dmeta.functions import extract_metadata


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
    # clear all existing .docx files [not inplace]
    os.chdir(TESTS_DIR_PATH)
    clear_all()


def test4():
    # clear all existing .docx files [inplace]
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
