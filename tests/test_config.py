# bandit: skip=B101
import os
import pytest
from ocrex.config import Config


def test_default_config():
    config = Config()
    assert os.path.basename(config.input_dir) == "input"  # nosec B101
    assert os.path.basename(config.output_dir) == "output"  # nosec B101
    assert config.workers >= 1  # nosec B101
    assert config.enable_preprocessing is True  # nosec B101
    assert config.deskew is True  # nosec B101
    assert config.denoise is True  # nosec B101
    assert config.optimize_level in [0, 1, 2, 3]  # nosec B101
    assert config.pdf_dpi > 0  # nosec B101
    assert isinstance(config.verbose, bool)  # nosec B101


def test_custom_config(tmp_path):
    input_dir = str(tmp_path / "in")
    output_dir = str(tmp_path / "out")
    config = Config(
        input_dir=input_dir,
        output_dir=output_dir,
        workers=8,
        enable_preprocessing=False,
        deskew=False,
        denoise=False,
        optimize_level=2,
        pdf_dpi=600,
        verbose=True,
    )
    assert config.input_dir == input_dir  # nosec B101
    assert config.output_dir == output_dir  # nosec B101
    assert config.workers == 8  # nosec B101
    assert config.enable_preprocessing is False  # nosec B101
    assert config.deskew is False  # nosec B101
    assert config.denoise is False  # nosec B101
    assert config.optimize_level == 2  # nosec B101
    assert config.pdf_dpi == 600  # nosec B101
    assert config.verbose is True  # nosec B101
