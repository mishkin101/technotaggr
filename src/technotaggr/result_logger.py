"""Result logging for TechnoTaggr."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from .config import DEFAULT_OUTPUT_DIR
from .inference import AudioAnalysisResult

logger = logging.getLogger(__name__)


@dataclass
class SessionResults:
    """Container for all results from a processing session."""

    session_timestamp: str
    input_directory: str
    output_directory: str
    total_files: int
    successful_files: int
    failed_files: int
    classifiers_used: list[str]
    results: list[dict[str, Any]] = field(default_factory=list)


class ResultLogger:
    """Logger for inference results with JSON output."""

    def __init__(
        self,
        output_dir: Path = DEFAULT_OUTPUT_DIR,
        input_dir: Path | None = None,
    ):
        """Initialize the result logger.

        Args:
            output_dir: Directory to write result files.
            input_dir: Input directory being processed (for metadata).
        """
        self.output_dir = Path(output_dir)
        self.input_dir = input_dir
        self.session_timestamp = datetime.now()
        self._results: list[AudioAnalysisResult] = []
        self._classifiers_used: set[str] = set()
        self._failed_count: int = 0

    def log_result(self, result: AudioAnalysisResult) -> None:
        """Log a single analysis result.

        Args:
            result: The analysis result to log.
        """
        self._results.append(result)

        # Track classifiers used
        for pred in result.predictions:
            self._classifiers_used.add(pred.classifier_name)

        logger.debug(f"Logged result for: {result.audio_path}")

    def log_failure(self, audio_path: Path, error: str) -> None:
        """Log a failed analysis.

        Args:
            audio_path: Path to the audio file that failed.
            error: Error message.
        """
        self._failed_count += 1
        logger.error(f"Failed to process {audio_path}: {error}")

    def _format_result(self, result: AudioAnalysisResult) -> dict[str, Any]:
        """Format a single result for JSON output."""
        return {
            "audio_file": result.audio_path,
            "audio_duration_seconds": round(result.audio_duration_seconds, 3),
            "sample_rate": result.sample_rate,
            "models": [
                {
                    "model_name": pred.classifier_name,
                    "model_version": pred.classifier_version,
                    "model_path": pred.classifier_path,
                    "embedding_model": pred.embedding_model_name,
                    "embedding_model_path": pred.embedding_model_path,
                    "classes": pred.classes,
                    "num_segments": pred.num_segments,
                    "segment_predictions": pred.segment_predictions,
                    "aggregated_predictions": pred.aggregated_predictions,
                }
                for pred in result.predictions
            ],
        }

    def get_session_results(self) -> SessionResults:
        """Get the complete session results.

        Returns:
            SessionResults object with all logged results.
        """
        return SessionResults(
            session_timestamp=self.session_timestamp.isoformat(),
            input_directory=str(self.input_dir) if self.input_dir else "",
            output_directory=str(self.output_dir),
            total_files=len(self._results) + self._failed_count,
            successful_files=len(self._results),
            failed_files=self._failed_count,
            classifiers_used=sorted(self._classifiers_used),
            results=[self._format_result(r) for r in self._results],
        )

    def save(self, filename: str | None = None) -> Path:
        """Save results to a JSON file.

        Args:
            filename: Optional custom filename. If not provided, uses
                      timestamped filename.

        Returns:
            Path to the saved JSON file.
        """
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename if not provided
        if filename is None:
            timestamp_str = self.session_timestamp.strftime("%Y%m%d_%H%M%S")
            filename = f"results_{timestamp_str}.json"

        output_path = self.output_dir / filename

        # Get session results
        session_results = self.get_session_results()

        # Write JSON file
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(asdict(session_results), f, indent=2, ensure_ascii=False)

        logger.info(f"Results saved to: {output_path}")
        return output_path

    def print_summary(self) -> None:
        """Print a summary of the session to the console."""
        session = self.get_session_results()

        print("\n" + "=" * 60)
        print("TechnoTaggr Analysis Summary")
        print("=" * 60)
        print(f"Session: {session.session_timestamp}")
        print(f"Input:   {session.input_directory}")
        print(f"Output:  {session.output_directory}")
        print("-" * 60)
        print(f"Total files:      {session.total_files}")
        print(f"Successful:       {session.successful_files}")
        print(f"Failed:           {session.failed_files}")
        print(f"Classifiers used: {len(session.classifiers_used)}")
        print("-" * 60)

        # Print per-file summary
        if self._results:
            print("\nPer-file Results:")
            for result in self._results:
                audio_name = Path(result.audio_path).name
                print(f"\n  {audio_name}")
                print(f"    Duration: {result.audio_duration_seconds:.1f}s")
                for pred in result.predictions:
                    # Find top prediction
                    if pred.aggregated_predictions:
                        top_class = max(
                            pred.aggregated_predictions.items(),
                            key=lambda x: x[1],
                        )
                        print(
                            f"    {pred.classifier_name}: "
                            f"{top_class[0]} ({top_class[1]:.2%})"
                        )

        print("\n" + "=" * 60)

