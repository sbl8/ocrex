"""
OCRex Preprocessor
Optimized for performance, memory efficiency, and security.
Handles image pre-processing—including auto-rotation (using Tesseract's
OSD with OpenCV fallback), deskewing, and denoising.
Includes concurrent processing support for multiple images.
"""

import cv2
import numpy as np
import pytesseract
import tempfile
import logging
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List


def detect_rotation(image_path: str) -> int:
    """
    Detects text rotation using Tesseract OCR's OSD mode.
    Falls back to OpenCV-based line detection if Tesseract fails.
    Returns one of {0, 90, 180, 270} degrees.
    """
    try:
        osd_output = pytesseract.image_to_osd(image_path)
        # Parse output for a line like "Rotate: 90"
        for line in osd_output.splitlines():
            if "Rotate:" in line:
                angle = int(line.split(":")[-1].strip())
                corrected_angle = (360 - angle) % 360
                logging.info(
                    f"[Auto-Rotate] Detected rotation angle: {
                        corrected_angle}° for {image_path}"
                )
                return corrected_angle
        return 0
    except Exception as e:
        logging.warning(
            f"[Auto-Rotate] Tesseract OSD failed for {
                image_path}. Falling back to OpenCV. Error: {e}"
        )
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            logging.error(f"[Auto-Rotate] Unable to load image: {image_path}")
            return 0
        edges = cv2.Canny(image, 50, 150)
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)
        angles = []
        if lines is not None:
            for line in lines:
                rho, theta = line[0]
                angle = np.degrees(theta)
                # Check for nearly horizontal or vertical lines
                if (80 < angle < 100) or (260 < angle < 280):
                    angles.append(angle)
        if angles:
            avg_angle = np.median(angles)
            if 85 <= avg_angle <= 95:
                return 90
            elif 175 <= avg_angle <= 185:
                return 180
            elif 265 <= avg_angle <= 275:
                return 270
        return 0


def rotate_image(image_path: str, angle: int) -> str:
    """
    Rotates the image at image_path by the given angle.
    Only supports rotations of 0, 90, 180, or 270 degrees.
    Returns the path to the rotated image.
    """
    if angle == 0:
        return image_path  # No rotation needed
    image = cv2.imread(image_path)
    if image is None:
        logging.error(f"[Auto-Rotate] Cannot load image: {image_path}")
        return image_path
    rotation_mappings = {
        90: cv2.ROTATE_90_CLOCKWISE,
        180: cv2.ROTATE_180,
        270: cv2.ROTATE_90_COUNTERCLOCKWISE,
    }
    if angle in rotation_mappings:
        rotated = cv2.rotate(image, rotation_mappings[angle])
    else:
        logging.error(f"[Auto-Rotate] Invalid rotation angle: {angle}")
        return image_path
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    cv2.imwrite(temp_file.name, rotated)
    logging.info(f"[Auto-Rotate] Saved rotated image: {temp_file.name}")
    return temp_file.name


def _process_single_image(
    image_path: str, deskew: bool, denoise: bool, auto_rotate: bool
) -> str:
    """
    Processes a single image by auto-rotating, deskewing, and denoising.
    This internal function is intended for concurrent execution.
    Returns the path to the processed image.
    """
    logging.info(f"[Preprocessing] Processing image: {image_path}")
    # Auto-rotate if enabled
    if auto_rotate:
        rotation_angle = detect_rotation(image_path)
        image_path = rotate_image(image_path, rotation_angle)
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"[Preprocessing] Cannot load image {image_path}")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if denoise:
        gray = cv2.fastNlMeansDenoising(
            gray, None, h=30, templateWindowSize=7, searchWindowSize=21
        )
    if deskew:
        coords = np.column_stack(np.where(gray > 0))
        if coords.size > 0:
            angle = cv2.minAreaRect(coords)[-1]
            angle = -(90 + angle) if angle < -45 else -angle
            (h, w) = gray.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            gray = cv2.warpAffine(
                gray,
                M,
                (w, h),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE,
            )
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    cv2.imwrite(temp_file.name, gray)
    return temp_file.name


def preprocess_image(
    image_path: str,
    deskew: bool = True,
    denoise: bool = True,
    auto_rotate: bool = True,
) -> str:
    """
    Preprocess a single image file.
    Returns the path to the processed image.
    """
    return _process_single_image(image_path, deskew, denoise, auto_rotate)


def preprocess_images_concurrent(
    image_paths: List[str],
    deskew: bool = True,
    denoise: bool = True,
    auto_rotate: bool = True,
    max_workers: int = None,
) -> List[str]:
    """
    Concurrently preprocess a list of image files.
    Utilizes ProcessPoolExecutor to parallelize processing.
    Returns a list of paths to the processed images.
    """
    results = []
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        future_to_image = {
            executor.submit(
                _process_single_image, img, deskew, denoise, auto_rotate
            ): img
            for img in image_paths
        }
        for future in tqdm(
            as_completed(future_to_image),
            total=len(future_to_image),
            desc="Preprocessing Images",
        ):
            try:
                processed_path = future.result()
                results.append(processed_path)
            except Exception as e:
                logging.error(
                    f"[Preprocessing] Error processing image {future_to_image[
                        future]}: {e}"
                )
    return results
