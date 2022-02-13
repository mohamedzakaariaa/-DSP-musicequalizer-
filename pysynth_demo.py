from scipy.io import wavfile
import numpy as np
import pyaudio
player = pyaudio.PyAudio()

dictionary_of_notes = {}
dictionary_of_strings = {}
dictionary_of_drums = {}
piano_notes = ["C4", "C#", "D4", "D#", "E4",
               "F4", "F#", "G4", "G#", "A4", "A#", "B4"]
guitar_string = ["s1", "s2", "s3", "s4", "s5", "s6"]
drums = ["d1", "d2", "d3", "d4"]
for string in guitar_string:
    sample_rate, data = wavfile.read(
        f"guitar_strings/{string}.wav")
    print(sample_rate)
    if data.ndim == 1:
        main_graph_data = (data.tolist())
    else:
        main_graph_data = (data[:, 0].tolist())
# print(len(self.main_graph_data))
# print(self.main_graph_sample_rate)
    # current_signal_duration = len(
    #     main_graph_data)/sample_rate
# print(self.current_signal_duration)
    # main_graph_time = list((np.linspace(
    #     0, current_signal_duration, (len(main_graph_data)))))
    main_graph_data = np.array(main_graph_data)
    main_graph_data = main_graph_data.astype(np.int16)
    dictionary_of_strings[string] = main_graph_data

for drum in drums:
    sample_rate, data = wavfile.read(
        f"drums/{drum}.wav")
    print(sample_rate)
    if data.ndim == 1:
        main_graph_data = (data.tolist())
    else:
        main_graph_data = (data[:, 0].tolist())
# print(len(self.main_graph_data))
# print(self.main_graph_sample_rate)
    # current_signal_duration = len(
    #     main_graph_data)/sample_rate
# print(self.current_signal_duration)
    # main_graph_time = list((np.linspace(
    #     0, current_signal_duration, (len(main_graph_data)))))
    main_graph_data = np.array(main_graph_data)
    main_graph_data = main_graph_data.astype(np.int16)
    dictionary_of_drums[drum] = main_graph_data

for note in piano_notes:
    sample_rate, data = wavfile.read(
        f"piano_notes/{note}.wav")
    print(sample_rate)
    if data.ndim == 1:
        main_graph_data = (data.tolist())
    else:
        main_graph_data = (data[:, 0].tolist())
# print(len(self.main_graph_data))
# print(self.main_graph_sample_rate)
    # current_signal_duration = len(
    #     main_graph_data)/sample_rate
# print(self.current_signal_duration)
    # main_graph_time = list((np.linspace(
    #     0, current_signal_duration, (len(main_graph_data)))))
    main_graph_data = np.array(main_graph_data)
    main_graph_data = main_graph_data.astype(np.int16)
    dictionary_of_notes[note] = main_graph_data
stream = player.open(format=pyaudio.paInt16,
                     channels=1,
                     rate=sample_rate,
                     output=True)
# play. May repeat with different volume values (if done interactively)
for key in dictionary_of_notes:
    stream.write(1*dictionary_of_notes[key])
