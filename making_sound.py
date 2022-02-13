from numpy.lib.function_base import blackman
import pyaudio
import numpy as np
import sounddevice as sd
# import pygame
from scipy.io import wavfile
p = pyaudio.PyAudio()

# pygame.mixer.pre_init(44100, size=-16, channels=1)
# pygame.mixer.init()

volume = 0.5     # range [0.0, 1.0]
fs = 44100       # sampling rate, Hz, must be integer
duration = 5.0  # in seconds, may be float
f1 = 261.6256      # sine frequency, Hz, may be float
f2 = 220.0
# generate samples, note conversion to float32 array
samples = (np.sin(2*np.pi*np.arange(fs*duration)*f1/fs))
s2 = ((1/2)*np.sin((2*np.pi*np.arange(fs*duration)*f1*2/fs)+np.pi/2))
s3 = ((1/3)*np.sin((2*np.pi*np.arange(fs*duration)*f1*3/fs)+np.pi))
s4 = ((1/4)*np.sin((2*np.pi*np.arange(fs*duration)*f1*4/fs)+2*np.pi))
s5 = ((1/5)*np.sin((2*np.pi*np.arange(fs*duration)*f1*5/fs)+4*np.pi))
# s6 = ((1/6)*np.sin((2*np.pi*np.arange(fs*duration)*f1*6/fs)+np.pi))

# samples = samples + s2+s3+s4+s5
# sd.play(samples,fs,blocking=True)
# sound = pygame.sndarray.make_sound(samples)
# sound.play()


# +s6
sample_rate, data = wavfile.read(
    f"music/final.wav")
if data.ndim == 1:
    main_graph_data = (data.tolist())
else:
    main_graph_data = (data[:, 0].tolist())
    main_graph_data = np.array(main_graph_data)
    main_graph_data = main_graph_data.astype(np.int16)
# print(len(samples))
# +s3
# +s4+s5+s6
# samples = samples.astype(np.float32)
# s2 = (np.sin(2*np.pi*np.arange(fs*duration)*f2))
# samples = (np.concatenate(s1,s2)).astype(np.float32)

# for paFloat32 sample values must be in range [-1.0, 1.0]
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=int(sample_rate),
                output=True)
# sd.play(main_graph_data,sample_rate)
print(sample_rate)
# # play. May repeat with different volume values (if done interactively)
stream.write(volume*main_graph_data)
stream.stop_stream()
stream.close()

p.terminate()
