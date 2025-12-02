
# Project Summary:
You are helping me develop a python package (TechnoTaggr) that analyzes audio files using the essentia tensoflow models provided and adds metadata tags to the audio files. This is a simple, modern and modular codebase that can be extended to add gui/webui interfaces later. I am using `uv` to manage the virtual environment and install the dependencies. Do not modify the `pyproject.toml` file or the `uv.lock` file. 

## Tagging format
The audio files should be tagged using the ID3v2 comments tag `COMM` with the following information:
  
1. Pick the class with the highet likelyhood from each classifier
2. For every song, return a list of these classes.

name     comments                              
funken  happy, relaxed, bass, chords, Rev40, house