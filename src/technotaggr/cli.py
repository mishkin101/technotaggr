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
from .postprocessing import postprocess_results, print_postprocess_summary
from .result_logger import ResultLogger
from .visualization import get_latest_session, run_dashboard


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
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Analyze subcommand
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze audio files and generate predictions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  technotaggr analyze /path/to/music
  technotaggr analyze /path/to/music --output-dir ./results
  technotaggr analyze /path/to/music -v --recursive
        """,
    )

    analyze_parser.add_argument(
        "input_dir",
        type=Path,
        help="Directory containing audio files to analyze",
    )

    analyze_parser.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory for output files (default: {DEFAULT_OUTPUT_DIR})",
    )

    analyze_parser.add_argument(
        "--models-dir",
        "-m",
        type=Path,
        default=DEFAULT_MODELS_DIR,
        help="Directory containing model files (default: package models)",
    )

    analyze_parser.add_argument(
        "--recursive",
        "-r",
        action="store_true",
        help="Search for audio files recursively in subdirectories",
    )

    analyze_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose (debug) logging",
    )

    analyze_parser.add_argument(
        "--no-summary",
        action="store_true",
        help="Don't print summary to console after processing",
    )

    # Postprocess subcommand
    postprocess_parser = subparsers.add_parser(
        "postprocess",
        help="Add 16-bar phrase predictions to existing results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  technotaggr postprocess results.json
  technotaggr postprocess results.json --output processed_results.json
  technotaggr postprocess results.json --audio-base-path /path/to/music
        """,
    )

    postprocess_parser.add_argument(
        "json_file",
        type=Path,
        help="Path to the results JSON file to post-process",
    )

    postprocess_parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Output path for processed results (default: overwrite input)",
    )

    postprocess_parser.add_argument(
        "--audio-base-path",
        "-a",
        type=Path,
        default=None,
        help="Base path to resolve relative audio file paths (default: cwd)",
    )

    postprocess_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose (debug) logging",
    )

    postprocess_parser.add_argument(
        "--no-summary",
        action="store_true",
        help="Don't print summary to console after processing",
    )

    # Visualize subcommand
    visualize_parser = subparsers.add_parser(
        "visualize",
        help="Launch interactive dashboard to visualize analysis results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  technotaggr visualize
  technotaggr visualize --session-file results_20251201_093052.json
  technotaggr visualize --port 8080
        """,
    )

    visualize_parser.add_argument(
        "--session-file",
        "-s",
        type=Path,
        default=None,
        help="Path to a specific session JSON file (default: latest session)",
    )

    visualize_parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host address to bind to (default: 127.0.0.1)",
    )

    visualize_parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=8050,
        help="Port number for the dashboard (default: 8050)",
    )

    visualize_parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help="Run dashboard in debug mode (auto-reload on changes)",
    )

    visualize_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose (debug) logging",
    )

    return parser


def progress_callback(current: int, total: int, path: Path) -> None:
    """Print progress during batch processing."""
    print(f"[{current}/{total}] Processing: {path.name}")


def run_analyze(args: argparse.Namespace) -> int:
    """Run the analyze command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, non-zero for errors).
    """
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


def run_postprocess(args: argparse.Namespace) -> int:
    """Run the postprocess command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    logger = logging.getLogger(__name__)

    # Validate input file
    if not args.json_file.exists():
        logger.error(f"JSON file does not exist: {args.json_file}")
        return 1

    if not args.json_file.is_file():
        logger.error(f"Path is not a file: {args.json_file}")
        return 1

    print(f"Post-processing: {args.json_file}")
    print("-" * 40)

    try:
        output_path, summary = postprocess_results(
            json_path=args.json_file,
            output_path=args.output,
            audio_base_path=args.audio_base_path,
        )
        print("-" * 40)
        print(f"\nResults saved to: {output_path}")

        # Print summary
        if not args.no_summary:
            print_postprocess_summary(summary)

        return 0
    except Exception as e:
        logger.error(f"Post-processing failed: {e}")
        return 1


def run_visualize(args: argparse.Namespace) -> int:
    """Run the visualize command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    logger = logging.getLogger(__name__)

    # Determine session file
    session_file = args.session_file

    if session_file:
        # Validate provided session file
        if not session_file.exists():
            # Try resolving relative to DEFAULT_OUTPUT_DIR
            resolved = DEFAULT_OUTPUT_DIR / session_file.name
            if resolved.exists():
                session_file = resolved
            else:
                logger.error(f"Session file does not exist: {session_file}")
                return 1

        if not session_file.is_file():
            logger.error(f"Path is not a file: {session_file}")
            return 1
    else:
        # Get latest session
        session_file = get_latest_session()
        if not session_file:
            logger.error(
                f"No session files found in {DEFAULT_OUTPUT_DIR}. "
                "Run 'technotaggr analyze' first to generate results."
            )
            return 1
        print(f"Using latest session: {session_file.name}")

    try:
        run_dashboard(
            session_file=session_file,
            host=args.host,
            port=args.port,
            debug=args.debug,
        )
        return 0
    except Exception as e:
        logger.error(f"Dashboard failed: {e}")
        return 1


def run_cli(args: argparse.Namespace) -> int:
    """Run the CLI with parsed arguments.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    # Setup logging
    verbose = getattr(args, "verbose", False)
    setup_logging(verbose)

    # Route to appropriate command
    if args.command == "analyze":
        return run_analyze(args)
    elif args.command == "postprocess":
        return run_postprocess(args)
    elif args.command == "visualize":
        return run_visualize(args)
    else:
        # No command specified - show help
        print("Usage: technotaggr <command> [options]")
        print("\nCommands:")
        print("  analyze      Analyze audio files and generate predictions")
        print("  postprocess  Add 16-bar phrase predictions to existing results")
        print("  visualize    Launch interactive visualization dashboard")
        print("\nRun 'technotaggr <command> --help' for more information.")
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
