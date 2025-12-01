"""Inference pipeline for TechnoTaggr."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import essentia
from essentia.standard import (
    TensorflowPredict2D,
    TensorflowPredictEffnetDiscogs,
    TensorflowPredictMusiCNN,
)

from .audio import get_audio_duration, load_audio

# Suppress essentia warning messages
essentia.EssentiaLogger().warningActive = False
from .model_loader import ClassifierConfig, EmbeddingModelConfig

logger = logging.getLogger(__name__)


# Mapping of algorithm names to Essentia classes
ALGORITHM_MAP = {
    "TensorflowPredictMusiCNN": TensorflowPredictMusiCNN,
    "TensorflowPredictEffnetDiscogs": TensorflowPredictEffnetDiscogs,
    "TensorflowPredict2D": TensorflowPredict2D,
}


@dataclass
class PredictionResult:
    """Result from a single classifier on a single audio file."""

    classifier_name: str
    classifier_version: str
    classifier_path: str
    embedding_model_name: str
    embedding_model_path: str
    classes: list[str]
    segment_predictions: list[list[float]]
    aggregated_predictions: dict[str, float]
    num_segments: int


@dataclass
class AudioAnalysisResult:
    """Complete analysis result for a single audio file."""

    audio_path: str
    audio_duration_seconds: float
    sample_rate: int
    predictions: list[PredictionResult] = field(default_factory=list)


class EmbeddingExtractor:
    """Wrapper for feature extractor models."""

    def __init__(self, config: EmbeddingModelConfig):
        """Initialize the embedding extractor.

        Args:
            config: Configuration for the embedding model.
        """
        self.config = config
        self._model: Any = None

    def _load_model(self) -> None:
        """Lazily load the model."""
        if self._model is not None:
            return

        algorithm_cls = ALGORITHM_MAP.get(self.config.algorithm)
        if algorithm_cls is None:
            raise ValueError(f"Unknown algorithm: {self.config.algorithm}")

        logger.info(f"Loading embedding model: {self.config.name}")
        self._model = algorithm_cls(
            graphFilename=self.config.model_path.as_posix(),
            output=self.config.output_node,
        )

    def extract(self, audio: np.ndarray) -> np.ndarray:
        """Extract embeddings from audio.

        Args:
            audio: Audio signal as a 1D numpy array.

        Returns:
            Embeddings as a 2D numpy array (segments x embedding_dim).
        """
        self._load_model()
        embeddings = self._model(audio)
        logger.debug(f"Extracted embeddings: shape={embeddings.shape}")
        return embeddings


class Classifier:
    """Wrapper for classification head models."""

    def __init__(self, config: ClassifierConfig):
        """Initialize the classifier.

        Args:
            config: Configuration for the classifier model.
        """
        self.config = config
        self._model: Any = None

    def _load_model(self) -> None:
        """Lazily load the model."""
        if self._model is not None:
            return

        algorithm_cls = ALGORITHM_MAP.get(self.config.algorithm)
        if algorithm_cls is None:
            raise ValueError(f"Unknown algorithm: {self.config.algorithm}")

        logger.info(f"Loading classifier: {self.config.name}")
        self._model = algorithm_cls(
            graphFilename=self.config.model_path.as_posix(),
            input=self.config.input_node,
            output=self.config.output_node,
        )

    def predict(self, embeddings: np.ndarray) -> np.ndarray:
        """Run classification on embeddings.

        Args:
            embeddings: Embeddings as a 2D numpy array.

        Returns:
            Predictions as a 2D numpy array (segments x num_classes).
        """
        self._load_model()
        predictions = self._model(embeddings)
        logger.debug(f"Predictions: shape={predictions.shape}")
        return predictions


class InferencePipeline:
    """Main inference pipeline for batch processing."""

    def __init__(self, classifiers: list[ClassifierConfig]):
        """Initialize the inference pipeline.

        Args:
            classifiers: List of classifier configurations to use.
        """
        self.classifier_configs = classifiers

        # Cache for embedding extractors (keyed by model name)
        self._embedding_extractors: dict[str, EmbeddingExtractor] = {}

        # Cache for classifiers (keyed by model path)
        self._classifiers: dict[str, Classifier] = {}

        # Cache for embeddings per audio file and embedding model
        self._embeddings_cache: dict[tuple[str, str], np.ndarray] = {}

    def _get_embedding_extractor(
        self, config: EmbeddingModelConfig
    ) -> EmbeddingExtractor:
        """Get or create an embedding extractor."""
        if config.name not in self._embedding_extractors:
            self._embedding_extractors[config.name] = EmbeddingExtractor(config)
        return self._embedding_extractors[config.name]

    def _get_classifier(self, config: ClassifierConfig) -> Classifier:
        """Get or create a classifier."""
        key = str(config.model_path)
        if key not in self._classifiers:
            self._classifiers[key] = Classifier(config)
        return self._classifiers[key]

    def _get_embeddings(
        self,
        audio: np.ndarray,
        audio_path: Path,
        embedding_config: EmbeddingModelConfig,
    ) -> np.ndarray:
        """Get embeddings for audio, using cache if available."""
        cache_key = (str(audio_path), embedding_config.name)

        if cache_key not in self._embeddings_cache:
            extractor = self._get_embedding_extractor(embedding_config)
            self._embeddings_cache[cache_key] = extractor.extract(audio)

        return self._embeddings_cache[cache_key]

    def clear_cache(self) -> None:
        """Clear the embeddings cache."""
        self._embeddings_cache.clear()
        logger.debug("Cleared embeddings cache")

    def analyze_audio(self, audio_path: Path) -> AudioAnalysisResult:
        """Analyze a single audio file with all classifiers.

        Args:
            audio_path: Path to the audio file.

        Returns:
            AudioAnalysisResult containing predictions from all classifiers.
        """
        logger.info(f"Analyzing: {audio_path.name}")

        # We need to track which sample rate was used for loading
        # Use the first classifier's embedding model sample rate
        if not self.classifier_configs:
            raise ValueError("No classifiers configured")

        first_config = self.classifier_configs[0]
        sample_rate = first_config.embedding_model.sample_rate

        # Load audio once (assuming all models use the same sample rate)
        audio = load_audio(audio_path, sample_rate)
        duration = get_audio_duration(audio, sample_rate)

        result = AudioAnalysisResult(
            audio_path=str(audio_path),
            audio_duration_seconds=duration,
            sample_rate=sample_rate,
        )

        # Run each classifier
        for classifier_config in self.classifier_configs:
            try:
                prediction = self._run_classifier(
                    audio, audio_path, classifier_config
                )
                result.predictions.append(prediction)
            except Exception as e:
                logger.error(
                    f"Error running classifier {classifier_config.name} "
                    f"on {audio_path.name}: {e}"
                )

        # Clear embeddings cache after processing each file to save memory
        self.clear_cache()

        return result

    def _run_classifier(
        self,
        audio: np.ndarray,
        audio_path: Path,
        config: ClassifierConfig,
    ) -> PredictionResult:
        """Run a single classifier on audio.

        Args:
            audio: Audio signal as a numpy array.
            audio_path: Path to the audio file (for caching).
            config: Classifier configuration.

        Returns:
            PredictionResult with class probabilities.
        """
        # Get embeddings (cached)
        embeddings = self._get_embeddings(
            audio, audio_path, config.embedding_model
        )

        # Run classifier
        classifier = self._get_classifier(config)
        predictions = classifier.predict(embeddings)

        # Convert to list for JSON serialization
        segment_predictions = predictions.tolist()

        # Aggregate predictions (mean across segments)
        mean_predictions = np.mean(predictions, axis=0)
        aggregated = {
            class_name: float(prob)
            for class_name, prob in zip(config.classes, mean_predictions)
        }

        return PredictionResult(
            classifier_name=config.name,
            classifier_version=config.version,
            classifier_path=str(config.model_path),
            embedding_model_name=config.embedding_model.name,
            embedding_model_path=str(config.embedding_model.model_path),
            classes=config.classes,
            segment_predictions=segment_predictions,
            aggregated_predictions=aggregated,
            num_segments=len(segment_predictions),
        )

    def analyze_batch(
        self,
        audio_paths: list[Path],
        on_progress: callable = None,
    ) -> list[AudioAnalysisResult]:
        """Analyze multiple audio files.

        Args:
            audio_paths: List of paths to audio files.
            on_progress: Optional callback(current, total, path) for progress.

        Returns:
            List of AudioAnalysisResult objects.
        """
        results: list[AudioAnalysisResult] = []
        total = len(audio_paths)

        for i, path in enumerate(audio_paths):
            if on_progress:
                on_progress(i + 1, total, path)

            try:
                result = self.analyze_audio(path)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to analyze {path}: {e}")

        return results

