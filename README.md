<div align="center">
    <img src="https://github.com/openscilab/dmeta/raw/main/otherfiles/logo.png" width="280" height="400">
    <br/>
    <br/>
    <a href="https://codecov.io/gh/openscilab/dmeta">
        <img src="https://codecov.io/gh/openscilab/dmeta/branch/main/graph/badge.svg" alt="Codecov"/>
    </a>
    <a href="TODO">
        <img src="TODO" alt="PyPI version" height="18">
    </a>
    <a href="https://www.python.org/">
        <img src="https://img.shields.io/badge/built%20with-Python3-green.svg" alt="built with Python3">
    </a>
    <a href="TODO">
        <img src="TODO" alt="Discord Channel">
    </a>
</div>

----------

## Table of contents

* [Overview](https://github.com/openscilab/dmeta#overview)
* [Installation](https://github.com/openscilab/dmeta#installation)
* [Usage](https://github.com/openscilab/dmeta#usage)
* [Issues & Bug Reports](https://github.com/openscilab/dmeta#issues--bug-reports)
* [Todo](https://github.com/openscilab/dmeta/blob/main/TODO.md)
* [Contribution](https://github.com/openscilab/dmeta/blob/main/.github/CONTRIBUTING.md)
* [Authors](https://github.com/openscilab/dmeta/blob/main/AUTHORS.md)
* [License](https://github.com/openscilab/dmeta/blob/main/LICENSE)
* [Show Your Support](https://github.com/openscilab/dmeta#show-your-support)
* [Changelog](https://github.com/openscilab/dmeta/blob/main/CHANGELOG.md)
* [Code of Conduct](https://github.com/openscilab/dmeta/blob/main/.github/CODE_OF_CONDUCT.md)


## Overview
<p align="justify">
DMeta is an open source Python package that removes metadata of microsoft office files.
</p>
<table>
    <tr>
        <td align="center">PyPI Counter</td>
        <td align="center">
            <a href="TODO">
                <img src="TODO">
            </a>
        </td>
    </tr>
    <tr>
        <td align="center">Github Stars</td>
        <td align="center">
            <a href="https://github.com/openscilab/dmeta">
                <img src="TODO">
            </a>
        </td>
    </tr>
</table>
<table>
    <tr> 
        <td align="center">Branch</td>
        <td align="center">main</td>
        <td align="center">dev</td>
    </tr>
    <tr>
        <td align="center">CI</td>
        <td align="center">
            <img src="https://github.com/openscilab/dmeta/workflows/CI/badge.svg?branch=main">
        </td>
        <td align="center">
            <img src="https://github.com/openscilab/dmeta/workflows/CI/badge.svg?branch=dev">
            </td>
    </tr>
</table>


## Installation

### PyPI

- Check [Python Packaging User Guide](https://packaging.python.org/installing/)
- Run `pip install dmeta==0.1`
### Source code
- Download [Version 0.1](https://github.com/openscilab/dmeta/archive/v0.1.zip) or [Latest Source](https://github.com/openscilab/dmeta/archive/dev.zip)
- Run `pip install .`

## Usage
### Programmatically 
#### Clear metadata for a .docx file
```python
import os
from dmeta.functions import clear

DOCX_FILE_PATH = os.path.join(os.getcwd(), "SAMPLE.docx")
clear(DOCX_FILE_PATH)
```
#### Clear metadata for all existing .docx files in the current directory
```python
from dmeta.functions import clear_all
clear_all()
```
#### Update metadata for a .docx file
```python
import os
from dmeta.functions import update

CONFIG_FILE_PATH = os.path.join(os.getcwd(), "CONFIG.json") 
DOCX_FILE_PATH = os.path.join(os.getcwd(), "SAMPLE.docx")
update(DOCX_FILE_PATH, DOCX_FILE_PATH)
```

### Update metadata for all existing .docx files in the current directory
```python
import os
from dmeta.functions import update_all

CONFIG_FILE_PATH = os.path.join(os.getcwd(), "CONFIG.json") 
update_all(CONFIG_FILE_PATH)
```

### CLI
⚠️ You can use `dmeta` or `python -m dmeta` to run this program
#### Version
```console
dmeta -v
dmeta --version
```
### Clear metadata for a .docx file
```console
dmeta --clear "./test_a.docx"
```
### Clear metadata for all existing .docx files in the current directory
```console
dmeta --clear-all
```
### Update metadata for a .docx file
```console
dmeta --update "./test_a.docx" --config "./config.json"
```
### Update metadata for all existing .docx files in the current directory
```console
dmeta --update-all --config "./config.json"
```

## Supported files
| File format | support | 
| ---------------- | ---------------- | 
| Microsoft word office(.docx) | &#x2705; | 

## Issues & bug reports

Just fill an issue and describe it. We'll check it ASAP! or send an email to [info@openscilab.com](mailto:info@openscilab.com "info@openscilab.com"). 

- Please complete the issue template
 
You can also join our discord server

<a href="TODO">
  <img src="TODO" alt="Discord Channel">
</a>


## Show Your Support


### Star this repo

Give a ⭐️ if this project helped you!

### Donate to our project
If you do like our project and we hope that you do, can you please support us? Our project is not and is never going to be working for profit. We need the money just so we can continue doing what we do ;-) .			

<a href="https://openscilab.com/#donation" target="_blank"><img src="https://github.com/openscilab/dmeta/raw/main/otherfiles/donation.png" height="90px" width="270px" alt="DMeta Donation"></a>