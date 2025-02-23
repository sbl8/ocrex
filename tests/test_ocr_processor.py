# bandit: skip=B101
import pytest
from ocrex.ocr_processor import run_ocr


def test_run_ocr_invalid_file():
    with pytest.raises(RuntimeError):
        run_ocr(
            "nonexistent.pdf",
            "output.pdf",
            optimize_level=1,
            show_progress=False,
        )
