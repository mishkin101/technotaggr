"""Gradio web interface for TechnoTaggr."""

from __future__ import annotations

import io
import logging
from dataclasses import asdict
from pathlib import Path

import gradio as gr

from .audio import discover_audio_files
from .config import DEFAULT_MODELS_DIR, DEFAULT_OUTPUT_DIR
from .inference import InferencePipeline
from .model_loader import discover_classifiers
from .result_logger import ResultLogger


class LogCapture(logging.Handler):
    """Custom logging handler to capture logs to a string buffer."""

    def __init__(self):
        super().__init__()
        self.log_buffer = io.StringIO()
        self.setFormatter(
            logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

    def emit(self, record):
        """Emit a log record to the buffer."""
        try:
            msg = self.format(record)
            self.log_buffer.write(msg + "\n")
        except Exception:
            self.handleError(record)

    def get_logs(self) -> str:
        """Get all captured logs."""
        return self.log_buffer.getvalue()

    def clear(self):
        """Clear the log buffer."""
        self.log_buffer = io.StringIO()


def analyze_directory(
    directory_path: str | None,
    models_dir: str = None,
) -> tuple[dict | None, str]:
    """Analyze audio files in a directory.

    Args:
        directory_path: Path to directory containing audio files.
        models_dir: Optional custom models directory.

    Returns:
        Tuple of (results_dict, log_output).
    """
    # Set up log capture
    log_capture = LogCapture()
    log_capture.setLevel(logging.INFO)
    root_logger = logging.getLogger()
    root_logger.addHandler(log_capture)
    root_logger.setLevel(logging.INFO)

    # Also reduce verbosity of essentia logger
    logging.getLogger("essentia").setLevel(logging.WARNING)

    try:
        # Validate input directory
        if not directory_path:
            error_msg = "Please select a directory"
            log_capture.log_buffer.write(f"ERROR: {error_msg}\n")
            return None, log_capture.get_logs()

        input_dir = Path(directory_path)
        if not input_dir.exists():
            error_msg = f"Directory does not exist: {directory_path}"
            log_capture.log_buffer.write(f"ERROR: {error_msg}\n")
            return None, log_capture.get_logs()

        if not input_dir.is_dir():
            error_msg = f"Path is not a directory: {directory_path}"
            log_capture.log_buffer.write(f"ERROR: {error_msg}\n")
            return None, log_capture.get_logs()

        # Use custom models dir if provided, otherwise use default
        if models_dir:
            models_path = Path(models_dir)
        else:
            models_path = DEFAULT_MODELS_DIR

        # Discover audio files
        log_capture.log_buffer.write(
            f"Scanning for audio files in: {input_dir}\n"
        )
        audio_files = discover_audio_files(input_dir, recursive=False)

        if not audio_files:
            warning_msg = "No audio files found in directory"
            log_capture.log_buffer.write(f"WARNING: {warning_msg}\n")
            return None, log_capture.get_logs()

        log_capture.log_buffer.write(
            f"Found {len(audio_files)} audio file(s)\n\n"
        )

        # Discover classifiers
        classification_heads_dir = models_path / "classification-heads"
        feature_extractors_dir = models_path / "feature-extractors"

        log_capture.log_buffer.write("Discovering classifiers...\n")
        classifiers = discover_classifiers(
            classification_heads_dir,
            feature_extractors_dir,
        )

        if not classifiers:
            error_msg = "No classifiers found. Check models directory."
            log_capture.log_buffer.write(f"ERROR: {error_msg}\n")
            return None, log_capture.get_logs()

        log_capture.log_buffer.write(
            f"Loaded {len(classifiers)} classifier(s)\n\n"
        )

        # Create inference pipeline
        pipeline = InferencePipeline(classifiers)

        # Create result logger
        result_logger = ResultLogger(
            output_dir=DEFAULT_OUTPUT_DIR,
            input_dir=input_dir,
        )

        # Process audio files
        log_capture.log_buffer.write("Starting analysis...\n")
        log_capture.log_buffer.write("-" * 40 + "\n")

        for i, audio_path in enumerate(audio_files, 1):
            log_capture.log_buffer.write(
                f"[{i}/{len(audio_files)}] Processing: {audio_path.name}\n"
            )

            try:
                result = pipeline.analyze_audio(audio_path)
                result_logger.log_result(result)
                log_capture.log_buffer.write("  ✓ Success\n")
            except Exception as e:
                result_logger.log_failure(audio_path, str(e))
                log_capture.log_buffer.write(f"  ✗ Failed: {e}\n")

        log_capture.log_buffer.write("-" * 40 + "\n\n")

        # Save results
        output_path = result_logger.save()
        log_capture.log_buffer.write(f"Results saved to: {output_path}\n\n")

        # Get session results as dict
        session_results = result_logger.get_session_results()
        results_dict = asdict(session_results)

        # Add summary to logs
        log_capture.log_buffer.write("=" * 60 + "\n")
        log_capture.log_buffer.write("Analysis Summary\n")
        log_capture.log_buffer.write("=" * 60 + "\n")
        log_capture.log_buffer.write(
            f"Total files:      {results_dict['total_files']}\n"
        )
        log_capture.log_buffer.write(
            f"Successful:       {results_dict['successful_files']}\n"
        )
        log_capture.log_buffer.write(
            f"Failed:           {results_dict['failed_files']}\n"
        )
        log_capture.log_buffer.write(
            f"Classifiers used: {len(results_dict['classifiers_used'])}\n"
        )
        log_capture.log_buffer.write("=" * 60 + "\n")

        return results_dict, log_capture.get_logs()

    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        log_capture.log_buffer.write(f"\nERROR: {error_msg}\n")
        logging.exception("Error during analysis")
        return None, log_capture.get_logs()

    finally:
        # Remove the log handler
        root_logger.removeHandler(log_capture)


def create_interface() -> gr.Blocks:
    """Create the Gradio interface.

    Returns:
        Gradio Blocks interface.
    """
    with gr.Blocks(title="TechnoTaggr Audio Analysis") as demo:
        gr.Markdown("# 🎵 TechnoTaggr Audio Analysis")
        gr.Markdown(
            "Analyze audio files using Essentia TensorFlow models. "
            "Select a directory containing audio files and click Analyze."
        )

        with gr.Row():
            with gr.Column(scale=2):
                directory_input = gr.FileExplorer(
                    label="Select Audio Directory",
                    file_count="single",
                    value="song-data/smol",
                )
                analyze_button = gr.Button(
                    "🚀 Analyze Audio Files",
                    variant="primary",
                    size="lg",
                )

        with gr.Row():
            with gr.Column():
                logs_output = gr.Textbox(
                    label="Progress & Logs",
                    lines=15,
                    max_lines=20,
                    interactive=False,
                )

        with gr.Row():
            with gr.Column():
                json_output = gr.JSON(
                    label="Analysis Results",
                    open=True,
                    show_indices=True,
                )

        # Connect the analyze button
        analyze_button.click(
            fn=analyze_directory,
            inputs=[directory_input],
            outputs=[json_output, logs_output],
        )

        # Add examples section
        gr.Markdown("---")
        gr.Markdown(
            """
            ### 📖 About the Results
            
            The results include predictions from multiple classifiers:
            - **fs_loop_ds**: Identifies musical elements (bass, chords, fx, melody, percussion)
            - **mood classifiers**: Detects emotional characteristics (aggressive, happy, relaxed, sad)
            - **nsynth instrument**: Identifies instrument types
            - **nsynth reverb**: Detects reverb characteristics (dry/wet)
            - **tonal/atonal**: Determines tonality of the audio
            
            Each prediction includes:
            - Aggregated predictions: Average probabilities across all segments
            - Segment predictions: Detailed predictions for each audio segment
            - Top predicted class and confidence percentage
            """
        )

    return demo


def launch_app(
    share: bool = False,
    server_name: str = "127.0.0.1",
    server_port: int = 7860,
) -> None:
    """Launch the Gradio web interface.

    Args:
        share: If True, create a public sharing link.
        server_name: Server hostname to bind to.
        server_port: Server port to bind to.
    """
    demo = create_interface()
    demo.launch(
        share=share,
        server_name=server_name,
        server_port=server_port,
    )


if __name__ == "__main__":
    launch_app()

