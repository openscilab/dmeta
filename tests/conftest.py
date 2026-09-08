# -*- coding: utf-8 -*-
"""Session fixture hygiene for the DMeta test suite.

Layers:
  1. setup  — GC stale artifacts, snapshot committed fixtures
  2. run    — tests execute
  3. teardown — restore fixtures, GC generated artifacts

MP3/FLAC tests assert metadata before and after clearance, so they work on
their own copy of the sample (`audio_file`) instead of the shared fixture.
"""
import shutil
import subprocess
from pathlib import Path

import pytest

from dmeta.functions import has_audio_metadata

TESTS_DIR = Path(__file__).resolve().parent
REPO_DIR = TESTS_DIR.parent

_FIXTURE_FILES = (
    "test.mp3",
    "test.flac",
    "test.png",
    "test.jpg",
    "test.gif",
    "test_a.docx",
    "test_b.docx",
    "test_.docx",
    "test_a.pptx",
    "test_a.xlsx",
    "config.json",
)

_AUDIO_FIXTURES = (
    "test.mp3",
    "test.flac",
)

_ARTIFACT_FILE_GLOBS = (
    "*_cleaned*",
    "*_cleared.*",
    "*_updated.*",
)
_ARTIFACT_DIR_GLOBS = (
    "*_unzipped",
    "*_cleared_unzipped",
    "*_updated_unzipped",
)


def _gc_artifacts():
    for pattern in _ARTIFACT_FILE_GLOBS:
        for path in TESTS_DIR.glob(pattern):
            if path.is_file():
                path.unlink()
    for pattern in _ARTIFACT_DIR_GLOBS:
        for path in TESTS_DIR.glob(pattern):
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)


def _enriched_audio_bytes(name):
    """
    Read a sample that still carries metadata.

    CI clears `tests/` in place (`dmeta --clear-all --inplace`) before pytest
    runs, so fall back to the committed sample when the working copy is bare.
    """
    src = TESTS_DIR / name
    if src.is_file() and has_audio_metadata(str(src)):
        return src.read_bytes()
    return subprocess.check_output(
        ["git", "cat-file", "blob", "HEAD:tests/" + name],
        cwd=str(REPO_DIR))


@pytest.fixture(scope="session")
def _fixture_backup(tmp_path_factory):
    """Snapshot fixtures for session restore."""
    _gc_artifacts()
    backup_root = tmp_path_factory.mktemp("dmeta_fixture_backup")
    mapping = {}
    for name in _FIXTURE_FILES:
        src = TESTS_DIR / name
        if not src.is_file():
            continue
        dest = backup_root / name
        shutil.copy2(src, dest)
        mapping[name] = dest
    yield mapping
    for name, dest in mapping.items():
        shutil.copy2(dest, TESTS_DIR / name)
    _gc_artifacts()


@pytest.fixture(scope="session", autouse=True)
def _session_hygiene(_fixture_backup):
    """Drive session setup/teardown for every pytest run."""
    yield


@pytest.fixture(scope="session")
def _audio_samples():
    """Enriched MP3/FLAC bytes, read once per session."""
    return {name: _enriched_audio_bytes(name) for name in _AUDIO_FIXTURES}


@pytest.fixture
def audio_file(_audio_samples, tmp_path):
    """Write an enriched sample into the test's own directory."""
    def _write(name):
        path = tmp_path / name
        path.write_bytes(_audio_samples[name])
        return str(path)
    return _write
