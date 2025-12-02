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
and for each audio file, the following structure is logged into `results` after the sesison information in the same json file:

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
after running `postprocess` as a CLI command, The JSON file is modified to include `bar_predictions` after the `segment_predictions` along with the `aggregated_bar_predictions` for every `model` in every audio file as follows:

```json
        //..end of "aggregated_predictions"
        "bar_predictions": [
                    [
                      0.20208349517163107,
                      0.09563070404178955,
                      0.14462723977425518,
                      0.5524411569623386,
                      0.005217404543038677
                    ],
                    ...,
        ],
        "aggregated_bar_predictions": {
                    "bass": 0.312211227110546,
                    "chords": 0.10097990340676487,
                    "fx": 0.1541110559763825,
                    "melody": 0.4162067808676512,
                    "percussion": 0.016491033385853584
                  }
      ... //more model results
    ... //more audio file results
```

# Role:
Your role is to understand the code in `src` and the logging structure to implement the visualization logic below. I have installed plotly and dash, so use that library for visualizaiton purposes to create a `Dash` app. I have added relevant documentation for `Dash`in `/Users/mishkin/Desktop/gitclones/technotaggr/prompts/docs/Dash` as reference for how to construct the layout of the app. I should be able to view the dashboard locally by running the CLI command.

Create a CLI command that can process the JSON data from `DEFAULT_OUTPUT_DIR` with a `--session-file` paramater or visualize the JSON data from the last session run.

- Make a plot for every model and show:
    - generate a `probability` vs`bar_predictions` line plot grouped by every class. 
    - generate a `probability` vs`segment_predictions` line plot grouped by every class.
    - generate a plot that shows the aggregate result across all classes for `bar_predictions`
    - generate a plot that shows the aggregate result across all classes for `segment_predictions`

