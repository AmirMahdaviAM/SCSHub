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

from ..ui.scs_extractor_ui import ScsExtractorUi
from ...common.tool import (
    Downloader,
    signal_bus,
    scshub_log,
    scshub_badge,
    scshub_infobar,
    scshub_file_remover,
)
from ...common.info import (
    SCS_EXTRACTOR_LOG,
    SCS_TOOL_UNZIP,
    SCS_TOOL_PATH,
    SCS_TOOL_URL,
    SCS_TOOL_ZIP,
)


NAME = "SCSExtractor"

logger = logging.getLogger(NAME)


class ScsExtractorWidget(QWidget, ScsExtractorUi):

    def __init__(self, infobar_pos):
        super().__init__()

        self.INFOBAR_POS = infobar_pos

        self.INPUT = ""
        self.OUTPUT = ""

        self.TEMP_OUT = []
        self.TEMP_LOG = []

        self.main_process = None

        self.setupUi(self)
        self.init_ui()

        signal_bus.scs_exist.connect(self.tools_exist)

        scshub_file_remover(SCS_EXTRACTOR_LOG)

    def init_ui(self):

        self.top_card_lyt.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.download_btn.setIcon(FluentIcon.DOWNLOAD)
        self.download_btn.clicked.connect(lambda: self.downloader())
        self.download_btn.hide()

        self.input_btn.setIcon(FluentIcon.DOWN)
        self.input_btn.clicked.connect(lambda: self.get_file())
        self.input_btn.installEventFilter(ToolTipFilter(self.input_btn))

        self.output_btn.setIcon(FluentIcon.UP)
        self.output_btn.clicked.connect(lambda: self.get_folder())
        self.output_btn.installEventFilter(ToolTipFilter(self.output_btn))

        self.extract_btn.setIcon(FluentIcon.LINK)
        self.extract_btn.clicked.connect(lambda: self.extractor_process())

        self.iobuffer_chk.stateChanged.connect(
            lambda state: (
                self.iobuffer_spn.setEnabled(True) if state else self.iobuffer_spn.setDisabled(True)
            )
        )
        self.iobuffer_chk.installEventFilter(ToolTipFilter(self.iobuffer_chk))

    def extractor_process(self):

        command = f'"{SCS_TOOL_PATH}" extract "{self.INPUT}" -root "{self.OUTPUT}"'

        if self.iobuffer_chk.isChecked():
            command += f" -io-buffers-size {self.iobuffer_spn.text()[:-3]}"

        logger.info(command)

        if self.main_process == None:
            self.main_process = QProcess()
            self.main_process.setProcessChannelMode(QProcess.MergedChannels)
            self.main_process.readyRead.connect(self.extractor_output)
            self.main_process.stateChanged.connect(self.extractor_state)
            self.main_process.finished.connect(self.extractor_finish)
            self.main_process.waitForFinished(100)
            self.main_process.start(command)

    def extractor_output(self):

        # get output data from process and decode it
        output = self.main_process.readAllStandardOutput()
        decoded_output = bytes(output).decode("utf-8")
        splitted_output = decoded_output.splitlines()

        for line in splitted_output:
            striped_line = line.strip()
            if striped_line != "":
                self.TEMP_OUT.append(striped_line)

                if "error" in striped_line.lower() or "hashfs" in striped_line.lower():
                    self.TEMP_LOG.append(striped_line)

    def extractor_state(self, state):

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
            self.extract_btn.setDisabled(True)

            logger.info(f"{NAME} Running")

        elif state_name == "NotRunning":
            self.working_infobar.close()

            self.input_btn.setEnabled(True)
            self.output_btn.setEnabled(True)
            self.extract_btn.setEnabled(True)

            logger.info(f"{NAME} Finished")

    def extractor_finish(self):

        temp_out = ""
        for line in self.TEMP_OUT:
            temp_out += f"{line.lower()}\n"

        if "error" in temp_out:
            scshub_infobar(
                self.INFOBAR_POS,
                "error_btn",
                self.tr("Error occurred during process"),
                SCS_EXTRACTOR_LOG,
            )
            logger.error(f"Error occurred during process, check {SCS_EXTRACTOR_LOG}")

        else:
            scshub_infobar(
                self.INFOBAR_POS, "success_btn", self.tr("Process finished"), self.OUTPUT
            )
            logger.info("Process completed successfully")

        if self.TEMP_LOG != []:
            scshub_log(SCS_EXTRACTOR_LOG, self.TEMP_LOG)

        self.main_process = None
        self.TEMP_OUT = []
        self.TEMP_LOG = []

    def get_file(self):

        if platform == "win32":
            file_dialog = QFileDialog().getOpenFileName(
                self, "Select file", filter="SCS archive (*.scs)"
            )

            # only if file selected
            if file_dialog[0]:
                file_path = file_dialog[0].replace("/", "\\")

                # enable buttons after file selected for first time
                if self.INPUT == "":
                    self.output_btn.setEnabled(True)
                    self.extract_btn.setEnabled(True)
                    self.iobuffer_chk.setEnabled(True)

                self.INPUT = file_path

                output_path = f"{file_path[:-4]}_exp"
                self.OUTPUT = output_path

                self.input_btn.setToolTip(file_path)
                self.output_btn.setToolTip(output_path)

                scshub_badge(self.top_card, self.input_btn)
                scshub_badge(self.top_card, self.output_btn)

                scshub_infobar(self.INFOBAR_POS, "success", self.tr("File imported"))
                logger.info(f'Set input file to "{file_path}"')

        else:
            scshub_infobar(self.INFOBAR_POS, "error", self.tr("Only work in windows"))
            logger.error(f"{NAME} Not work in {platform}, {NAME} only work in windows")

    def get_folder(self):

        folder_dialog = QFileDialog().getExistingDirectory(self, "Select folder")

        # only if folder selected
        if folder_dialog:
            folder_path = folder_dialog.replace("/", "\\")

            self.OUTPUT = folder_path

            self.output_btn.setToolTip(folder_path)

            scshub_infobar(self.INFOBAR_POS, "success", self.tr("Folder selected"))
            logger.info(f'Set output folder to "{folder_path}"')

    def downloader(self):

        if platform == "win32":
            self.downloader_process = Downloader(logger, SCS_TOOL_URL, SCS_TOOL_ZIP, SCS_TOOL_UNZIP)
            self.downloader_process.started.connect(self.downloader_start)
            self.downloader_process.result.connect(self.downloader_finish)
            self.downloader_process.start()

        else:
            scshub_infobar(self.INFOBAR_POS, "error", self.tr("Only work in windows"))
            logger.error(f"{NAME} Not work in {platform}, {NAME} only work in windows")

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
                signal_bus.scs_exist.emit(True)

                scshub_infobar(self.INFOBAR_POS, "success", self.tr("Downloaded"))

            case 1:
                signal_bus.scs_exist.emit(False)

                scshub_infobar(self.INFOBAR_POS, "error", self.tr("Error during download"))

    def tools_exist(self, exist: bool):

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
