# Role 
Your role is to help me develop a python package (TechnoTaggr) that analyzes audio files using the essentia tensoflow models provided and adds metadata tags to the audio files. Create a simple, modern and modular codebase that can be extended to add gui/webui interfaces later. I am using `uv` to manage the virtual environment and install the dependencies. Do not modify the `pyproject.toml` file or the `uv.lock` file. List necessary dependencies so that I can install them manually. Use `pathlib` for file operations.

For the initial version, the code should focus the core functionality of batch analyzing audio files using the essentia tensoflow models provided and logging the prediction outputs in a easily debuggable way. The tagging functionality, gui and webui interfaces can be added later.

# Functionality
- It should support the following file types: AIFF, MP3, WAV. 
- CLI interface that allows:
    - Batch processing of audio files using an input directory
    - output directory specification with sane defaults
    - robust logging of model execution and results detailed below
- Use the `mutagen` (https://mutagen.readthedocs.io/en/latest/user/id3.html) package to read and write the metadata to the audio files. It is already been installed to the virtual environment with `uv`.

# Provided models
The models are stored in the `./models` directory. There are two folders: classification heads (`./models/classification-heads`) and the feature extractors (`./models/feature-extractors`). Each model has an associated JSON file in the same directory that contains the model configuration and metadata. It also contains the expected sample rate and Essentia Tensorflow `algorithm` name to use to extract the features.

for example, the `./models/classification-heads/fs_loop_ds/fs_loop_ds-msd-musicnn-1.json` file contains the configuration and metadata for the `fs_loop_ds` classification head model that uses the `msd-musicnn-1` feature extractor.
```json
{
    "inference": {
        "sample_rate": 16000,
        "algorithm": "TensorflowPredict2D",
        "embedding_model": {
            "algorithm": "TensorflowPredictMusiCNN",
            "model_name": "msd-musicnn-1",
            "link": "https://essentia.upf.edu/models/feature-extractors/musicnn/msd-musicnn-1.pb"
        }
    },
}
```
## Model file naming conventions:

- Classification heads: <target_task>-<source_dataset>-<architecture>-<version>
- Feature extractors (MusiCNN): <dataset>-<architecture>-<version>
- Feature extractors (DiscogsEffnet): <dataset>-<architecture>-<batch_size>-<version>

Terms:
- target_task: classification objective (e.g., mood_happy, fs_loop_ds)
- source_dataset: training dataset of feature extractor (e.g., msd, discogs)
- architecture: model architecture (e.g., musicnn, effnet)
- batch_size: batch size parameter (e.g., bs64)
- version: incremental model version number

### Model usage:

In the below example, the embedding model is used to create embeddings of the audio file. The classifier model is used to classify the embeddings into classes: `happy` and `non_happy`.

1. The `sample_rate` of 16000 during loading is determined by the value in the JSON file of the embedding model (`technotaggr/src/technotaggr/models/feature-extractors/musicnn/msd-musicnn-1/msd-musicnn-1.json`) under `inference.sample_rate`. 
2. The algorithm from the Essentia library used to load the embeddings is specificed by the `algorithm` key under `inference` from the embedding JSON file. (`technotaggr/src/technotaggr/models/feature-extractors/musicnn/msd-musicnn-1/msd-musicnn-1.json`). The classifier model knows to use the same algorithm to load the embeddings as specified by the `algorithm` key under `embedding_model`. (defined in `technotaggr/src/technotaggr/models/classification-heads/mood_happy/mood_happy-msd-musicnn-1.json`)
3. The embeddings are obtained after loading by specifying the output parameter to be the `name` of the embedding layer that has `"output_purpose": "embeddings"`. 
4. The classifier model (defined in `technotaggr/src/technotaggr/models/classification-heads/mood_happy/mood_happy-msd-musicnn-1.json`) is used to classify the embeddings into classes: `happy` and `non_happy`; the `output` parameter is specified to be the `name` of the softmax layer that has `"output_purpose": "predictions"`. 

```python
from essentia.standard import MonoLoader, TensorflowPredictMusiCNN, TensorflowPredict2D
# name = "1-01 Funken.aiff"
audio_path = Path(data / names["name_0"]).as_posix()
embedded_model_path = Path("/Users/mishkin/Desktop/Music_classifier/technotaggr/src/technotaggr/models/feature-extractors/musicnn/msd-musicnn-1/msd-musicnn-1.pb").as_posix()
classifier_model_path = Path("/Users/mishkin/Desktop/Music_classifier/technotaggr/src/technotaggr/models/classification-heads/mood_happy/mood_happy-msd-musicnn-1.pb").as_posix()
audio = MonoLoader(filename= audio_path, sampleRate=16000, resampleQuality=4)()
embedding_model = TensorflowPredictMusiCNN(graphFilename=embedded_model_path, output="model/dense/BiasAdd")
embeddings = embedding_model(audio)

model = TensorflowPredict2D(graphFilename=classifier_model_path, output="model/Softmax")
predictions = model(embeddings)

# output:
# [[3.2144077 3.123539 ]
#  [3.4414551 3.2013047]
#  [3.2752292 2.8495169]
#  ...
#  [3.326894  3.7588181]
#  [3.328467  3.7594488]
#  [3.3267756 3.7581882]]
# (2337, 2)
# [   INFO   ] TensorflowPredict: Successfully loaded graph file: `../models/msd-musicnn-1.pb`
# [   INFO   ] TensorflowPredict: Successfully loaded graph file: `../models/deam-msd-musicnn-2.pb`
```

### Model Logging:
Create a robust logger for model inference, tracking prediction outputs from all the models in ``technotaggr/src/technotaggr/models/classification-heads` using the above model usage example as a guide. Log the results in a JSON file containing: prediction output probabiltities from the `output_purpose: predictions` node name, the associated `classes` found in each classifier model's JSON file and the audio segment duration. Also track the input parameters used for the model inference, such as the audio file path, the model path, the model name, and the model version. Use a unique, timestamped filename for each JSON file for easy debugging.