#!/usr/bin/env python

import setuptools

from chord_project_service import __version__

with open("README.md", "r") as rf:
    long_description = rf.read()

setuptools.setup(
    name="chord_project_service",
    version=__version__,

    python_requires=">=3.6",
    install_requires=["Flask", "jsonschema"],

    author="David Lougheed",
    author_email="david.lougheed@mail.mcgill.ca",

    description="Project service for the CHORD project.",
    long_description=long_description,
    long_description_content_type="text/markdown",

    packages=["chord_project_service"],
    include_package_data=True,

    url="TODO",
    license="LGPLv3",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ]
)
