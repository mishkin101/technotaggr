"""Post-processing for 16-bar musical phrase aggregation."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import librosa
import numpy as np

logger = logging.getLogger(__name__)


def estimate_bpm(audio_path: Path) -> float:
    """Estimate BPM of an audio file using librosa.

    Args:
        audio_path: Path to the audio file.

    Returns:
        Estimated BPM as a float.
    """
    logger.debug(f"Estimating BPM for: {audio_path}")

    # Load audio with librosa (uses 22050 Hz by default, good for beat tracking)
    y, sr = librosa.load(audio_path, sr=None)

    # Use beat_track to estimate tempo
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

    # tempo can be an array in some librosa versions, extract scalar
    if isinstance(tempo, np.ndarray):
        tempo = float(tempo[0]) if tempo.size > 0 else 120.0
    else:
        tempo = float(tempo)

    logger.debug(f"Estimated BPM: {tempo:.1f}")
    return tempo


def calculate_phrase_duration(bpm: float) -> float:
    """Calculate the duration of a 16-bar phrase in 4/4 time.

    Formula: 16 bars * 4 beats per bar * (60 seconds per minute / BPM)

    Args:
        bpm: Beats per minute.

    Returns:
        Duration in seconds.
    """
    return 16 * 4 * (60 / bpm)


def chunk_predictions(
    predictions: list[list[float]],
    segments_per_phrase: float,
) -> list[list[list[float]]]:
    """Split segment predictions into 16-bar phrase chunks.

    Args:
        predictions: List of segment predictions (segments x classes).
        segments_per_phrase: Approximate number of segments per 16-bar phrase.

    Returns:
        List of chunks, where each chunk is a list of segment predictions.
    """
    if not predictions:
        return []

    # Convert to numpy for easier slicing
    pred_array = np.array(predictions)
    num_segments = len(predictions)

    # Round segments_per_phrase to get chunk size
    chunk_size = max(1, round(segments_per_phrase))

    # Create chunks
    chunks = []
    for start in range(0, num_segments, chunk_size):
        end = min(start + chunk_size, num_segments)
        chunk = pred_array[start:end].tolist()
        chunks.append(chunk)

    return chunks


def compute_bar_predictions(
    chunks: list[list[list[float]]],
    classes: list[str],
) -> tuple[list[list[float]], dict[str, float]]:
    """Compute mean predictions for each 16-bar phrase and overall aggregation.

    Args:
        chunks: List of phrase chunks, each containing segment predictions.
        classes: List of class names.

    Returns:
        Tuple of (bar_predictions, aggregated_bar_predictions):
        - bar_predictions: Mean prediction for each phrase (phrases x classes)
        - aggregated_bar_predictions: Mean of bar_predictions as dict
    """
    if not chunks:
        return [], {}

    # Compute mean for each chunk (phrase)
    bar_predictions = []
    for chunk in chunks:
        chunk_array = np.array(chunk)
        chunk_mean = np.mean(chunk_array, axis=0).tolist()
        bar_predictions.append(chunk_mean)

    # Compute overall mean from bar predictions
    bar_array = np.array(bar_predictions)
    overall_mean = np.mean(bar_array, axis=0)

    aggregated_bar_predictions = {
        class_name: float(prob)
        for class_name, prob in zip(classes, overall_mean)
    }

    return bar_predictions, aggregated_bar_predictions


def postprocess_audio_result(
    result: dict[str, Any],
    audio_base_path: Path | None = None,
) -> dict[str, Any]:
    """Add 16-bar phrase predictions to a single audio result.

    Args:
        result: Audio result dictionary from the JSON file.
        audio_base_path: Base path to resolve relative audio paths.

    Returns:
        Updated result dictionary with BPM and bar predictions.
    """
    audio_file = result["audio_file"]
    audio_path = Path(audio_file)

    # Resolve relative paths if needed
    if not audio_path.is_absolute() and audio_base_path:
        audio_path = audio_base_path / audio_path

    if not audio_path.exists():
        logger.warning(f"Audio file not found: {audio_path}")
        return result

    # Estimate BPM
    bpm = estimate_bpm(audio_path)
    phrase_duration = calculate_phrase_duration(bpm)

    # Add BPM and phrase duration to result
    result["bpm"] = round(bpm, 2)
    result["phrase_duration_seconds"] = round(phrase_duration, 3)

    # Get audio duration and calculate segment duration
    audio_duration = result["audio_duration_seconds"]

    # Process each model's predictions
    for model in result.get("models", []):
        num_segments = model.get("num_segments", 0)
        segment_predictions = model.get("segment_predictions", [])
        classes = model.get("classes", [])

        if num_segments == 0 or not segment_predictions:
            continue

        # Calculate segment duration and segments per phrase
        segment_duration = audio_duration / num_segments
        segments_per_phrase = phrase_duration / segment_duration

        logger.debug(
            f"Model {model['model_name']}: "
            f"{num_segments} segments, "
            f"{segment_duration:.2f}s per segment, "
            f"{segments_per_phrase:.1f} segments per 16-bar phrase"
        )

        # Chunk predictions and compute bar predictions
        chunks = chunk_predictions(segment_predictions, segments_per_phrase)
        bar_predictions, aggregated_bar_predictions = compute_bar_predictions(
            chunks, classes
        )

        # Add to model result
        model["bar_predictions"] = bar_predictions
        model["aggregated_bar_predictions"] = aggregated_bar_predictions

    return result


def postprocess_results(
    json_path: Path,
    output_path: Path | None = None,
    audio_base_path: Path | None = None,
) -> Path:
    """Process a results JSON file to add 16-bar phrase predictions.

    Args:
        json_path: Path to the input JSON results file.
        output_path: Optional output path. If None, overwrites input file.
        audio_base_path: Base path to resolve relative audio paths.
            If None, uses the current working directory.

    Returns:
        Path to the output JSON file.
    """
    logger.info(f"Post-processing results from: {json_path}")

    # Load existing results
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Use audio_base_path or current working directory
    if audio_base_path is None:
        audio_base_path = Path.cwd()

    # Process each audio result
    results = data.get("results", [])
    total = len(results)

    for i, result in enumerate(results, 1):
        audio_file = result.get("audio_file", "unknown")
        logger.info(f"[{i}/{total}] Processing: {Path(audio_file).name}")

        try:
            postprocess_audio_result(result, audio_base_path)
        except Exception as e:
            logger.error(f"Failed to post-process {audio_file}: {e}")

    # Determine output path
    if output_path is None:
        output_path = json_path

    # Save updated results
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info(f"Post-processed results saved to: {output_path}")
    return output_path

