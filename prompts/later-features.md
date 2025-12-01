# later 


- Arguments to choose tags to process: {mood, sound loop, instrument, tonality, reverb, vocals, genre} or to include all of them.
- The user should be able to make a copy of their files or overwrite the original files. 
- Convert flac to aiff

# Post-processing Initial Logic:
I need to store the duration of audio segements predictions are computed. This information is obtained from the embedding model(`technotaggr/src/technotaggr/models/feature-extractors`) associated with each classifier model(`technotaggr/src/technotaggr/models/classification-heads`).

In the embedding model JSON fles, the schema contains an `inputs` field with a `shape` field for both:

- discogs-effnet-bs64-1 model
    - (`technotaggr/src/technotaggr/models/feature-extractors/discogs-effnet/discogs-effnet-bs64-1/discogs-effnet-bs64-1.json`)
    - shape: [batch size, frame size, mel spectrogram features]

- musicnn model
    - (`technotaggr/src/technotaggr/models/feature-extractors/musicnn/msd-musicnn-1/msd-musicnn-1.json`)
    - shape: [frame size, spectrogram features]

A frame size of 64 corresponds to a 1 second interval of audio.


## General rules:
- Use type hints for all function parameters and return values
- Follow PEP 8 style guidelines and prefer f-strings for formatting
- Handle errors with specific exception types, avoid bare except clauses
- Write pytest tests for all business logic with descriptive test names
- Use Pydantic for data validation and structured models
- Include docstrings for public functions using Google style format
- Prefer pathlib over os.path and use context managers for resources

### Inputs:

When the user uploads audiofiles, the package should ensure only the supported file types are uploaded and warn the user if they are not. The user should be able to make a copy of their files or overwrite the original files. If they do not want the overwritten changes, then they should be able to specify a different output directory with a copy of the original files. Give the user the option to convert the files that are supported but not process the incorrect types. 

- Make this a Python Package that is uploadable to PyPI using uv, following the licensing and packaging guidelines accoring to the CC BY-NC-ND 4.0 license. Make sure to cite the use of Essentia.
- Try to intall Essentia PyPi package from (https://pypi.org/project/essentia-tensorflow/) with support for Linux and MacOS. 
- Find any necessary dependencies for the Essentia Tensoflow models and Mutagen library and install them.


# model naming prompt

Using my file tree output below, develop a summary of the model naming conventions, the mappings to the file names and fix my incorrect mapping.

File tree:
```
technotaggr
├── __init__.py
├── audio.py
├── cli.py
├── inference.py
├── model_registry.py
├── models
│   ├── classification-heads
│   │   ├── fs_loop_ds
│   │   │   ├── fs_loop_ds-msd-musicnn-1.json
│   │   │   └── fs_loop_ds-msd-musicnn-1.pb
│   │   ├── mood_aggressive
│   │   │   ├── mood_aggressive-msd-musicnn-1.json
│   │   │   └── mood_aggressive-msd-musicnn-1.pb
│   │   ├── mood_happy
│   │   │   ├── mood_happy-msd-musicnn-1.json
│   │   │   └── mood_happy-msd-musicnn-1.pb
│   │   ├── mood_relaxed
│   │   │   ├── mood_relaxed-msd-musicnn-1.json
│   │   │   └── mood_relaxed-msd-musicnn-1.pb
│   │   ├── mood_sad
│   │   │   ├── mood_sad-msd-musicnn-1.json
│   │   │   └── mood_sad-msd-musicnn-1.pb
│   │   ├── nsynth_instrument
│   │   │   ├── nsynth_instrument-discogs-effnet-1.json
│   │   │   └── nsynth_instrument-discogs-effnet-1.pb
│   │   ├── nsynth_reverb
│   │   │   ├── nsynth_reverb-discogs-effnet-1.json
│   │   │   └── nsynth_reverb-discogs-effnet-1.pb
│   │   └── tonal_atonal
│   │       ├── tonal_atonal-msd-musicnn-1.json
│   │       └── tonal_atonal-msd-musicnn-1.pb
│   ├── feature-extractors
│   │   ├── discogs-effnet
│   │   │   └── discogs-effnet-bs64-1
│   │   │       ├── discogs-effnet-bs64-1.json
│   │   │       └── discogs-effnet-bs64-1.pb
│   │   └── musicnn
│   │       └── msd-musicnn-1
│   │           ├── msd-musicnn-1.json
│   │           └── msd-musicnn-1.pb
└── post_processing.py
```

My potentially incorrect mappings/naming conventions:
```
- classifiers: `<target_task>-<architecture>-<source_task>-<version>.pb`
- classification heads: `<target_task>-<architecture>-<source_task>-<version>.pb`
- MusiCNN: `<task>-<architecture>-<version>.pb`
- OpenL3: `<architecture>-<params>-<version>.pb`
- Spleeter: `<architecture>-<params>-<version>.pb`
- TempoCNN: `<architecture>-<params>-<version>.pb`
- VGG: `<task>-<architecture>-<version>.pb`
- VGGish: `<task>-<architecture>-<version>.pb`
- YAMNet: `<task>-<architecture>-<version>.pb`
- DiscogsEffnet: `<task>-<architecture>-<batch_size>-<version>.pb`

Where:
- `<architecture>`: the architecture of the model (refers only to the source model on the transfer learning classifiers).
- `<task>` and `<source-task>`: the dataset in which the model, or the source model was trained.
- `<target-task>`: the dataset in which the target model was trained (only for the transfer learning classifiers).
- `<params>`: parameters specific to a particular family of models.
- `<version>`: represents the incremental version of the model. We do not guaranty full compatibility between different versions.
- `<batch_size>`: batch size. Applicable for models not supporting dynamic batch sizes.
```

Based the file names, fix the mappings and create a minimal summary to be used in an LLM prompt.

## output:
Model file naming conventions:
- Classification heads: <target_task>-<source_dataset>-<architecture>-<version>
- Feature extractors (MusiCNN): <dataset>-<architecture>-<version>
- Feature extractors (DiscogsEffnet): <dataset>-<architecture>-<batch_size>-<version>

Terms:
- target_task: classification objective (e.g., mood_happy, fs_loop_ds)
- source_dataset: training dataset of feature extractor (e.g., msd, discogs)
- architecture: model architecture (e.g., musicnn, effnet)
- batch_size: batch size parameter (e.g., bs64)
- version: incremental model version number

# Post-processing Duration Script Prompt

I need to create a script that will calculate the duration of audio segements from the `output_purpose: predictions` nodes specified in the JSON files (For example, @technotaggr/src/technotaggr/models/classification-heads/mood_aggressive/mood_aggressive-msd-musicnn-1.json ) for each model in@classification-heads. Using the below information as a guide, Search the essentia documentation for the `patch_size` variable used in the `TensorflowInputMusiCNN' for each embedding model:  @technotaggr/src/technotaggr/models/feature-extractors/discogs-effnet/discogs-effnet-bs64-1/discogs-effnet-bs64-1.json , @technotaggr/src/technotaggr/models/feature-extractors/musicnn/msd-musicnn-1/msd-musicnn-1.json.

< how to bridgethe below example and what I want the function to do?>

### Input Embedding Shape Logic

The @notebooks/tutorial_tensorflow_real-time_simultaneous_classifiers.ipynb notebook specifies paramaters that control the duration of audio that `TensorflowPredictMusiCNN` uses internally with the `TensorflowInputMusiCNN' algorithm.  A `patch_size` of 64 is 1 second.  All embedding model in Essentia uses the `TensorflowInputMusiCNN' internally to calculate the input shape for the mel-spectrogram used as an input for the embedding model function.

For example, `model/Placeholder` in the `inputs` schema from @technotaggr/src/technotaggr/models/feature-extractors/musicnn/msd-musicnn-1/msd-musicnn-1.json  corresponds to a 3 second interval of audio using a (time, features) shape of [187, 96].


## Tagging format
The audio files should be tagged using the ID3v2 comments tag `COMM` with the following information:
    - mood tags from the binary classifiers should be aggregatd into one field: "moods: happy, relaxed, etc."
    - `fs_loop` should use the field "sound_loop" and contain the two highest classes: "sound_loop: bass, chords"
    - `nsynth` instrument should use the field instrument and contain the two highest classes: "instrument: guitar, bass"
    - `tonal_atonal` should use the field "tonality": "tonality: atonal"
    - `nsynth_reverb` should use the field "reverb": "reverb: wet"
    - vocals:
    - MTG-Jamendo should use the field `genre` and contain the two highest classes: "mtg_jamendo: electronic, house""