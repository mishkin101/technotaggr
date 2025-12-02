# Project Summary:
You are helping me develop a python package (TechnoTaggr) that analyzes audio files using the essentia tensoflow models provided and adds metadata tags to the audio files. This is a simple, modern and modular codebase that can be extended to add gui/webui interfaces later. I am using `uv` to manage the virtual environment and install the dependencies. Do not modify the `pyproject.toml` file or the `uv.lock` file. 

## Logging Structure:
The session information is logged in the following structure, and exposes all models used from `technotaggr/src/technotaggr/models/classification-heads` and `technotaggr/src/technotaggr/models/classifier-heads`:

```json
"session_timestamp": "2025-12-01T00:43:58.791865",
  "input_directory": "song_data/smol",
  "output_directory": "/Users/mishkin/Desktop/gitclones/technotaggr/technotaggr_results",
  "total_files": 3,
  "successful_files": 3,
  "failed_files": 0,
  "classifiers_used": [
    "fs_loop_ds",
    "mood aggressive",
    "mood happy",
    "mood relaxed",
    "mood sad",
    "nsynth instrument",
    "nsynth reverb",
    "tonal/atonal"
  ]
```
and for each audio file, the following structure is logged into `results` after the sesison informaiton in the same json file:

```json
"results": [
    {
      "audio_file": "song_data/smol/01 Power to the Soul.aiff",
      "audio_duration_seconds": 396.0,
      "sample_rate": 16000,
      "models": [
        {
          "model_name": "fs_loop_ds",
          "model_version": "1",
          "model_path": "/Users/mishkin/Desktop/gitclones/technotaggr/src/technotaggr/models/classification-heads/fs_loop_ds/fs_loop_ds-msd-musicnn-1.pb",
          "embedding_model": "msd-musicnn-1",
          "embedding_model_path": "/Users/mishkin/Desktop/gitclones/technotaggr/src/technotaggr/models/feature-extractors/musicnn/msd-musicnn-1/msd-musicnn-1.pb",
          "classes": [
            "bass",
            "chords",
            "fx",
            "melody",
            "percussion"
          ],
          "num_segments": 265,
          "segment_predictions": [
            [
              0.1599259227514267,
              0.1552872210741043,
              0.26213452219963074,
              0.40136954188346863,
              0.021282831206917763
            ],
            ...
          ,
          ]
          "aggregated_predictions": {
            "bass": 0.1599259227514267,
            "chords": 0.1552872210741043,
            "fx": 0.26213452219963074,
            "melody": 0.40136954188346863,
            "percussion": 0.021282831206917763
          },
        },
      ], 
      ... //more model results
    },
    ... //more audio file results
  ]
```
# Role:

Your role is to understand the code in `src` and the logging structure to implement the post-processing logic below.

For post-processing, you will need to aggregate the `segment_predictions` for each `audio_file` into chunks of 16-bar musical phrase segements using the following instructions:

- We can assume that the song are in 4/4 time. 
- For every audio file, use librosa to calculate the BPM of the song.
- for steps 1-4, You should do this for every model and for every audio file.

### 'segment_predictions' duration logic:

### Input Embedding Shape Logic
A `patch_size` of 64 is 1 second.  All embedding model in Essentia uses the `TensorflowInputMusiCNN` internally to calculate the input shape for the mel-spectrogram used as an input for the embedding model function.

For the embedding models found in `technotaggr/src/technotaggr/models/feature-extractors`, the `patch_size` corresponds to the `inputs` schema for the `shape` field in one of the list indices.

- `model/Placeholder` in the `inputs` schema from `technotaggr/src/technotaggr/models/feature-extractors/musicnn/msd-musicnn-1/msd-musicnn-1.json`  corresponds to a 3 second interval of audio using a (time, features) `shape` of [187, 96] where `patch_size` = 187 (the first index of the `shape` list).

- `serving_default_melspectrogram` in the `inputs` schema from `technotaggr/src/technotaggr/models/feature-extractors/discogs-effnet/discogs-effnet-bs64-1/discogs-effnet-bs64-1.json`  corresponds to a 2 second interval of audio using a (batch size, time, features) `shape` of [64, 128, 96] where `patch_size` = 128 (the second index of the `shape` list).


1. For every song: calculate the duration (in seconds) of a 16-bar musical phrase using the BPM of the song according to the formula:

duration = 16 bars * 4 beats per bar * (60 seconds per minute / BPM)

2. Caluclate the number of `segment_predictions` needed for one 16-bar musical phrase. Create a new list of `segment_predictions` for each 16-bar musical phrase chunks for each audio file. The number of `segment_predictions` needed for a 16 bar musical phrase may not be a whole number, so find a way to approximate the chunks.

3. Compute the mean probability of `segment_predictions` in every `class` for each 16 bar phrase. 

4. Then, compute the mean probability for each `class` in the entire audio file, aggregating the mean probabilities from all 16 bar phrases. 


You should add these results to the json file produced from `results_logger.py`. In particular, append the raw post-processed predictions for 16 bar phrases into a `bar_predictions` field, following the same structure as the `segment_predictions` field for each audio file. Then, append the aggregated predictions for an entire audio file to an `aggregated_bar_predictions` field after the `aggregate_predictions` field. 



### Output logging and verification:


