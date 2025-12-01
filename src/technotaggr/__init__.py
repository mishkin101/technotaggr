"""TechnoTaggr - Audio analysis using Essentia TensorFlow models.

This package provides tools for analyzing audio files using pre-trained
machine learning models for music classification and tagging.

Usage:
    CLI:
        technotaggr /path/to/music --output-dir ./results

    Python API:
        from technotaggr import InferencePipeline, discover_classifiers
        
        classifiers = discover_classifiers()
        pipeline = InferencePipeline(classifiers)
        result = pipeline.analyze_audio(Path("song.mp3"))
"""

from .audio import discover_audio_files, load_audio
from .cli import main
from .config import DEFAULT_MODELS_DIR, DEFAULT_OUTPUT_DIR, SUPPORTED_FORMATS
from .inference import (
    AudioAnalysisResult,
    Classifier,
    EmbeddingExtractor,
    InferencePipeline,
    PredictionResult,
)
from .model_loader import (
    ClassifierConfig,
    EmbeddingModelConfig,
    discover_classifiers,
    load_classifier_config,
)
from .result_logger import ResultLogger, SessionResults

__version__ = "0.1.0"

__all__ = [
    # Config
    "SUPPORTED_FORMATS",
    "DEFAULT_MODELS_DIR",
    "DEFAULT_OUTPUT_DIR",
    # Audio
    "load_audio",
    "discover_audio_files",
    # Model Loading
    "ClassifierConfig",
    "EmbeddingModelConfig",
    "load_classifier_config",
    "discover_classifiers",
    # Inference
    "EmbeddingExtractor",
    "Classifier",
    "InferencePipeline",
    "PredictionResult",
    "AudioAnalysisResult",
    # Result Logging
    "ResultLogger",
    "SessionResults",
    # CLI
    "main",
]
