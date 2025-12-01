"""Configuration and path management for TechnoTaggr."""

from pathlib import Path

# Supported audio file formats
SUPPORTED_FORMATS: set[str] = {".aiff", ".mp3", ".wav"}

# Package root directory
PACKAGE_DIR: Path = Path(__file__).parent

# Default models directory (within the package)
DEFAULT_MODELS_DIR: Path = PACKAGE_DIR / "models"

# Classification heads directory
CLASSIFICATION_HEADS_DIR: Path = DEFAULT_MODELS_DIR / "classification-heads"

# Feature extractors directory
FEATURE_EXTRACTORS_DIR: Path = DEFAULT_MODELS_DIR / "feature-extractors"

# Default output directory for results
DEFAULT_OUTPUT_DIR: Path = Path.cwd() / "technotaggr_results"

# Audio loading settings
DEFAULT_RESAMPLE_QUALITY: int = 4

