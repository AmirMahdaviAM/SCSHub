import re
import logging

from PyQt5.QtCore import Qt, QProcess, QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QWidget, QFileDialog, QVBoxLayout

from qfluentwidgets import ToolTipFilter, FluentIcon

from ..ui.pix_hasher_fil_ui import PixFileHasherUi
from ..ui.pix_hasher_str_ui import PixStringHasherUi
from ...common.tool import signal_bus, scshub_infobar, scshub_badge
from ...common.info import PIX_CONVERTER_PATH

NAME = "PIXHasher"

logger = logging.getLogger(NAME)


class PixFileHasher(QWidget, PixFileHasherUi):

    def __init__(self, infobar_pos):
        super().__init__()

        self.INFOBAR_POS = infobar_pos

        self.INPUT = ""

        self.setupUi(self)
        self.init_ui()

        signal_bus.pix_exist.connect(
            lambda bool: (
                self.input_btn.setEnabled(True) if bool else self.input_btn.setDisabled(True)
            )
        )

    def init_ui(self):

        self.top_card_lyt.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.input_btn.setIcon(FluentIcon.DOWN)
        self.input_btn.clicked.connect(lambda: self.get_file())
        self.input_btn.installEventFilter(ToolTipFilter(self.input_btn))

    def calculate_process(self):

        command = f'"{PIX_CONVERTER_PATH}" --calc-cityhash64-file "{self.INPUT}"'

        logger.info(command)

        self.main_process = QProcess()
        self.main_process.setProcessChannelMode(QProcess.MergedChannels)
        self.main_process.readyRead.connect(self.calculate_output)
        self.main_process.waitForFinished(100)
        self.main_process.start(command)

    def calculate_output(self):

        # get output data from process and decode it
        output = self.main_process.readAllStandardOutput()
        decoded_output = bytes(output).decode("utf-8")
        splitted_output = decoded_output.splitlines()

        for line in splitted_output:
            if line.startswith("CityHash64"):
                rgx_find = re.findall(r"CityHash64[\S]*\s\S\s([0-9]*)\s\(([a-zA-Z0-9]*)\)", line)
                self.hash_line.setText((rgx_find[0][0]))
                self.hex_line.setText((rgx_find[0][1]))

    def get_file(self):

        file_dialog = QFileDialog().getOpenFileName(self, "Select file")

        # only if file selected
        if file_dialog[0]:
            file_path = file_dialog[0].replace("/", "\\")

            self.INPUT = file_path

            self.input_btn.setToolTip(file_path)

            scshub_badge(self.top_card, self.input_btn)

            scshub_infobar(self.INFOBAR_POS, "success", self.tr("File imported"))
            logger.info(f'Set input file to "{file_path}"')

            self.calculate_process()


class PixStringHasher(QWidget, PixStringHasherUi):

    def __init__(self, infobar_pos):
        super().__init__()

        self.INFOBAR_POS = infobar_pos

        self.setupUi(self)
        self.init_ui()

        signal_bus.pix_exist.connect(
            lambda bool: (
                self.input_line.setEnabled(True) if bool else self.input_line.setDisabled(True)
            )
        )

    def init_ui(self):

        self.input_line.textChanged.connect(self.calculate_process)
        self.input_line.returnPressed.connect(lambda: self.calculate_process())
        self.input_line.setValidator(QRegExpValidator(QRegExp("[\S]*")))

    def calculate_process(self):

        if self.input_line.text() != "":
            command = f'"{PIX_CONVERTER_PATH}" --calc-cityhash64 {self.input_line.text()}'

            logger.info(command)

            self.main_process = QProcess()
            self.main_process.setProcessChannelMode(QProcess.MergedChannels)
            self.main_process.readyRead.connect(self.calculate_output)
            self.main_process.waitForFinished(100)
            self.main_process.start(command)

        else:
            self.hash_line.setText("")
            self.hex_line.setText("")

    def calculate_output(self):

        # get output data from process and decode it
        output = self.main_process.readAllStandardOutput()
        decoded_output = bytes(output).decode("utf-8")
        splitted_output = decoded_output.splitlines()

        for line in splitted_output:
            if line.startswith("CityHash64"):
                rgx_find = re.findall(r"CityHash64[\S]*\s\S\s([0-9]*)\s\(([a-zA-Z0-9]*)\)", line)
                self.hash_line.setText((rgx_find[0][0]))
                self.hex_line.setText((rgx_find[0][1]))


class PixHasherWidget(QWidget):

    def __init__(self, infobar_pos):
        super().__init__()

        self.INFOBAR_POS = infobar_pos

        self.main_lyt = QVBoxLayout(self)
        self.main_lyt.setContentsMargins(0, 0, 0, 0)
        self.main_lyt.setSpacing(20)
        self.main_lyt.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.hash_file = PixFileHasher(infobar_pos)
        self.hash_string = PixStringHasher(infobar_pos)

        self.main_lyt.addWidget(self.hash_file)
        self.main_lyt.addWidget(self.hash_string)
