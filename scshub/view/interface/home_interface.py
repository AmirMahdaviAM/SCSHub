from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPixmap, QPainter, QColor, QBrush, QPainterPath, QLinearGradient
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

from qfluentwidgets import ScrollArea, FluentIcon, isDarkTheme

from ...common.card import LinkCardView, InterfaceCardView
from ...common.tool import ScsHubIcon, StyleSheet, SCSHUB_GITHUB_URL, SCSHUB_FORUM_URL


class BannerWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setFixedHeight(330)

        self.banner = QPixmap(":/SCSHub/image/header.png")

        self.homeLabel = QLabel(self.tr("SCS Hub"), self)
        self.homeLabel.setObjectName("homeLabel")

        self.linkCardView = LinkCardView(self)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(0, 20, 0, 0)
        self.vBoxLayout.addWidget(self.homeLabel)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.addWidget(self.linkCardView, 1, Qt.AlignBottom)
        self.vBoxLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.linkCardView.addCard(
            ScsHubIcon.SCS,
            self.tr("SCS Forum"),
            self.tr("Forum topic and all information about SCS Hub"),
            SCSHUB_FORUM_URL,
        )
        self.linkCardView.addCard(
            FluentIcon.GITHUB,
            self.tr("GitHub Repo"),
            self.tr("Repository with source code and details"),
            SCSHUB_GITHUB_URL,
        )

    def paintEvent(self, e):
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHints(QPainter.SmoothPixmapTransform | QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        path = QPainterPath()
        path.setFillRule(Qt.WindingFill)
        w, h = self.width(), self.height()
        path.addRoundedRect(QRectF(0, 0, w, h), 10, 10)
        path.addRect(QRectF(0, h - 50, 50, 50))
        path.addRect(QRectF(w - 50, 0, 50, 50))
        path.addRect(QRectF(w - 50, h - 50, 50, 50))
        path = path.simplified()

        # init linear gradient effect
        gradient = QLinearGradient(0, 0, 0, h)

        # draw background color
        if not isDarkTheme():
            gradient.setColorAt(0, QColor(207, 216, 228, 255))
            gradient.setColorAt(1, QColor(207, 216, 228, 0))
        else:
            gradient.setColorAt(0, QColor(0, 0, 0, 125))
            gradient.setColorAt(1, QColor(0, 0, 0, 0))

        painter.fillPath(path, QBrush(gradient))

        # draw banner image
        pixmap = self.banner.scaled(self.size(), transformMode=Qt.SmoothTransformation)
        painter.fillPath(path, QBrush(pixmap))


class HomeInterface(ScrollArea):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setObjectName("homeInterface")

        self.view = QWidget(self)
        self.view.setObjectName("view")

        self.setWidget(self.view)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)

        self.banner = BannerWidget(self)

        self.vBoxLayout = QVBoxLayout(self.view)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(40)
        self.vBoxLayout.addWidget(self.banner)

        StyleSheet.HOME_INTERFACE.apply(self)

        appsView = InterfaceCardView(self.tr("Apps"), self.view)

        appsView.addSampleCard(
            ScsHubIcon.PIX_CONVERTER,
            self.tr("Converter PIX"),
            self.tr("Extractor and converter (*.PMX to *.PIX)"),
            "pixInterface",
        )
        appsView.addSampleCard(
            ScsHubIcon.SCS_EXTRACTOR,
            self.tr("SCS Extractor"),
            self.tr("Extract whole *.scs archive file without conversion"),
            "scsInterface",
        )
        appsView.addSampleCard(
            FluentIcon.SETTING,
            self.tr("Settings"),
            self.tr("Place to configure and personlize app"),
            "settingInterface",
        )

        self.vBoxLayout.addWidget(appsView)
