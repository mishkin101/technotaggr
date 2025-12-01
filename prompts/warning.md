Help me suppress the warning messages from the essentia library: `[ WARNING  ] No network created, or last created network has been deleted...`

Here is a relevant github issue:
```
Hi!

I created a code to extract Loudness EBUR128 with standard mode, the feature is returned but I realised there is a WARNING message printed which is not so clear.

[ WARNING  ] No network created, or last created network has been deleted...

I found out other issues discussing about multithreading in C++ but in my case, I am running a Python script.

Here my code to reproduce it:

    loudness_EBUR128 = es.LoudnessEBUR128(sampleRate=sample_rate)
    audio = es.AudioLoader(filename=str(audio_file))()[0]
    (
    ebur128_momentary,
    ebur128_short_term,
    ebur128.integrated,
    ebur128.loudnessRange,
    ) = loudness_EBUR128(
    audio
    )

Activity
xaviliz
xaviliz commented on Oct 30, 2024
xaviliz
(Xavi Lizarraga)
on Oct 30, 2024
Contributor
Author

It was solved by instantiating once each algorithm and using the configure() method for reusing them.
xaviliz
closed this as completedon Oct 30, 2024
julianallchin
julianallchin commented on Nov 9, 2024
Julian Allchin
on Nov 9, 2024

Can you please explain in more detail?
dzharikhin
dzharikhin commented on Jul 19
dzharikhin
(Dmitriy Zharikhin)
on Jul 19
Contributor

workaround to silence annoying logs: essentia.EssentiaLogger().warningActive = False
xaviliz
xaviliz commented on Jul 22
xaviliz
(Xavi Lizarraga)
on Jul 22
Contributor
Author

    Can you please explain in more detail?

sorry for my late reply. Of course, I can.

If you want to use essentia algorithms recursively, you need to instantiante once your algorithms:

loudness_EBUR128 = es.LoudnessEBUR128(sampleRate=sample_rate)
audio_loader = es.AudioLoader(filename=str(audio_paths[0]))

Then, each essentia algorithm has a configure() method.

results = list()
for audio_path in audio_paths:
    audio_loader.configure(filename=str(audio_path))
    audio, sample_rate, _, _, _, _ = audio_loader()
    loudness_EBUR128.configure(sampleRate=sample_rate)
    results.append(loudness_EBUR128()[0])

In that way the warning is silenced becasue you update the algorithm network at each iteration, instead of creating a new one. That's what the warning message is pointing out.

    workaround to silence annoying logs: essentia.EssentiaLogger().warningActive = False

You can do that but using configure() you don't need to create algorithm instancies for each iteration. It is more compact and more optimized. Hope this helps.
```