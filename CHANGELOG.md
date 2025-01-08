# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Removed
- `extract_namespaces` function in `util.py`
### Added
- `DMetaBaseError` added to `dmeta/__init__.py`
- `overwrite_metadata` function added to `functions.py`
### Changed
- `update` function in `functions.py` refactored
- `clear` function in `functions.py` refactored
- `README.md` updated
- GitHub actions are limited to the `dev` and `main` branches
- `Python 3.13` added to `test.yml`
## [0.2] - 2024-08-14
### Added
- `dmeta/errors.py`
- `pptx` and `xlsx` support
- `get_microsoft_format` function in `util.py`
- `SECURITY.md`
- `inplace` parameter in the `clear` function in `functions.py`
- `inplace` parameter in the `clear_all` function in `functions.py`
- `inplace` parameter in the `update` function in `functions.py`
- `inplace` parameter in the `update_all` function in `functions.py`
- `inplace` parameter in CLI
- `inplace` tests
### Changed
- `run_dmeta` in `functions.py`
- `read_json` in `util.py`
- `get_microsoft_format` in `util.py`
- error messages in `params.py`
- `clear` function in `functions.py`
- `extract` function in `util.py`
- `remove_format` function in `util.py`
- `clear` function in `functions.py`
- `clear_all` function in `functions.py`
- `update` function in `functions.py`
- `update_all` function in `functions.py`
- `extract_namespaces` function in `util.py`
- `README.md` updated
## [0.1] - 2024-06-19
### Added
- `CLI` handler
- `main` function in `__main__.py`
- `README.md`
- `clear` function in `functions.py`
- `clear_all` function in `functions.py`
- `update` function in `functions.py`
- `update_all` function in `functions.py`
- `run_dmeta` function in `functions.py`
- `dmeta_help` function in `functions.py`
- `extract_namespaces` function in `util.py`
- `remove_format` function in `util.py`
- `extract_docx` function in `util.py`
- `read_json` function in `util.py`

[Unreleased]: https://github.com/openscilab/dmeta/compare/v0.2...dev
[0.2]: https://github.com/openscilab/dmeta/compare/v0.1...v0.2
[0.1]: https://github.com/openscilab/dmeta/compare/9a4ad10...v0.1
