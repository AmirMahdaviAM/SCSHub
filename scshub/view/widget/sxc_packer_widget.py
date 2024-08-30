import os
import logging
from sys import platform

from PyQt5.QtCore import Qt, QProcess
from PyQt5.QtWidgets import QWidget, QFileDialog

from qfluentwidgets import (
    IndeterminateProgressRing,
    InfoBarPosition,
    ToolTipFilter,
    InfoBarIcon,
    FluentIcon,
    InfoBar,
)

from ..ui.sxc_packer_ui import SxcPackerUi
from ...common.tool import signal_bus, scshub_file_remover, scshub_infobar, scshub_badge, scshub_log
from ...common.info import SXC_PACKER_PATH, SXC_PACKER_LOG


NAME = "SXCPacker"

logger = logging.getLogger(NAME)


class SxcPackerWidget(QWidget, SxcPackerUi):

    def __init__(self, infobar_pos):
        super().__init__()

        self.INFOBAR_POS = infobar_pos

        self.INPUT = ""
        self.OUTPUT = ""

        self.ENCRYPT_FILE = ""
        self.HIDDEN_FILE = ""
        self.STORED_FILE = ""
        self.EXCLUDE_FILE = ""

        self.TEMP_OUT = []
        self.TEMP_LOG = []

        self.main_process = None

        self.setupUi(self)
        self.init_ui()
        self.option_ui()

        signal_bus.sxc_exist.connect(
            lambda exist: (
                self.input_btn.setEnabled(True) if exist else self.input_btn.setDisabled(True)
            )
        )

        scshub_file_remover(SXC_PACKER_LOG)

    def init_ui(self):

        self.main_lyt.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.top_card_lyt.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.input_btn.setIcon(FluentIcon.DOWN)
        self.input_btn.clicked.connect(lambda: self.get_folder())
        self.input_btn.installEventFilter(ToolTipFilter(self.input_btn))

        self.output_btn.setIcon(FluentIcon.UP)
        self.output_btn.clicked.connect(lambda: self.get_save_file())
        self.output_btn.installEventFilter(ToolTipFilter(self.output_btn))

        self.pack_btn.setIcon(FluentIcon.ZIP_FOLDER)
        self.pack_btn.clicked.connect(lambda: self.packer_process())

    def option_ui(self):

        # encrypt list | -e
        self.encrypt_chk.installEventFilter(ToolTipFilter(self.encrypt_chk))
        self.encrypt_btn.installEventFilter(ToolTipFilter(self.encrypt_btn))
        self.checkbox_state(self.encrypt_chk, self.encrypt_btn)
        self.encrypt_btn.clicked.connect(lambda: self.get_file("encrypt"))

        # hidden list | -h
        self.hidden_chk.installEventFilter(ToolTipFilter(self.hidden_chk))
        self.hidden_btn.installEventFilter(ToolTipFilter(self.hidden_btn))
        self.checkbox_state(self.hidden_chk, self.hidden_btn)
        self.hidden_btn.clicked.connect(lambda: self.get_file("hidden"))

        # stored list | -s
        self.stored_chk.installEventFilter(ToolTipFilter(self.stored_chk))
        self.stored_btn.installEventFilter(ToolTipFilter(self.stored_btn))
        self.checkbox_state(self.stored_chk, self.stored_btn)
        self.stored_btn.clicked.connect(lambda: self.get_file("stored"))

        # exclude list | -x
        self.exclude_chk.installEventFilter(ToolTipFilter(self.exclude_chk))
        self.exclude_btn.installEventFilter(ToolTipFilter(self.exclude_btn))
        self.checkbox_state(self.exclude_chk, self.exclude_btn)
        self.exclude_btn.clicked.connect(lambda: self.get_file("exclude"))

    def checkbox_state(self, checkbox: QWidget, widget: QWidget):

        checkbox.stateChanged.connect(
            lambda state: widget.setEnabled(True) if state else widget.setDisabled(True)
        )

    def packer_process(self):

        command = f'"{SXC_PACKER_PATH}" -i "{self.INPUT}" -o "{self.OUTPUT}"'

        if self.encrypt_chk.isChecked() and self.ENCRYPT_FILE != "":
            command += f" -e {self.ENCRYPT_FILE}"

        if self.hidden_chk.isChecked() and self.HIDDEN_FILE != "":
            command += f" -h {self.HIDDEN_FILE}"

        if self.stored_chk.isChecked() and self.STORED_FILE != "":
            command += f" -s {self.STORED_FILE}"

        if self.exclude_chk.isChecked() and self.EXCLUDE_FILE != "":
            command += f" -x {self.EXCLUDE_FILE}"

        logger.info(command)

        if self.main_process == None:
            self.main_process = QProcess()
            self.main_process.setProcessChannelMode(QProcess.MergedChannels)
            self.main_process.readyRead.connect(self.packer_output)
            self.main_process.stateChanged.connect(self.packer_state)
            self.main_process.finished.connect(self.packer_finish)
            self.main_process.waitForFinished(100)
            self.main_process.start(command)

    def packer_output(self):

        # get output data from process and decode it
        output = self.main_process.readAllStandardOutput()
        decoded_output = bytes(output).decode("utf-8")
        splitted_output = decoded_output.splitlines()

        for line in splitted_output:
            striped_line = line.strip()
            if striped_line != "":
                self.TEMP_OUT.append(striped_line)

                if (
                    "total" in striped_line.lower()
                    or "processed" in striped_line.lower()
                    or "time" in striped_line.lower()
                    or "error" in striped_line.lower()
                    or "found" in striped_line.lower()
                ):
                    self.TEMP_LOG.append(striped_line)

    def packer_state(self, state):

        states = {
            QProcess.NotRunning: "NotRunning",
            QProcess.Starting: "Starting",
            QProcess.Running: "Running",
        }
        state_name = states[state]

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

            self.input_btn.setDisabled(True)
            self.output_btn.setDisabled(True)
            self.pack_btn.setDisabled(True)

            logger.info(f"{NAME} Running")

        elif state_name == "NotRunning":
            self.working_infobar.close()

            self.input_btn.setEnabled(True)
            self.output_btn.setEnabled(True)
            self.pack_btn.setEnabled(True)

            logger.info(f"{NAME} Finished")

    def packer_finish(self):

        temp_out = ""
        for line in self.TEMP_OUT:
            temp_out += f"{line.lower()}\n"

        if "error" in temp_out or "unable" in temp_out or "unhandled" in temp_out:
            scshub_infobar(
                self.INFOBAR_POS,
                "error_btn",
                self.tr("Error occurred during process"),
                SXC_PACKER_LOG,
            )
            logger.error(f"Error occurred during process, check {SXC_PACKER_LOG}")

        elif "warning" in temp_out:
            scshub_infobar(
                self.INFOBAR_POS,
                "warn_btn",
                self.tr("Process finished with warnings"),
                SXC_PACKER_LOG,
            )
            logger.warning(f"Process finished with warnings, check {SXC_PACKER_LOG}")

        else:
            scshub_infobar(
                self.INFOBAR_POS,
                "success_btn",
                self.tr("Process finished"),
                os.path.split(self.OUTPUT)[0],
            )
            logger.info("Process completed successfully")

        if self.TEMP_LOG != []:
            scshub_log(SXC_PACKER_LOG, self.TEMP_LOG)

            for line in self.TEMP_LOG:
                self.log_txt.insertPlainText(line + "\n")

        self.log_txt.moveCursor(-1)
        self.log_txt.insertPlainText("\n")

        self.main_process = None
        self.TEMP_OUT = []
        self.TEMP_LOG = []

    def get_file(self, mode: str):

        file_dialog = QFileDialog().getOpenFileName(self, "Select file", filter="Text file (*.txt)")

        # only if file selected
        if file_dialog[0]:
            file_path = file_dialog[0].replace("/", "\\")

            match mode:
                case "encrypt":
                    self.ENCRYPT_FILE = file_path

                    self.encrypt_btn.setToolTip(file_path)

                    scshub_badge(self.top_card, self.encrypt_btn)

                    logger.info(f'Set encrypt file to "{file_path}"')

                case "hidden":
                    self.HIDDEN_FILE = file_path

                    self.hidden_btn.setToolTip(file_path)

                    scshub_badge(self.top_card, self.hidden_btn)

                    logger.info(f'Set hidden file to "{file_path}"')

                case "stored":
                    self.STORED_FILE = file_path

                    self.stored_btn.setToolTip(file_path)

                    scshub_badge(self.top_card, self.stored_btn)

                    logger.info(f'Set stored file to "{file_path}"')

                case "exclude":
                    self.EXCLUDE_FILE = file_path

                    self.exclude_btn.setToolTip(file_path)

                    scshub_badge(self.top_card, self.exclude_btn)

                    logger.info(f'Set exclude file to "{file_path}"')

        scshub_infobar(self.INFOBAR_POS, "success", self.tr("File imported"))

    def get_folder(self):

        if platform == "win32":
            folder_dialog = QFileDialog().getExistingDirectory(self, "Select folder")

            # only if folder selected
            if folder_dialog:
                folder_path = folder_dialog.replace("/", "\\")

                # enable buttons after file selected for first time
                if self.INPUT == "":
                    self.output_btn.setEnabled(True)
                    self.pack_btn.setEnabled(True)
                    self.encrypt_chk.setEnabled(True)
                    self.hidden_chk.setEnabled(True)
                    self.stored_chk.setEnabled(True)
                    self.exclude_chk.setEnabled(True)

                self.INPUT = folder_path

                output_path = f"{folder_path}.scs"
                self.OUTPUT = output_path

                self.input_btn.setToolTip(folder_path)
                self.output_btn.setToolTip(output_path)

                scshub_badge(self.top_card, self.input_btn)
                scshub_badge(self.top_card, self.output_btn)

                scshub_infobar(self.INFOBAR_POS, "success", self.tr("Folder imported"))
                logger.info(f'Set input folder to "{folder_path}"')

        else:
            scshub_infobar(self.INFOBAR_POS, "error", self.tr("Only work in windows"))
            logger.error(f"{NAME} Not work in {platform}, {NAME} only work in windows")

    def get_save_file(self):

        file_dialog = QFileDialog().getSaveFileName(self, "Save file", filter="SCS archive (*.scs)")

        # only if file selected
        if file_dialog[0]:
            file_path = file_dialog[0].replace("/", "\\")

            self.OUTPUT = file_path

            self.output_btn.setToolTip(file_path)

            scshub_infobar(self.INFOBAR_POS, "success", self.tr("File imported"))
            logger.info(f'Set output file to "{file_path}"')
