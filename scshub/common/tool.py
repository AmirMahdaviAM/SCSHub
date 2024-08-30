import os
import logging
import shutil
import zipfile
import requests
from sys import platform
from enum import Enum
from subprocess import Popen

from PyQt5.QtCore import pyqtSignal, QObject, QThread, Qt

from qfluentwidgets import (
    InfoBarPosition,
    FluentIconBase,
    StyleSheetBase,
    MessageBoxBase,
    SubtitleLabel,
    DotInfoBadge,
    PushButton,
    BodyLabel,
    InfoBar,
    Theme,
    qconfig,
    setFont,
    getIconColor,
)


class ScsHubIcon(FluentIconBase, Enum):

    LOGO = "logo"

    SCS = "scs"

    PIX_I = "interface/pix"
    PIX_FILL = "interface/pix_fill"
    SCS_I = "interface/scs"
    SCS_FILL = "interface/scs_fill"
    SXC_I = "interface/sxc"
    SXC_FILL = "interface/sxc_fill"
    TOBJ_I = "interface/tobj"
    TOBJ_FILL = "interface/tobj_fill"
    DEF_I = "interface/def"
    DEF_FILL = "interface/def_fill"

    FILE = "file/file"
    FOLDER = "file/folder"
    ANIM = "file/anim"
    MODEL = "file/model"
    PREFAB = "file/prefab"
    TEXT = "file/text"
    TEXTURE = "file/texture"
    TOBJ = "file/tobj"

    def path(self, theme=Theme.AUTO):
        return f":/vector/{self.value}_{getIconColor(theme)}.svg"


class ScsHubDialog(MessageBoxBase):

    def __init__(self, title, contet, parent=None):
        super().__init__(parent)

        self.titleLabel = SubtitleLabel(title, self)

        self.text = BodyLabel(self)
        self.text.setText(contet)
        setFont(self.text, 16)

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addSpacing(12)
        self.viewLayout.addWidget(self.text)

        self.widget.setMinimumWidth(350)


class ScsHubStyleSheet(StyleSheetBase, Enum):

    LINK_CARD = "link_card"
    INTERFACE_CARD = "interface_card"

    def path(self, theme=Theme.AUTO):
        theme = qconfig.theme if theme == Theme.AUTO else theme
        return f":/style/{theme.value.lower()}/{self.value}.qss"


class Downloader(QThread):

    result = pyqtSignal(int)

    def __init__(
        self, logger: logging.Logger, url: str, save_path: str, unzip_path: str = "", parent=None
    ):
        super().__init__(parent)

        self.logger = logger
        self.url = url
        self.save_path = save_path
        self.unzip_path = unzip_path

    def run(self):

        try:
            self.logger.info(f"Starting download")

            # download from url
            result = requests.get(self.url)

            # save file to save_path
            with open(self.save_path, "wb") as f:
                f.write(result.content)

            # make it executable on linux
            if platform == "linux" or platform == "darwin":

                from stat import S_IEXEC, S_IXGRP

                st = os.stat(self.save_path)
                os.chmod(self.save_path, st.st_mode | S_IEXEC | S_IXGRP)

            # unzip downloaded file
            if self.unzip_path != "":
                with zipfile.ZipFile(self.save_path, "r") as zip_ref:
                    zip_ref.extractall(self.unzip_path)

                scshub_file_remover(self.save_path)

            self.result.emit(0)

            self.logger.info(f"Downloaded finished successfully")

        except Exception:
            self.result.emit(1)

            self.logger.info("Error accured during download")


class SignalBus(QObject):

    mica_enabled = pyqtSignal(bool)
    colorize = pyqtSignal(bool)
    switch_interface = pyqtSignal(str)
    window_width = pyqtSignal(int)

    pix_exist = pyqtSignal(bool)
    sxc_exist = pyqtSignal(bool)
    scs_exist = pyqtSignal(bool)


signal_bus = SignalBus()


def scshub_dir_remover(dir: str):

    if os.path.isdir(dir):
        shutil.rmtree(dir)


def scshub_file_remover(file: str):

    if os.path.isfile(file):
        os.remove(file)


def scshub_infobar(parent, type: str, msg: str, open: str = ""):

    match type:

        case "success":
            InfoBar.success(
                title=parent.tr("Success"),
                content=msg,
                orient=Qt.Horizontal,
                isClosable=True,
                duration=1500,
                position=InfoBarPosition.TOP_RIGHT,
                parent=parent,
            )

        case "success_btn":
            success = InfoBar.success(
                title=parent.tr("Success"),
                content=msg,
                orient=Qt.Vertical,
                isClosable=True,
                duration=1500,
                position=InfoBarPosition.TOP_RIGHT,
                parent=parent,
            )
            if platform == "win32":
                button = PushButton("Open Folder")
                button.clicked.connect(lambda: Popen(f"explorer.exe {open}"))
                success.addWidget(button)

        case "error":
            InfoBar.error(
                title=parent.tr("Error"),
                content=msg,
                orient=Qt.Horizontal,
                isClosable=True,
                duration=1500,
                position=InfoBarPosition.TOP_RIGHT,
                parent=parent,
            )

        case "error_btn":
            error = InfoBar.error(
                title=parent.tr("Error"),
                content=msg,
                orient=Qt.Vertical,
                isClosable=True,
                duration=1500,
                position=InfoBarPosition.TOP_RIGHT,
                parent=parent,
            )
            if platform == "win32":
                button = PushButton("Open Log")
                button.clicked.connect(lambda: Popen(f"explorer.exe {open}"))
                error.addWidget(button)

        case "warn":
            InfoBar.warning(
                title=parent.tr("Warning"),
                content=msg,
                orient=Qt.Horizontal,
                isClosable=True,
                duration=1500,
                position=InfoBarPosition.TOP_RIGHT,
                parent=parent,
            )

        case "warn_btn":
            warn = InfoBar.warning(
                title=parent.tr("Warning"),
                content=msg,
                orient=Qt.Vertical,
                isClosable=True,
                duration=1500,
                position=InfoBarPosition.TOP_RIGHT,
                parent=parent,
            )
            if platform == "win32":
                button = PushButton("Open Folder")
                button.clicked.connect(lambda: Popen(f"explorer.exe {open}"))
                warn.addWidget(button)

        case "info":
            InfoBar.info(
                title=parent.tr("Info"),
                content=msg,
                orient=Qt.Horizontal,
                isClosable=True,
                duration=2000,
                position=InfoBarPosition.TOP_RIGHT,
                parent=parent,
            )


def scshub_badge(parent, target):

    badge = DotInfoBadge.success(parent, target)
    badge.setFixedSize(6, 6)
    badge.show()

    return badge


def scshub_log(file, data):

    with open(file, "at", encoding="utf-8") as f:
        f.write("=====  Start  =====\n")
        f.writelines(line + "\n" for line in data)
        f.write("=====   End   =====\n\n")
