"""
Configuration module for OCRex.
This module defines the Config class which stores all configuration
settings for OCRex.

These settings ensure that original PDFs remain unaltered and all
outputs are generated as new files.Parameters can be customized via
command-line arguments or by modifying these defaults.

Note: All paths are resolved relative to the current working directory
if not explicitly provided.
"""

import os


class Config:
    """
    Configuration class for OCRex.

    Attributes:
        input_dir (str): Directory containing original PDF files.
        output_dir (str): Directory where OCR-processed PDFs will be saved.
        workers (int): Number of parallel worker processes to use.
        enable_preprocessing (bool): Toggle for enabling image pre-processing.
        deskew (bool): Toggle for enabling deskewing during pre-processing.
        denoise (bool): Toggle for enabling denoising during pre-processing.
        optimize_level (int): Optimization level for OCRmyPDF (0, 1, 2, or 3).
        pdf_dpi (int): DPI for converting PDFs to images for OCR.
        verbose (bool): Toggle for enabling verbose logging.
    """

    def __init__(self, **kwargs):
        self.input_dir = kwargs.get(
            "input_dir", os.path.join(os.getcwd(), "input")
        )
        self.output_dir = kwargs.get(
            "output_dir", os.path.join(os.getcwd(), "output")
        )
        self.workers = int(kwargs.get("workers", 4))
        self.enable_preprocessing = kwargs.get("enable_preprocessing", True)
        self.deskew = kwargs.get("deskew", True)
        self.denoise = kwargs.get("denoise", True)
        self.optimize_level = int(kwargs.get("optimize_level", 1))
        self.pdf_dpi = int(kwargs.get("pdf_dpi", 300))
        self.verbose = kwargs.get("verbose", False)
