import os
import logging
from random import randint

from PyQt5.QtCore import Qt, QProcess, QSize, QEasingCurve, QPropertyAnimation
from PyQt5.QtWidgets import QWidget, QFileDialog, QListWidgetItem

from qfluentwidgets import (
    IndeterminateProgressRing,
    InfoBarPosition,
    FluentIconBase,
    ToolTipFilter,
    InfoBarIcon,
    FluentIcon,
    InfoLevel,
    InfoBar,
)

from ..ui.pix_converter_ui import PixConverterUi
from ...common.tool import (
    ScsHubIcon,
    Downloader,
    signal_bus,
    scshub_log,
    scshub_badge,
    scshub_infobar,
    scshub_file_remover,
)
from ...common.info import PIX_CONVERTER_PATH, PIX_CONVERTER_URL, PIX_CONVERTER_LOG

NAME = "PIXConverter"

logger = logging.getLogger(NAME)


class PixConverterWidget(QWidget, PixConverterUi):

    def __init__(self, infobar_pos):
        super().__init__()

        self.INFOBAR_POS = infobar_pos

        self.INPUTS = []
        self.OUTPUT = ""

        self.MODE = "-extract_f"
        self.PIX_MODE = ""

        self.PATH = "/"
        self.ANIM_PATH = "/"
        self.SUFFIX = ""

        self.LAST_FILE = ""
        self.ANIM_FILES = []

        self.TEMP_OUT = []
        self.TEMP_OUT_ANIM = []
        self.TEMP_LOG = []

        self.main_process = None
        self.other_process = None

        self.setupUi(self)
        self.init_ui()
        self.option_ui()

        signal_bus.pix_exist.connect(self.tools_exist)

        scshub_file_remover(PIX_CONVERTER_LOG)

    def init_ui(self):

        self.top_card_lyt.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.download_btn.setIcon(FluentIcon.DOWNLOAD)
        self.download_btn.clicked.connect(lambda: self.downloader())
        self.download_btn.hide()

        self.reset_btn.setIcon(FluentIcon.DELETE)
        self.reset_btn.clicked.connect(lambda: self.reset_inputs())
        self.reset_btn.installEventFilter(ToolTipFilter(self.reset_btn))

        self.input_btn.setIcon(FluentIcon.DOWN)
        self.input_btn.clicked.connect(lambda: self.get_file())
        self.input_btn.installEventFilter(ToolTipFilter(self.input_btn))

        self.output_btn.setIcon(FluentIcon.UP)
        self.output_btn.clicked.connect(lambda: self.get_folder())
        self.output_btn.installEventFilter(ToolTipFilter(self.output_btn))

        self.extract_btn.setIcon(FluentIcon.LINK)
        self.extract_btn.clicked.connect(lambda: self.extract_mode())

        self.extract_sgmnt.addItem("file", self.tr("File"), lambda: self.change_mode("file"))
        self.extract_sgmnt.addItem("model", self.tr("Model"), lambda: self.change_mode("model"))
        self.extract_sgmnt.addItem("tobj", self.tr("TOBJ"), lambda: self.change_mode("tobj"))
        self.extract_sgmnt.addItem("folder", self.tr("Folder"), lambda: self.change_mode("folder"))
        self.extract_sgmnt.installEventFilter(ToolTipFilter(self.extract_sgmnt))

        self.anim_tgl.setIcon(ScsHubIcon.ANIM)
        self.anim_tgl.clicked.connect(lambda: self.toggle_card())
        self.anim_tgl.installEventFilter(ToolTipFilter(self.anim_tgl))

        self.material_tgl.setIcon(ScsHubIcon.TEXT)
        self.material_tgl.installEventFilter(ToolTipFilter(self.material_tgl))

        self.texture_tgl.setIcon(ScsHubIcon.TEXTURE)
        self.texture_tgl.installEventFilter(ToolTipFilter(self.texture_tgl))

    def option_ui(self):

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

        self.anim_card.hide()
        self.anim_list.currentTextChanged.connect(self.goto_folder_anim)
        self.anim_badge.setLevel(InfoLevel.INFOAMTION)

        self.folder_list.currentTextChanged.connect(self.goto_folder)
        self.folder_badge.setLevel(InfoLevel.INFOAMTION)

        self.file_list.currentTextChanged.connect(self.select_file)
        self.file_badge.setLevel(InfoLevel.INFOAMTION)

    def toggle_card(self):

        # anim card
        if (
            self.extract_sgmnt._currentRouteKey == "model"
            and self.anim_tgl.isEnabled()
            and self.anim_tgl.isChecked()
        ):
            self.anim_card.show()
            self.anim_card_anim = QPropertyAnimation(self.anim_card, b"maximumSize")
            self.anim_card_anim.setEndValue(QSize(500, 16777215))
            self.anim_card_anim.setDuration(500)
            self.anim_card_anim.setEasingCurve(QEasingCurve.OutQuad)
            self.anim_card_anim.start()
            self.anim_card_anim.finished.connect(lambda: self.anim_card.setMaximumWidth(16777215))

        else:
            self.anim_card_anim = QPropertyAnimation(self.anim_card, b"maximumSize")
            self.anim_card_anim.setStartValue(QSize(500, 16777215))
            self.anim_card_anim.setEndValue(QSize(0, 16777215))
            self.anim_card_anim.setDuration(500)
            self.anim_card_anim.setEasingCurve(QEasingCurve.OutQuad)
            self.anim_card_anim.start()
            self.anim_card_anim.finished.connect(lambda: self.anim_card.hide())

        # file card
        if self.extract_sgmnt._currentRouteKey == "folder":
            self.file_card_anim = QPropertyAnimation(self.file_card, b"maximumSize")
            self.file_card_anim.setStartValue(QSize(750, 16777215))
            self.file_card_anim.setEndValue(QSize(0, 16777215))
            self.file_card_anim.setDuration(500)
            self.file_card_anim.setEasingCurve(QEasingCurve.OutQuad)
            self.file_card_anim.start()
            self.file_card_anim.finished.connect(lambda: self.file_card.hide())

        else:
            self.file_card.show()
            self.file_card_anim = QPropertyAnimation(self.file_card, b"maximumSize")
            self.file_card_anim.setEndValue(QSize(750, 16777215))
            self.file_card_anim.setDuration(500)
            self.file_card_anim.setEasingCurve(QEasingCurve.OutQuad)
            self.file_card_anim.start()
            self.file_card_anim.finished.connect(lambda: self.file_card.setMaximumWidth(16777215))

    def change_mode(self, mode: str):

        match mode:
            case "file":
                self.MODE = "-extract_f"
                self.SUFFIX = ""
                self.anim_tgl.setDisabled(True)
                self.material_tgl.setDisabled(True)
                self.texture_tgl.setDisabled(True)
                self.file_lbl.setText(self.tr("File"))

            case "model":
                self.MODE = "-m"
                self.SUFFIX = ".pmd"
                self.anim_tgl.setEnabled(True)
                self.material_tgl.setEnabled(True)
                self.texture_tgl.setEnabled(True)
                self.file_lbl.setText(self.tr("Model"))

            case "tobj":
                self.MODE = "-t"
                self.SUFFIX = ".tobj"
                self.anim_tgl.setDisabled(True)
                self.material_tgl.setDisabled(True)
                self.texture_tgl.setDisabled(True)
                self.file_lbl.setText(self.tr("TOBJ"))

            case "folder":
                self.MODE = "-extract_d"
                self.anim_tgl.setDisabled(True)
                self.material_tgl.setDisabled(True)
                self.texture_tgl.setDisabled(True)

        self.toggle_card()
        self.refresh_path()

    def list_mode(self):

        self.PIX_MODE = "list"

        argument = ""

        for file_path in self.INPUTS:
            argument += f'-b "{file_path}" '

        argument += f"-listdir {self.PATH}"

        self.converter_process(argument)

    def extract_mode(self):

        self.PIX_MODE = "extract"

        argument = ""

        for file_path in self.INPUTS:
            argument += f'-b "{file_path}" '

        argument += f"{self.MODE}"

        if self.MODE != "-extract_d":
            # check if file selected
            if "." in os.path.basename(self.PATH):
                # single model mode
                if self.MODE == "-m":
                    argument += f" {self.PATH[:-4]}"

                    if self.material_tgl.isChecked():
                        argument += f" -matFormat147"

                    if self.texture_tgl.isChecked():
                        argument += f" -ddsDxt10"

                    if self.anim_tgl.isChecked():
                        self.select_file_anim()

                        if self.ANIM_FILES != []:
                            for file in self.ANIM_FILES:
                                anim = os.path.join(
                                    self.PATH.replace(self.LAST_FILE, ""), file[:-4]
                                ).replace("\\", "/")
                                argument += f" {anim}"

                # single tobj or exprot file mode
                elif self.MODE == "-t" or self.MODE == "-extract_f":
                    argument += f" {self.PATH}"
                    argument += f' -e "{self.OUTPUT}"'

                self.converter_process(argument)

            else:
                scshub_infobar(self.INFOBAR_POS, "info", "No file selected")

        # extract folder mode
        elif self.MODE == "-extract_d":
            argument += f" {self.PATH}"
            argument += f' -e "{self.OUTPUT}"'

            self.converter_process(argument)

    def anim_mode(self):

        argument = ""

        for file_path in self.INPUTS:
            argument += f'-b "{file_path}" '

        argument += f"-listdir {self.ANIM_PATH}"

        self.anim_process(argument)

    def converter_process(self, argument: str):

        command = f'"{PIX_CONVERTER_PATH}" {argument}'

        logger.info(command)

        if self.main_process == None:
            self.main_process = QProcess()
            self.main_process.setProcessChannelMode(QProcess.MergedChannels)
            self.main_process.readyRead.connect(self.converter_output)
            self.main_process.stateChanged.connect(self.converte_state)
            self.main_process.finished.connect(self.converter_finish)
            self.main_process.waitForFinished(100)
            self.main_process.start(command)

    def converter_output(self):

        # get output data from process and decode it
        output = self.main_process.readAllStandardOutput()
        decoded_output = bytes(output).decode("utf-8")
        splitted_output = decoded_output.splitlines()

        for line in splitted_output:
            striped_line = line.strip()
            if striped_line != "":
                self.TEMP_OUT.append(striped_line)

                if (
                    not striped_line.startswith("-- done")
                    and not striped_line.startswith("*")
                    and not striped_line.startswith("[D]")
                    and not striped_line.startswith("[F]")
                ):
                    self.TEMP_LOG.append(striped_line)

    def converte_state(self, state):

        states = {
            QProcess.NotRunning: "NotRunning",
            QProcess.Starting: "Starting",
            QProcess.Running: "Running",
        }
        state_name = states[state]

        if self.PIX_MODE == "extract":

            if state_name == "Running":
                self.working_infobar = InfoBar.new(
                    InfoBarIcon.INFORMATION,
                    self.tr("Working"),
                    "",
                    Qt.Horizontal,
                    False,
                    -1,
                    InfoBarPosition.TOP,
                    self.INFOBAR_POS,
                )
                ring_wgt = IndeterminateProgressRing(self)
                ring_wgt.setFixedSize(22, 22)
                ring_wgt.setStrokeWidth(4)
                self.working_infobar.addWidget(ring_wgt)

                self.reset_btn.setDisabled(True)
                self.input_btn.setDisabled(True)
                self.output_btn.setDisabled(True)
                self.extract_btn.setDisabled(True)
                self.extract_sgmnt.setDisabled(True)
                self.anim_tgl.setDisabled(True)
                self.material_tgl.setDisabled(True)
                self.texture_tgl.setDisabled(True)
                self.home_btn.setDisabled(True)
                self.back_btn.setDisabled(True)
                self.navbar.setDisabled(True)
                self.folder_list.setDisabled(True)
                self.file_list.setDisabled(True)
                self.anim_list.setDisabled(True)
                self.refresh_btn.setDisabled(True)

                logger.info(f"{NAME} Running")

            elif state_name == "NotRunning":
                self.working_infobar.close()

                self.reset_btn.setEnabled(True)
                self.input_btn.setEnabled(True)
                self.output_btn.setEnabled(True)
                self.extract_btn.setEnabled(True)
                self.extract_sgmnt.setEnabled(True)
                self.anim_tgl.setEnabled(True)
                self.material_tgl.setEnabled(True)
                self.texture_tgl.setEnabled(True)
                self.home_btn.setEnabled(True)
                self.back_btn.setEnabled(True)
                self.navbar.setDisabled(True)
                self.folder_list.setEnabled(True)
                self.file_list.setEnabled(True)
                self.anim_list.setEnabled(True)
                self.refresh_btn.setEnabled(True)

                logger.info(f"{NAME} Finished")

    def converter_finish(self):

        self.TEMP_OUT.sort()

        match self.PIX_MODE:

            case "list":
                self.folder_list.clearSelection()
                self.folder_list.clear()
                self.file_list.clearSelection()
                self.file_list.clear()

                folders = []
                files = []

                for line in self.TEMP_OUT:
                    # create directory list
                    if line.startswith("[D] "):
                        folders.append(os.path.relpath(line[4:], self.PATH))

                    # create file list
                    elif line.startswith("[F] "):
                        # cheack suffix and only include specified in list26
                        if line.endswith(self.SUFFIX) and not line.endswith(
                            (".pmg", ".pmc", ".pma")
                        ):
                            files.append(os.path.relpath(line[4:], self.PATH))

                # set list count to badges
                self.folder_badge.setText(str(len(folders)))
                self.file_badge.setText(str(len(files)))

                # add items in list to list view
                for folder in folders:
                    self.folder_list.addItem(
                        QListWidgetItem(FluentIconBase.qicon(ScsHubIcon.FOLDER), folder)
                    )

                # add items in list to list view and ignore it if in (-extract_d) mode
                if self.MODE != "-extract_d":
                    for file in files:
                        if file.endswith(".pmd"):
                            self.file_list.addItem(
                                QListWidgetItem(FluentIconBase.qicon(ScsHubIcon.MODEL), file)
                            )

                        elif file.endswith(".ppd"):
                            self.file_list.addItem(
                                QListWidgetItem(FluentIconBase.qicon(ScsHubIcon.PREFAB), file)
                            )

                        elif file.endswith(".tobj"):
                            self.file_list.addItem(
                                QListWidgetItem(FluentIconBase.qicon(ScsHubIcon.TOBJ), file)
                            )

                        elif file.endswith((".dds", ".png", ".jpg", ".mask")):
                            self.file_list.addItem(
                                QListWidgetItem(FluentIconBase.qicon(ScsHubIcon.TEXTURE), file)
                            )

                        elif file.endswith(
                            (".mat", ".sii", ".sui", ".txt", ".cfg", ".dat", ".soundref")
                        ):
                            self.file_list.addItem(
                                QListWidgetItem(FluentIconBase.qicon(ScsHubIcon.TEXT), file)
                            )

                        else:
                            self.file_list.addItem(
                                QListWidgetItem(FluentIconBase.qicon(ScsHubIcon.FILE), file)
                            )

            case "extract":
                temp_out = ""
                for line in self.TEMP_OUT:
                    temp_out += f"{line.lower()}\n"

                if (
                    "error" in temp_out
                    or "no" in temp_out
                    or "not" in temp_out
                    or "unable" in temp_out
                    or "cannot" in temp_out
                    or "failed" in temp_out
                    or "readDir" in temp_out
                    or "invalid" in temp_out
                    or "unknown" in temp_out
                    or "unexpected" in temp_out
                    or "unsupported" in temp_out
                ):
                    scshub_infobar(
                        self.INFOBAR_POS,
                        "error_btn",
                        self.tr("Error occurred during process"),
                        PIX_CONVERTER_LOG,
                    )
                    logger.error(f"Error occurred during process, check {PIX_CONVERTER_LOG}")

                elif "warning" in temp_out:
                    scshub_infobar(
                        self.INFOBAR_POS,
                        "warn_btn",
                        self.tr("Process finished with warnings"),
                        PIX_CONVERTER_LOG,
                    )
                    logger.warning(f"Process finished with warnings, check {PIX_CONVERTER_LOG}")

                else:
                    path = os.path.join(self.OUTPUT, self.PATH[1:]).replace("/", "\\")
                    finalPath = os.path.split(path)[0]
                    scshub_infobar(
                        self.INFOBAR_POS, "success_btn", self.tr("Process finished"), finalPath
                    )
                    logger.info("Process completed successfully")

                if self.TEMP_LOG != []:
                    scshub_log(PIX_CONVERTER_LOG, self.TEMP_LOG)

        self.main_process = None
        self.TEMP_OUT = []
        self.TEMP_LOG = []

    def anim_process(self, argument: str):

        command = f'"{PIX_CONVERTER_PATH}" {argument}'

        if self.other_process == None:
            self.other_process = QProcess()
            self.other_process.readyReadStandardOutput.connect(self.anim_output)
            self.other_process.finished.connect(self.anim_finish)
            self.other_process.waitForFinished(100)
            self.other_process.start(command)

    def anim_output(self):

        # get output data from process and decode it
        output = self.other_process.readAllStandardOutput()
        decoded_output = bytes(output).decode("utf-8")
        splitted_output = decoded_output.splitlines()

        for line in splitted_output:
            if line.strip() != "":
                self.TEMP_OUT_ANIM.append(line.strip())

    def anim_finish(self):

        self.anim_list.clearSelection()
        self.anim_list.clear()
        self.ANIM_FILES = []

        self.anim_list.addItem(QListWidgetItem(FluentIconBase.qicon(FluentIcon.UP), ".."))

        folders = []
        files = []

        for line in self.TEMP_OUT_ANIM:
            # create directory list
            if line.startswith("[D] "):
                folders.append(os.path.relpath(line[4:], self.ANIM_PATH))

            # create file list
            elif line.startswith("[F] "):

                # cheack suffix and only include pma file
                if line.endswith(".pma"):
                    files.append(os.path.relpath(line[4:], self.ANIM_PATH))

        # set list count to badges
        self.anim_badge.setText(str(len(files)))

        # add items in list to list view
        for folder in folders:
            self.anim_list.addItem(QListWidgetItem(FluentIconBase.qicon(ScsHubIcon.FOLDER), folder))

        for file in files:
            item = QListWidgetItem(FluentIconBase.qicon(ScsHubIcon.FOLDER), file)
            item.setCheckState(0)
            self.anim_list.addItem(item)

        self.other_process = None
        self.TEMP_OUT_ANIM = []

    def reset_inputs(self):

        self.INPUTS = []
        self.OUTPUT = ""

        self.input_btn.setToolTip("")
        self.input_badge.close()
        self.output_btn.setToolTip("")
        self.output_badge.close()

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

    def go_back(self):

        self.remove_last_selcted()

        if not self.navbar.currentIndex() == 0:
            self.navbar.popItem()

        self.list_mode()

    def refresh_path(self):

        self.remove_last_selcted()

        self.list_mode()
        self.anim_mode()

    def go_home(self):

        self.PATH = "/"
        self.ANIM_PATH = "/"

        self.add_root_item()

        self.list_mode()
        self.anim_mode()

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

        self.list_mode()

    def goto_folder(self, selected: str):

        # check if not empty and add last item to navbar_itemgation bar
        if selected != "":
            self.remove_last_selcted()

            # update path and add seelcted folder to it
            self.PATH = os.path.join(self.PATH, selected).replace("\\", "/")

            navbar_item = os.path.split(self.PATH)
            self.navbar.addItem(f"{selected}{randint(11, 99)}", navbar_item[1])

            self.list_mode()

    def select_file(self, selected: str):

        self.remove_last_selcted()

        # update path and add seelcted file to it
        self.PATH = os.path.join(self.PATH, selected).replace("\\", "/")

        self.LAST_FILE = selected

    def goto_folder_anim(self, selected: str):

        if selected != "":
            if not selected.endswith(".pma"):
                if selected == ".." and self.ANIM_PATH != "/":
                    go_back = os.path.split(self.ANIM_PATH)
                    self.ANIM_PATH = go_back[0].replace("\\", "/")
                else:
                    self.ANIM_PATH = os.path.join(self.ANIM_PATH, selected).replace("\\", "/")
                    self.ANIM_FILES = []

                self.anim_mode()

    def select_file_anim(self):

        self.ANIM_FILES = []

        for index in range(self.anim_list.count()):
            item = self.anim_list.item(index)

            if item.checkState() == 2:

                anim_path = f"{self.ANIM_PATH}/{item.text()[-4]}"

                self.ANIM_FILES.append(anim_path)

    def get_file(self):

        file_dialog = QFileDialog().getOpenFileNames(
            self, "Select file", filter="SCS archives (*.zip *.scs)"
        )
        if file_dialog[0]:
            file_path = file_dialog[0]

            # enable buttons after file selected for first time
            if self.INPUTS == []:
                self.reset_btn.setEnabled(True)
                self.output_btn.setEnabled(True)
                self.extract_btn.setEnabled(True)
                self.refresh_btn.setEnabled(True)
                self.extract_sgmnt.setEnabled(True)
                self.extract_sgmnt.setCurrentItem("file")

                self.input_badge = scshub_badge(self.top_card, self.input_btn)

            for file in file_path:
                self.INPUTS.append(file)

            # set export path to (<firstSelectedFile>_exp)
            if self.OUTPUT == "":
                output_path = f"{self.INPUTS[0][:-4]}_exp"

                self.OUTPUT = output_path

                self.output_btn.setToolTip(output_path)

                self.output_badge = scshub_badge(self.top_card, self.output_btn)

            # set buttons tooltip
            tooltip = ""
            for file in self.INPUTS:
                tooltip += f"{file}\n"

            self.input_btn.setToolTip(tooltip[:-1])

            scshub_infobar(self.INFOBAR_POS, "success", self.tr("File imported"))
            logger.info(f'Set input file to "{self.INPUTS}"')

            self.add_root_item()
            self.go_home()

    def get_folder(self):

        folder_dialog = QFileDialog().getExistingDirectory(self, "Select folder")

        # only if folder selected
        if folder_dialog:
            folder_path = folder_dialog

            self.OUTPUT = folder_path

            self.output_btn.setToolTip(folder_path)

            scshub_infobar(self.INFOBAR_POS, "success", self.tr("Folder selected"))
            logger.info(f'Set output folder to "{folder_path}"')

    def downloader(self):

        self.downloader_process = Downloader(logger, PIX_CONVERTER_URL, PIX_CONVERTER_PATH)
        self.downloader_process.started.connect(self.downloader_start)
        self.downloader_process.result.connect(self.downloader_finish)
        self.downloader_process.start()

    def downloader_start(self):

        self.download_infobar = InfoBar.new(
            InfoBarIcon.INFORMATION,
            self.tr("Downloading"),
            "",
            Qt.Horizontal,
            False,
            -1,
            InfoBarPosition.TOP,
            self.INFOBAR_POS,
        )
        ring_wgt = IndeterminateProgressRing(self)
        ring_wgt.setFixedSize(22, 22)
        ring_wgt.setStrokeWidth(4)
        self.download_infobar.addWidget(ring_wgt)

        self.download_btn.setDisabled(True)

    def downloader_finish(self, result: int):

        self.download_infobar.close()

        match result:
            case 0:
                signal_bus.pix_exist.emit(True)

                scshub_infobar(self.INFOBAR_POS, "success", self.tr("Downloaded"))

            case 1:
                signal_bus.pix_exist.emit(False)

                scshub_infobar(self.INFOBAR_POS, "error", self.tr("Error during download"))

    def tools_exist(self, exist):

        if exist:
            self.input_btn.setEnabled(True)
            self.download_btn.hide()
            self.download_btn.setDisabled(True)

            logger.info(f"{NAME} exist")

        else:
            self.input_btn.setDisabled(True)
            self.download_btn.show()
            self.download_btn.setEnabled(True)

            logger.info(f"{NAME} not exist")
