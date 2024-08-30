from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout

from qfluentwidgets import ScrollArea

from ...common.component import InterfaceCardView, BannerWidget
from ...common.tool import ScsHubIcon


class HomeInterface(ScrollArea):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setObjectName("home_interface")

        self.view = QWidget(self)

        self.setWidget(self.view)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)
        self.setStyleSheet("border: none; background-color: transparent;")

        self.banner = BannerWidget(self)

        self.main_lyt = QVBoxLayout(self.view)
        self.main_lyt.setContentsMargins(0, 0, 0, 0)
        self.main_lyt.setSpacing(40)
        self.main_lyt.addWidget(self.banner)

        interface_card_view = InterfaceCardView(self.tr("Tools"), self.view)

        interface_card_view.add_card(
            ScsHubIcon.SCS_I,
            self.tr("SCS"),
            self.tr("Official extractor and packer"),
            "scs_interface",
        )
        interface_card_view.add_card(
            ScsHubIcon.PIX_I,
            self.tr("PIX"),
            self.tr("Extractor and converter"),
            "pix_interface",
        )
        interface_card_view.add_card(
            ScsHubIcon.SXC_I,
            self.tr("SXC"),
            self.tr("Advanced extractor, finder and packer"),
            "sxc_interface",
        )
        interface_card_view.add_card(
            ScsHubIcon.TOBJ_I,
            self.tr("TOBJ"),
            self.tr("Full TOBJ editor"),
            "tobj_interface",
        )
        interface_card_view.add_card(
            ScsHubIcon.DEF_I,
            self.tr("DEF"),
            self.tr("Accessory def creator"),
            "def_interface",
        )

        self.main_lyt.addWidget(interface_card_view)
