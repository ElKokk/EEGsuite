# ui.py
"""
Defines the UI control panel for EEG plot adjustments and filter settings.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QCheckBox
)


class GraphUI:
    def __init__(self, filters):
        self.filters = filters
        self.control_container = QWidget()
        self.control_vbox = QVBoxLayout()

        self._init_y_range_controls()
        self._init_psd_controls()

        self.control_vbox.addLayout(self.filters.get_filter_layout())
        self.control_container.setLayout(self.control_vbox)
        self.control_container.setMaximumHeight(500)

    def _init_y_range_controls(self):
        self.y_min_input = QLineEdit("-100")
        self.y_max_input = QLineEdit("100")
        self.y_auto_checkbox = QCheckBox("Auto")
        self.y_auto_checkbox.setChecked(False)
        self.y_apply_btn = QPushButton("Apply Y Range")

        y_layout = QHBoxLayout()
        y_layout.addWidget(QLabel("Y Min:"))
        y_layout.addWidget(self.y_min_input)
        y_layout.addWidget(QLabel("Y Max:"))
        y_layout.addWidget(self.y_max_input)
        y_layout.addWidget(self.y_auto_checkbox)
        y_layout.addWidget(self.y_apply_btn)

        self.control_vbox.addLayout(y_layout)

    def _init_psd_controls(self):
        self.psd_y_min_input = QLineEdit("-3")
        self.psd_y_max_input = QLineEdit("3")
        self.psd_y_auto_checkbox = QCheckBox("Auto")
        self.psd_y_auto_checkbox.setChecked(True)
        self.psd_y_apply_btn = QPushButton("Apply PSD Y Range")

        psd_layout = QHBoxLayout()
        psd_layout.addWidget(QLabel("PSD Y Min:"))
        psd_layout.addWidget(self.psd_y_min_input)
        psd_layout.addWidget(QLabel("PSD Y Max:"))
        psd_layout.addWidget(self.psd_y_max_input)
        psd_layout.addWidget(self.psd_y_auto_checkbox)
        psd_layout.addWidget(self.psd_y_apply_btn)

        self.control_vbox.addLayout(psd_layout)
