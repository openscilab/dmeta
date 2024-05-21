from dmeta.functions import update, update_all, clear, clear_all
import os 

TESTS_DIR_PATH = os.path.join(os.getcwd(), "tests")

def test_clear():
    clear(os.path.join(TESTS_DIR_PATH, "test_a.docx"))
    # check the clearance


def test_clear_all():
    os.chdir(TESTS_DIR_PATH)
    clear_all()
    # check all files clearance


def test_update():
    # test meta-data is updated
    update(os.path.join(TESTS_DIR_PATH, "config.json"), os.path.join(TESTS_DIR_PATH, "test_a.docx"))


def test_update_all():
    # test all files meta-data are updated
    os.chdir(TESTS_DIR_PATH)
    update_all(os.path.join(TESTS_DIR_PATH, "config.json"))
