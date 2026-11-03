# -*- coding: utf-8 -*-
"""
Session fixture hygiene for the DMeta test suite.

Layers:
  1. setup  — GC stale artifacts, snapshot committed fixtures
  2. run    — tests execute against private per-test copies
  3. teardown — restore fixtures, GC generated artifacts

Clearance tests assert metadata before and after, so they operate on a private
copy of the sample (`sample_file`) rather than the shared committed fixture.
Supporting a new format is a single entry in `_FIXTURES`.
"""
import shutil
import subprocess
from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).resolve().parent
REPO_DIR = TESTS_DIR.parent

# Every committed sample the suite relies on, across all supported formats.
_FIXTURES = (
    "test_a.docx", "test_b.docx", "test_.docx", "test_a.pptx", "test_a.xlsx",
    "test.png", "test.jpg", "test.gif", "test.mp3", "test.flac", "test.pdf",
    "config.json",
)

_ARTIFACT_FILE_GLOBS = ("*_cleaned*", "*_cleared.*", "*_updated.*")
_ARTIFACT_DIR_GLOBS = ("*_unzipped", "*_cleared_unzipped", "*_updated_unzipped")


def _gc_artifacts():
    """
    Delete generated test artifacts under the tests directory.

    :return: None
    """
    for pattern in _ARTIFACT_FILE_GLOBS:
        for path in TESTS_DIR.glob(pattern):
            if path.is_file():
                path.unlink()
    for pattern in _ARTIFACT_DIR_GLOBS:
        for path in TESTS_DIR.glob(pattern):
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)


def _committed_bytes(name):
    """
    Read a fixture's committed, metadata-bearing bytes.

    CI strips `tests/` in place (`dmeta --clear-all --inplace`) before pytest, so
    the committed blob in HEAD is the reliable source; the working copy is used
    only for a fixture that is not committed yet.

    :param name: fixture file name under tests/
    :type name: str
    :return: raw file bytes
    """
    try:
        return subprocess.check_output(
            ["git", "cat-file", "blob", "HEAD:tests/" + name],
            cwd=str(REPO_DIR), stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return (TESTS_DIR / name).read_bytes()


@pytest.fixture(scope="session")
def _samples():
    """
    Committed bytes for every fixture, read once per session.

    :return: mapping of fixture names to file bytes
    """
    return {name: _committed_bytes(name) for name in _FIXTURES}


@pytest.fixture(scope="session", autouse=True)
def _session_hygiene(tmp_path_factory, _samples):
    """
    GC and snapshot fixtures at setup, restore and GC at teardown.

    Depending on `_samples` captures fixture bytes during setup, before any
    in-place clearance strips a not-yet-committed working copy.

    :param tmp_path_factory: pytest temporary path factory
    :type tmp_path_factory: pytest.TempPathFactory
    :param _samples: session-level committed fixture bytes
    :type _samples: dict
    :return: None
    """
    _gc_artifacts()
    backup = tmp_path_factory.mktemp("dmeta_fixture_backup")
    saved = {}
    for name in _FIXTURES:
        src = TESTS_DIR / name
        if src.is_file():
            dest = backup / name
            shutil.copy2(src, dest)
            saved[name] = dest
    yield
    for name, dest in saved.items():
        shutil.copy2(dest, TESTS_DIR / name)
    _gc_artifacts()


@pytest.fixture
def sample_file(_samples, tmp_path):
    """
    Write a named fixture's metadata-bearing bytes into the test's own directory.

    :param _samples: session-level committed fixture bytes
    :type _samples: dict
    :param tmp_path: per-test temporary directory
    :type tmp_path: pathlib.Path
    :return: callable mapping a fixture name to its fresh temp-file path
    """
    def _write(name):
        """
        Write one fixture into tmp_path.

        :param name: fixture file name such as test.pdf
        :type name: str
        :return: path to the written file
        """
        path = tmp_path / name
        path.write_bytes(_samples[name])
        return str(path)
    return _write
