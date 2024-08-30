import os
import logging
import binascii
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QWidget, QFileDialog

from qfluentwidgets import ToolTipFilter, FluentIcon, Flyout, InfoBarIcon

from ..ui.tobj_editor_ui import TobjEditorUi
from ...common.tool import scshub_file_remover, scshub_infobar, scshub_badge


NAME = "TOBJEditor"

logger = logging.getLogger(NAME)


class TobjEditorWidget(QWidget, TobjEditorUi):

    def __init__(self, infobar_pos):
        super().__init__()

        self.INFOBAR_POS = infobar_pos

        self.INPUT = ""
        self.OUTPUT = ""

        self.ORG_VALUE = {}

        self.UNKNOWN40 = "0000000000000000000000000000000001000000"  # empty unknown hex
        self.UNKNOWN08 = "00000000"  # empty unknown hex
        self.UNKNOWN04 = "0001"  # empty unknown hex
        self.UNKNOWN02 = "00"  # empty unknown hex

        # ve ve ve ve  uk uk uk uk  uk uk uk uk  uk uk uk uk
        # uk uk uk uk  01 uk uk uk  ty uk mg mn  mp uk au av
        # aw nc uk na  uk uk cc uk  le le le le  uk uk uk uk

        self.FILENAME = ""  # filename.tobj
        self.VESRION = "010ab170"  # default
        self.TYPE = "02"  # 02 generic, 05 cubic
        self.ADDR_U = "02"  # 00 repeat, 01 clamp, 02 clamp_to_edge, 03 clamp_to_border, 04 mirror, 05 mirror_clamp, 06 mirror_clamp_to_edge
        self.ADDR_V = "02"  # 00 repeat, 01 clamp, 02 clamp_to_edge, 03 clamp_to_border, 04 mirror, 05 mirror_clamp, 06 mirror_clamp_to_edge
        self.ADDR_W = "02"  # 00 repeat, 01 clamp, 02 clamp_to_edge, 03 clamp_to_border, 04 mirror, 05 mirror_clamp, 06 mirror_clamp_to_edge
        self.MAG_FILTER = "03"  # 00 nearest, 01 linear, 03 default
        self.MIN_FILTER = "03"  # 00 nearest, 01 linear, 03 default
        self.MIPMAP_FILTER = "03"  # 00 nearest, 01 trilinear, 02 nomipmaps, 03 default
        self.COLOR_SPACE = "00"  # 00 srgb, 01 tsnormal & linear
        self.USAGE = "00"
        self.NO_COMPRESS = "00"  # 00 false, 01 true
        self.NO_ANISOTROPIC = "00"  # 00 false, 01 true
        self.LENGTH = "22000000"  # texture path character length hex number
        self.TEXTURE_PATH = "/vehicle/truck/share/dashboard.dds"  # path to dds texture

        self.preview_img_buffer = BytesIO()
        self.preview_img = QImage()
        self.preview_temp_buffer = BytesIO()
        self.preview_temp = QImage()

        self.setupUi(self)
        self.temp_texture()
        self.init_ui()
        self.option_ui()
        self.preview()

    def init_ui(self):

        self.main_lyt.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.top_card_lyt.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.input_btn.setIcon(FluentIcon.DOWN)
        self.input_btn.clicked.connect(lambda: self.get_file())
        self.input_btn.installEventFilter(ToolTipFilter(self.input_btn))

        self.output_btn.setIcon(FluentIcon.UP)
        self.output_btn.clicked.connect(lambda: self.get_folder())
        self.output_btn.installEventFilter(ToolTipFilter(self.output_btn))

        self.output_badge = False

        self.revert_btn.setIcon(FluentIcon.UPDATE)
        self.revert_btn.clicked.connect(lambda: self.revert_value())
        self.revert_btn.installEventFilter(ToolTipFilter(self.revert_btn))

        self.save_btn.setIcon(FluentIcon.SAVE)
        self.save_btn.clicked.connect(lambda: self.write_file())
        self.save_btn.installEventFilter(ToolTipFilter(self.save_btn))

        self.save_sgmnt.addItem("binary", self.tr("Binary"))
        self.save_sgmnt.addItem("text", self.tr("Text"))
        self.save_sgmnt.setCurrentItem("binary")
        self.save_sgmnt.installEventFilter(ToolTipFilter(self.save_sgmnt))

        self.filename_line.installEventFilter(ToolTipFilter(self.filename_line))

    def option_ui(self):

        self.cube_path_card.setDisabled(True)
        self.cube_path_card.hide()

        self.texture_path_line.textChanged.connect(lambda: self.change_value("texture"))

        self.type_items = {"Generic": "02"}
        self.addr_items = {
            "Repeat": "00",
            "Clamp": "01",
            "Clamp to Edge": "02",
            "Clamp to Border": "03",
            "Mirror": "04",
            "Mirror Clamp": "05",
            "Mirror Clamp to Edge": "06",
        }
        self.filter_items = {"Nearest": "00", "Linear": "01", "Default": "03"}
        self.mipmap_items = {
            "Nearest": "00",
            "Trilinear": "01",
            "No MipMaps": "02",
            "MipMaps": "03",
        }
        self.color_space_items = {"SRGB": "00", "Linear": "01"}
        self.usage_items = ["TSNormal", "Ui", "Default"]

        self.type_cmb.addItems(self.type_items.keys())
        self.type_cmb.setCurrentIndex(0)
        self.type_cmb.installEventFilter(ToolTipFilter(self.type_cmb))
        self.type_cmb.currentTextChanged.connect(lambda: self.change_value("type"))

        self.addr_u_cmb.addItems(self.addr_items.keys())
        self.addr_u_cmb.setCurrentIndex(1)
        self.addr_u_cmb.installEventFilter(ToolTipFilter(self.addr_u_cmb))
        self.addr_u_cmb.currentTextChanged.connect(lambda: self.change_value("addr_u"))

        self.addr_v_cmb.addItems(self.addr_items.keys())
        self.addr_v_cmb.setCurrentIndex(1)
        self.addr_v_cmb.installEventFilter(ToolTipFilter(self.addr_v_cmb))
        self.addr_v_cmb.currentTextChanged.connect(lambda: self.change_value("addr_v"))

        self.addr_w_cmb.setDisabled(True)
        # self.addr_w_cmb.addItems(self.addr_items.keys())
        # self.addr_w_cmb.setCurrentIndex(1)
        # self.addr_w_cmb.installEventFilter(ToolTipFilter(self.addr_w_cmb))
        # self.addr_w_cmb.currentTextChanged.connect(lambda: self.changeValue("addr_w"))

        self.mag_filter_cmb.addItems(self.filter_items.keys())
        self.mag_filter_cmb.setCurrentIndex(2)
        self.mag_filter_cmb.installEventFilter(ToolTipFilter(self.mag_filter_cmb))
        self.mag_filter_cmb.currentTextChanged.connect(lambda: self.change_value("mag_filter"))

        self.min_filter_cmb.addItems(self.filter_items.keys())
        self.min_filter_cmb.setCurrentIndex(1)
        self.min_filter_cmb.removeItem(2)
        self.min_filter_cmb.installEventFilter(ToolTipFilter(self.min_filter_cmb))
        self.min_filter_cmb.currentTextChanged.connect(lambda: self.change_value("min_filter"))

        self.mipmap_filter_cmb.addItems(self.mipmap_items.keys())
        self.mipmap_filter_cmb.setCurrentIndex(3)
        self.mipmap_filter_cmb.currentTextChanged.connect(
            lambda: self.change_value("mipmap_filter")
        )

        self.color_space_cmb.addItems(self.color_space_items.keys())
        self.color_space_cmb.installEventFilter(ToolTipFilter(self.color_space_cmb))
        self.color_space_cmb.currentTextChanged.connect(lambda: self.change_value("color_space"))

        self.usage_cmb.addItems(self.usage_items)
        self.usage_cmb.setCurrentIndex(2)
        self.usage_cmb.installEventFilter(ToolTipFilter(self.usage_cmb))
        self.usage_cmb.currentTextChanged.connect(lambda: self.change_value("usage"))

        self.no_compress_swch.checkedChanged.connect(lambda: self.change_value("no_compress"))

        self.no_nisotropic_swch.checkedChanged.connect(lambda: self.change_value("no_anisotropic"))

        self.texture_img.setBorderRadius(4, 4, 4, 4)

    def revert_value(self):

        if self.ORG_VALUE != {}:
            self.FILENAME = self.ORG_VALUE["filename"]
            self.TEXTURE_PATH = self.ORG_VALUE["texture_path"]
            self.TYPE = self.ORG_VALUE["type"]
            self.ADDR_U = self.ORG_VALUE["addr_u"]
            self.ADDR_V = self.ORG_VALUE["addr_v"]
            self.ADDR_W = self.ORG_VALUE["addr_w"]
            self.MAG_FILTER = self.ORG_VALUE["mag_filter"]
            self.MIN_FILTER = self.ORG_VALUE["min_filter"]
            self.MIPMAP_FILTER = self.ORG_VALUE["mipmap_filter"]
            self.COLOR_SPACE = self.ORG_VALUE["color_space"]
            self.USAGE = self.ORG_VALUE["usage"]
            self.NO_COMPRESS = self.ORG_VALUE["no_compress"]
            self.NO_ANISOTROPIC = self.ORG_VALUE["no_anisotropic"]
            self.LENGTH = self.ORG_VALUE["length"]

            self.updateUi()

    def updateUi(self):

        self.filename_line.setText(self.FILENAME)

        self.texture_path_line.setText(self.TEXTURE_PATH)

        self.addr_u_cmb.setCurrentIndex(int(self.ADDR_U[1]))
        self.addr_v_cmb.setCurrentIndex(int(self.ADDR_V[1]))
        self.addr_w_cmb.setCurrentIndex(int(self.ADDR_W[1]))

        if self.MAG_FILTER == "03":
            self.mag_filter_cmb.setCurrentIndex(2)
        else:
            self.mag_filter_cmb.setCurrentIndex(int(self.MAG_FILTER[1]))

        if self.MIN_FILTER != "03":
            self.min_filter_cmb.setCurrentIndex(int(self.MIN_FILTER[1]))

        self.mipmap_filter_cmb.setCurrentIndex(int(self.MIPMAP_FILTER[1]))

        self.color_space_cmb.setCurrentIndex(int(self.COLOR_SPACE[1]))

        self.usage_cmb.setCurrentIndex(int(self.USAGE[1]))

        if self.NO_COMPRESS == "01":
            self.no_compress_swch.setChecked(True)
        else:
            self.no_compress_swch.setChecked(False)

        if self.NO_ANISOTROPIC == "01":
            self.no_nisotropic_swch.setChecked(True)
        else:
            self.no_nisotropic_swch.setChecked(False)

        self.preview()

    def change_value(self, attribute: str):

        match attribute:
            case "texture":
                self.TEXTURE_PATH = self.texture_path_line.text()
                self.LENGTH = self.texture_path_length(self.TEXTURE_PATH)

            case "type":
                if self.type_cmb.currentIndex() == 0:
                    self.TYPE = "02"
                    self.addr_w_cmb.setDisabled(True)

            case "addr_u":
                self.ADDR_U = f"0{self.addr_u_cmb.currentIndex()}"

            case "addr_v":
                self.ADDR_V = f"0{self.addr_v_cmb.currentIndex()}"

            case "addr_w":
                if self.addr_w_cmb.isEnabled():
                    self.ADDR_W = f"0{self.addr_w_cmb.currentIndex()}"
                else:
                    self.ADDR_W = "03"

            case "mag_filter":
                if self.mag_filter_cmb.currentIndex() != 2:
                    self.MAG_FILTER = f"0{self.mag_filter_cmb.currentIndex()}"
                else:
                    self.MAG_FILTER = "03"

            case "min_filter":
                if self.min_filter_cmb.currentIndex() != 2:
                    self.MIN_FILTER = f"0{self.min_filter_cmb.currentIndex()}"
                else:
                    self.MIN_FILTER = "03"

            case "mipmap_filter":
                self.MIPMAP_FILTER = f"0{self.mipmap_filter_cmb.currentIndex()}"

            case "color_space":
                self.COLOR_SPACE = f"0{self.color_space_cmb.currentIndex()}"

            case "usage":
                if self.usage_cmb.currentIndex() == 1:
                    self.mipmap_filter_cmb.setCurrentIndex(2)
                    self.mipmap_filter_cmb.setDisabled(True)
                    self.no_compress_swch.setChecked(True)
                    self.no_compress_swch.setDisabled(True)
                    self.MIPMAP_FILTER = "02"
                    self.NO_COMPRESS = "01"
                else:
                    self.mipmap_filter_cmb.setCurrentIndex(3)
                    self.mipmap_filter_cmb.setEnabled(True)
                    self.no_compress_swch.setChecked(False)
                    self.no_compress_swch.setEnabled(True)
                    self.MIPMAP_FILTER = "03"
                    self.NO_COMPRESS = "00"

            case "no_compress":
                if self.no_compress_swch.isChecked():
                    self.NO_COMPRESS = "01"
                else:
                    self.NO_COMPRESS = "00"

            case "no_anisotropic":
                if self.no_nisotropic_swch.isChecked():
                    self.NO_ANISOTROPIC = "01"
                else:
                    self.NO_ANISOTROPIC = "00"

        self.preview()

    def preview(self):

        # preview text
        # type
        preview_text = "map"
        preview_text += f"	2d"

        # texture_path
        if self.TEXTURE_PATH != "":
            preview_text += f"	{os.path.basename(self.TEXTURE_PATH)}"

        # addr_u, addr_v, addr_w
        preview_text += f'\naddr	{self.addr_u_cmb.currentText().lower().replace(" ", "_")}'

        preview_text += f'	{self.addr_v_cmb.currentText().lower().replace(" ", "_")}'

        if self.addr_w_cmb.isEnabled():
            preview_text += f'	{self.addr_w_cmb.currentText().lower().replace(" ", "_")}'

        # mag_filter, min_filter
        if self.mag_filter_cmb.currentIndex() != 2:
            preview_text += f'\nfilter	{self.mag_filter_cmb.currentText().lower().replace(" ", "")}'
            self.min_filter_cmb.setEnabled(True)

        else:
            self.min_filter_cmb.setDisabled(True)

        if self.min_filter_cmb.isEnabled():
            preview_text += f'	{self.min_filter_cmb.currentText().lower().replace(" ", "")}'

        # mipmap_filter
        if self.usage_cmb.currentIndex() != 1:
            if self.mipmap_filter_cmb.currentIndex() != 3:
                preview_text += f'\n{self.mipmap_filter_cmb.currentText().lower().replace(" ", "").replace("map", "")}'

        # color_space
        if self.color_space_cmb.currentIndex() == 1:
            preview_text += f"\ncolor_space	{self.color_space_cmb.currentText().lower()}"

        # usage
        if self.usage_cmb.currentIndex() != 2:
            preview_text += f"\nusage	{self.usage_cmb.currentText().lower()}"

        # no_compress
        if self.usage_cmb.currentIndex() != 1:
            if self.no_compress_swch.isChecked():
                preview_text += "\nnocompress"

        # no_anisotropic
        if self.no_nisotropic_swch.isChecked():
            preview_text += "\nnoanisotropic"

        self.preview_text_txt.setPlainText(preview_text)

        # preview binary
        preview_binary = f"01 0a  b1 70   00 00  00 00    00 00  00 00   00 00  00 00\n"
        preview_binary += f"00 00  00 00   01 00  00 00    {self.TYPE} 00  {self.MAG_FILTER} {self.MIN_FILTER}   {self.MIPMAP_FILTER} 00  {self.ADDR_U} {self.ADDR_V}\n"
        preview_binary += f"{self.ADDR_W} {self.NO_COMPRESS}  00 {self.NO_ANISOTROPIC}   00 01  {self.COLOR_SPACE} 00    {self.LENGTH[:2]} 00  00 00   00 00  00 00\n"
        preview_binary += self.TEXTURE_PATH

        self.preview_binary_txt.setPlainText(preview_binary)

    def temp_texture(self):

        preview_temp_img = Image.new("RGBA", (278, 278), (0, 0, 0, 10))
        ImageDraw.Draw(preview_temp_img).text(
            (44, 94),
            "No Texture\nFound",
            (0, 0, 0, 60),
            ImageFont.load_default(40),
            spacing=16,
            align="center",
        )
        preview_temp_img.save(self.preview_temp_buffer, "png")
        self.preview_temp_buffer.seek(0)

        self.preview_temp.loadFromData(self.preview_temp_buffer.getvalue())

        self.texture_img.setImage(self.preview_temp)
        self.texture_img.scaledToWidth(278)

    def load_texture(self):

        input_dds = f"{self.INPUT[:-4]}dds"

        if os.path.isfile(input_dds):

            input = Image.open(input_dds)
            input.save(self.preview_img_buffer, "png")
            self.preview_img_buffer.seek(0)

            self.preview_img.loadFromData(self.preview_img_buffer.getvalue())

            self.texture_img.setImage(self.preview_img)
            self.texture_img.scaledToWidth(278)

        else:
            self.texture_img.setImage(self.preview_temp)
            self.texture_img.scaledToWidth(278)

    def texture_path_length(self, file: str):

        return f"{hex(len(file))[2:]:0<8}"

    def read_file(self):

        with open(self.INPUT, "rb") as f:
            read_hex = f.read(48).hex()
            read_path = f.read().decode()

        self.ORG_VALUE = {
            "filename": os.path.basename(self.INPUT)[:-5],
            "texture_path": read_path,
            "type": read_hex[48:50],
            "addr_u": read_hex[60:62],
            "addr_v": read_hex[62:64],
            "addr_w": read_hex[64:66],
            "mag_filter": read_hex[52:54],
            "min_filter": read_hex[54:56],
            "mipmap_filter": read_hex[56:58],
            "color_space": read_hex[76:78],
            "usage": "02",
            "no_compress": read_hex[66:68],
            "no_anisotropic": read_hex[70:72],
            "length": read_hex[80:82],
        }

        self.revert_value()
        self.load_texture()

    def write_file(self):

        if self.OUTPUT == "":
            Flyout.create(
                title="Output path is not set",
                content="Import a tobj file or choose ouput folder",
                icon=InfoBarIcon.ERROR,
                target=self.save_btn,
                parent=self.top_card,
            )

        elif self.filename_line.text() == "":
            Flyout.create(
                title="File name is empty",
                content="Set name for file to be saved",
                icon=InfoBarIcon.ERROR,
                target=self.save_btn,
                parent=self,
            )

        else:
            final_binary = (
                self.VESRION
                + self.UNKNOWN40
                + self.TYPE
                + self.UNKNOWN02
                + self.MAG_FILTER
                + self.MIN_FILTER
                + self.MIPMAP_FILTER
                + self.UNKNOWN02
                + self.ADDR_U
                + self.ADDR_V
                + self.ADDR_W
                + self.NO_COMPRESS
                + self.UNKNOWN02
                + self.NO_ANISOTROPIC
                + self.UNKNOWN04
                + self.COLOR_SPACE
                + self.UNKNOWN02
                + self.LENGTH
                + self.UNKNOWN08
            )

            output_file = os.path.join(self.OUTPUT, f"{self.filename_line.text()}.tobj")

            scshub_file_remover(output_file)

            # binary mode
            if self.save_sgmnt._currentRouteKey == "binary":
                # write hex data
                with open(output_file, "xb") as f:
                    f.write(binascii.unhexlify(final_binary))

                # write texture path
                with open(output_file, "a") as f:
                    f.write(self.TEXTURE_PATH)

            # text mode
            elif self.save_sgmnt._currentRouteKey == "text":
                with open(output_file, "x", encoding="utf-8") as f:
                    f.write(self.preview_text_txt.toPlainText())

            scshub_infobar(
                self.INFOBAR_POS, "success_btn", self.tr("Process finished"), self.OUTPUT
            )
            logger.info("Process completed successfully")

    def get_file(self):

        file_dialog = QFileDialog().getOpenFileName(
            self, "Select file", filter="Tobj file (*.tobj)"
        )

        # only if file selected
        if file_dialog[0]:
            file_path = file_dialog[0].replace("/", "\\")

            # check for type
            with open(file_path, "rb") as f:
                read_hex = f.read(48).hex()

            # proces if tobj is in generic type
            if read_hex[48:50] == "02":

                # enable buttons after file selected for first time
                if self.INPUT == "":
                    self.save_btn.setEnabled(True)
                    self.revert_btn.setEnabled(True)

                self.INPUT = file_path
                self.OUTPUT = os.path.split(file_path)[0]

                self.input_btn.setToolTip(file_path)
                self.output_btn.setToolTip(self.OUTPUT)

                scshub_badge(self.top_card, self.input_btn)

                if self.output_badge == False:
                    scshub_badge(self.top_card, self.output_btn)
                    self.output_badge = True

                scshub_infobar(self.INFOBAR_POS, "success", self.tr("File imported"))
                logger.info(f'Set input file to "{file_path}"')

                self.read_file()

            else:
                scshub_infobar(self.INFOBAR_POS, "error", self.tr("Only generic tobj supported"))
                logger.error(f"Error loading tobj, only generic tobj supported")

    def get_folder(self):

        folder_dialog = QFileDialog().getExistingDirectory(self, "Select folder")

        # only if folder selected
        if folder_dialog:
            folder_path = folder_dialog.replace("/", "\\")

            # enable buttons after folder selected for first time
            if self.OUTPUT == "":
                self.save_btn.setEnabled(True)

            self.OUTPUT = folder_path

            self.output_btn.setToolTip(self.OUTPUT)

            if self.output_badge == False:
                scshub_badge(self.top_card, self.output_btn)
                self.output_badge = True

            scshub_infobar(self.INFOBAR_POS, "success", self.tr("Folder selected"))
            logger.info(f'Set output folder to "{self.OUTPUT}"')
