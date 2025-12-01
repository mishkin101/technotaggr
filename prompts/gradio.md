Your role is to develop a gradio interface for `technotaggr` that allows the user to upload audio files and see the predictions from the models.

Requirements:
- A `FileExplorer` component to choose the input directory. Use the default of `song-data/smol` if no directory is chosen.
- Uses a JSON component to display the results for each audio file in a readable format.
- Relevant `gradio` documentation are available in the `prompts/docs/` directory.
- Have a way to show progress and errors/logs from the cli output.

Here is the cli output of `uv run technotaggr song-data/smol`:
```
2025-12-01 09:31:42 [INFO] technotaggr.result_logger: Results saved to: /Users/adb/stuff/gitclones/technotaggr/technotaggr_results/results_20251201_093127.json

Results saved to: /Users/adb/stuff/gitclones/technotaggr/technotaggr_results/results_20251201_093127.json

============================================================
TechnoTaggr Analysis Summary
============================================================
Session: 2025-12-01T09:31:27.913856
Input:   song-data/smol
Output:  /Users/adb/stuff/gitclones/technotaggr/technotaggr_results
------------------------------------------------------------
Total files:      3
Successful:       3
Failed:           0
Classifiers used: 8
------------------------------------------------------------

Per-file Results:

  01 Heal My Soul.aiff
    Duration: 300.0s
    fs_loop_ds: chords (37.49%)
    mood aggressive: not_aggressive (95.83%)
    mood happy: non_happy (94.62%)
    mood relaxed: relaxed (57.70%)
    mood sad: non_sad (93.86%)
    nsynth instrument: mallet (46.67%)
    nsynth reverb: wet (94.89%)
    tonal/atonal: atonal (85.34%)

  1-01 Neck Carver.aiff
    Duration: 296.9s
    fs_loop_ds: bass (31.64%)
    mood aggressive: aggressive (97.69%)
    mood happy: non_happy (99.85%)
    mood relaxed: non_relaxed (98.77%)
    mood sad: non_sad (99.55%)
    nsynth instrument: mallet (99.25%)
    nsynth reverb: wet (99.74%)
    tonal/atonal: atonal (100.00%)

  29 - BT Premiere： CSP - Funk [ASWVA001].mp3
    Duration: 325.9s
    fs_loop_ds: melody (38.26%)
    mood aggressive: aggressive (84.74%)
    mood happy: non_happy (95.53%)
    mood relaxed: non_relaxed (90.72%)
    mood sad: non_sad (100.00%)
    nsynth instrument: mallet (93.56%)
    nsynth reverb: wet (96.36%)
    tonal/atonal: atonal (99.63%)

============================================================
```