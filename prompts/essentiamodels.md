
Write a script to download models from the Essentia models website. We want the following classifiers in `classification-heads/` (https://essentia.upf.edu/models/):
``` 
"fs_loop_ds",
    "mood aggressive",
    "mood happy",
    "mood relaxed",
    "mood sad",
    "nsynth instrument",
    "nsynth reverb",
    "tonal/atonal"
```
And the models: `msd-musicnn-1` and `discogs-effnet-1`.

For example, in `Index of /models/classification-heads/mood_happy/`
we want to only download the following 2 files:
```
mood_happy-msd-musicnn-1.json
mood_happy-msd-musicnn-1.pb
```
in the page:
```
mood_happy-msd-musicnn-1-tfjs/                     20-Feb-2023 15:42                   -
mood_happy-audioset-vggish-1.json                  16-May-2023 07:55                2318
mood_happy-audioset-vggish-1.onnx                  16-May-2023 07:55               53298
mood_happy-audioset-vggish-1.pb                    16-May-2023 07:55               53658
mood_happy-audioset-yamnet-1.json                  16-May-2023 07:55                2324
mood_happy-audioset-yamnet-1.onnx                  16-May-2023 07:55              411698
mood_happy-audioset-yamnet-1.pb                    16-May-2023 07:55              412058
mood_happy-discogs-effnet-1.json                   28-Oct-2025 18:59                2350
mood_happy-discogs-effnet-1.onnx                   16-May-2023 07:55              514097
mood_happy-discogs-effnet-1.pb                     16-May-2023 07:55              514458
mood_happy-msd-musicnn-1.json                      16-May-2023 07:55                2309
mood_happy-msd-musicnn-1.onnx                      16-May-2023 07:55               82094
mood_happy-msd-musicnn-1.pb                        16-May-2023 07:55               82458
mood_happy-openl3-music-mel128-emb512-1.json       16-May-2023 07:55                2329
mood_happy-openl3-music-mel128-emb512-1.onnx       16-May-2023 07:55              206909
mood_happy-openl3-music-mel128-emb512-1.pb         16-May-2023 07:55              207258
```

We also want to download the the musicnn & discogs-effnet extractors in `feature-extractors/` (https://essentia.upf.edu/models/feature-extractors/):

Only the json and pb files:
```
msd-musicnn-1-tfjs.zip                             16-May-2023 07:46             2962330
msd-musicnn-1.json                                 16-May-2023 07:46                3299
msd-musicnn-1.onnx                                 18-May-2023 14:33             3168334
msd-musicnn-1.pb                                   16-May-2023 07:46             3197999
```

and in `https://essentia.upf.edu/models/feature-extractors/discogs-effnet/`