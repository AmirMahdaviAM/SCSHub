from PyQt5.QtCore import Qt, QUrl, QRectF, QEasingCurve
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget, QHBoxLayout
from PyQt5.QtGui import (
    QDesktopServices,
    QLinearGradient,
    QPainterPath,
    QPainter,
    QPixmap,
    QColor,
    QBrush,
    QImage,
    QFont,
)
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGraphicsDropShadowEffect

from qfluentwidgets import (
    SingleDirectionScrollArea,
    ElevatedCardWidget,
    IconWidget,
    FlowLayout,
    CardWidget,
    FluentIcon,
    TextWrap,
    BodyLabel,
    setFont,
    themeColor,
    isDarkTheme,
)

from .tool import ScsHubStyleSheet, ScsHubIcon, signal_bus
from .info import SCSHUB_GITHUB_URL, SCSHUB_FORUM_URL
from .config import cfg


class BannerWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setFixedHeight(330)

        self.main_lyt = QVBoxLayout(self)
        self.main_lyt.setContentsMargins(0, 28, 0, 0)
        self.main_lyt.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        shadow_effect = QGraphicsDropShadowEffect(self)
        shadow_effect.setBlurRadius(15)
        shadow_effect.setOffset(0, 4)

        self.home_label = BodyLabel(self.tr("SCS Hub"), self)
        self.home_label.setContentsMargins(36, 0, 0, 0)
        self.home_label.setGraphicsEffect(shadow_effect)
        setFont(self.home_label, 42, QFont.DemiBold)

        self.link_card_view = LinkCardView(self)
        self.link_card_view.add_card(
            ScsHubIcon.SCS,
            self.tr("SCS Forum"),
            self.tr("Forum topic and all information about SCS Hub"),
            SCSHUB_FORUM_URL,
        )
        self.link_card_view.add_card(
            FluentIcon.GITHUB,
            self.tr("GitHub Repo"),
            self.tr("Repository with source code and details"),
            SCSHUB_GITHUB_URL,
        )

        self.main_lyt.addWidget(self.home_label)
        self.main_lyt.setSpacing(0)
        self.main_lyt.addWidget(self.link_card_view, 1, Qt.AlignBottom)

        # set banner colorizer to theme signals
        cfg.themeColorChanged.connect(self.banner_colorizer)
        cfg.themeChanged.connect(self.banner_colorizer)
        signal_bus.colorize.connect(self.banner_colorizer)

        # on app initialize, run banner colorizer if
        # config value is true
        if cfg.colorize.value:
            self.banner_colorizer(themeColor())

    def banner_colorizer(self, color):

        # run change color loop only if config value is true
        if cfg.colorize.value:
            item = QImage(":/image/banner_overlay_white.png")
            self.item = item.scaled(1070, 330, Qt.KeepAspectRatio)

            # because this slot connected to two signal and
            # they have diffrent value type, use preferd one
            # if not available by sender
            if not isinstance(color, QColor):
                color = themeColor()

            # change pixel color to themeColor color and
            # preserve default alpha value
            for y in range(self.item.height()):
                for x in range(self.item.width()):
                    pcolor = self.item.pixelColor(x, y)
                    if pcolor.alpha() > 0:
                        n_color = color
                        n_color.setAlpha(pcolor.alpha())
                        self.item.setPixelColor(x, y, n_color)

    def paintEvent(self, e):
        super().paintEvent(e)

        painter = QPainter(self)
        painter.setRenderHints(QPainter.SmoothPixmapTransform | QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        w, h = self.width(), self.height()
        path = QPainterPath()
        path.setFillRule(Qt.WindingFill)
        path.addRoundedRect(QRectF(0, 0, w, h), 10, 10)
        path.addRect(QRectF(0, h - 50, 50, 50))
        path.addRect(QRectF(w - 50, 0, 50, 50))
        path.addRect(QRectF(w - 50, h - 50, 50, 50))
        path = path.simplified()

        gradient = QLinearGradient(0, 0, 0, h)

        if isDarkTheme():
            gradient.setColorAt(0, QColor(0, 0, 0, 100))
            grid = QPixmap(":/image/banner_background_white.png")
            item = QImage(":/image/banner_overlay_white.png")

        else:
            gradient.setColorAt(0, QColor(0, 0, 0, 30))
            grid = QPixmap(":/image/banner_background_black.png")
            item = QImage(":/image/banner_overlay_black.png")

        gradient.setColorAt(1, QColor(0, 0, 0, 0))
        item = item.scaled(self.width(), self.height(), Qt.KeepAspectRatio)
        grid = grid.scaled(w, h, Qt.KeepAspectRatio)

        painter.fillPath(path, QBrush(gradient))
        painter.fillPath(path, QBrush(grid))

        # use static or dynamic image based on config value
        if cfg.colorize.value:
            painter.fillPath(path, QBrush(self.item))
        else:
            painter.fillPath(path, QBrush(item))


class LinkCard(ElevatedCardWidget):

    def __init__(self, icon, title, content, url, parent=None):
        super().__init__(parent=parent)

        self.url = QUrl(url)
        self.setFixedSize(198, 220)
        self.icon_widget = IconWidget(icon, self)
        self.title_label = QLabel(title, self)
        self.content_label = QLabel(TextWrap.wrap(content, 20, False)[0], self)
        self.url_widget = IconWidget(FluentIcon.LINK, self)

        self.setCursor(Qt.PointingHandCursor)

        self.icon_widget.setFixedSize(54, 54)
        self.url_widget.setFixedSize(16, 16)

        self.v_box_lyt = QVBoxLayout(self)
        self.v_box_lyt.setSpacing(0)
        self.v_box_lyt.setContentsMargins(24, 24, 24, 24)
        self.v_box_lyt.addWidget(self.icon_widget)
        self.v_box_lyt.addSpacing(16)
        self.v_box_lyt.addWidget(self.title_label)
        self.v_box_lyt.addSpacing(8)
        self.v_box_lyt.addWidget(self.content_label)
        self.v_box_lyt.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.url_widget.move(170, 192)

        self.title_label.setObjectName("title_label")
        self.content_label.setObjectName("content_label")

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)

        QDesktopServices.openUrl(self.url)


class LinkCardView(SingleDirectionScrollArea):

    def __init__(self, parent=None):
        super().__init__(parent, Qt.Horizontal)

        self.view = QWidget(self)
        self.h_box_lyt = QHBoxLayout(self.view)

        self.h_box_lyt.setContentsMargins(36, 10, 36, 10)
        self.h_box_lyt.setSpacing(16)
        self.h_box_lyt.setAlignment(Qt.AlignLeft)

        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.view.setObjectName("view")
        ScsHubStyleSheet.LINK_CARD.apply(self)

    def add_card(self, icon, title, content, url):

        card = LinkCard(icon, title, content, url, self.view)
        self.h_box_lyt.addWidget(card, 0, Qt.AlignLeft)


class InterfaceCard(CardWidget):

    def __init__(self, icon, title, content, route_key, parent=None):
        super().__init__(parent=parent)

        self.route_key = route_key

        self.setCursor(Qt.PointingHandCursor)

        self.icon_widget = IconWidget(icon, self)
        self.title_label = QLabel(title, self)
        self.content_label = QLabel(TextWrap.wrap(content, 45, False)[0], self)

        self.h_box_lyt = QHBoxLayout(self)
        self.v_box_lyt = QVBoxLayout()

        self.setFixedSize(360, 90)
        self.icon_widget.setFixedSize(48, 48)

        self.h_box_lyt.setSpacing(28)
        self.h_box_lyt.setContentsMargins(20, 0, 0, 0)
        self.v_box_lyt.setSpacing(2)
        self.v_box_lyt.setContentsMargins(0, 0, 0, 0)
        self.v_box_lyt.setAlignment(Qt.AlignVCenter)

        self.h_box_lyt.setAlignment(Qt.AlignVCenter)
        self.h_box_lyt.addWidget(self.icon_widget)
        self.h_box_lyt.addLayout(self.v_box_lyt)
        self.v_box_lyt.addStretch(1)
        self.v_box_lyt.addWidget(self.title_label)
        self.v_box_lyt.addWidget(self.content_label)
        self.v_box_lyt.addStretch(1)

        self.title_label.setObjectName("title_label")
        self.content_label.setObjectName("content_label")

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)

        signal_bus.switch_interface.emit(self.route_key)


class InterfaceCardView(QWidget):

    def __init__(self, title: str, parent=None):
        super().__init__(parent=parent)

        self.title_label = QLabel(title, self)
        self.v_box_lyt = QVBoxLayout(self)
        self.flow_lyt = FlowLayout(needAni=True)
        self.flow_lyt.ease = QEasingCurve.OutQuad

        self.v_box_lyt.setContentsMargins(36, 5, 36, 5)
        self.v_box_lyt.setSpacing(10)
        self.flow_lyt.setContentsMargins(0, 0, 0, 0)
        self.flow_lyt.setHorizontalSpacing(12)
        self.flow_lyt.setVerticalSpacing(12)

        self.v_box_lyt.addWidget(self.title_label)
        self.v_box_lyt.addLayout(self.flow_lyt, 1)

        self.title_label.setObjectName("view_title_label")
        ScsHubStyleSheet.INTERFACE_CARD.apply(self)

    def add_card(self, icon, title, content, route_key):

        card = InterfaceCard(icon, title, content, route_key, self)
        self.flow_lyt.addWidget(card)
