# TechnoTaggr

Audio tagging toolkit built on [Essentia TensorFlow models](https://github.com/MTG/essentia?tab=AGPL-3.0-1-ov-file#readme) using the `essentia-tensorflow` package. TechnoTaggr scans folders of audio, runs prepackaged classifiers (mood, tonality, instruments, loops, Jamendo genres, etc.), and saves structured JSON that you can post-process into 16‑bar phrase summaries and explore through a Plotly Dash UI.

Here is a demo of the [Dashboard with Ploty](https://24f505ed-de77-41db-9819-40dcb8f4b7d9.plotly.app/)

## In progress Work:
- post-processing framework and data analysis beyond initial aggregation logic for 16 bar measures common in techno music.
- curating new techno dataset + finetuning models
- Adding functionality to add tags into wav, mp3, and .aiff files.

## What’s inside
- Prebundled Essentia feature extractors (MusiCNN, Discogs EffNet) and classification heads in `src/technotaggr/models`
- CLI for batch analysis (`analyze`), 16‑bar phrase aggregation (`postprocess`), and interactive visualization (`visualize`)
- JSON session logging with per-segment probabilities and aggregated scores
- Dash dashboard with dark theme, per-model plots, and session metadata panels
- Python API for embedding extraction, classification, and result logging

## Setup (uv)
```bash
uv venv
source .venv/bin/activate
uv sync

# Optional: refresh bundled Essentia models
uv run python src/technotaggr/download_models.py
```

## CLI usage
Run commands with `uv run` (or directly if the package is installed). Supported audio formats: `.mp3`, `.wav`, `.aiff`.

### Analyze audio
Scan a directory, run every discovered classifier, and write a timestamped results file to `technotaggr_results/`.
```bash
uv run technotaggr analyze song_data/smol \
  --output-dir technotaggr_results \
  --recursive \
  --verbose
```
- Discovers audio files, loads matching feature extractors/classifiers, and caches embeddings per file to avoid redundant work.
- Each classifier yields per-segment probabilities plus an aggregated mean per class.
- A session summary prints to the console and is saved as `results_YYYYMMDD_HHMMSS.json`.

### Post-process 16‑bar phrases
Estimate BPM with librosa, compute 16‑bar phrase (bar) probabilities from the segment outputs, and append them to the results JSON.
```bash
uv run technotaggr postprocess technotaggr_results/results_*.json \
  --audio-base-path song_data/smol \
  --output technotaggr_results/results_postprocessed.json
```
- Adds `bpm`, `phrase_duration_seconds`, per-phrase `bar_predictions`, and `aggregated_bar_predictions` (mean across phrases).
- Uses embedding model patch sizes (with 50% overlap) to infer segment duration; falls back to audio-length/segment-count if needed.
- Prints a per-embedding summary of segment duration, segments per phrase, and number of phrases found.

### Visualize results (Dash)
Launch the Dash dashboard to explore a session file (defaults to the latest JSON in `technotaggr_results`).
```bash
uv run technotaggr visualize \
  --session-file technotaggr_results/results_postprocessed.json \
  --port 8050
```
- Session dropdown: pick any `results_*.json`.
- Audio dropdown: pick a track within that session.
- Info panel: shows session timestamp, input/output folders, total/success/fail counts, and classifiers used.
- For each model:
  - Line plot of per-segment probabilities (always)
  - Line plot of 16‑bar phrase probabilities (when post-processed data is present)
  - Side-by-side bar charts of aggregated segment means and aggregated phrase means

## Result file shape
Results live in `technotaggr_results/` as JSON:
- Session metadata: `session_timestamp`, `input_directory`, `output_directory`, `total_files`, `successful_files`, `failed_files`, `classifiers_used`
- `results`: one entry per audio file with `audio_file`, `audio_duration_seconds`, `sample_rate`, and `models`
  - Each `model` contains `model_name`, `model_version`, paths to classifier/embedding graphs, `classes`, `num_segments`, `segment_predictions`, and `aggregated_predictions`
  - After `postprocess`, models also include `bar_predictions` and `aggregated_bar_predictions`, and the audio entry gains `bpm` and `phrase_duration_seconds`

## Python API quickstart
```python
from pathlib import Path
from technotaggr import InferencePipeline, discover_classifiers

classifiers = discover_classifiers()  # loads configs from src/technotaggr/models
pipeline = InferencePipeline(classifiers)
result = pipeline.analyze_audio(Path("song.mp3"))

for pred in result.predictions:
    top_class, score = max(pred.aggregated_predictions.items(), key=lambda x: x[1])
    print(pred.classifier_name, top_class, score)
```

## Models
- Classification heads included: loop detection, tonal/atonal, mood (aggressive/happy/relaxed/sad), NSynth instrument/reverb, Jamendo genre, and more under `models/classification-heads/`.
- Feature extractors included: MusiCNN (`msd-musicnn-1`) and Discogs EffNet (`discogs-effnet-bs64-1`).
- If you need to re-fetch them, run `uv run python src/technotaggr/download_models.py` (uses curl to pull from Essentia’s model hub).

[Back to top](#technotaggr)
