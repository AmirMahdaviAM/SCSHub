from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout

from ..widget.scs_extractor_wdiget import ScsExtractorWidget
from ..widget.scs_packer_widget import ScsPackerWidget
from ...common.tool import signal_bus


class ScsInterface(QWidget):

    def __init__(self):
        super().__init__()

        self.setObjectName("scs_interface")

        self.main_lyt = QVBoxLayout(self)
        self.main_lyt.setContentsMargins(36, 36, 36, 36)
        self.main_lyt.setSpacing(20)
        self.main_lyt.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scs_extractor = ScsExtractorWidget(self)
        self.scs_packer = ScsPackerWidget(self)

        self.main_lyt.addWidget(self.scs_extractor)
        self.main_lyt.addWidget(self.scs_packer)

        signal_bus.window_width.connect(self.edge_spacer)

    def edge_spacer(self, width):

        spacer_width = int((width - 1070) / 2)
        self.main_lyt.setContentsMargins(spacer_width, 36, spacer_width, 36)
