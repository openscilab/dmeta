import os
from PIL import Image
from dmeta.functions import update, update_all, clear, clear_all
from dmeta.functions import clear_jpeg_metadata
from dmeta.functions import clear_png_metadata
from dmeta.functions import clear_gif_metadata
from dmeta.functions import extract_metadata


def _safe_remove(file_path: str) -> None:
    """Remove a file if it exists and differs from the original."""
    if file_path and os.path.exists(file_path):
        os.remove(file_path)


TESTS_DIR_PATH = os.path.join(os.getcwd(), "tests")


def test1():
    # clear a single .docx file [not inplace]
    microsoft_file_name = os.path.join(TESTS_DIR_PATH, "test_a.docx")
    output_path = clear(microsoft_file_name)
    assert output_path is not None, "clear() returned None"
    for value in extract_metadata(output_path).values():
        assert value == ""
    # Clean up created file
    _safe_remove(output_path)


def test2():
    # clear a single .pptx file [inplace]
    microsoft_file_name = os.path.join(TESTS_DIR_PATH, "test_a.pptx")
    _ = clear(microsoft_file_name, in_place=True)
    for value in extract_metadata(microsoft_file_name).values():
        assert value == ""


def test3():
    # clear all existing .docx files [not inplace]
    original_dir = os.getcwd()
    try:
        os.chdir(TESTS_DIR_PATH)
        # Get list of files before clearing
        original_files = set(os.listdir("."))
        clear_all()
        # Clean up newly created files
        new_files = set(os.listdir(".")) - original_files
        for new_file in new_files:
            if os.path.isfile(new_file):
                os.remove(new_file)
    finally:
        os.chdir(original_dir)


def test4():
    # clear all existing files [inplace]
    original_dir = os.getcwd()
    try:
        os.chdir(TESTS_DIR_PATH)
        clear_all(in_place=True)
    finally:
        os.chdir(original_dir)


def test5():
    # update a single .docx file [not inplace]
    microsoft_file_name = os.path.join(TESTS_DIR_PATH, "test_a.docx")
    _author = extract_metadata(microsoft_file_name)["authors"]
    output_path = update(
        os.path.join(TESTS_DIR_PATH, "config.json"), microsoft_file_name, in_place=False
    )
    assert output_path is not None, "update() returned None"
    assert extract_metadata(microsoft_file_name)["authors"] == _author
    assert extract_metadata(output_path)["authors"] == "UPDATED-AUTHOR"
    # Clean up created file
    _safe_remove(output_path)


def test6():
    # update a single .docx file [inplace]
    microsoft_file_name = os.path.join(TESTS_DIR_PATH, "test_a.docx")
    _ = update(
        os.path.join(TESTS_DIR_PATH, "config.json"), microsoft_file_name, in_place=True
    )
    assert extract_metadata(microsoft_file_name)["authors"] == "UPDATED-AUTHOR"


def test7():
    # update all existing .docx files [not inplace]
    original_dir = os.getcwd()
    try:
        os.chdir(TESTS_DIR_PATH)
        # Get list of files before update
        original_files = set(os.listdir("."))
        update_all(os.path.join(TESTS_DIR_PATH, "config.json"))
        # Clean up newly created files
        new_files = set(os.listdir(".")) - original_files
        for new_file in new_files:
            if os.path.isfile(new_file):
                os.remove(new_file)
    finally:
        os.chdir(original_dir)


def test8():
    # update all existing files [inplace]
    original_dir = os.getcwd()
    try:
        os.chdir(TESTS_DIR_PATH)
        update_all(os.path.join(TESTS_DIR_PATH, "config.json"), in_place=True)
    finally:
        os.chdir(original_dir)


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
    assert output_path is not None, "clear_png_metadata() returned None"
    with Image.open(output_path) as img:
        assert img.info == {}
    # Clean up created file
    _safe_remove(output_path)


def test11():
    # clear the metadata of the .jpg file [not inplace]
    jpeg_file = os.path.join(TESTS_DIR_PATH, "test.jpg")
    output_path = clear_jpeg_metadata(jpeg_file, in_place=False, verbose=False)
    assert output_path is not None, "clear_jpeg_metadata() returned None"
    with Image.open(output_path) as img:
        assert img.info == {}
    # Clean up created file
    _safe_remove(output_path)


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
    assert output_path is not None, "clear_gif_metadata() returned None"
    with Image.open(output_path) as img:
        assert "comment" not in img.info
    # Clean up created file
    _safe_remove(output_path)


def test14():
    # clear the metadata of the .gif file [inplace]
    gif_file = os.path.join(TESTS_DIR_PATH, "test.gif")
    clear_gif_metadata(gif_file, in_place=True, verbose=False)
    with Image.open(gif_file) as img:
        assert "comment" not in img.info
