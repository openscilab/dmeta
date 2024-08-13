<div align="center">
    <img src="https://github.com/openscilab/dmeta/raw/main/otherfiles/logo.png" width="280" height="400">
    <br/>
    <br/>
    <a href="https://codecov.io/gh/openscilab/dmeta"><img src="https://codecov.io/gh/openscilab/dmeta/branch/dev/graph/badge.svg" alt="Codecov"></a>
    <a href="https://badge.fury.io/py/dmeta"><img src="https://badge.fury.io/py/dmeta.svg" alt="PyPI version" height="18"></a>
    <a href="https://www.python.org/"><img src="https://img.shields.io/badge/built%20with-Python3-green.svg" alt="built with Python3"></a>
    <a href="https://discord.gg/626twyuPZG"><img src="https://img.shields.io/discord/1064533716615049236.svg" alt="Discord Channel"></a>
</div>

----------

## Overview
<p align="justify">
DMeta is an open source Python package that removes metadata of Microsoft Office files.
</p>
<table>
    <tr>
        <td align="center">PyPI Counter</td>
        <td align="center">
            <a href="http://pepy.tech/project/dmeta">
                <img src="http://pepy.tech/badge/dmeta">
            </a>
        </td>
    </tr>
    <tr>
        <td align="center">Github Stars</td>
        <td align="center">
            <a href="https://github.com/openscilab/dmeta">
                <img src="https://img.shields.io/github/stars/openscilab/dmeta.svg?style=social&label=Stars">
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
            <img src="https://github.com/openscilab/dmeta/actions/workflows/test.yml/badge.svg?branch=main">
        </td>
        <td align="center">
            <img src="https://github.com/openscilab/dmeta/actions/workflows/test.yml/badge.svg?branch=dev">
            </td>
    </tr>
</table>


## Installation

### PyPI

- Check [Python Packaging User Guide](https://packaging.python.org/installing/)
- Run `pip install dmeta==0.2`
### Source code
- Download [Version 0.2](https://github.com/openscilab/dmeta/archive/v0.2.zip) or [Latest Source](https://github.com/openscilab/dmeta/archive/dev.zip)
- Run `pip install .`

## Usage
### In Python
⚠️ Use `in_place` to apply the changes directly to the original file.

⚠️`in_place` flag is `False` by default.

#### Clear metadata for a .docx file in place
```python
import os
from dmeta.functions import clear

DOCX_FILE_PATH = os.path.join(os.getcwd(), "sample.docx")
clear(DOCX_FILE_PATH, in_place=True)
```
#### Clear metadata for all existing microsoft files (.docx|.pptx|.xlsx) in the current directory
```python
from dmeta.functions import clear_all
clear_all()
```
#### Update metadata for a .pptx file in place
```python
import os
from dmeta.functions import update

CONFIG_FILE_PATH = os.path.join(os.getcwd(), "config.json") 
DOCX_FILE_PATH = os.path.join(os.getcwd(), "sample.pptx")
update(CONFIG_FILE_PATH, DOCX_FILE_PATH, in_place=True)
```
#### Update metadata for all existing microsoft files (.docx|.pptx|.xlsx) in the current directory
```python
import os
from dmeta.functions import update_all

CONFIG_FILE_PATH = os.path.join(os.getcwd(), "config.json") 
update_all(CONFIG_FILE_PATH)
```

### CLI
⚠️ You can use `dmeta` or `python -m dmeta` to run this program

⚠️ Use `--inplace` to apply the changes directly to the original file.


#### Version
```console
dmeta -v
dmeta --version
```
#### Clear metadata for a .docx file in place
```console
dmeta --clear "./test_a.docx" --inplace
```
#### Clear metadata for all existing microsoft files (.docx|.pptx|.xlsx) in the current directory
```console
dmeta --clear-all
```
#### Update metadata for a .xlsx file in place
```console
dmeta --update "./test_a.xlsx" --config "./config.json" --inplace
```
#### Update metadata for all existing microsoft files (.docx|.pptx|.xlsx) files in the current directory
```console
dmeta --update-all --config "./config.json"
```

## Supported files
| File format | support | 
| ---------------- | ---------------- | 
| Microsoft Word (.docx) | &#x2705; |
| Microsoft PowerPoint (.pptx) | &#x2705; |
| Microsoft Excel (.xlsx) | &#x2705; |


## Issues & bug reports

Just fill an issue and describe it. We'll check it ASAP! or send an email to [dmeta@openscilab.com](mailto:dmeta@openscilab.com "dmeta@openscilab.com"). 

- Please complete the issue template
 
You can also join our discord server

<a href="https://discord.gg/626twyuPZG">
  <img src="https://img.shields.io/discord/1064533716615049236.svg?style=for-the-badge" alt="Discord Channel">
</a>


## Show your support


### Star this repo

Give a ⭐️ if this project helped you!

### Donate to our project
If you do like our project and we hope that you do, can you please support us? Our project is not and is never going to be working for profit. We need the money just so we can continue doing what we do ;-) .			

<a href="https://openscilab.com/#donation" target="_blank"><img src="https://github.com/openscilab/dmeta/raw/main/otherfiles/donation.png" height="90px" width="270px" alt="DMeta Donation"></a>
