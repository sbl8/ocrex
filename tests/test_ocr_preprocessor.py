# bandit: skip=B101
import os
import cv2
import numpy as np
from ocrex.preprocessor import preprocess_image


def create_dummy_image(path: str, angle: int = 0):
    """
    Creates a simple white image with black text rotated by `angle` degrees.
    """
    image = np.full((200, 200, 3), 255, dtype=np.uint8)
    cv2.putText(
        image, "TEST", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2
    )
    if angle != 0:
        M = cv2.getRotationMatrix2D((100, 100), angle, 1.0)
        image = cv2.warpAffine(image, M, (200, 200))
    cv2.imwrite(path, image)


def test_preprocess_image_auto_rotate(tmp_path):
    dummy_image = tmp_path / "dummy.png"
    create_dummy_image(str(dummy_image), angle=90)
    processed_path = preprocess_image(
        str(dummy_image), deskew=True, denoise=True, auto_rotate=True
    )
    assert os.path.exists(processed_path)  # nosec B101
    processed = cv2.imread(processed_path, cv2.IMREAD_GRAYSCALE)
    assert processed is not None  # nosec B101
    os.remove(processed_path)
    os.remove(str(dummy_image))


def test_preprocess_image_no_rotate(tmp_path):
    dummy_image = tmp_path / "dummy.png"
    create_dummy_image(str(dummy_image), angle=0)
    processed_path = preprocess_image(
        str(dummy_image), deskew=True, denoise=True, auto_rotate=False
    )
    assert os.path.exists(processed_path)  # nosec B101
    processed = cv2.imread(processed_path, cv2.IMREAD_GRAYSCALE)
    assert processed is not None  # nosec B101
    os.remove(processed_path)
    os.remove(str(dummy_image))
