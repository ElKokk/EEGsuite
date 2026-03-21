# filters.py
"""
Filter classes and logic for EEG signal processing.
"""
import numpy as np
from PyQt5.QtWidgets import QCheckBox, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit
from brainflow.data_filter import DataFilter, FilterTypes, DetrendOperations
from scipy.signal import butter, lfilter, lfilter_zi, iirnotch, filtfilt


class RealtimeNotchFilter:
    def __init__(self, f0=50.0, Q=100.0, fs=512.0):
        self.b, self.a = iirnotch(f0, Q, fs)
        self.zi = lfilter_zi(self.b, self.a) * 0

    def filter_sample(self, sample):
        filtered, self.zi = lfilter(self.b, self.a, [sample], zi=self.zi)
        return filtered[0]

    def filter(self, chunk):
        filtered, self.zi = lfilter(self.b, self.a, chunk, zi=self.zi)
        return filtered


class RealtimeHighPass:
    def __init__(self, cutoff, fs, order=4):
        nyq = 0.5 * fs
        self.b, self.a = butter(order, cutoff / nyq, btype='high')
        self.zi = lfilter_zi(self.b, self.a) * 0

    def filter(self, sample):
        filtered, self.zi = lfilter(self.b, self.a, [sample], zi=self.zi)
        return filtered[0]

    def filter_chunk(self, samples):
        filtered, self.zi = lfilter(self.b, self.a, samples, zi=self.zi)
        return filtered


class GraphFilters:
    def __init__(self, sampling_rate, exg_channels):
        self.sampling_rate = sampling_rate
        self.exg_channels = exg_channels

        self.filter_enable = {
            'bandpass': QCheckBox("Bandpass (3–333 Hz)"),
            'notch50x': QCheckBox("Notch 50+H Hz"),
            'notchff50': QCheckBox("Notch ff 50 Hz"),
            'detrend': QCheckBox("Detrend"),
            'rthp': QCheckBox("RTHP1Hz"),
            'notchrt50': QCheckBox("Notch rt 50 Hz")
        }

        self.filter_enable['bandpass'].setChecked(False)
        self.filter_enable['detrend'].setChecked(True)
        self.filter_enable['rthp'].setChecked(True)

        self.bp_low_input = QLineEdit("3.0")
        self.bp_high_input = QLineEdit("333.0")

        self.rthp_filters = [RealtimeHighPass(1.0, sampling_rate) for _ in exg_channels]
        self.rtnotch_filters = [RealtimeNotchFilter(50.0, 30.0, sampling_rate) for _ in exg_channels]

    def get_filter_layout(self):
        vlayout = QVBoxLayout()
        h1 = QHBoxLayout()
        h1.addWidget(QLabel("Bandpass:"))
        h1.addWidget(QLabel("Low"))
        h1.addWidget(self.bp_low_input)
        h1.addWidget(QLabel("High"))
        h1.addWidget(self.bp_high_input)
        h1.addWidget(self.filter_enable['bandpass'])
        h1.addWidget(self.filter_enable['detrend'])

        h2 = QHBoxLayout()
        h2.addWidget(self.filter_enable['notch50x'])
        h2.addWidget(self.filter_enable['notchff50'])
        h2.addWidget(self.filter_enable['notchrt50'])
        h2.addWidget(self.filter_enable['rthp'])

        vlayout.addLayout(h1)
        vlayout.addLayout(h2)
        return vlayout

    def apply_filters(self, sig, count):
        filtered_sig = sig.copy()

        if self.filter_enable['detrend'].isChecked():
            DataFilter.detrend(filtered_sig, DetrendOperations.LINEAR.value)

        if self.filter_enable['bandpass'].isChecked():
            try:
                low = float(self.bp_low_input.text())
                high = float(self.bp_high_input.text())
                DataFilter.perform_bandpass(
                    filtered_sig, self.sampling_rate, low, high,
                    2, FilterTypes.BUTTERWORTH_ZERO_PHASE, 0
                )
            except ValueError:
                print("Invalid bandpass cutoff values.")

        if self.filter_enable['notch50x'].isChecked():
            for freq in [50, 100, 150, 200, 250]:
                DataFilter.perform_bandstop(
                    filtered_sig, self.sampling_rate,
                    freq - 2.0, freq + 2.0,
                    2, FilterTypes.BUTTERWORTH_ZERO_PHASE, 0
                )

        if self.filter_enable['notchff50'].isChecked():
            b, a = iirnotch(50.0, 50.0, self.sampling_rate)
            filtered_sig = filtfilt(b, a, filtered_sig)

        if self.filter_enable['rthp'].isChecked():
            filtered_sig[:] = [self.rthp_filters[count].filter(s) for s in filtered_sig]

        if self.filter_enable['notchrt50'].isChecked():
            filtered_sig[:] = [self.rtnotch_filters[count].filter_sample(s) for s in filtered_sig]

        return filtered_sig
