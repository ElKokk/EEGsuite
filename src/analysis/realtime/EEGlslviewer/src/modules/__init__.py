from PyQt5.QtWidgets import QWidget

class PlotManager:
    def __init__(self, ui, board_shim, filters, exg_channels, virtual_index, sampling_rate, main_widget):
        self.main_widget = QWidget()
        self._init_plot()
