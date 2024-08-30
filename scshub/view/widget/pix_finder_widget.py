import os
import logging
from random import randint

from PyQt5.QtCore import Qt, QProcess
from PyQt5.QtWidgets import QWidget, QFileDialog, QListWidgetItem, QAbstractItemView

from qfluentwidgets import (
    FluentIconBase,
    ToolTipFilter,
    FluentIcon,
    InfoLevel,
)

from ..ui.pix_finder_ui import PixFinderUi
from ...common.tool import ScsHubIcon, signal_bus, scshub_infobar, scshub_badge, scshub_log
from ...common.info import PIX_CONVERTER_PATH, PIX_FINDER_LOG


NAME = "PIXFinder"

logger = logging.getLogger(NAME)


class PixFinderWidget(QWidget, PixFinderUi):

    def __init__(self, infobar_pos):
        super().__init__()

        self.INFOBAR_POS = infobar_pos

        self.INPUTS = []
        self.OUTPUT = ""

        self.PATH = "/"

        self.LAST_FILE = ""

        self.TEMP_OUT = []
        self.TEMP_LOG = []

        self.main_process = None
        self.anim_process = None

        self.setupUi(self)
        self.init_ui()

        signal_bus.pix_exist.connect(
            lambda exist: (
                self.input_btn.setEnabled(True) if exist else self.input_btn.setDisabled(True)
            )
        )

    def init_ui(self):

        self.top_card_lyt.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.reset_btn.setIcon(FluentIcon.DELETE)
        self.reset_btn.clicked.connect(lambda: self.reset_inputs())
        self.reset_btn.installEventFilter(ToolTipFilter(self.reset_btn))

        self.input_btn.setIcon(FluentIcon.DOWN)
        self.input_btn.clicked.connect(lambda: self.get_file())
        self.input_btn.installEventFilter(ToolTipFilter(self.input_btn))

        self.find_btn.setIcon(FluentIcon.SEARCH)
        self.find_btn.clicked.connect(lambda: self.finder_process())

        self.navbar.setSpacing(10)
        self.navbar.setFixedHeight(19)
        self.navbar.currentItemChanged.connect(lambda objectname: self.change_path(objectname))

        self.back_btn.setIcon(FluentIcon.LEFT_ARROW)
        self.back_btn.installEventFilter(ToolTipFilter(self.back_btn))
        self.back_btn.clicked.connect(lambda: self.go_back())

        self.home_btn.setIcon(FluentIcon.HOME)
        self.home_btn.installEventFilter(ToolTipFilter(self.home_btn))
        self.home_btn.clicked.connect(lambda: self.go_home())

        self.refresh_btn.setIcon(FluentIcon.UPDATE)
        self.refresh_btn.installEventFilter(ToolTipFilter(self.refresh_btn))
        self.refresh_btn.clicked.connect(lambda: self.refresh_path())

        self.model_list.doubleClicked.connect(self.finder_process)
        self.model_list.currentTextChanged.connect(self.goto_folder)
        self.model_badge.setLevel(InfoLevel.INFOAMTION)

        self.anim_list.setSelectionMode(QAbstractItemView.NoSelection)
        self.anim_badge.setLevel(InfoLevel.INFOAMTION)

    def list_process(self):

        argument = ""

        for file_path in self.INPUTS:
            argument += f'-b "{file_path}" '

        argument += f"-listdir {self.PATH}"

        command = f'"{PIX_CONVERTER_PATH}" {argument}'

        logger.info(command)

        if self.main_process == None:
            self.main_process = QProcess()
            self.main_process.setProcessChannelMode(QProcess.MergedChannels)
            self.main_process.readyRead.connect(self.list_output)
            self.main_process.finished.connect(self.list_finish)
            self.main_process.waitForFinished(100)
            self.main_process.start(command)

    def list_output(self):

        # get output data from process and decode it
        output = self.main_process.readAllStandardOutput()
        decoded_output = bytes(output).decode("utf-8")
        splitted_output = decoded_output.splitlines()

        for line in splitted_output:
            if line.strip() != "":
                self.TEMP_OUT.append(line.strip())

    def list_finish(self):

        self.TEMP_OUT.sort()

        self.model_list.clearSelection()
        self.model_list.clear()
        self.anim_list.clearSelection()
        self.anim_list.clear()

        folders = []
        files = []

        for line in self.TEMP_OUT:
            # create directory list
            if line.startswith("[D] "):
                folders.append(os.path.relpath(line[4:], self.PATH))

            # create file list
            elif line.startswith("[F] "):
                # cheack suffix and only include specified in list
                if line.endswith(".pmg"):
                    files.append(os.path.relpath(line[4:], self.PATH))

        # set list count to badges
        self.model_badge.setText(str(len(files)))

        # add items in list to list view
        for folder in folders:
            self.model_list.addItem(
                QListWidgetItem(FluentIconBase.qicon(ScsHubIcon.FOLDER), folder)
            )

        for file in files:
            self.model_list.addItem(QListWidgetItem(FluentIconBase.qicon(ScsHubIcon.MODEL), file))

        self.main_process = None
        self.TEMP_OUT = []

    def finder_process(self):

        if "." in os.path.basename(self.PATH):
            argument = ""

            for file_path in self.INPUTS:
                argument += f'-b "{file_path}" '

            argument += f"--find-model-animations {self.PATH[:-4]}"

            command = f'"{PIX_CONVERTER_PATH}" {argument}'

            logger.info(command)

            if self.anim_process == None:
                self.anim_process = QProcess()
                self.anim_process.readyReadStandardOutput.connect(self.finder_output)
                self.anim_process.finished.connect(self.finder_finish)
                self.anim_process.waitForFinished(100)
                self.anim_process.start(command)

        else:
            scshub_infobar(self.INFOBAR_POS, "info", "No file selected")

    def finder_output(self):

        # get output data from process and decode it
        output = self.anim_process.readAllStandardOutput()
        decoded_output = bytes(output).decode("utf-8")
        splitted_output = decoded_output.splitlines()

        for line in splitted_output:
            striped_line = line.strip()
            if striped_line != "":
                self.TEMP_OUT.append(striped_line)

                if (
                    "unable" in striped_line.lower()
                    or "unknown" in striped_line.lower()
                    or "invalid" in striped_line.lower()
                    or "skeleton" in striped_line.lower()
                    or "unexpected" in striped_line.lower()
                    or striped_line.startswith("/")
                ):
                    self.TEMP_LOG.append(striped_line)

    def finder_finish(self):

        self.anim_list.clearSelection()
        self.anim_list.clear()

        self.TEMP_OUT.sort()

        temp_out = ""
        for line in self.TEMP_OUT:
            temp_out += f"{line.lower()}\n"

        if (
            "unable" in temp_out
            or "invalid" in temp_out
            or "skeleton" in temp_out
            or "unexpected" in temp_out
        ):
            scshub_infobar(
                self.INFOBAR_POS,
                "error_btn",
                self.tr("Error occurred during process"),
                PIX_FINDER_LOG,
            )
            logger.error(f"Error occurred during process, check {PIX_FINDER_LOG}")

        else:
            files = []

            for line in self.TEMP_OUT:
                if line.startswith("/"):
                    files.append(line)

            # set list count to badges
            self.anim_badge.setText(str(len(files)))

            for file in files:
                self.anim_list.addItem(QListWidgetItem(FluentIconBase.qicon(ScsHubIcon.ANIM), file))

            scshub_infobar(self.INFOBAR_POS, "success", self.tr("Finished succesfully"))
            logger.info("Process completed successfully")

        if self.TEMP_LOG != []:
            scshub_log(PIX_FINDER_LOG, self.TEMP_LOG)

        self.anim_process = None
        self.TEMP_OUT = []
        self.TEMP_LOG = []

    def reset_inputs(self):

        self.INPUTS = []

        self.input_btn.setToolTip("")
        self.input_badge.close()

        self.navbar.clear()
        self.refresh_path()

    def add_root_item(self):

        self.navbar.clear()

        if len(self.INPUTS) < 2:
            self.navbar.addItem("root", f"{os.path.split(self.INPUTS[0])[1]}")
        else:
            self.navbar.addItem("root", "multi-archive")

    def remove_last_selcted(self):

        if self.PATH.endswith(self.LAST_FILE):
            self.PATH = self.PATH.replace(self.LAST_FILE, "")

    def refresh_path(self):

        self.remove_last_selcted()

        self.list_process()

    def change_path(self, selected: str):

        # back to root of scs file if first item selected in navbar_itemgation bar
        if selected == "root":
            self.PATH = "/"

            self.back_btn.setDisabled(True)
            self.home_btn.setDisabled(True)

        # find selected item index in saved path string and
        # delete all after item name itself and update new path
        else:
            self.PATH = self.PATH[0 : self.PATH.find(selected[:-2]) + len(selected[:-2])].replace(
                "\\", "/"
            )
            self.back_btn.setEnabled(True)
            self.home_btn.setEnabled(True)

        self.list_process()

    def go_back(self):

        self.remove_last_selcted()

        if not self.navbar.currentIndex() == 0:
            self.navbar.popItem()

        self.list_process()

    def go_home(self):

        self.PATH = "/"
        self.ANIM_PATH = "/"

        self.add_root_item()

        self.list_process()

    def goto_folder(self, selected: str):

        # check if not empty and add last item to navbar_itemgation bar
        if selected != "":
            self.remove_last_selcted()

            if not selected.endswith(".pmg"):
                # update path and add seelcted folder to it
                self.PATH = os.path.join(self.PATH, selected).replace("\\", "/")

                navbar_item = os.path.split(self.PATH)
                self.navbar.addItem(f"{selected}{randint(11, 99)}", navbar_item[1])

                self.list_process()

            else:
                self.PATH = os.path.join(self.PATH, selected).replace("\\", "/")
                self.LAST_FILE = selected

    def get_file(self):

        file_dialog = QFileDialog().getOpenFileNames(
            self, "Select file", filter="SCS archives (*.zip *.scs)"
        )
        if file_dialog[0]:
            file_path = file_dialog[0]

            # enable buttons after file selected for first time
            if self.INPUTS == []:
                self.reset_btn.setEnabled(True)
                self.find_btn.setEnabled(True)
                self.refresh_btn.setEnabled(True)

                self.input_badge = scshub_badge(self.top_card, self.input_btn)

            for file in file_path:
                self.INPUTS.append(file)

            # set buttons tooltip
            tooltip = ""
            for file in self.INPUTS:
                tooltip += f"{file}\n"

            self.input_btn.setToolTip(tooltip[:-1])

            scshub_infobar(self.INFOBAR_POS, "success", self.tr("File imported"))
            logger.info(f'Set input file to "{self.INPUTS}"')

            self.add_root_item()
            self.list_process()
