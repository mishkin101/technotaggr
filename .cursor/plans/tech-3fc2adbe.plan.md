<!-- 3fc2adbe-cdf3-48f7-9fde-2af89d93e9d9 cbcd916a-f8db-4f77-8ec3-c230a2e19f8f -->
# TechnoTaggr Core Implementation

## Architecture Overview

Create a modular package structure under `src/technotaggr/` with clear separation of concerns:

```
src/technotaggr/
├── __init__.py          # Package exports and main entry point
├── cli.py               # CLI interface using argparse
├── config.py            # Configuration and path management
├── audio.py             # Audio loading utilities
├── models/              # Existing model files (unchanged)
├── model_loader.py      # Model configuration and loading
├── inference.py         # Inference pipeline
└── result_logger.py     # JSON result logging
```

## Implementation Plan

### 1. Configuration Module (`config.py`)

- Define `SUPPORTED_FORMATS = {'.aiff', '.mp3', '.wav'}`
- Default paths for models directory and output directory
- Use `pathlib.Path` throughout

### 2. Model Loader Module (`model_loader.py`)

- `ModelConfig` dataclass to parse JSON metadata (sample_rate, algorithm, embedding_model, classes, output nodes)
- `load_model_config(json_path: Path) -> ModelConfig` - Parse JSON and extract:
  - Embedding output node (find `output_purpose: "embeddings"`)
  - Prediction output node (find `output_purpose: "predictions"`)
- `discover_models(models_dir: Path) -> list[ModelConfig]` - Auto-discover all classification heads with valid JSON
- Skip models like `mtg_jamendo_genre` that lack JSON files

### 3. Audio Module (`audio.py`)

- `load_audio(path: Path, sample_rate: int) -> np.ndarray` - Wrapper around `essentia.standard.MonoLoader`
- `discover_audio_files(input_dir: Path) -> list[Path]` - Find all supported audio files

### 4. Inference Module (`inference.py`)

- `EmbeddingExtractor` class - Load and cache feature extractors (MusiCNN or EffNet)
- `Classifier` class - Load classification head and run predictions
- `InferencePipeline` class:
  - Manages embedding extractors and classifiers
  - Caches embeddings per audio file to avoid recomputation
  - Returns structured results with probabilities and class labels

### 5. Result Logger Module (`result_logger.py`)

- `InferenceResult` dataclass containing:
  - `audio_path`, `audio_duration_seconds`
  - `model_name`, `model_version`, `model_path`
  - `embedding_model_name`, `embedding_model_path`
  - `classes`, `predictions` (per-segment probabilities)
  - `aggregated_predictions` (mean across segments)
  - `timestamp`
- `ResultLogger` class:
  - `log_result(result: InferenceResult)` - Append to session results
  - `save(output_dir: Path)` - Write timestamped JSON file (e.g., `results_20251201_143022.json`)

### 6. CLI Module (`cli.py`)

- Arguments:
  - `input_dir` (required) - Directory containing audio files
  - `--output-dir` (optional, default: `./technotaggr_results`)
  - `--models-dir` (optional, default: package models directory)
  - `--verbose` / `-v` - Enable verbose console logging
- Process flow:

  1. Discover audio files in input directory
  2. Load all model configurations
  3. For each audio file, run all classifiers
  4. Log results to JSON file

### 7. Main Entry Point (`__init__.py`)

- Update `main()` to invoke CLI
- Export key classes for programmatic usage

## Key Code Patterns

**Model inference flow** (based on provided example):

```python
from essentia.standard import MonoLoader, TensorflowPredictMusiCNN, TensorflowPredict2D

# Load audio at model's required sample rate
audio = MonoLoader(filename=audio_path, sampleRate=16000, resampleQuality=4)()

# Extract embeddings using feature extractor
embedding_model = TensorflowPredictMusiCNN(
    graphFilename=embedding_model_path,
    output="model/dense/BiasAdd"  # from embedding JSON: output_purpose="embeddings"
)
embeddings = embedding_model(audio)

# Run classifier
classifier = TensorflowPredict2D(
    graphFilename=classifier_path,
    output="model/Softmax"  # from classifier JSON: output_purpose="predictions"
)
predictions = classifier(embeddings)
```

**Dynamic algorithm selection** based on JSON `inference.algorithm`:

- `TensorflowPredictMusiCNN` for MusiCNN embeddings
- `TensorflowPredictEffnetDiscogs` for EffNet embeddings
- `TensorflowPredict2D` for all classification heads

## JSON Output Format

```json
{
  "session_timestamp": "2025-12-01T14:30:22",
  "results": [
    {
      "audio_file": "/path/to/audio.aiff",
      "audio_duration_seconds": 180.5,
      "models": [
        {
          "model_name": "mood_happy",
          "model_version": "2",
          "model_path": "/path/to/mood_happy-msd-musicnn-1.pb",
          "embedding_model": "msd-musicnn-1",
          "classes": ["happy", "non_happy"],
          "segment_predictions": [[0.7, 0.3], [0.65, 0.35], ...],
          "aggregated_predictions": {"happy": 0.68, "non_happy": 0.32}
        }
      ]
    }
  ]
}
```

## Dependencies

All required packages are already installed via `uv`:

- `essentia-tensorflow` - Audio analysis and ML inference
- `mutagen` - Audio metadata (for future tagging feature)

No additional dependencies required.

### To-dos

- [x] Create config.py with supported formats and path defaults
- [x] Create model_loader.py with JSON parsing and model discovery
- [x] Create audio.py with MonoLoader wrapper and file discovery
- [x] Create inference.py with embedding extractors and classifiers
- [x] Create result_logger.py with timestamped JSON output
- [x] Create cli.py with argparse interface
- [x] Update __init__.py to wire up CLI entry point