from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget, QHBoxLayout

from qfluentwidgets import (IconWidget, TextWrap, SingleDirectionScrollArea, FlowLayout, CardWidget,
                            ElevatedCardWidget , FluentIcon)

from .tool import StyleSheet, signalBus


class LinkCard(ElevatedCardWidget):

    def __init__(self, icon, title, content, url, parent=None):
        super().__init__(parent=parent)
        self.url = QUrl(url)
        self.setFixedSize(198, 220)
        self.iconWidget = IconWidget(icon, self)
        self.titleLabel = QLabel(title, self)
        self.contentLabel = QLabel(TextWrap.wrap(content, 20, False)[0], self)
        self.urlWidget = IconWidget(FluentIcon.LINK, self)

        self.__initWidget()

    def __initWidget(self):
        self.setCursor(Qt.PointingHandCursor)
        
        self.iconWidget.setFixedSize(54, 54)
        self.urlWidget.setFixedSize(16, 16)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(24, 24, 24, 24)
        self.vBoxLayout.addWidget(self.iconWidget)
        self.vBoxLayout.addSpacing(16)
        self.vBoxLayout.addWidget(self.titleLabel)
        self.vBoxLayout.addSpacing(8)
        self.vBoxLayout.addWidget(self.contentLabel)
        self.vBoxLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.urlWidget.move(170, 192)

        self.titleLabel.setObjectName('titleLabel')
        self.contentLabel.setObjectName('contentLabel')

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        QDesktopServices.openUrl(self.url)

class LinkCardView(SingleDirectionScrollArea):

    def __init__(self, parent=None):
        super().__init__(parent, Qt.Horizontal)
        self.view = QWidget(self)
        self.hBoxLayout = QHBoxLayout(self.view)

        self.hBoxLayout.setContentsMargins(30, 10, 30, 10)
        self.hBoxLayout.setSpacing(16)
        self.hBoxLayout.setAlignment(Qt.AlignLeft)

        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.view.setObjectName('view')
        StyleSheet.LINK_CARD.apply(self)

    def addCard(self, icon, title, content, url):
        """ add link card """
        card = LinkCard(icon, title, content, url, self.view)
        self.hBoxLayout.addWidget(card, 0, Qt.AlignLeft)


class InterfaceCard(CardWidget):

    def __init__(self, icon, title, content, routeKey, parent=None):
        super().__init__(parent=parent)
        self.routekey = routeKey

        self.setCursor(Qt.PointingHandCursor)

        self.iconWidget = IconWidget(icon, self)
        self.titleLabel = QLabel(title, self)
        self.contentLabel = QLabel(TextWrap.wrap(content, 45, False)[0], self)

        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()

        self.setFixedSize(360, 90)
        self.iconWidget.setFixedSize(48, 48)

        self.hBoxLayout.setSpacing(28)
        self.hBoxLayout.setContentsMargins(20, 0, 0, 0)
        self.vBoxLayout.setSpacing(2)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setAlignment(Qt.AlignVCenter)

        self.hBoxLayout.setAlignment(Qt.AlignVCenter)
        self.hBoxLayout.addWidget(self.iconWidget)
        self.hBoxLayout.addLayout(self.vBoxLayout)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(self.titleLabel)
        self.vBoxLayout.addWidget(self.contentLabel)
        self.vBoxLayout.addStretch(1)

        self.titleLabel.setObjectName('titleLabel')
        self.contentLabel.setObjectName('contentLabel')

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        signalBus.switchToInterface.emit(self.routekey)

class InterfaceCardView(QWidget):

    def __init__(self, title: str, parent=None):
        super().__init__(parent=parent)
        self.titleLabel = QLabel(title, self)
        self.vBoxLayout = QVBoxLayout(self)
        self.flowLayout = FlowLayout()

        self.vBoxLayout.setContentsMargins(30, 5, 30, 5)
        self.vBoxLayout.setSpacing(10)
        self.flowLayout.setContentsMargins(0, 0, 0, 0)
        self.flowLayout.setHorizontalSpacing(12)
        self.flowLayout.setVerticalSpacing(12)

        self.vBoxLayout.addWidget(self.titleLabel)
        self.vBoxLayout.addLayout(self.flowLayout, 1)

        self.titleLabel.setObjectName('viewTitleLabel')
        StyleSheet.SAMPLE_CARD.apply(self)

    def addSampleCard(self, icon, title, content, routeKey):
        """ add sample card """
        card = InterfaceCard(icon, title, content, routeKey, self)
        self.flowLayout.addWidget(card)