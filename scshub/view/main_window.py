import os, logging

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, QEventLoop, QTimer
from PyQt5.QtWidgets import QApplication

from qfluentwidgets import NavigationItemPosition, MSFluentWindow, SplashScreen, FluentIcon, toggleTheme

from .interface.home_interface import HomeInterface
from .interface.pix_interface import PixInterface
from .interface.scs_interface import ScsInterface
from .interface.setting_interface import SettingInterface

from ..common import resource
from ..common.config import cfg
from ..common.tool import ScsHubIcon, signalBus


# logging config
logging.basicConfig(level=logging.INFO, filename="scshub.log", filemode="w", encoding="utf-8",
                    format="%(levelname)s %(name)s - (%(asctime)s):[Line:%(lineno)s|%(filename)s] %(message)s",
                    datefmt="%Y/%m/%d|%H:%M:%S")
logger = logging.getLogger("SCSHub")


class MainWindow(MSFluentWindow):

    def __init__(self):
        super().__init__()

        logger.info("App Started")
        self.initWindow()
        self.initNavigation()
        self.connectSignalToSlot()


    def initWindow(self):

        self.resize(960, 780)
        self.setMinimumSize(750, 540)
        self.setMicaEffectEnabled(False)
        self.setWindowIcon(QIcon(":/SCSHub/image/logo.svg"))
        self.setWindowTitle("SCS Hub")
        
        self.setMicaEffectEnabled(cfg.get(cfg.micaEnabled))

        # center window
        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)

        # splash screen
        self.splashScreen = SplashScreen(":/SCSHub/image/splash.svg", self)
        self.splashScreen.setIconSize(QSize(300, 300))
        self.splashScreen.raise_()
        self.show()
        loop = QEventLoop(self)
        QTimer.singleShot(700, loop.quit)
        loop.exec()
        self.splashScreen.finish()

    def initNavigation(self):

        self.homeInterface = HomeInterface()
        self.pixInterface = PixInterface()
        self.scsInterface = ScsInterface()
        self.settingInterface = SettingInterface()

        # top
        self.addSubInterface(self.homeInterface, FluentIcon.HOME, self.tr("Home"), FluentIcon.HOME_FILL)
        self.addSubInterface(self.pixInterface, ScsHubIcon.PIX_CONVERTER, self.tr("Converter"), ScsHubIcon.PIX_CONVERTER_FILL)
        self.addSubInterface(self.scsInterface, ScsHubIcon.SCS_EXTRACTOR, self.tr("Extractor"), ScsHubIcon.SCS_EXTRACTOR_FILL)
        
        # bottom
        self.navigationInterface.addItem( "theme", FluentIcon.CONSTRACT, self.tr("Theme"), toggleTheme, False, position=NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.settingInterface, FluentIcon.LIBRARY, self.tr("Settings"), FluentIcon.LIBRARY_FILL, NavigationItemPosition.BOTTOM)

        # set active interface
        self.navigationInterface.setCurrentItem(self.homeInterface.objectName())
        
    def connectSignalToSlot(self):
        signalBus.micaEnableChanged.connect(self.setMicaEffectEnabled)
        signalBus.switchToInterface.connect(self.switchToInterface)

    def switchToInterface(self, routeKey):
        match routeKey:
            case "pixInterface":
                self.stackedWidget.setCurrentWidget(self.pixInterface, popOut=False)
                logger.info("Switch to pixInterface")

            case "scsInterface":
                self.stackedWidget.setCurrentWidget(self.scsInterface, popOut=False)
                logger.info("Switch to scsInterface")

            case "settingInterface":
                self.stackedWidget.setCurrentWidget(self.settingInterface, popOut=True)
                logger.info("Switch to settingInterface")

            case _:
                self.stackedWidget.setCurrentWidget(self.homeInterface, popOut=False)
                logger.info("Switch to homeInterface")

