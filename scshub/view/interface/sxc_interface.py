from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout

from qfluentwidgets import ScrollArea

from ..widget.sxc_finder_widget import SxcFinderWidget
from ..widget.sxc_packer_widget import SxcPackerWidget
from ...common.tool import signal_bus


class SxcInterface(ScrollArea):

    def __init__(self):
        super().__init__()

        self.setObjectName("sxc_interface")

        self.main_widget = QWidget(self)

        self.main_lyt = QVBoxLayout(self.main_widget)
        self.main_lyt.setContentsMargins(0, 0, 0, 0)
        self.main_lyt.setSpacing(20)
        self.main_lyt.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.sxc_finder = SxcFinderWidget(self)
        self.sxc_packer = SxcPackerWidget(self)

        self.main_lyt.addWidget(self.sxc_finder)
        self.main_lyt.addWidget(self.sxc_packer)

        self.setViewportMargins(36, 36, 36, 36)
        self.setWidget(self.main_widget)
        self.setWidgetResizable(True)
        self.setStyleSheet("border: none; background: transparent;")

        signal_bus.window_width.connect(self.edge_spacer)

    def edge_spacer(self, width):

        spacer_width = int((width - 1070) / 2)
        self.setViewportMargins(spacer_width, 36, spacer_width, 36)
