import numpy as np
import sounddevice as sd

class Guitar():
    def __init__(self):
        self.base_tones = {"s1": 27, "s2": 36, "s3": 49, "s4": 65, "s5": 83, "s6": 110}
        self.tones = {"s1": 82, "s2": 110, "s3": 147, "s4": 196, "s5": 247, "s6": 330}
        super().__init__()

    def karplus_strong(self, wavetable, n_samples):
        samples = []
        current_sample = 0
        previous_value = 0
        while len(samples) < n_samples:
            wavetable[current_sample] = 0.5 * (wavetable[current_sample] + previous_value)
            samples.append(wavetable[current_sample])
            previous_value = samples[-1]
            current_sample += 1
            current_sample = current_sample % wavetable.size
        return np.array(samples)

    def multiply_freqs(self, factor):
        for key in self.tones.keys():
            self.tones[key] = self.base_tones[key] * factor
        print(self.tones)


    def play(self, note):
        freq = self.tones[note]
        fs = 30000
        wavetable_size = fs // freq

        wavetable = (2 * np.random.randint(0, 2, wavetable_size) - 1).astype(np.float64)
        sample1 = self.karplus_strong(wavetable, 2 * fs)
        sd.play(sample1, fs)
