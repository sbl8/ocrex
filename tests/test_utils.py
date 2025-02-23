# bandit: skip=B101
import os
from ocrex.utils import pdf_to_images, images_to_pdf, cleanup_temp_files
from PIL import Image


def create_dummy_pdf(path: str):
    image = Image.new("RGB", (100, 100), color="white")
    image.save(path, "PDF", resolution=100.0)


def test_pdf_to_images(tmp_path):
    dummy_pdf = tmp_path / "dummy.pdf"
    create_dummy_pdf(str(dummy_pdf))
    images = pdf_to_images(str(dummy_pdf), dpi=100)
    assert len(images) >= 1  # nosec B101
    for img in images:
        assert os.path.exists(img)  # nosec B101
        os.remove(img)
    os.remove(str(dummy_pdf))


def test_images_to_pdf(tmp_path):
    dummy_img1 = tmp_path / "img1.png"
    dummy_img2 = tmp_path / "img2.png"
    image1 = Image.new("RGB", (100, 100), color="white")
    image2 = Image.new("RGB", (100, 100), color="black")
    image1.save(str(dummy_img1))
    image2.save(str(dummy_img2))
    output_pdf = tmp_path / "output.pdf"
    images_to_pdf([str(dummy_img1), str(dummy_img2)], str(output_pdf))
    assert os.path.exists(str(output_pdf))  # nosec B101
    os.remove(str(dummy_img1))
    os.remove(str(dummy_img2))
    os.remove(str(output_pdf))


def test_cleanup_temp_files(tmp_path):
    temp_file = tmp_path / "temp.txt"
    temp_file.write_text("Temporary content")
    assert os.path.exists(str(temp_file))  # nosec B101
    cleanup_temp_files([str(temp_file)])
    assert not os.path.exists(str(temp_file))  # nosec B101
