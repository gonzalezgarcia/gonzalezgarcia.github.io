---
layout: page
title: One-shot auditory disambiguation  
description: A showcase of ambiguous auditory stimuli and their disambiguation
category: work
---

Perception is not always straightforward. Sometimes, sensory inputs can be highly ambiguous. Think for instance you are listening for the first time to the new song of Shakira. You might find youself in the situation of not being able to understand the lyrics. This is because the auditory stimulus is ambiguous and you cannot really make up your mind about what you are hearing. However, if you were to read the lyrics, or somebody would tell you what she's saying, you would be able to **disambiguate** the song, probably forever.

Here, I present an example of ambiguous auditory stimuli we can create artificially from natural speech. For most of us, the following clip is highly ambiguous. Listen to it and try to see if you understand what this person is saying!

{% include audio.liquid path="assets/audio/caption_bench_distorded.wav" controls=true %}
<div class="caption">
    Feel free to listen to the clip as many times as you want :)
</div>

Now, there are many ways to disambiguate this clip. Let's try three of them, which vary in how likely they are to induce disambiguation-

1) **Take a look at the scene the clip is describing**. This is the least likely to induce disambiguation, but it might help you to get a sense of what the person is saying.
 {% include figure.liquid loading="eager" path="assets/audio/bench.jpg" max-width="300px" class="img-fluid rounded z-depth-1" %} 

Can you identify what he's saying now?

{% include audio.liquid path="assets/audio/caption_bench_distorded.wav" controls=true %}
-----

2) **Read the caption of the audio**. This is _very_ likely to induce disambiguation. Let's try it out! Read the following while playing the audio:
##### *"a wooden bench sitting in front of a stonewall"*
{% include audio.liquid path="assets/audio/caption_bench_distorded.wav" controls=true %}
-----

3) **Listed to the undistorted version of the clip**. This is also very likely to induce disambiguation. On the left, you can listen to the undistorted version of the clip. On the right, the distorted one. Does it sound clearer now?

<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include audio.liquid path="assets/audio/caption_bench_distorded.wav" controls=true %}
        
    </div>
    <div class="col-sm mt-3 mt-md-0">
        {% include audio.liquid path="assets/audio/bench.wav" controls=true %}
    </div>
</div>
<div class="caption">
    Distorted (left) and undistorted (right) versions of the same clip.
</div>

-----

#### Do you want to try more examples?

Here are a few more examples of ambiguous auditory stimuli:

1) 
<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include audio.liquid path="assets/audio/caption_bikini_distorded.wav" controls=true %}
        
    </div>
    <div class="col-sm mt-3 mt-md-0">
        {% include audio.liquid path="assets/audio/bikini.wav" controls=true %}
    </div>
</div>
<div class="caption">
    Distorted (left) and undistorted (right) versions of the same clip.
</div>

2)
<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include audio.liquid path="assets/audio/caption_rope_distorded.wav" controls=true %}
        
    </div>
    <div class="col-sm mt-3 mt-md-0">
        {% include audio.liquid path="assets/audio/rope.wav" controls=true %}
    </div>
</div>
<div class="caption">
    Distorted (left) and undistorted (right) versions of the same clip.
</div>

3)
<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include audio.liquid path="assets/audio/caption_peacock_distorded.wav" controls=true %}
        
    </div>
    <div class="col-sm mt-3 mt-md-0">
        {% include audio.liquid path="assets/audio/peacock.wav" controls=true %}
    </div>
</div>
<div class="caption">
    Distorted (left) and undistorted (right) versions of the same clip.
</div>

