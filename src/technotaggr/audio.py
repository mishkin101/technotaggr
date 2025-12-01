"""Audio loading and file discovery utilities for TechnoTaggr."""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
from essentia.standard import MonoLoader

from .config import DEFAULT_RESAMPLE_QUALITY, SUPPORTED_FORMATS

logger = logging.getLogger(__name__)


def load_audio(
    path: Path,
    sample_rate: int,
    resample_quality: int = DEFAULT_RESAMPLE_QUALITY,
) -> np.ndarray:
    """Load an audio file as a mono signal.

    Args:
        path: Path to the audio file.
        sample_rate: Target sample rate in Hz.
        resample_quality: Resampling quality (0-4, higher is better).

    Returns:
        Audio signal as a 1D numpy array.

    Raises:
        FileNotFoundError: If the audio file doesn't exist.
        RuntimeError: If the audio file cannot be loaded.
    """
    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {path}")

    logger.debug(f"Loading audio: {path} at {sample_rate} Hz")

    try:
        loader = MonoLoader(
            filename=path.as_posix(),
            sampleRate=sample_rate,
            resampleQuality=resample_quality,
        )
        audio = loader()
        logger.debug(f"Loaded {len(audio)} samples ({len(audio) / sample_rate:.2f}s)")
        return audio
    except Exception as e:
        raise RuntimeError(f"Failed to load audio file {path}: {e}") from e


def get_audio_duration(audio: np.ndarray, sample_rate: int) -> float:
    """Calculate the duration of an audio signal in seconds.

    Args:
        audio: Audio signal as a numpy array.
        sample_rate: Sample rate in Hz.

    Returns:
        Duration in seconds.
    """
    return len(audio) / sample_rate


def discover_audio_files(
    input_dir: Path,
    supported_formats: set[str] = SUPPORTED_FORMATS,
    recursive: bool = False,
) -> list[Path]:
    """Discover audio files in a directory.

    Args:
        input_dir: Directory to search for audio files.
        supported_formats: Set of supported file extensions (lowercase, with dot).
        recursive: If True, search subdirectories recursively.

    Returns:
        List of paths to discovered audio files, sorted alphabetically.

    Raises:
        NotADirectoryError: If input_dir is not a directory.
    """
    if not input_dir.is_dir():
        raise NotADirectoryError(f"Not a directory: {input_dir}")

    audio_files: list[Path] = []

    if recursive:
        iterator = input_dir.rglob("*")
    else:
        iterator = input_dir.iterdir()

    for path in iterator:
        if path.is_file() and path.suffix.lower() in supported_formats:
            audio_files.append(path)

    audio_files.sort()
    logger.info(f"Discovered {len(audio_files)} audio file(s) in {input_dir}")
    return audio_files

