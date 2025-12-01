<!-- 8d02ed85-4655-483d-9e88-dde2f0e42de0 56d6799a-0e34-4d92-8585-dd0843b97439 -->
# Gradio Interface for TechnoTaggr

## Implementation Approach

Create a new file [`src/technotaggr/app.py`](src/technotaggr/app.py) that will house the Gradio interface with the following components:

### 1. Interface Components

**FileExplorer Component**

- Set up to browse directories on the local filesystem
- Default value: `song-data/smol`
- Configure `file_count="single"` to select one directory at a time
- Set `root` parameter to workspace root for sandboxed browsing

**JSON Component**

- Display the formatted results from the analysis
- Use `open=True` for expanded view by default
- Configure with appropriate height for readability

**Textbox/Log Component**

- Capture and display real-time logs and progress
- Use `lines=10-15` for scrollable log view
- Show status updates during processing

**Button Component**

- Trigger the analysis process
- Clear, actionable label like "Analyze Audio Files"

### 2. Core Functionality

**Analysis Function**
The main processing function will:

1. Accept the selected directory path from FileExplorer
2. Set up logging to capture output to a string buffer
3. Discover audio files using `discover_audio_files()`
4. Discover classifiers using `discover_classifiers()`
5. Create `InferencePipeline` and `ResultLogger` instances
6. Process files with progress callbacks that yield updates to the UI
7. Return both the JSON results and accumulated logs

**Log Capture**

- Use Python's `io.StringIO` and custom logging handler
- Capture INFO and ERROR level messages
- Format logs for readable display in the UI

### 3. Integration Points

Reuse existing technotaggr modules:

- [`audio.py`](src/technotaggr/audio.py) - `discover_audio_files()`
- [`model_loader.py`](src/technotaggr/model_loader.py) - `discover_classifiers()`
- [`inference.py`](src/technotaggr/inference.py) - `InferencePipeline.analyze_audio()`
- [`result_logger.py`](src/technotaggr/result_logger.py) - `ResultLogger.get_session_results()`
- [`config.py`](src/technotaggr/config.py) - `DEFAULT_MODELS_DIR`, `DEFAULT_OUTPUT_DIR`

### 4. Entry Point

Add a new CLI command or function to launch the Gradio app:

- Create `launch_app()` function in `app.py`
- Optionally add `technotaggr-ui` script entry point in [`pyproject.toml`](pyproject.toml)
- Configure Gradio with `share=False` for local use by default

### 5. Error Handling

- Gracefully handle missing directories
- Show user-friendly error messages when no audio files found
- Display individual file processing errors in the log output
- Validate directory selection before processing

## Key Files to Create/Modify

- **Create**: `src/technotaggr/app.py` - Main Gradio interface implementation
- **Modify**: `pyproject.toml` - Add new script entry point (optional)

### To-dos

- [ ] Create app.py with Gradio interface layout and components
- [ ] Implement analysis function that integrates with existing pipeline
- [ ] Set up log capture mechanism to display progress and errors
- [ ] Add script entry point in pyproject.toml for easy launching
- [ ] Test the interface with sample data from song-data/smol