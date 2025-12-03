This package provides tools for analyzing audio files using pre-trained
machine learning models for music classification and tagging.

Usage:
    CLI:
        technotaggr /path/to/music --output-dir ./results

    Python API:
        from technotaggr import InferencePipeline, discover_classifiers
        
        classifiers = discover_classifiers()
        pipeline = InferencePipeline(classifiers)
        result = pipeline.analyze_audio(Path("song.mp3"))

# Basic usage
python technotaggr song_data/smol

# With options:
technotaggr song_data/smol --output-dir ./results -v --recursive

# Post-process the audio files for techno 16-bar phrases:

# Visualize the latest session
technotaggr visualize

# Visualize a specific session file
technotaggr visualize --session-file results_20251202_091856.json

# Run on a different port
technotaggr visualize --port 8080

# Todo

- [ ] https://essentia.upf.edu/models.html#fsd-sinet
- [ ] Make post-processing logic for the prediction outputs.