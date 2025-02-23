"""
Utilities module for OCRex.
Provides helper functions for:
  - Converting PDFs to image files using pdf2image.
  - Compiling a list of images into a single PDF using Pillow.
  - Cleaning up temporary files created during processing.

All functions are designed to be non-destructive, memory-efficient,
and to handle errors gracefully.
"""

import os
import tempfile
import logging
from typing import List
from pdf2image import convert_from_path
from PIL import Image


def pdf_to_images(pdf_path: str, dpi: int = 300) -> List[str]:
    """
    Convert a PDF file into a list of image file paths.

    Uses the pdf2image library to convert each page of the PDF into an image.
    Each image is saved as a temporary PNG file so that the original PDF
    remains unchanged.

    Args:
        pdf_path (str): The path to the input PDF file.
        dpi (int): Resolution for converting PDF pages to
        images (default is 300 DPI).

    Returns:
        List[str]: A list containing the file paths of the generated images.

    Raises:
        RuntimeError: If the PDF conversion fails.
    """
    logging.info(f"[PDF2IMG] Converting PDF to images: {pdf_path}")
    try:
        images = convert_from_path(pdf_path, dpi=dpi)
        image_files = []
        for i, image in enumerate(images):
            temp_file = tempfile.NamedTemporaryFile(
                delete=False, suffix=".png"
            )
            image.save(temp_file.name, "PNG")
            image_files.append(temp_file.name)
            logging.debug(
                f"[PDF2IMG] Saved temporary image {i} to {temp_file.name}"
            )
        logging.info(
            f"[PDF2IMG] PDF conversion completed successfully: {pdf_path}"
        )
        return image_files
    except Exception as e:
        logging.error(
            f"[PDF2IMG] Error converting PDF to images for {pdf_path}: {e}"
        )
        raise RuntimeError(f"PDF conversion failed for {pdf_path}") from e


def images_to_pdf(image_paths: List[str], output_pdf_path: str) -> None:
    """
    Compile a list of images into a single PDF file.

    Uses the Pillow library to combine images into one PDF.
    The first image is used as the base, and subsequent images are appended.
    Each image is converted to RGB mode if necessary to ensure compatibility.

    Args:
        image_paths (List[str]): A list of file paths for the images to be
        compiled.

        output_pdf_path (str): The destination file path for the compiled PDF.

    Raises:
        RuntimeError: If the PDF creation process fails.
    """
    logging.info(f"[IMG2PDF] Compiling images into PDF: {output_pdf_path}")
    try:
        if not image_paths:
            raise ValueError("No image paths provided for PDF creation.")

        image_list = []
        for img_path in image_paths:
            try:
                image = Image.open(img_path)
                if image.mode != "RGB":
                    image = image.convert("RGB")
                image_list.append(image)
                logging.debug(f"[IMG2PDF] Processed image for PDF: {img_path}")
            except Exception as inner_e:
                logging.error(
                    f"[IMG2PDF] Error processing image {img_path}: {inner_e}"
                )
                continue

        if not image_list:
            raise ValueError("No valid images to compile into PDF.")

        # Save images as a single PDF file.
        image_list[0].save(
            output_pdf_path, save_all=True, append_images=image_list[1:]
        )
        logging.info(f"[IMG2PDF] Successfully compiled PDF: {output_pdf_path}")
    except Exception as e:
        logging.error(
            f"[IMG2PDF] Error compiling image for {output_pdf_path}: {e}"
        )
        raise RuntimeError(f"Failed to create PDF: {output_pdf_path}") from e


def cleanup_temp_files(file_paths: List[str]) -> None:
    """
    Remove temporary files specified in the file_paths list.

    Args:
        file_paths (List[str]): A list of file paths to be removed.

    Logs warnings for any files that cannot be removed.
    """
    for file_path in file_paths:
        try:
            os.remove(file_path)
            logging.debug(f"[Cleanup] Removed temporary file: {file_path}")
        except Exception as e:
            logging.warning(
                f"[Cleanup] Failed to remove temporary file{file_path}: {e}"
            )
