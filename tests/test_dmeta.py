import os
from PIL import Image
from dmeta.functions import update, update_all, clear, clear_all
from dmeta.functions import clear_png_metadata

TESTS_DIR_PATH = os.path.join(os.getcwd(), "tests")

def test1():
    # clear a single .docx file [not inplace]
    clear(os.path.join(TESTS_DIR_PATH, "test_a.docx"))


def test2():
    # clear a single .docx file [inplace]
    clear(os.path.join(TESTS_DIR_PATH, "test_a.docx"), in_place=True)


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
    update(os.path.join(TESTS_DIR_PATH, "config.json"), os.path.join(TESTS_DIR_PATH, "test_a.docx"))


def test6():
    # update a single .docx file [inplace]
    update(os.path.join(TESTS_DIR_PATH, "config.json"), os.path.join(TESTS_DIR_PATH, "test_a.docx"), in_place=True)


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
