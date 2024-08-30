from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout

from qfluentwidgets import SegmentedWidget, PopUpAniStackedWidget

from ..widget.pix_converter_widget import PixConverterWidget
from ..widget.pix_finder_widget import PixFinderWidget
from ..widget.pix_hasher_widget import PixHasherWidget

from ...common.tool import signal_bus


class PixInterface(QWidget):

    def __init__(self):
        super().__init__()

        self.setObjectName("pix_interface")

        self.main_lyt = QVBoxLayout(self)
        self.main_lyt.setContentsMargins(36, 36, 36, 36)
        self.main_lyt.setSpacing(10)

        self.tab_lyt = QHBoxLayout()
        self.tab_lyt.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.tab = SegmentedWidget(self)
        self.tab.setFixedWidth(500)

        self.tab_lyt.addWidget(self.tab)

        self.stacked_widget = PopUpAniStackedWidget(self)

        self.pix_converter = PixConverterWidget(self)
        self.pix_finder = PixFinderWidget(self)
        self.pix_hasher = PixHasherWidget(self)

        self.add_widget(self.pix_converter, "pix_converter", self.tr("Converter"))
        self.add_widget(self.pix_finder, "pix_finder", self.tr("Anim Finder"))
        self.add_widget(self.pix_hasher, "pix_hasher", self.tr("Hasher"))

        self.main_lyt.addLayout(self.tab_lyt)
        self.main_lyt.addWidget(self.stacked_widget)

        self.stacked_widget.setCurrentWidget(self.pix_converter)
        self.tab.setCurrentItem("pix_converter")

        signal_bus.window_width.connect(self.edge_spacer)

    def edge_spacer(self, width):

        spacer_width = int((width - 1070) / 2)
        self.main_lyt.setContentsMargins(spacer_width, 36, spacer_width, 36)

    def add_widget(self, widget, route_key, text):
        self.stacked_widget.addWidget(widget)
        self.tab.addItem(
            routeKey=route_key,
            text=text,
            onClick=lambda: self.stacked_widget.setCurrentWidget(widget),
        )
