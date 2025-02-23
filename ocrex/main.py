#!/usr/bin/env python3
"""
Main entry point for OCRex.
Processes PDFs in bulk using OCRmyPDF with optional pre-processing.
Provides colored terminal output, progress bars, and extensive CLI parameters.
This version leverages robust concurrency, asynchronous progress updates,
and comprehensive error handling to ensure stability and performance.
"""

import os
import sys
import argparse
import multiprocessing
import logging
from rich.console import Console
from rich.progress import Progress
from ocrex.config import Config
from ocrex.preprocessor import preprocess_image
from ocrex.ocr_processor import run_ocr
from ocrex.utils import pdf_to_images, images_to_pdf, cleanup_temp_files
from ocrex.logger_setup import setup_logger

console = Console()


def process_file(pdf_file, config):
    """
    Process a single PDF file: optionally pre-process,
    run OCR, and save output.
    Ensures that the original PDF remains unaltered.
    """
    console.print(f"[cyan]Processing file:[/cyan] [bold]{pdf_file}[/bold]")
    try:
        working_pdf = pdf_file
        temp_files = []
        if config.enable_preprocessing:
            # Convert PDF to images using the specified DPI
            images = pdf_to_images(pdf_file, dpi=config.pdf_dpi)
            preprocessed_images = []
            # Preprocess each image (auto-rotate, deskew, denoise) sequentially
            for image_file in images:
                processed = preprocess_image(
                    image_file,
                    deskew=config.deskew,
                    denoise=config.denoise,
                    auto_rotate=True,
                )
                preprocessed_images.append(processed)
                temp_files.extend([processed, image_file])
            # Reassemble processed images into a new PDF file
            preprocessed_pdf = pdf_file.replace(".pdf", "_preprocessed.pdf")
            images_to_pdf(preprocessed_images, preprocessed_pdf)
            working_pdf = preprocessed_pdf
            temp_files.append(preprocessed_pdf)
        # Run OCR on the (possibly preprocessed) PDF file
        output_pdf = os.path.join(
            config.output_dir,
            os.path.basename(pdf_file).replace(".pdf", "_ocr.pdf"),
        )
        run_ocr(working_pdf, output_pdf, optimize_level=config.optimize_level)
        # Cleanup any temporary files created during processing
        cleanup_temp_files(temp_files)
        console.print(
            f"[green]Completed file:[/green] [bold]{
                pdf_file}[/bold] -> [magenta]{output_pdf}[/magenta]"
        )
    except Exception as e:
        console.print(f"[red]Error processing file {pdf_file}: {e}[/red]")
        logging.exception(e)


def main():
    parser = argparse.ArgumentParser(
        description="Bulk OCR tool for declassified documents using OCRmyPDF"
    )
    parser.add_argument(
        "--input_dir",
        type=str,
        default="./input",
        help="Directory containing PDF files",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./output",
        help="Directory for output OCR PDFs",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=multiprocessing.cpu_count(),
        help="Number of parallel workers",
    )
    parser.add_argument(
        "--enable_preprocessing",
        dest="enable_preprocessing",
        action="store_true",
        help="Enable image preprocessing (default)",
    )
    parser.add_argument(
        "--disable_preprocessing",
        dest="enable_preprocessing",
        action="store_false",
        help="Disable image preprocessing",
    )
    parser.set_defaults(enable_preprocessing=True)
    parser.add_argument(
        "--deskew",
        dest="deskew",
        action="store_true",
        help="Enable deskewing in preprocessing (default)",
    )
    parser.add_argument(
        "--no_deskew",
        dest="deskew",
        action="store_false",
        help="Disable deskewing in preprocessing",
    )
    parser.set_defaults(deskew=True)
    parser.add_argument(
        "--denoise",
        dest="denoise",
        action="store_true",
        help="Enable denoising in preprocessing (default)",
    )
    parser.add_argument(
        "--no_denoise",
        dest="denoise",
        action="store_false",
        help="Disable denoising in preprocessing",
    )
    parser.set_defaults(denoise=True)
    parser.add_argument(
        "--optimize_level",
        type=int,
        default=1,
        choices=[0, 1, 2, 3],
        help="OCRmyPDF optimization level",
    )
    parser.add_argument(
        "--pdf_dpi",
        type=int,
        default=300,
        help="DPI for PDF to image conversion",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose logging"
    )
    args = parser.parse_args()

    # Build the configuration object from CLI parameters
    config = Config(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        workers=args.workers,
        enable_preprocessing=args.enable_preprocessing,
        deskew=args.deskew,
        denoise=args.denoise,
        optimize_level=args.optimize_level,
        pdf_dpi=args.pdf_dpi,
        verbose=args.verbose,
    )

    # Validate input and output directories
    if not os.path.exists(config.input_dir):
        console.print(
            f"[red]Input directory '{config.input_dir}' does not exist.[/red]"
        )
        sys.exit(1)
    if not os.path.exists(config.output_dir):
        os.makedirs(config.output_dir)

    setup_logger(verbose=config.verbose)

    # Gather all PDF files from the input directory
    pdf_files = [
        os.path.join(config.input_dir, f)
        for f in os.listdir(config.input_dir)
        if f.lower().endswith(".pdf")
    ]
    if not pdf_files:
        console.print(
            f"[yellow]No PDF files found in '{config.input_dir}'.[/yellow]"
        )
        sys.exit(0)

    console.print(
        f"[cyan]Starting OCR processing for [bold]{
            len(pdf_files)}[/bold] files using [bold]{
                config.workers}[/bold] workers...[/cyan]"
    )

    # Process files concurrently using a multiprocessing pool with progress
    with Progress() as progress:
        task = progress.add_task(
            "[green]Processing PDFs...", total=len(pdf_files)
        )
        with multiprocessing.Pool(processes=config.workers) as pool:
            results = [
                pool.apply_async(process_file, args=(pdf_file, config))
                for pdf_file in pdf_files
            ]
            for r in results:
                r.wait()  # Ensure each file is fully processed
                progress.advance(task)
    console.print("[bold green]OCR processing complete.[/bold green]")


if __name__ == "__main__":
    main()
