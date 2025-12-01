# Plan

# General rules:
- Use type hints for all function parameters and return values
- Follow PEP 8 style guidelines and prefer f-strings for formatting
- Handle errors with specific exception types, avoid bare except clauses
- Write pytest tests for all business logic with descriptive test names
- Use Pydantic for data validation and structured models
- Include docstrings for public functions using Google style format
- Prefer pathlib over os.path and use context managers for resources

/start simple & work up (no pep8, "Handle errors with specific exception types, avoid bare except clauses" in the first prompt)

### Purpose:
Create a Python packages named "TechnoTaggr" that allows used add metadata tags to their audio files using the provided essentia tensoflow models in the models folder. 

# Model Structure:

The models are stored in the models folder of the project. The models consist of the classification heads and the feature extractors stored in the models/classification-heads and models/feature-extractors folders respectively. 

## Model naming conventions
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


Use the JSON files to construct the Essentia Tensoflow classifier models, searching for them in the models/feature-extractors folder for the required embeddings. The JSON files also contain the expected sample rate and Essentia Tensorflow algorithm to use to extract the features. 

Refer to the @Essentia documentation for how to construct the Essentia Tensoflow models with the required parameters to run inference.

### Functionality:
- The supported file types are: FLAC, AIFF, MP3, WAV
- The user should be able to upload any number of audio files 
- There should be optional arguments for the user to choose which tags they want from the following set:
{mood, sound loop, instrument, tonality, reverb, vocals, genre} or to include all of them.
- The user should be able to make a copy of their files or overwrite the original files. 
- Option to save output to a specified directory.

/Only add the bare minimum functionality to get the framework of modules/workflow working, add other features in later prompts.

## Processing Logic:

### Inputs:

When the user uploads audiofiles, the package should ensure only the supported file types are uploaded and warn the user if they are not. The user should be able to make a copy of their files or overwrite the original files. If they do not want the overwritten changes, then they should be able to specify a different output directory with a copy of the original files. Give the user the option to convert the files that are supported but not process the incorrect types. 

### Preprocessing:
The audio files should be converted to the correct sampling rate and input specification for the Essentia Tensoflow models according to the JSON files in the models/feature-extractors folder. The BPM of each song is also required for the post-processing step, so find it in the exisiting file or use Librosa to extract it.

### Prediction:
Run the Essentia Tensoflow models on the preprocessed audio files and get the predictions. The classes for each prediction are also saved in the JSON files in the models/classification-heads folder. Since predictions are made on time segements according to the model input, the raw values for all the time segments for each model should be stored as intermediate data to use for the post-processing step in order to determine the final class for the target task.

### Post-processing:
For the post processing step, we will first aggregate the predictions from the time segments for each audio file to reflect the length of 16-bar musical phrase segements. We can assume that the song are in 4/4 time. You will need to calculate the duration (in seconds) of a 16-bar musical phrase using the BPM of the song according to the formula:

duration = 16 bars * 4 beats per bar * (60 seconds per minute / BPM)

For every model, you will tranaform the initial time segements into the duration for a 16-bar musical phrases and compute the mean probability for each 16 bar phrase. Then, compute the mean probability for the entire audio file, aggregating the mean probabilities from all 16 bar phrases. You should do this for every model and for every audio file.

The audio files must be returned with model predictions added to the comments tag in the audiofile metadata in the following format:
    - mood tags from the binar classifiers should be aggregatd into one field: "moods: happy, relaxed, etc."
    - fs_loop should use the field "sound_loop" and contain the two highest classes: "sound_loop: bass, chords"
    - Nsynth instrument should use the field instrument and contain the two highest classes: "instrument: guitar, bass"
    - tonal_atonal should use the field "tonality": "tonality: atonal"
    - nsynth_reverb should use the field "reverb": "reverb: wet"
    - vocals:
    - MTG-Jamendo should use the field "genre" and contain the two highest classes: "mtg_jamendo: electronic, house""


# Directory Structure:

I have provided the followinf direcroty stucture to reflect the above processing logic. Use your own reasoning to determine how to best organize the code, creating necessayr functions and interoperability to reflect the above processing logic.

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



### Tech Stack:
- Make this a Python Package that is uploadable to PyPI using uv, following the licensing and packaging guidelines accoring to the CC BY-NC-ND 4.0 license. Make sure to cite the use of Essentia.
- Try to intall Essentia PyPi package from (https://pypi.org/project/essentia-tensorflow/) with support for Linux and MacOS. 
-Find any necessary dependencies for the Essentia Tensoflow models and Mutagen library and install them.
- Build the CLI interface with Click.
- Use the most relevant metatadata for the comment tag for the above suppported audiofiles types, prioritzing widely used encoding schemes such as ID3v2 for MP3 files, Vorbis Comments for FLAC, COMT chunks for AIFF. 
- Use the Mutagen library to read and write the metadata to the audio files.




______
 


### Questions
- How to compile from source or PyPI to instruct to install Essentia Package?
- Do I need to include any documentation from Essenita?
- How specific does the teck stack have to be? include intended functionality about the fils, or just give an overview of the input -> preprocessing -> predicition -> post-processing process?
- Do I need multiple agents for anything? if so, for what?
- How specific do the guidleines need to be for the audio file conversion and metadata writing?
- **TODO**: ADD mtg-jamendo model