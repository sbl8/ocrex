#!/usr/bin/env python3
"""
OCRex v0.0.1 - Setup Script
A professional, modular OCR processing tool for bulk PDF ingestion.
"""

from setuptools import setup, find_packages

setup(
    name="ocrex",
    version="0.0.1",
    description="A non-destructive, bulk PDF OCR tool using OCRmyPDF.",
    author="sbl8",
    author_email="sbl8@tuta.io",
    url="https://github.com/sbl8/ocrex",
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=[
        "ocrmypdf>=13.6.0",
        "pdf2image>=1.16.0",
        "Pillow>=9.0.0",
        "opencv-python-headless>=4.5.0",
        "rich>=12.0.0",
        "pytesseract>=0.3.8",
    ],
    entry_points={"console_scripts": ["ocrex=ocrex.main:main"]},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Optical Character Recognition",
    ],
    python_requires=">=3.6",
)
