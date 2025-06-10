# -*- coding: utf-8 -*-
"""Setup module."""
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def get_requires():
    """Read requirements.txt."""
    requirements = open("requirements.txt", "r").read()
    return list(filter(lambda x: x != "", requirements.split()))


def read_description():
    """Read README.md and CHANGELOG.md."""
    try:
        with open("README.md") as r:
            description = "\n"
            description += r.read()
        with open("CHANGELOG.md") as c:
            description += "\n"
            description += c.read()
        return description
    except Exception:
        return '''Removing metadata'''


setup(
    name='DMeta',
    packages=['dmeta'],
    version='0.4',
    description='Removing microsoft office files\' metadata',
    long_description=read_description(),
    long_description_content_type='text/markdown',
    author='DMeta Development Team',
    author_email='dmeta@openscilab.com',
    url='https://github.com/openscilab/dmeta',
    download_url='https://github.com/openscilab/dmeta/tarball/v0.4',
    keywords="python3 python metadata remove",
    project_urls={
            'Source': 'https://github.com/openscilab/dmeta',
    },
    install_requires=get_requires(),
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Manufacturing',
        'Intended Audience :: Science/Research',
        'Topic :: Security',
        'Topic :: Utilities',
    ],
    license='MIT',
    entry_points={
            'console_scripts': [
                'dmeta = dmeta.__main__:main',
            ]
    }
)
