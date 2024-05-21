from dmeta.functions import update, update_all, clear, clear_all


def test_clear():
    clear("test_a.docx")
    # check the clearance


def test_clear_all():
    clear_all()
    # check all files clearance


def test_update():
    # test meta-data is updated
    update("config.json","test_a.docx")


def test_update_all():
    # test all files meta-data are updated
    update_all("config.json")
