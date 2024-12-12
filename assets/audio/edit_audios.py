# load audio files from the assets/audio folder and add a silent part at the beginning and at the end of the audio files (1 second each)

import os
import scipy.io.wavfile as wav
import numpy as np

# path to the audio files

path = '/assets/audio/'

# list of audio files

audio_files = os.listdir(path)

# add a silent part at the beginning and at the end of the audio files (1 second each)

for audio_file in audio_files:
    rate, data = wav.read(path + audio_file)
    silent_part = np.zeros(rate)
    data = np.concatenate((silent_part, data, silent_part))
    wav.write(path + audio_file, rate, data)
    print(audio_file + ' has been edited')
    
print('All audio files have been edited')

