"""Command-line interface for TechnoTaggr."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from .audio import discover_audio_files
from .config import DEFAULT_MODELS_DIR, DEFAULT_OUTPUT_DIR
from .inference import InferencePipeline
from .model_loader import discover_classifiers
from .result_logger import ResultLogger


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the CLI.

    Args:
        verbose: If True, enable DEBUG level logging.
    """
    level = logging.DEBUG if verbose else logging.INFO
    format_str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

    # Configure root logger
    logging.basicConfig(
        level=level,
        format=format_str,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Reduce verbosity of some loggers
    if not verbose:
        logging.getLogger("essentia").setLevel(logging.WARNING)


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="technotaggr",
        description="Analyze audio files using Essentia TensorFlow models.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/music
  %(prog)s /path/to/music --output-dir ./results
  %(prog)s /path/to/music -v --recursive
        """,
    )

    parser.add_argument(
        "input_dir",
        type=Path,
        help="Directory containing audio files to analyze",
    )

    parser.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory for output files (default: {DEFAULT_OUTPUT_DIR})",
    )

    parser.add_argument(
        "--models-dir",
        "-m",
        type=Path,
        default=DEFAULT_MODELS_DIR,
        help="Directory containing model files (default: package models)",
    )

    parser.add_argument(
        "--recursive",
        "-r",
        action="store_true",
        help="Search for audio files recursively in subdirectories",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose (debug) logging",
    )

    parser.add_argument(
        "--no-summary",
        action="store_true",
        help="Don't print summary to console after processing",
    )

    return parser


def progress_callback(current: int, total: int, path: Path) -> None:
    """Print progress during batch processing."""
    print(f"[{current}/{total}] Processing: {path.name}")


def run_cli(args: argparse.Namespace) -> int:
    """Run the CLI with parsed arguments.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    # Validate input directory
    if not args.input_dir.exists():
        logger.error(f"Input directory does not exist: {args.input_dir}")
        return 1

    if not args.input_dir.is_dir():
        logger.error(f"Input path is not a directory: {args.input_dir}")
        return 1

    # Discover audio files
    logger.info(f"Scanning for audio files in: {args.input_dir}")
    audio_files = discover_audio_files(
        args.input_dir,
        recursive=args.recursive,
    )

    if not audio_files:
        logger.warning("No audio files found in input directory")
        return 0

    print(f"Found {len(audio_files)} audio file(s)")

    # Discover classifiers
    classification_heads_dir = args.models_dir / "classification-heads"
    feature_extractors_dir = args.models_dir / "feature-extractors"

    logger.info("Discovering classifiers...")
    classifiers = discover_classifiers(
        classification_heads_dir,
        feature_extractors_dir,
    )

    if not classifiers:
        logger.error("No classifiers found. Check models directory.")
        return 1

    print(f"Loaded {len(classifiers)} classifier(s)")

    # Create inference pipeline
    pipeline = InferencePipeline(classifiers)

    # Create result logger
    result_logger = ResultLogger(
        output_dir=args.output_dir,
        input_dir=args.input_dir,
    )

    # Process audio files
    print("\nStarting analysis...")
    print("-" * 40)

    for i, audio_path in enumerate(audio_files, 1):
        print(f"[{i}/{len(audio_files)}] {audio_path.name}")

        try:
            result = pipeline.analyze_audio(audio_path)
            result_logger.log_result(result)
        except Exception as e:
            result_logger.log_failure(audio_path, str(e))
            logger.error(f"Failed to process {audio_path.name}: {e}")

    print("-" * 40)

    # Save results
    output_path = result_logger.save()
    print(f"\nResults saved to: {output_path}")

    # Print summary
    if not args.no_summary:
        result_logger.print_summary()

    return 0


def main() -> None:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()

    try:
        exit_code = run_cli(args)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        exit_code = 130
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()

