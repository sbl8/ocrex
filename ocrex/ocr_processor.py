"""
OCRex OCR Processor
A wrapper for OCRmyPDF.
"""

import logging
import ocrmypdf
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Tuple


def _run_ocr_single(
    input_pdf: str, output_pdf: str, optimize_level: int
) -> None:
    """
    Internal function to run OCR on a single PDF using OCRmyPDF.
    """
    ocrmypdf.ocr(
        input_pdf,
        output_pdf,
        language="eng",
        optimize=optimize_level,
        use_threads=True,
        skip_text=True,
        force_ocr=False,
    )


def run_ocr(
    input_pdf: str,
    output_pdf: str,
    optimize_level: int = 1,
    show_progress: bool = True,
) -> None:
    """
    Runs OCR processing on a single PDF file.
    Displays progress via tqdm if enabled.
    Ensures full error handling to prevent system crashes.

    Args:
        input_pdf (str): Path to the input PDF.
        output_pdf (str): Path where the OCR-processed PDF will be saved.
        optimize_level (int): OCRmyPDF optimization level (0-3).
        show_progress (bool): Toggle progress bar display.

    Raises:
        RuntimeError: If OCR processing fails.
    """
    logging.info(f"[OCR] Starting OCR for {input_pdf}")
    try:
        if show_progress:
            with tqdm(
                total=1,
                desc=f"OCR: {input_pdf}",
                leave=True,
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}",
            ) as pbar:
                _run_ocr_single(input_pdf, output_pdf, optimize_level)
                pbar.update(1)
        else:
            _run_ocr_single(input_pdf, output_pdf, optimize_level)
        logging.info(f"[OCR] Completed OCR for {output_pdf}")
    except Exception as e:
        logging.error(f"[OCR] Failed OCR for {input_pdf}: {e}")
        raise RuntimeError(
            f"[OCR] OCR processing failed for {input_pdf}"
        ) from e


def run_ocr_batch(
    pdf_tasks: List[Tuple[str, str, int]],
    max_workers: int = None,
    show_progress: bool = True,
) -> None:
    """
    Runs OCR processing concurrently on a batch of PDF files.
    Each task is a tuple: (input_pdf, output_pdf, optimize_level).

    Args:
        pdf_tasks (List[Tuple[str, str, int]]): List of OCR tasks.
        max_workers (int): Maximum number of parallel processes.
        show_progress (bool): Toggle progress bar display.
    """
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        future_to_task = {
            executor.submit(_run_ocr_single, inp, outp, opt): (inp, outp)
            for inp, outp, opt in pdf_tasks
        }
        if show_progress:
            for future in tqdm(
                as_completed(future_to_task),
                total=len(future_to_task),
                desc="Batch OCR",
            ):
                task = future_to_task[future]
                try:
                    future.result()
                    logging.info(f"[OCR] Completed: {task[0]} -> {task[1]}")
                except Exception as e:
                    logging.error(f"[OCR] Failed processing {task[0]}: {e}")
        else:
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    future.result()
                    logging.info(f"[OCR] Completed: {task[0]} -> {task[1]}")
                except Exception as e:
                    logging.error(f"[OCR] Failed processing {task[0]}: {e}")
