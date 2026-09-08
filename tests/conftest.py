# -*- coding: utf-8 -*-
"""
Session fixture hygiene for the DMeta test suite.

Layers:
  1. setup  — GC stale artifacts, snapshot committed fixtures
  2. run    — tests execute
  3. teardown — restore fixtures, GC generated artifacts

Audio tests that need enriched before/after checks use the `audio_fixtures`
fixture to re-copy MP3/FLAC samples after earlier in-place / clear_all runs.
"""
import shutil
from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).resolve().parent

_FIXTURE_FILES = (
    "test.mp3",
    "test.flac",
    "test_id3.flac",
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
    "test_id3.flac",
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
                path.unlink(missing_ok=True)
    for pattern in _ARTIFACT_DIR_GLOBS:
        for path in TESTS_DIR.glob(pattern):
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)


@pytest.fixture(scope="session")
def _fixture_backup(tmp_path_factory):
    """Snapshot fixtures for session restore; shared with audio_fixtures."""
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


@pytest.fixture
def audio_fixtures(_fixture_backup):
    """Restore committed audio fixtures before an MP3/FLAC test."""
    for name in _AUDIO_FIXTURES:
        dest = _fixture_backup.get(name)
        if dest is not None:
            shutil.copy2(dest, TESTS_DIR / name)
    yield
