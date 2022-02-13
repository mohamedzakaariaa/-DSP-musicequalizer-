import os
from datetime import datetime
from PyQt5 import QtGui, QtWidgets
from PyQt5 import QtCore
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from matplotlib.colors import NoNorm, same_color
import pyqtgraph
from GUI import Ui_MainWindow
import sys
import numpy as np
from math import *
# import numpy.fft as fft
from PyQt5.QtCore import QThread, QUrl, pyqtSignal
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from scipy.io import wavfile
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import matplotlib.pyplot as plt
import pyaudio
# from datetime import datetime
import logging
# import sounddevice as sd
# import pygame
import librosa
import librosa.display
import matplotlib
from sound import sound
import qdarkstyle
matplotlib.use('Qt5Agg')


class MainWindow(QtWidgets.QMainWindow):
    play_piano_note = pyqtSignal(str)
    play_drums = pyqtSignal(int)
    play_guitar_string = pyqtSignal(str)
    play_modified_sound = pyqtSignal(np.ndarray)
    play_note = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gui = Ui_MainWindow()
        self.gui.setupUi(self)
        self.gui.instruments_widget.hide()
        self.spectrogram_canvas = Canvas()
        self.gui.spectrogram_graph.hide()
        self.gui.spectrogram_layout.addWidget(self.spectrogram_canvas)
        self.plotted_signal = np.array([])
        self.main_graph_data = []
        self.main_graph_sample_rate = 0
        self.current_signal_duration = 0
        self.main_graph_time = []
        self.x_range1 = self.gui.main_graph.getViewBox(
        ).state['viewRange'][0]
        self.play_is_clicked = False
        self.counter = 0
        self.updating_counter = 0
        self.time_length = 0
        self.data_length = 0
        self.step = 0
        self.selected_string = 0
        self.modified_signal = np.array([])
        self.current_slider_gain = [1.0] * 3
        self.slider_gains = [0.0, 0.25, 0.50, 0.75,
                             0.85, 1.0, 2.0, 4.0, 6.0, 8.0, 10.0]
        self.instroments_sliders = {}
        self.instroments_label = {}
        self.x_axis_data = []
        self.y_axis_data = []
        self.gui.piano_widget.setMaximumHeight(16777215)
        self.gui.piano_widget.setMaximumWidth(16777215)
        self.gui.guitar_widget.setMaximumHeight(16777215)
        self.gui.guitar_widget.setMaximumWidth(16777215)
        self.gui.drums_widget.setMaximumHeight(16777215)
        self.gui.drums_widget.setMaximumWidth(16777215)
        self.gui.piano_widget.hide()
        self.gui.guitar_widget.hide()
        self.gui.drums_widget.hide()
        self.player = QMediaPlayer()
        self.audio = pyaudio.PyAudio()
        for index in range(3):
            self.instroments_sliders[index] = getattr(
                self.gui, 'slider{}'.format(index+1))
            self.instroments_label[index] = getattr(
                self.gui, 'label{}'.format(index+1))
        # for index, slider in self.instroments_sliders.items():
        #     slider.sliderReleased.connect(
        #         lambda index=index: self.slider_gain_updated(index))
        self.gui.slider1.sliderReleased.connect(
            lambda: self.slider_gain_updated(0))
        self.gui.slider2.sliderReleased.connect(
            lambda: self.slider_gain_updated(1))
        self.gui.slider3.sliderReleased.connect(
            lambda: self.slider_gain_updated(2))
        # self.frequency_ranges_dictionary = {0: [60, 170], 1: [170, 310], 2: [310, 600], 3: [600, 1000], 4: [
        #     1000, 3000], 5: [3000, 6000], 6: [6000, 12000, ], 7: [12000, 14000], 8: [14000, 16000], 9: [16000, 22000]}
        self.gui.volume_slider.setMaximum(100)
        self.gui.volume_slider.setMinimum(0)
        self.pen1 = pyqtgraph.mkPen((255, 0, 0), width=3)
        self.pen2 = pyqtgraph.mkPen((255, 255, 0), width=3)
        self.max_icon = QtGui.QPixmap("icons/max.png")
        self.highMid_icon = QtGui.QPixmap("icons/2.png")
        self.min_icon = QtGui.QPixmap("icons/mute.png")
        self.lowMid_icon = QtGui.QPixmap("icons/1.png")
        self.pause_icon = QtGui.QIcon()
        self.pause_icon.addPixmap(QtGui.QPixmap(
            "icons/pause.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.play_icon = QtGui.QIcon()
        self.play_icon.addPixmap(QtGui.QPixmap(
            "icons/play.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Critical)
        self.msg.setText("Error")
        self.msg.setWindowTitle("Error")
        self.gui.open_action.triggered.connect(self.open_signal)
        self.gui.play_pause_botton.clicked.connect(self.play_pause)
        self.gui.volume_slider.valueChanged.connect(self.change_volume)
        self.gui.piano_calling_button.clicked.connect(self.show_piano)
        self.gui.guitar_calling_button.clicked.connect(self.show_guitar)
        self.gui.drums_calling_button.clicked.connect(self.show_drums)
        self.sound = sound()
        self.sound_thread = QThread()
        self.sound.moveToThread(self.sound_thread)
        self.sound_thread.start()
        self.play_drums.connect(self.sound.Bongo)
        self.play_guitar_string.connect(self.sound.guitar)
        self.play_piano_note.connect(self.sound.piano)
        self.play_modified_sound.connect(self.sound.play_modified_sound)
        self.gui.guitar_dial.valueChanged.connect(
            self.sound.guitar_multiply_freqs)
        self.play_note.connect(self.sound.piano)
        self.gui.octave_slider.valueChanged.connect(
            self.set_cuurent_played_octave)
        # self.gui.drum1_button.clicked.connect(lambda: self.play_drum("C"))
        # self.gui.drum2_button.clicked.connect(lambda: self.play_drum("C#"))
        # self.gui.drum3_button.clicked.connect(lambda: self.play_drum("d3"))
        # self.gui.drum4_button.clicked.connect(lambda: self.play_drum("d4"))
        self.gui.drums_button.clicked.connect(self.play_drum)
        self.gui.drums_slider.valueChanged.connect(self.adjust_drums_power)

        self.curr_octave = 4
        self.drumms_power = 5
        self.drums_power_ramges = [2,2.5,3,3.5,4,4.2,4.4,4.6,4.8,5,5.2,5.4,5.6,5.8,6,6.5,7,7.5,8,9]
        self.piano_btns = {
            self.gui.B_button, self.gui.C_button, self.gui.Csharp_button,
            self.gui.D_button, self.gui.Dsharp_sharp, self.gui.E_button,
            self.gui.F_button, self.gui.Fsharp_button, self.gui.G_button,
            self.gui.Gsharp_button, self.gui.A_button, self.gui.Asharp_button,
            self.gui.B_button
        }
        self._piano_notes, self.piano_notes = [
            "C", "D", "E", "F", "G", "A", "B"], []
        self.adjust_piano_btns()
        # for i, btn in enumerate(self.piano_btns):
        #     btn.clicked.connect(self.play_piano_of(self.piano_notes[i]))

        self.gui.string1.clicked.connect(lambda: self.play_guitar("s1"))
        self.gui.string2.clicked.connect(lambda: self.play_guitar("s2"))
        self.gui.string3.clicked.connect(lambda: self.play_guitar("s3"))
        self.gui.string4.clicked.connect(lambda: self.play_guitar("s4"))
        self.gui.string5.clicked.connect(lambda: self.play_guitar("s5"))
        self.gui.string6.clicked.connect(lambda: self.play_guitar("s6"))
        self.show()

    def play_drum(self):
        self.play_drums.emit(self.drumms_power)

    def adjust_drums_power(self):
        self.drumms_power = self.drums_power_ramges[self.gui.drums_slider.value()]

    def adjust_piano_btns(self):
        self.piano_notes.clear()
        for note in self._piano_notes:
            self.piano_notes.append(f"{note}{self.curr_octave}")
            self.piano_notes.append(f"{note}{self.curr_octave}#")

        self.piano_notes = list(
            set(self.piano_notes) -
            {f"B{self.curr_octave}#", f"E{self.curr_octave}#"}
        )
        for i, btn in enumerate(self.piano_btns):
            btn.disconnect()
            btn.clicked.connect(self.play_piano_of(self.piano_notes[i]))

    def set_cuurent_played_octave(self):
        value = self.gui.octave_slider.value()
        self.curr_octave = int(value)
        self.gui.label_16.setText(str(value))
        self.adjust_piano_btns()

    def play_piano_of(self, note):
        return lambda: self.play_piano(note)

    def show_piano(self):
        self.gui.instruments_widget.show()
        self.gui.guitar_widget.hide()
        self.gui.drums_widget.hide()
        self.gui.piano_widget.show()

    def play_piano(self, key):
        self.play_note.emit(key)

    # def play_drum(self, key):
    #     self.play_drum_number.emit(key)

    def play_guitar(self, key):
        self.play_guitar_string.emit(key)

    # def play_piano(self, key):
    #     self.play_piano_note.emit(key)

    def show_guitar(self):
        self.gui.instruments_widget.show()
        self.gui.piano_widget.hide()
        self.gui.drums_widget.hide()
        self.gui.guitar_widget.show()

    def show_drums(self):
        self.gui.instruments_widget.show()
        self.gui.piano_widget.hide()
        self.gui.guitar_widget.hide()
        self.gui.drums_widget.show()

    def open_signal(self):
        self.main_graph_data.clear()
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            None, "Open File", r"D:/SBME_3/1st_term/DSP/tasks/task3/music", "music(*.wav)", options=options)
        if file_path == '':
            self.warning_message("please choose a file ")
        else:
            self.main_graph_sample_rate, data = wavfile.read(
                file_path)
            if data.ndim == 1:
                self.main_graph_data = (data.tolist())
            else:
                self.main_graph_data = (data[:, 0].tolist())
                self.plotted_signal = self.main_graph_data
            self.current_signal_duration = len(
                self.main_graph_data)/self.main_graph_sample_rate
            self.main_graph_time = list((np.linspace(
                0, self.current_signal_duration, (len(self.main_graph_data)))))
            self.plot_main_graph()
            print(len(self.main_graph_data))
            print(self.current_signal_duration)
            print((len(self.main_graph_data))/100)
            print(self.main_graph_sample_rate)
            self.plot_spectrogram(self.main_graph_data,
                                self.main_graph_sample_rate)
            url = QUrl.fromLocalFile(file_path)
            content = QMediaContent(url)
            self.player.setMedia(content)
            self.player.setVolume(50)
            self.gui.volume_slider.setValue(50)
            logger.info("the file has been opened successfully")

    def modify_signal(self):
        self.player.stop()
        self.player = None
        self.gui.play_pause_botton.setIcon(self.pause_icon)
        frequency_content = np.fft.rfftfreq(
            len(self.main_graph_data), d=1/self.main_graph_sample_rate)
        self.ranges = [[800, 2000], [0, 1000], [1800, 11000]]
        modified_signal = np.fft.rfft(self.main_graph_data)
        slider_min_max = []
        for slider in range(0, 3):
            range_min_frequency = frequency_content > self.ranges[slider][0]
            range_max_frequency = frequency_content <= self.ranges[slider][1]
            for is_in_min_frequency, is_in_max_frequency in zip(range_min_frequency, range_max_frequency):
                slider_min_max.append(
                    is_in_min_frequency and is_in_max_frequency)
            modified_signal[slider_min_max] *= self.current_slider_gain[slider]
            slider_min_max = []
        # range_min_frequency1 = frequency_content > 800
        # range_max_frequency1 = frequency_content <= 2000
        # slider_min_max = []

        # for is_in_min_frequency, is_in_max_frequency in zip(range_min_frequency1, range_max_frequency1):
        #     slider_min_max1.append(
        #         is_in_min_frequency and is_in_max_frequency)
        # modified_signal[slider_min_max1] *= self.current_slider_gain[0]
        # range_min_frequency2 = frequency_content > 0
        # range_max_frequency2 = frequency_content <= 1000
        # slider_min_max2 = []
        # for is_in_min_frequency, is_in_max_frequency in zip(range_min_frequency2, range_max_frequency2):
        #     slider_min_max2.append(
        #         is_in_min_frequency and is_in_max_frequency)
        # modified_signal[slider_min_max2] *= self.current_slider_gain[1]
        # range_min_frequency3 = frequency_content > 1800
        # range_max_frequency3 = frequency_content <= 11000
        # slider_min_max3 = []
        # for is_in_min_frequency, is_in_max_frequency in zip(range_min_frequency3, range_max_frequency3):
        #     slider_min_max3.append(
        #         is_in_min_frequency and is_in_max_frequency)
        # modified_signal[slider_min_max3] *= self.current_slider_gain[2]
        self.samples_after = np.fft.irfft(modified_signal)
        self.plotted_signal = self.samples_after
        self.spectrogram_canvas.ax.clear()
        self.color_bar.remove()
        self.plot_spectrogram(self.samples_after, self.main_graph_sample_rate)
        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(
            lambda: self.update_Xaxis(self.plotted_signal))
        self.timer.start()
        if os.path.exists("Output.wav"):
            # print("path is exist")
            os.remove("Output.wav")
        # if os.path.exists("Output.wav"):
            # print("path is exist")
        # self.plot_modified_graph()
        # self.now = datetime.now()
        # self.now = f'{self.now:%Y-%m-%d %H-%M-%S.%f %p}'
        self.play_modified_music(self.main_graph_sample_rate, self.samples_after[int(
            self.updating_counter*self.time_length):].astype(np.int16))
        # self.timer.stop()
        # self.stream = self.audio.open(format=pyaudio.paFloat32,
        #                               channels=1,
        #                               rate=48000,
        #                               output=True)
        # self.stream.write(1*self.samples_after)
        # self.stream = self.audio.open(format=pyaudio.paInt16,
        #                               channels=1,
        #                               rate=48000,
        #                               output=True)

        # self.samples_after = np.array(self.samples_after)
        # self.samples_after = self.samples_after.astype(np.int16)
        # print(len(self.samples_after))
        # self.play_modified_sound.emit(self.samples_after)
        # self.stream.write(1*self.samples_after)
        # self.stream.stop_stream()

    def slider_gain_updated(self, index):
        slider_gain = self.slider_gains[self.instroments_sliders[index].value(
        )]
        self.instroments_label[index].setText(f"{slider_gain} dB")
        self.current_slider_gain[index] = slider_gain
        self.modify_signal()

    def change_volume(self):
        current_value = int(self.gui.volume_slider.value())
        self.gui.volume_value_label.setText(str(current_value))
        self.player.setVolume(current_value)
        if current_value > 80:
            self.gui.volume_image_label.setPixmap(self.max_icon)
        elif current_value <= 80 and current_value >= 40:
            self.gui.volume_image_label.setPixmap(self.highMid_icon)
        elif current_value < 40 and current_value > 0:
            self.gui.volume_image_label.setPixmap(self.lowMid_icon)
        else:
            self.gui.volume_image_label.setPixmap(self.min_icon)
        logger.debug(f"volume has changed to  {current_value}")

    def play_pause(self):
        if len(self.main_graph_data) == 0:
            self.warning_message("please choose file before pressing play!! 😑")
        else:
            if self.play_is_clicked:
                self.pause_signal()
            else:
                self.play_signal()

    def warning_message(self, message):
        self.msg.setInformativeText(message)
        logger.warning(message)
        self.msg.exec_()

    def pause_signal(self):
        self.gui.play_pause_botton.setIcon(self.play_icon)
        self.player.pause()
        self.timer.stop()
        self.play_is_clicked = False

    def plot_main_graph(self):
        # print(len(self.main_graph_time))
        self.data_length = int(len(self.main_graph_data)/108)
        self.time_length = int(len(self.main_graph_data)/(108))
        print(f"d = {self.data_length}")
        self.x_axis_data = self.main_graph_time[:self.time_length]
        self.y_axis_data = self.plotted_signal[:self.data_length]
        self.gui.main_graph.setYRange(
            (min(self.plotted_signal)-0.5), (max(self.plotted_signal)+0.5))
        # self.gui.main_graph.setXRange(0, .05)
        # print(len(self.main_graph_data))
        self.gui.main_graph.clear()
        # self.gui.main_graph.setXRange(0, 1)
        self.main_graph_plot = self.gui.main_graph.plot(
            self.x_axis_data, self.y_axis_data, pen=self.pen1)
        # plot2 = self.gui.main_graph.plotItem.plot(
        #     self.main_graph_time[:int(self.time_length/2)], self.main_graph_data[:int(self.data_length/2)], pen=self.pen2)

        # plotWidget = pyqtgraph.plot(self.main_graph_time,self.main_graph_data,self.pen1)
        logger.debug(f"the music has been plotted successfully ")

    def play_signal(self):
        # if self.x_range1[0] > (self.main_graph_time[self.time_length-1])+0.1:
        #     self.x_range1[0] = 0
        #     self.x_range1[1] = 1
        #     self.updating_counter = 0
        #     self.gui.main_graph.setXRange(self.x_range1[0], self.x_range1[1])
        self.gui.play_pause_botton.setIcon(self.pause_icon)
        self.player.play()
        self.play_is_clicked = True
        # print(self.time_length)
        # print(
        #     f"the max range is {self.x_range1[1]} and min range is {self.x_range1[0]}")
        # no_of_updates = ((self.current_signal_duration)*1000)/20
        # step = ((self.current_signal_duration)/30)/no_of_updates
        # print(f"the desired length of the graph is = {step*no_of_updates}")

        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(
            lambda: self.update_Xaxis(self.plotted_signal))
        self.timer.start()

    def update_Xaxis(self, data):
        self.x_axis_data.clear()
        self.y_axis_data.clear()
        self.x_axis_data.extend(
            self.main_graph_time[int(self.time_length+(self.time_length*self.updating_counter)):int(self.time_length+(self.time_length*(self.updating_counter+1)))])
        self.y_axis_data.extend(
            data[int(self.time_length+(self.time_length*self.updating_counter)):int(self.time_length+(self.time_length*(self.updating_counter+1)))])
        self.main_graph_plot.setData(
            np.array(self.x_axis_data), np.array(self.y_axis_data))
        self.updating_counter += 1
        print(f"the counter value is = {self.updating_counter}")
        if self.updating_counter > (len(data)/self.time_length):
            self.timer.stop()
            self.updating_counter = 0
            self.gui.play_pause_botton.setIcon(self.play_icon)
            self.play_is_clicked = False

    def play_modified_music(self, sample_rate, sound):
        wavfile.write(
            f'Output.wav', sample_rate, sound)
        self.player = QMediaPlayer()
        self.player.setMedia(QMediaContent(
            QUrl.fromLocalFile(f'Output.wav')))
        self.player.play()

    def plot_spectrogram(self, samples, sampling_rate):
        _, _, _, img = self.spectrogram_canvas.ax.specgram(
            samples, Fs=sampling_rate, cmap="viridis", vmin=0, vmax=50)
        self.color_bar = plt.colorbar(img, ax=self.spectrogram_canvas.ax)
        self.spectrogram_canvas.draw()


class Canvas(FigureCanvasQTAgg):
    def __init__(self):
        fig, self.ax = plt.subplots(figsize=(4, 4), dpi=100)
        super().__init__(fig)
        # self.setParent(parent)


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    # app.setStyleSheet(qdarkstyle.load_stylesheet())
    Emphasizer = MainWindow()
    logger = logging.getLogger("main.py")
    logger.setLevel(level=logging.DEBUG)
    logging.basicConfig(filename="logging_file.log")
    logger.info("lunching of the Application ")
    sys.exit(app.exec_())

# from pyqtgraph.widgets.MatplotlibWidget import MatplotlibWidget

    # def slider_gain_updated(self, index):
    #     logger.debug(f"slider no {index} has been moved")
    #     slider_gain = self.slider_gains[self.instroments_sliders[index].value()]
    #     self.instroments_label[index].setText(f'{slider_gain}')
    #     self.current_slider_gain[index] = slider_gain
    #     self.modify_signal()
    # self.gui.drums_calling_button.clicked.connect(
    #     self.set_stream_for_instruments)
    # self.gui.piano_calling_button.clicked.connect(
    #     self.set_stream_for_instruments)
    # self.gui.guitar_calling_button.clicked.connect(
    #     self.set_stream_for_instruments)
    # for i in reversed(range(self.gui.spectrogram_layout.count())):
    #     self.gui.spectrogram_layout.itemAt(i).widget().setParent(None)
    # axes = self.spectrogram_graph.axes.clear()
    # # axes = self.spectrogram_graph.axes.add_subplot(111)
    # data = np.array(samples).astype('float32')
    # D = np.abs(librosa.stft(data)) ** 2
    # S = librosa.feature.melspectrogram(S=D, y=data, sr=sampling_rate, n_mels=128,
    #                                    fmin=0, fmax=22000)
    # S_dB = librosa.power_to_db(S, ref=np.max)
    # img = librosa.display.specshow(S_dB, x_axis='time',
    #                                y_axis='mel', sr=sampling_rate,
    #                                fmin=0, fmax=22000, ax=axes,
    #                                cmap="jet")
    # # self.spectrogram_graph.getfigure().colorbar(img, ax=axes, format='%+2.0f dB')
    # self.spectrogram_graph.axes.imshow(img,
    #                                    cmap='hot', origin="lower", interpolation='nearest')
    # self.spectrogram_graph.draw()
    # self.gui.spectrogram_layout.addWidget(self.spectrogram_graph)

    # def generate_drums_sounds(self):
    #     dictionary_of_drums = {}
    #     drums = ["d1", "d2", "d3", "d4"]
    #     for drum in drums:
    #         sample_rate, data = wavfile.read(
    #             f"drums/{drum}.wav")
    #         if data.ndim == 1:
    #             main_graph_data = (data.tolist())
    #         else:
    #             main_graph_data = (data[:, 0].tolist())
    #         main_graph_data = np.array(main_graph_data)
    #         main_graph_data = main_graph_data.astype(np.int16)
    #         dictionary_of_drums[drum] = main_graph_data
    #     return dictionary_of_drums

    # def generate_guitar_sounds(self):
    #     dictionary_of_strings_sounds = {}
    #     guitar_strings = ["s1", "s2", "s3", "s4", "s5", "s6"]
    #     for string in guitar_strings:
    #         sample_rate, data = wavfile.read(
    #             f"guitar_strings/{string}.wav")
    #         if data.ndim == 1:
    #             main_graph_data = (data.tolist())
    #         else:
    #             main_graph_data = (data[:, 0].tolist())
    #         main_graph_data = np.array(main_graph_data)
    #         main_graph_data = main_graph_data.astype(np.int16)
    #         dictionary_of_strings_sounds[string] = main_graph_data
    #     return dictionary_of_strings_sounds

    # def generate_piano_sounds(self):
    #     dictionary_of_piano = {}
    #     piano_notes = ["C4", "C#", "D4", "D#", "E4",
    #                    "F4", "F#", "G4", "G#", "A4", "A#", "B4"]
    #     for note in piano_notes:
    #         sample_rate, data = wavfile.read(
    #             f"piano_notes/{note}.wav")
    #         if data.ndim == 1:
    #             main_graph_data = (data.tolist())
    #         else:
    #             main_graph_data = (data[:, 0].tolist())
    #         main_graph_data = np.array(main_graph_data)
    #         main_graph_data = main_graph_data.astype(np.int16)
    #         dictionary_of_piano[note] = main_graph_data
    #     return dictionary_of_piano


# class MplCanvas(FigureCanvasQTAgg):

#     def __init__(self, parent=None, width=5, height=4, dpi=100):
#         fig = Figure(figsize=(width, height), dpi=dpi)
#         self.axes = fig.add_subplot(111)
#         super(MplCanvas, self).__init__(fig)

    # self.gui.main_graph.setXRange(0, 0.1)
    # if self.x_range1[0] < (self.main_graph_time[self.time_length-1])+0.1:
    #     self.x_range1[0] = self.x_range1[0]+step
    #     self.x_range1[1] = self.x_range1[1]+step
    #     self.gui.main_graph.setXRange(self.x_range1[0], self.x_range1[1])
    # else:
    #     self.timer.stop()
    #     self.gui.play_pause_botton.setIcon(self.play_icon)
    #     self.play_is_clicked = False

    # print(
    # f"the max range is {self.x_range1[1]} and min range is {self.x_range1[0]}")
    # print(f"step = {step}")
    # print(f"no of updates = {no_of_updates}")
    # logger.info(
    #     f"the graph is moving with {(self.current_signal_duration/10)/(self.current_signal_duration)}")

    # def play_guitar(self, key):
    #     if self.selected_string == 0:
    #         self.warning_message("please select any string to play!! 🙂")
    #     else:
    #         volume = 0.5
    #         note = self.notes_of_guitar[self.selected_string][key -
    #                                                           1].astype(np.float32)
    #         self.stream.write(volume*note)

    # def set_string_number(self, number):
    #     self.selected_string = number

    # def play_piano(self, key):
    #     volume = 0.5
    #     note = self.notes_of_piano[key].astype(np.float32)
    #     self.stream.write(volume*note)

    # def piano_notes(self):
    #     notes = {}
    #     for key in self.note_freqs:
    #         freq = self.note_freqs[key]
    #         notes[key] = self.get_wave(freq=freq)
    #     return notes

    # def get_wave(self, freq, duration=3.0):
    #     amplitude = 4096
    #     wave = (np.sin(2*np.pi*np.arange(44100*duration)*freq/44100))
    #     for i in range(2, 7):
    #         wave += ((1/i)*np.sin(2*np.pi*np.arange(44100*duration)*freq*i/44100))
    #     return wave

    # # def get_guitar_wave(self, freq, duration=3.0):
    # #     amplitude = 4096
    # #     wave = (np.sin(2*np.pi*np.arange(44100*duration)*freq/44100))
    # #     for i in range(2, 7):
    # #         wave += ((1/i)*np.sin(2*np.pi*np.arange(44100*duration)*freq*i/44100))
    # #     return wave

    # def guitar_notes(self):
    #     guitar_notes = {}
    #     for key in self.strings_freq:
    #         string_notes = []
    #         for freq in self.strings_freq[key]:
    #             wave = self.get_wave(freq)
    #             string_notes.append(wave)
    #         guitar_notes[key] = string_notes
    #     return guitar_notes

    # def get_guitar_notes_freq(self):
    #     strings_freq = {}
    #     strings = [1, 2, 3, 4, 5, 6]
    #     first_fret_freq = [82.41, 110.00, 146.83, 196.00, 246.94, 329.63]
    #     for freq in first_fret_freq:
    #         string_frequences = []
    #         for index in range(12):
    #             string_frequences.append(freq*pow(2, (index/12)))
    #         strings_freq[first_fret_freq.index(
    #             freq)+1] = string_frequences
    #     return strings_freq

    # def getself.self.self._piano_notes_freq(self):
    #     octave = ['C', 'c', 'D', 'd', 'E', 'F', 'f', 'G', 'g', 'A', 'a', 'B']
    #     base_freq = 261.63

    #     note_freqs = {octave[i]: base_freq *
    #                   pow(2, (i/12)) for i in range(len(octave))}
    #     note_freqs[''] = 0.0

    #     return note_freqs

    # def get_panflute_notes(self):
    #     frequencies = [523.25, 587.33, 659.25, 739.99,
    #                    783.99, 880, 987.77, 1046.5, 1174.66, 1318.51, 1479.98, 1567.98]
    #     flute_notes = {}
    #     for index in range(len(frequencies)):
    #         flute_notes[index] = self.get_wave(freq=frequencies[index])
    #     return flute_notes
    # def play_pan_flute(self, key):
    #     volume = 0.5
    #     note = self.pan_flute_notes[key].astype(np.float32)
    #     self.stream.write(volume*note)

    # self.audio = pyaudio.PyAudio()
    # self.dictionary_of_drums = self.generate_drums_sounds()
    # self.dictionary_of_piano = self.generate_piano_sounds()
    # self.dictionary_of_strings = self.generate_guitar_sounds()
    # for index in range(10):
    #     self.instroments_sliders[index] = getattr(
    #         self.gui, 'band_{}'.format(index+1))
    #     self.instroments_label[index] = getattr(
    #         self.gui, 'band_{}_label'.format(index+1))
    # for slider in self.instroments_sliders.values():
    #     slider.setDisabled(True)
    #     slider.setStyleSheet('selection-background-color: grey')

    # for index, slider in self.instroments_sliders.items():
    #     slider.sliderReleased.connect(
    #         lambda index=index: self.slider_gain_updated(index))

    # self.strings_freq = self.get_guitar_notes_freq()
    # self.notes_of_guitar = self.guitar_notes()

    # self.stream = self.audio.open(format=pyaudio.paInt16,
    #                               channels=1,
    #                               rate=44100,
    #                               output=True)
    # self.note_freqs = self.getself.self.self._piano_notes_freq()
    # self.notes_of_piano = self.piano_notes()
    # self.pan_flute_notes = self.get_panflute_notes()

    # def set_stream_for_instruments(self):
    #     self.stream = self.audio.open(format=pyaudio.paInt16,
    #                                   channels=1,
    #                                   rate=44100,
    #                                   output=True)
    # elif index == 1:
    #     range_min_frequency = frequency_content > 0
    #     range_max_frequency = frequency_content <= 1000
    #     # 700 - 9000 guitar
    #     # contrabasson 20 - 150
    #     slider_min_max = []
    #     for is_in_min_frequency, is_in_max_frequency in zip(range_min_frequency, range_max_frequency):
    #         slider_min_max.append(
    #             is_in_min_frequency and is_in_max_frequency)
    #     modified_signal[slider_min_max] *= self.current_slider_gain[1]

    # elif index == 2:
    #     range_min_frequency = frequency_content > 1800
    #     range_max_frequency = frequency_content <= 11000
    #     # 0 - 880 drums
    #     # piccolo 500 - 4000
    #     slider_min_max = []
    #     for is_in_min_frequency, is_in_max_frequency in zip(range_min_frequency, range_max_frequency):
    #         slider_min_max.append(
    #             is_in_min_frequency and is_in_max_frequency)
    #     modified_signal[slider_min_max] *= self.current_slider_gain[2]

    # def modify_signal(self):
    #     frequency_content = np.fft.rfftfreq(
    #         len(self.main_graph_data), d=1/self.main_graph_sample_rate)
    #     modified_signal = np.fft.rfft(self.main_graph_data)
    #     for index, slider_gain in enumerate(self.current_slider_gain):
    #         # frequency_range_min = (index + 0) * \
    #         #     self.main_graph_sample_rate / (2 * 10)
    #         # frequency_range_max = (index + 1) * \
    #         #     self.main_graph_sample_rate / (2 * 10)
    #         frequency_range_min = self.frequency_ranges_dictionary[index][0]
    #         frequency_range_max = self.frequency_ranges_dictionary[index][1]
    #         range_min_frequency = frequency_content > frequency_range_min
    #         range_max_frequency = frequency_content <= frequency_range_max
    #         slider_min_max = []
    #         for is_in_min_frequency, is_in_max_frequency in zip(range_min_frequency, range_max_frequency):
    #             slider_min_max.append(
    #                 is_in_min_frequency and is_in_max_frequency)
    #         modified_signal[slider_min_max] *= slider_gain
    #     # self.samples_after = np.ndarray(shape=(1,len(self.main_graph_data)))
    #     self.samples_after = np.fft.irfft(modified_signal)

    #     # self.main_graph_data = self.samples_after
    #     # self.plot_modified_graph()
    #     # self.plot_spectrogram(self.samples_after[int((len(self.main_graph_data)/10)):int(
    #     # (2*(len(self.main_graph_data)/10)))], self.main_graph_sample_rate)
    #     self.player.stop()
    #     time = int(self.x_range1[0]*10*self.main_graph_sample_rate)
    #     # self.now = datetime.now()
    #     # self.now = f'{self.now:%Y-%m-%d %H-%M-%S.%f %p}'
    #     # # output_path = "D:/SBME_3/1st_term/DSP/tasks/task3/modified_files/Output.wav"
    #     # # if os.path.isfile(output_path):
    #     # #     os.remove(output_path)
    #     # wavfile.write(
    #     #     f"D:/SBME_3/1st_term/files/{self.now}Output.wav", self.main_graph_sample_rate, np.array(self.samples_after[int(time):]).astype(np.int16))
    #     # # self.player.setMedia(None)
    #     self.plot_modified_graph()
    #     # self.player.setMedia(QMediaContent(
    #     #     QUrl.fromLocalFile(f"D:/SBME_3/1st_term/files/{self.now}Output.wav")))
    #     # self.player.play()
    #     self.stream = self.audio.open(format=pyaudio.paInt16,
    #                                   channels=1,
    #                                   rate=self.main_graph_sample_rate,
    #                                   output=True)
    #     self.samples_after = np.array(self.samples_after)
    #     self.samples_after = self.samples_after.astype(np.int16)
    #     self.stream.write(1*self.samples_after)
    # def plot_modified_graph(self):
    #     self.data_length = int(len(self.samples_after)/10)
    #     self.gui.main_graph.setYRange(
    #         (min(self.samples_after)-0.5), (max(self.samples_after)+0.5))
    #     # self.gui.main_graph.setXRange(0, .05)
    #     # print(len(self.main_graph_data))
    #     self.gui.main_graph.plotItem.clear()
    #     self.x_range1[0] = 0
    #     self.x_range1[1] = 1
    #     self.gui.main_graph.setXRange(self.x_range1[0], self.x_range1[1])
    #     self.gui.main_graph.plotItem.plot(
    #         self.main_graph_time[:self.time_length], self.samples_after[:self.data_length], pen=self.pen1)
