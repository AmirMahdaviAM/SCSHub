import os
import re
import logging
from sys import platform
from pathlib import Path

from PyQt5.QtCore import Qt, QProcess
from PyQt5.QtWidgets import QWidget, QFileDialog

from qfluentwidgets import (
    IndeterminateProgressRing,
    InfoBarPosition,
    ToolTipFilter,
    InfoBarIcon,
    FluentIcon,
    InfoBar,
    Flyout,
)

from ..ui.sxc_finder_ui import SxcFinderUi
from ...common.tool import (
    Downloader,
    signal_bus,
    scshub_log,
    scshub_badge,
    scshub_infobar,
    scshub_file_remover,
    scshub_file_remover,
)
from ...common.info import (
    SXC_EXTRACTOR_PATH,
    SXC_FINDER_PATH,
    SXC_FINDER_LOG,
    SXC_HDB_PATH,
    SXC_HDB_URL,
    SXC_UNZIP,
    SXC_ZIP,
    SXC_URL,
)


NAME = "SXCFinder"

logger = logging.getLogger(NAME)


class SxcFinderWidget(QWidget, SxcFinderUi):

    def __init__(self, infobar_pos):
        super().__init__()

        self.INFOBAR_POS = infobar_pos

        self.INPUT = ""
        self.OUTPUT = ""

        self.INPUT_HIDDEN = ""
        self.EXPORT_HIDDEN = ""

        self.TEMP_OUT = []
        self.TEMP_LOG = []

        self.main_process = None

        self.tutorial = True
        self.finder_first_run = True
        self.run_count = 0

        self.setupUi(self)
        self.init_ui()

        signal_bus.sxc_exist.connect(self.tools_exist)

        scshub_file_remover(SXC_FINDER_LOG)

    def init_ui(self):

        self.main_lyt.setAlignment(Qt.AlignmentFlag.AlignTop)
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

        self.run_btn.setIcon(FluentIcon.PLAY)
        self.run_btn.clicked.connect(lambda: self.finder_process())

    def finder_process(self):

        if self.tutorial:
            Flyout.create(
                title="",
                content="Click run button several times until\nmissing item became unchanged.",
                icon=InfoBarIcon.INFORMATION,
                target=self.run_btn,
                parent=self.top_card,
            )
            self.tutorial = False

        self.run_count += 1

        if self.finder_first_run == True:
            if not os.path.isfile(self.EXPORT_HIDDEN):
                with open(self.EXPORT_HIDDEN, "at", encoding="utf-8") as f:
                    f.write("manifest.sii\n")

            command = f'"{SXC_FINDER_PATH}" "{self.INPUT}" "{self.EXPORT_HIDDEN}"'

            logger.info(command)

            if self.main_process == None:
                self.main_process = QProcess()
                self.main_process.setProcessChannelMode(QProcess.MergedChannels)
                self.main_process.readyRead.connect(self.extractor_output)
                self.main_process.stateChanged.connect(self.extractor_state)
                self.main_process.finished.connect(self.finder_finish)
                self.main_process.waitForFinished(100)
                self.main_process.start(command)

        else:
            self.content_search()

    def finder_finish(self):

        temp_out = ""
        for line in self.TEMP_OUT:
            temp_out += f"{line.lower()}\n"

        self.log_txt.insertPlainText(f"{self.run_count:0>2}: SXCFinder:\n")

        if "error" in temp_out:
            scshub_infobar(
                self.INFOBAR_POS,
                "error_btn",
                self.tr("Error occurred during process"),
                SXC_FINDER_LOG,
            )
            logger.error(f"Error occurred during process, check {SXC_FINDER_LOG}")

        else:
            scshub_infobar(
                self.INFOBAR_POS, "success_btn", self.tr("Process finished"), self.OUTPUT
            )
            logger.info("Process completed successfully")

        if self.TEMP_LOG != []:
            scshub_log(SXC_FINDER_LOG, self.TEMP_LOG)

            for line in self.TEMP_LOG:
                self.log_txt.insertPlainText(line + "\n")

        self.log_txt.moveCursor(-1)
        self.log_txt.insertPlainText("\n")

        self.main_process = None
        self.TEMP_OUT = []
        self.TEMP_LOG = []

        self.finder_first_run = False

        self.extractor_process()

    def content_search(self):

        suffix = ["*.pmd", "*.mat", "*.tobj", "*.sii", "*.sui", "*.dat", "*.soundref", "*.font"]
        files = []
        length = 0

        for sfx in suffix:
            glob = list(self.INPUT_HIDDEN.rglob(sfx))
            if glob != []:
                for item in glob:
                    files.append(item)

        if not os.path.isdir(self.OUTPUT):
            os.mkdir(self.OUTPUT)

        try:
            if os.path.isdir(self.INPUT_HIDDEN):

                self.working_infobar = InfoBar.new(
                    InfoBarIcon.INFORMATION,
                    self.tr("Working"),
                    "",
                    Qt.Horizontal,
                    False,
                    -1,
                    InfoBarPosition.TOP,
                    self,
                )
                ring_wgt = IndeterminateProgressRing(self)
                ring_wgt.setFixedSize(22, 22)
                ring_wgt.setStrokeWidth(4)
                self.working_infobar.addWidget(ring_wgt)

                for file in files:

                    extracted_path = []
                    read_data = None

                    # binary encode
                    if file.name.endswith((".pmd", ".tobj")):
                        with open(file, "rb") as f:
                            read_data = f.read().decode("latin-1")

                        # main regex search
                        binery_rgx_find = re.findall(r"\/[a-zA-Z0-9_\.\/]*\.[a-zA-Z]{3}", read_data)

                        # append finded items to list
                        for item in binery_rgx_find:
                            if item not in extracted_path:
                                extracted_path.append(item)

                    # normal encode
                    else:
                        with open(file, "r", encoding="utf-8") as f:
                            read_data = f.read()

                        # main regex search
                        normal_rgx_find = re.findall(
                            r"\/[a-zA-Z0-9_\.\/]*\.[a-zA-Z]{3,8}", read_data
                        )
                        icon_rgx_find = re.findall(
                            r"(icon[\s\t]*:{1}[\s\t]*)\"([a-zA-Z0-9_\.\/]*)\"", read_data
                        )

                        # append finded items to list
                        for item in normal_rgx_find:
                            if item not in extracted_path:
                                extracted_path.append(item)
                                if item.endswith(".pmd"):
                                    extracted_path.append(f"{item[:-3]}pmg")
                                elif item.endswith(".bank"):
                                    extracted_path.append(f"{item}.guids")

                        # append finded items to list
                        for item in icon_rgx_find:
                            if item[1].endswith(".jpg"):
                                extracted_path.append(item[1])
                            else:
                                extracted_path.append(f"/material/ui/accessory/{item[1]}.mat")
                                extracted_path.append(f"/material/ui/accessory/{item[1]}.tobj")
                                extracted_path.append(f"/material/ui/accessory/{item[1]}.dds")

                    length += 1

                    # write to file
                    with open(self.EXPORT_HIDDEN, "at", encoding="utf-8") as f:
                        f.writelines(paths + "\n" for paths in extracted_path)

                self.log_txt.insertPlainText(f"{self.run_count:0>2}: File Content Search:\n")
                self.log_txt.insertPlainText(f"Total {length} items found.")
                self.log_txt.insertPlainText("\n")
                self.log_txt.moveCursor(-1)
                self.log_txt.insertPlainText("\n")

                self.working_infobar.close()

                self.extractor_process()

        except Exception as msg:
            scshub_log(SXC_FINDER_LOG, msg)

            scshub_infobar(
                self.INFOBAR_POS,
                "error_btn",
                self.tr("Error occurred during process"),
                SXC_FINDER_LOG,
            )

    def extractor_process(self):

        if not os.path.isdir(self.OUTPUT):
            os.mkdir(self.OUTPUT)

        if not os.path.isfile(self.EXPORT_HIDDEN):
            with open(self.EXPORT_HIDDEN, "at", encoding="utf-8") as f:
                f.write("manifest.sii\n")

        command = f'"{SXC_EXTRACTOR_PATH}" "{self.INPUT}" -o "{self.OUTPUT}" -lq -af -bl "{self.EXPORT_HIDDEN}"'

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

        print(decoded_output)

        for line in splitted_output:
            striped_line = line.strip()
            if striped_line != "":
                self.TEMP_OUT.append(striped_line)

                if (
                    "total" in striped_line.lower()
                    or "processed" in striped_line.lower()
                    or "elapsed" in striped_line.lower()
                    or "error" in striped_line.lower()
                    or "invalid" in striped_line.lower()
                    or "found" in striped_line.lower()
                    or "unable to open" in striped_line.lower()
                ):
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
            self.run_btn.setDisabled(True)

            logger.info(f"{NAME} Running")

        elif state_name == "NotRunning":
            self.working_infobar.close()

            self.input_btn.setEnabled(True)
            self.output_btn.setEnabled(True)
            self.run_btn.setEnabled(True)

            logger.info(f"{NAME} Finished")

    def extractor_finish(self):

        temp_out = ""
        for line in self.TEMP_OUT:
            temp_out += f"{line.lower()}\n"

        self.log_txt.insertPlainText(f"{self.run_count:0>2}: SXCExtractor:\n")

        if (
            "error" in temp_out
            or "invalid" in temp_out
            or "missing" in temp_out
            or "not found" in temp_out
        ):
            scshub_infobar(
                self.INFOBAR_POS,
                "error_btn",
                self.tr("Error occurred during process"),
                SXC_FINDER_LOG,
            )
            logger.error(f"Error occurred during process, check {SXC_FINDER_LOG}")

        elif "warning" in temp_out:
            scshub_infobar(
                self.INFOBAR_POS,
                "warn_btn",
                self.tr("Process finished with warnings"),
                SXC_FINDER_LOG,
            )
            logger.warning(f"Process finished with warnings, check {SXC_FINDER_LOG}")

        else:
            scshub_infobar(
                self.INFOBAR_POS, "success_btn", self.tr("Process finished"), self.OUTPUT
            )
            logger.info("Process completed successfully")

        if self.TEMP_LOG != []:
            scshub_log(SXC_FINDER_LOG, self.TEMP_LOG)

            for line in self.TEMP_LOG:
                self.log_txt.insertPlainText(line + "\n")

        self.log_txt.moveCursor(-1)
        self.log_txt.insertPlainText("\n")

        self.main_process = None
        self.TEMP_OUT = []
        self.TEMP_LOG = []

    def get_file(self):

        if platform == "win32":
            file_dialog = QFileDialog().getOpenFileName(
                self, "Select file", filter="SCS archive (*.scs *.zip)"
            )

            # only if file selected
            if file_dialog[0]:
                file_path = file_dialog[0].replace("/", "\\")

                # enable buttons after file selected for first time
                if self.INPUT == "":
                    self.run_btn.setEnabled(True)

                self.INPUT = file_path

                output_path = f"{file_path[:-4]}_exp"
                self.OUTPUT = output_path

                self.INPUT_HIDDEN = Path(self.OUTPUT)
                self.EXPORT_HIDDEN = f"{file_path[:-3]}txt"

                self.input_btn.setToolTip(file_path)
                self.output_btn.setToolTip(output_path)

                self.run_count = 0
                self.finder_first_run = True
                self.log_txt.setPlainText("")

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

            logger.info(f'Set output folder to "{folder_path}"')

            scshub_infobar(self.INFOBAR_POS, "success", self.tr("Folder selected"))

    def downloader(self):

        if platform == "win32":
            self.downloader_process = Downloader(logger, SXC_URL, SXC_ZIP, SXC_UNZIP)
            self.downloader_process.started.connect(self.downloader_start)
            self.downloader_process.result.connect(self.downloader_finish)
            self.downloader_process.finished.connect(self.downloader_hdb)
            self.downloader_process.start()

        else:
            scshub_infobar(self.INFOBAR_POS, "error", self.tr("Only work in windows"))
            logger.error(f"{NAME} Not work in {platform}, {NAME} only work in windows")

    def downloader_hdb(self):

        self.downloadHdbProcess = Downloader(logger, SXC_HDB_URL, SXC_HDB_PATH)
        self.downloadHdbProcess.started.connect(self.downloader_start)
        self.downloadHdbProcess.result.connect(self.downloader_finish)
        self.downloadHdbProcess.start()

    def downloader_start(self):

        self.download_infobar = InfoBar.new(
            InfoBarIcon.INFORMATION,
            self.tr("Downloading"),
            "",
            Qt.Horizontal,
            False,
            -1,
            InfoBarPosition.TOP,
            self,
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
                signal_bus.sxc_exist.emit(True)

                scshub_infobar(self.INFOBAR_POS, "success", self.tr("Downloaded"))

                # self.installer()

            case 1:
                signal_bus.sxc_exist.emit(False)

                scshub_infobar(self.INFOBAR_POS, "error", self.tr("Error during download"))

    def installer(self):

        folder_dialog = QFileDialog().getExistingDirectory(self, "Select game root folder")

        # only if folder selected
        if folder_dialog:
            folder_path = folder_dialog.replace("/", "\\")

            bat_file = f"{SXC_UNZIP}\\installer.bat"
            db_file = f"{SXC_UNZIP}\\dblist.txt"
            hashdb_file = f"{SXC_UNZIP}\\sxc.hdb"

            scshub_file_remover(bat_file)
            scshub_file_remover(db_file)
            scshub_file_remover(hashdb_file)

            # files = ["base", "base_map", "base_share", "base_vehicle", "core", "def", "effect", "locale"]
            files = ["base", "core", "def", "effect", "locale"]

            for file in files:
                if file == "core" or file == "locale":
                    command = f'"{SXC_EXTRACTOR_PATH}" "{folder_path}\\{file}.scs" -137243 -lq\n'
                else:
                    command = f'"{SXC_EXTRACTOR_PATH}" "{folder_path}\\{file}.scs" -lq\n'

                index_path = (
                    f"{folder_path}\\{file.capitalize()}.idx\n".replace(":\\", "-")
                    .replace("\\", "_")
                    .replace(" ", "-")
                )
                index = f"{SXC_UNZIP}\\{index_path}"

                with open(bat_file, "a", encoding="utf-8") as f:
                    f.write(command)

                with open(db_file, "a", encoding="utf-8") as f:
                    f.write(index)

            with open(bat_file, "a", encoding="utf-8") as f:
                f.write(f'"{SXC_EXTRACTOR_PATH}" -b "{db_file}"')

        self.installer_process = QProcess()
        self.installer_process.stateChanged.connect(self.installer_state)
        self.installer_process.start(f"{SXC_UNZIP}\installer.bat")

    def installer_state(self, state):

        states = {
            QProcess.NotRunning: "NotRunning",
            QProcess.Starting: "Starting",
            QProcess.Running: "Running",
        }
        state_name = states[state]

        if state_name == "Running":
            self.installer_infobar = InfoBar.new(
                InfoBarIcon.INFORMATION,
                self.tr("Indexing game files"),
                "",
                Qt.Horizontal,
                False,
                -1,
                InfoBarPosition.TOP,
                self.INFOBAR_POS,
            )
            ringWgt = IndeterminateProgressRing(self)
            ringWgt.setFixedSize(22, 22)
            ringWgt.setStrokeWidth(4)
            self.installer_infobar.addWidget(ringWgt)

        elif state_name == "NotRunning":
            self.installer_infobar.close()

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
