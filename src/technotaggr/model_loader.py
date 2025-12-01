"""Model configuration loading and discovery for TechnoTaggr."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .config import CLASSIFICATION_HEADS_DIR, FEATURE_EXTRACTORS_DIR

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingModelConfig:
    """Configuration for a feature extractor (embedding) model."""

    name: str
    algorithm: str
    model_path: Path
    sample_rate: int
    output_node: str  # Node name for embeddings output


@dataclass
class ClassifierConfig:
    """Configuration for a classification head model."""

    name: str
    version: str
    description: str
    algorithm: str
    model_path: Path
    sample_rate: int
    classes: list[str]
    input_node: str  # Node name for input
    output_node: str  # Node name for predictions output
    embedding_model: EmbeddingModelConfig
    metadata: dict[str, Any] = field(default_factory=dict)


def _find_output_node(schema: dict[str, Any], purpose: str) -> str | None:
    """Find the output node name with the specified purpose."""
    outputs = schema.get("outputs", [])
    for output in outputs:
        if output.get("output_purpose") == purpose:
            return output.get("name")
    return None


def _find_input_node(schema: dict[str, Any]) -> str | None:
    """Find the first input node name from the schema."""
    inputs = schema.get("inputs", [])
    if inputs:
        return inputs[0].get("name")
    return None


def _load_embedding_model_config(
    model_name: str,
    algorithm: str,
    feature_extractors_dir: Path = FEATURE_EXTRACTORS_DIR,
) -> EmbeddingModelConfig | None:
    """Load configuration for a feature extractor model."""
    # Determine the architecture from algorithm name
    if "MusiCNN" in algorithm:
        arch_dir = feature_extractors_dir / "musicnn"
    elif "EffnetDiscogs" in algorithm or "Effnet" in algorithm:
        arch_dir = feature_extractors_dir / "discogs-effnet"
    else:
        logger.warning(f"Unknown embedding algorithm: {algorithm}")
        return None

    # Find the JSON config file (in the architecture directory)
    json_path = arch_dir / f"{model_name}.json"

    # Also check in a subdirectory with the model name (alternate structure)
    if not json_path.exists():
        json_path = arch_dir / model_name / f"{model_name}.json"

    if not json_path.exists():
        logger.warning(f"Embedding model JSON not found in {arch_dir}")
        return None

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"Failed to load embedding model config {json_path}: {e}")
        return None

    # Extract configuration
    inference = config.get("inference", {})
    sample_rate = inference.get("sample_rate", 16000)
    model_algorithm = inference.get("algorithm", algorithm)

    # Find the embeddings output node
    schema = config.get("schema", {})
    output_node = _find_output_node(schema, "embeddings")
    if not output_node:
        logger.warning(f"No embeddings output node found in {json_path}")
        return None

    # Find the .pb model file - check multiple possible locations:
    # 1. Same directory as JSON
    # 2. Subdirectory with model name
    pb_path = json_path.with_suffix(".pb")
    if not pb_path.exists():
        pb_path = arch_dir / model_name / f"{model_name}.pb"
    if not pb_path.exists():
        pb_path = arch_dir / f"{model_name}.pb"
    if not pb_path.exists():
        logger.warning(f"Embedding model file not found for {model_name}")
        return None

    return EmbeddingModelConfig(
        name=model_name,
        algorithm=model_algorithm,
        model_path=pb_path,
        sample_rate=sample_rate,
        output_node=output_node,
    )


def load_classifier_config(
    json_path: Path,
    feature_extractors_dir: Path = FEATURE_EXTRACTORS_DIR,
) -> ClassifierConfig | None:
    """Load a classifier configuration from its JSON file.

    Args:
        json_path: Path to the classifier's JSON configuration file.
        feature_extractors_dir: Directory containing feature extractor models.

    Returns:
        ClassifierConfig if successful, None otherwise.
    """
    if not json_path.exists():
        logger.warning(f"Classifier JSON not found: {json_path}")
        return None

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"Failed to load classifier config {json_path}: {e}")
        return None

    # Extract basic metadata
    name = config.get("name", json_path.stem)
    version = config.get("version", "unknown")
    description = config.get("description", "")
    classes = config.get("classes", [])

    # Extract inference configuration
    inference = config.get("inference", {})
    algorithm = inference.get("algorithm", "TensorflowPredict2D")
    sample_rate = inference.get("sample_rate", 16000)

    # Find the input and output nodes from schema
    schema = config.get("schema", {})
    input_node = _find_input_node(schema)
    if not input_node:
        logger.warning(f"No input node found in {json_path}")
        return None

    output_node = _find_output_node(schema, "predictions")
    if not output_node:
        logger.warning(f"No predictions output node found in {json_path}")
        return None

    # Load embedding model configuration
    embedding_info = inference.get("embedding_model", {})
    embedding_algorithm = embedding_info.get("algorithm")
    embedding_model_name = embedding_info.get("model_name")

    if not embedding_algorithm or not embedding_model_name:
        logger.warning(f"Missing embedding model info in {json_path}")
        return None

    embedding_config = _load_embedding_model_config(
        embedding_model_name,
        embedding_algorithm,
        feature_extractors_dir,
    )
    if not embedding_config:
        logger.warning(f"Failed to load embedding model for {json_path}")
        return None

    # Find the .pb model file (same directory as JSON, same base name)
    pb_path = json_path.with_suffix(".pb")
    if not pb_path.exists():
        logger.warning(f"Classifier model file not found: {pb_path}")
        return None

    return ClassifierConfig(
        name=name,
        version=version,
        description=description,
        algorithm=algorithm,
        model_path=pb_path,
        sample_rate=sample_rate,
        classes=classes,
        input_node=input_node,
        output_node=output_node,
        embedding_model=embedding_config,
        metadata={
            "author": config.get("author"),
            "email": config.get("email"),
            "release_date": config.get("release_date"),
            "framework": config.get("framework"),
            "framework_version": config.get("framework_version"),
            "dataset": config.get("dataset"),
        },
    )


def discover_classifiers(
    classification_heads_dir: Path = CLASSIFICATION_HEADS_DIR,
    feature_extractors_dir: Path = FEATURE_EXTRACTORS_DIR,
) -> list[ClassifierConfig]:
    """Discover all available classifier models.

    Args:
        classification_heads_dir: Directory containing classification head subdirectories.
        feature_extractors_dir: Directory containing feature extractor models.

    Returns:
        List of successfully loaded ClassifierConfig objects.
    """
    classifiers: list[ClassifierConfig] = []

    if not classification_heads_dir.exists():
        logger.error(f"Classification heads directory not found: {classification_heads_dir}")
        return classifiers

    # Iterate through each classifier subdirectory
    for classifier_dir in sorted(classification_heads_dir.iterdir()):
        if not classifier_dir.is_dir():
            continue

        # Find JSON files in the classifier directory
        json_files = list(classifier_dir.glob("*.json"))
        if not json_files:
            logger.debug(f"No JSON config found in {classifier_dir.name}, skipping")
            continue

        for json_path in json_files:
            config = load_classifier_config(json_path, feature_extractors_dir)
            if config:
                logger.info(f"Loaded classifier: {config.name} (v{config.version})")
                classifiers.append(config)
            else:
                logger.warning(f"Failed to load classifier from {json_path}")

    logger.info(f"Discovered {len(classifiers)} classifier(s)")
    return classifiers

