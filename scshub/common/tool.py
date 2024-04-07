import os, logging, requests
from sys import platform
from enum import Enum

from PyQt5.QtCore import QObject, QThread, pyqtSignal

from qfluentwidgets import FluentIconBase, Theme, StyleSheetBase, getIconColor, qconfig


# set logger
logger = logging.getLogger("SCSHub")


# info
YEAR = 2024
VERSION = "1.0"
GITHUB = "https://github.com/AmirMahdaviAM/"
TELEGRAM = "https://t.me/amirmdvi"
INSTAGRAM = "https://instagram.com/amirmdvl"

# link
SCSHUB_GITHUB_URL = "https://github.com/AmirMahdaviAM/SCSHub/"
SCSHUB_FEEDBACK_URL = "https://github.com/AmirMahdaviAM/SCSHub/issues"
SCSHUB_FORUM_URL = "https://forum.scssoft.com/viewtopic.php?t=328411"

# set tools path
TOOLS_PATH = os.path.join(os.getcwd(), "tools")

# create tool path if not exist
if not os.path.isdir(TOOLS_PATH):
    os.makedirs(TOOLS_PATH, exist_ok=True)

# set converter pix path and download url
if platform == "linux":
    PIX_URL = "https://github.com/simon50keda/ConverterPIX/raw/master/bin/linux/converter_pix"
    PIX_PATH = os.path.join(TOOLS_PATH, "converter_pix")
elif platform == "darwin":
    PIX_URL = "https://github.com/theHarven/ConverterPIX/raw/MacOS_binary/bin/macos/converter_pix"
    PIX_PATH = os.path.join(TOOLS_PATH, "converter_pix")
else:
    PIX_URL = "https://github.com/mwl4/ConverterPIX/raw/master/bin/win_x86/converter_pix.exe"
    PIX_PATH = os.path.join(TOOLS_PATH, "converter_pix.exe")

# set scs extractor path and download url
SCS_URL = "https://github.com/AmirMahdaviAM/SCSHub/raw/master/tools/scs_extractor.exe"
SCS_PATH = os.path.join(TOOLS_PATH, "scs_extractor.exe")

logger.info(f'Current working directory: "{TOOLS_PATH}"')


class ScsHubIcon(FluentIconBase, Enum):

    PIX_CONVERTER = "interface/pix_converter"
    PIX_CONVERTER_FILL = "interface/pix_converter_fill"
    SCS_EXTRACTOR = "interface/scs_extractor"
    SCS_EXTRACTOR_FILL = "interface/scs_extractor_fill"

    SCS = "scs"

    FILE = "file"
    FOLDER = "folder"
    ANIM = "anim"
    MODEL = "model"
    PREFAB = "prefab"
    TEXT = "text"
    TEXTURE = "texture"
    TOBJ = "tobj"

    def path(self, theme=Theme.AUTO):
        return f":/SCSHub/icon/{self.value}_{getIconColor(theme)}.svg"


class StyleSheet(StyleSheetBase, Enum):
    """Style sheet"""

    LINK_CARD = "link_card"
    SAMPLE_CARD = "sample_card"
    HOME_INTERFACE = "home_interface"
    SETTING_INTERFACE = "setting_interface"

    def path(self, theme=Theme.AUTO):
        theme = qconfig.theme if theme == Theme.AUTO else theme
        return f":/SCSHub/style/{theme.value.lower()}/{self.value}.qss"


class Downloader(QThread):
    """Download File from URL and saves it to PATH"""

    URL = ""
    PATH = ""
    result = pyqtSignal(int)

    def run(self):

        logger.info("Downloading ...")

        try:
            result = requests.get(self.URL)
            with open(self.PATH, "wb") as f:
                f.write(result.content)

            # make it executable on linux
            if platform == "linux" or platform == "darwin":

                from stat import S_IEXEC, S_IXGRP

                st = os.stat(self.PATH)
                os.chmod(self.PATH, st.st_mode | S_IEXEC | S_IXGRP)

            self.result.emit(0)

        except Exception:
            self.result.emit(1)

            logger.error("Unexpected error accured during downloading")


downloader = Downloader()


class SignalBus(QObject):

    micaEnableChanged = pyqtSignal(bool)
    switchToInterface = pyqtSignal(str)


signalBus = SignalBus()
