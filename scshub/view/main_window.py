import os
import logging

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, QEventLoop, QTimer
from PyQt5.QtWidgets import QApplication

from qfluentwidgets import (
    NavigationItemPosition,
    MSFluentWindow,
    SplashScreen,
    FluentIcon,
    setFont,
    toggleTheme,
)

from .interface.home_interface import HomeInterface
from .interface.scs_interface import ScsInterface
from .interface.pix_interface import PixInterface
from .interface.sxc_interface import SxcInterface
from .interface.tobj_interface import TobjInterface
from .interface.def_interface import DefInterface
from .interface.setting_interface import SettingInterface

from ..common.tool import ScsHubIcon, signal_bus
from ..common.config import cfg
from ..common import resource
from ..common.info import (
    PIX_CONVERTER_PATH,
    SCS_TOOL_PATH,
    SXC_UNZIP,
    MAIN_LOG,
)


logging.basicConfig(
    level=logging.INFO,
    filename=MAIN_LOG,
    filemode="w",
    encoding="utf-8",
    format="%(levelname)s %(name)s (%(asctime)s): %(message)s",
    datefmt="%Y/%m/%d|%H:%M:%S",
)

logger = logging.getLogger("SCSHub")


class MainWindow(MSFluentWindow):

    def __init__(self):
        super().__init__()

        logger.info("App Started")
        logger.info(f'Current working directory: "{os.getcwd()}"')

        self.init_window()
        self.init_navigation()
        self.tools_exist()
        self.signal_bus()

    def init_window(self):

        self.resize(1143, 780)
        # self.resize(1143, 600)
        self.setMinimumSize(1143, 450)
        self.setWindowIcon(QIcon(":/vector/logo_color.svg"))
        self.setWindowTitle("SCS Hub")
        self.setMicaEffectEnabled(cfg.get(cfg.mica_effect))

        # center window
        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        # splash screen
        self.splash_screen = SplashScreen(":/vector/logo_splash.svg", self)
        self.splash_screen.setIconSize(QSize(350, 350))
        self.splash_screen.raise_()
        self.show()
        loop = QEventLoop(self)
        QTimer.singleShot(350, loop.quit)
        loop.exec()
        self.splash_screen.finish()

    def init_navigation(self):

        self.home_interface = HomeInterface()
        self.scs_interface = ScsInterface()
        self.pix_interface = PixInterface()
        self.sxc_interface = SxcInterface()
        self.tobj_interface = TobjInterface()
        self.def_interface = DefInterface()
        self.setting_interface = SettingInterface()

        # top
        self.addSubInterface(
            interface=self.home_interface,
            icon=FluentIcon.HOME,
            text=self.tr("Home"),
            selectedIcon=FluentIcon.HOME_FILL,
            position=NavigationItemPosition.TOP,
        )

        # scroll
        self.addSubInterface(
            interface=self.scs_interface,
            icon=ScsHubIcon.SCS_I,
            text=self.tr("SCS"),
            selectedIcon=ScsHubIcon.SCS_FILL,
            position=NavigationItemPosition.SCROLL,
        )
        self.addSubInterface(
            interface=self.pix_interface,
            icon=ScsHubIcon.PIX_I,
            text=self.tr("PIX"),
            selectedIcon=ScsHubIcon.PIX_FILL,
            position=NavigationItemPosition.SCROLL,
        )
        self.addSubInterface(
            interface=self.sxc_interface,
            icon=ScsHubIcon.SXC_I,
            text=self.tr("SXC"),
            selectedIcon=ScsHubIcon.SXC_FILL,
            position=NavigationItemPosition.SCROLL,
        )
        self.addSubInterface(
            interface=self.tobj_interface,
            icon=ScsHubIcon.TOBJ_I,
            text=self.tr("TOBJ"),
            selectedIcon=ScsHubIcon.TOBJ_FILL,
            position=NavigationItemPosition.SCROLL,
        )
        self.addSubInterface(
            interface=self.def_interface,
            icon=ScsHubIcon.DEF_I,
            text=self.tr("DEF"),
            selectedIcon=ScsHubIcon.DEF_FILL,
            position=NavigationItemPosition.SCROLL,
        )

        # bottom
        self.navigationInterface.addItem(
            routeKey="theme",
            icon=FluentIcon.CONSTRACT,
            text=self.tr("Theme"),
            onClick=toggleTheme,
            selectable=False,
            position=NavigationItemPosition.BOTTOM,
        )
        self.addSubInterface(
            interface=self.setting_interface,
            icon=FluentIcon.SETTING,
            text=self.tr("Settings"),
            position=NavigationItemPosition.BOTTOM,
        )

        self.navigationInterface.setCurrentItem(self.home_interface.objectName())
        self.navigationInterface.setSelectedTextVisible(False)
        setFont(self.navigationInterface, 12)

    def tools_exist(self):

        # scs
        if os.path.isfile(SCS_TOOL_PATH):
            signal_bus.scs_exist.emit(True)
        else:
            signal_bus.scs_exist.emit(False)

        # pix
        if os.path.isfile(PIX_CONVERTER_PATH):
            signal_bus.pix_exist.emit(True)
        else:
            signal_bus.pix_exist.emit(False)

        # sxc
        if os.path.isdir(SXC_UNZIP):
            signal_bus.sxc_exist.emit(True)
        else:
            signal_bus.sxc_exist.emit(False)

    def switch_interface(self, route_key):

        match route_key:
            case "scs_interface":
                self.stackedWidget.setCurrentWidget(self.scs_interface, popOut=False)

            case "pix_interface":
                self.stackedWidget.setCurrentWidget(self.pix_interface, popOut=False)

            case "sxc_interface":
                self.stackedWidget.setCurrentWidget(self.sxc_interface, popOut=False)

            case "tobj_interface":
                self.stackedWidget.setCurrentWidget(self.tobj_interface, popOut=False)

    def resizeEvent(self, e):
        super().resizeEvent(e)

        signal_bus.window_width.emit(e.size().width())

    def signal_bus(self):

        signal_bus.mica_enabled.connect(self.setMicaEffectEnabled)
        signal_bus.switch_interface.connect(self.switch_interface)
