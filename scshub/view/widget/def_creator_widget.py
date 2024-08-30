import os
import logging

from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QWidget, QFileDialog

from qfluentwidgets import ToolTipFilter, FluentIcon, Flyout, InfoBarIcon, InfoLevel, setFont

from ..ui.def_creator_ui import DefCreatorUi
from ...common.tool import scshub_infobar, scshub_badge


NAME = "DefCreator"

logger = logging.getLogger(NAME)


class DefCreatorWidget(QWidget, DefCreatorUi):

    def __init__(self, infobar_pos):
        super().__init__()

        self.INFOBAR_POS = infobar_pos

        self.INPUT = ""
        self.OUTPUT = ""

        self.setupUi(self)
        self.init_ui()
        self.option_ui()
        self.toggle_template(0)
        self.preview()

        self.temp = 0
        self.done = False

    def init_ui(self):

        self.main_lyt.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.top_card_lyt.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.input_btn.setIcon(FluentIcon.DOWN)
        self.input_btn.clicked.connect(lambda: self.get_folder("input"))
        self.input_btn.installEventFilter(ToolTipFilter(self.input_btn))

        self.output_btn.setIcon(FluentIcon.UP)
        self.output_btn.clicked.connect(lambda: self.get_folder("output"))
        self.output_btn.installEventFilter(ToolTipFilter(self.output_btn))

        self.run_btn.setIcon(FluentIcon.PLAY)
        self.run_btn.clicked.connect(lambda: self.run())
        self.run_btn.installEventFilter(ToolTipFilter(self.run_btn))

        self.run_sgmnt.hide()
        # self.run_sgmnt.addItem("skip", self.tr("Skip exist"))
        # self.run_sgmnt.addItem("overwrite", self.tr("Overwrite"))
        # self.run_sgmnt.installEventFilter(ToolTipFilter(self.run_sgmnt))

        self.preview_name_lbl.setLevel(InfoLevel.INFOAMTION)
        setFont(self.preview_name_lbl, 12)

    def option_ui(self):

        self.option_lbl_lyt.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.option_wgt_lyt.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.truck_line.setValidator(QRegExpValidator(QRegExp("[a-z_0-9]{1,12}\.[a-z_0-9]{1,12}")))
        self.truck_line.installEventFilter(ToolTipFilter(self.truck_line))
        self.truck_line.textChanged.connect(lambda: self.preview())

        self.filename_cmb.addItems([self.tr("PMD filenames"), self.tr("Custom template")])
        self.filename_cmb.installEventFilter(ToolTipFilter(self.filename_cmb))
        self.filename_cmb.currentTextChanged.connect(lambda: self.preview())
        self.filename_cmb.currentIndexChanged.connect(self.toggle_template)

        self.template_line.setValidator(QRegExpValidator(QRegExp("[a-z_0-9]{1,10}")))
        self.template_line.installEventFilter(ToolTipFilter(self.template_line))
        self.template_line.textChanged.connect(lambda: self.preview())

        self.icon_line.setValidator(QRegExpValidator(QRegExp("[a-z_0-9/]*")))
        self.icon_line.installEventFilter(ToolTipFilter(self.icon_line))
        self.icon_line.textChanged.connect(lambda: self.preview())

    def toggle_template(self, index: int):

        if index == 0:
            self.template_lbl.hide()
            self.template_line.hide()
        else:
            self.template_lbl.show()
            self.template_line.show()

    def preview(self):

        # sii
        if self.filename_cmb.currentIndex() == 1:
            acc_file = f"{self.template_line.text()}01"
            acc_name = f'{self.template_line.text().capitalize().replace("_", " ")} 01'
        else:
            acc_file = "FILE"
            acc_name = "NAME"

        preview = f"accessory_addon_data : {acc_file}.{self.truck_line.text()}.FOLDER\n"
        preview += f'name: "{acc_name}"\n'
        preview += f"price: 100\n"
        preview += f"unlock: 0\n"

        if self.icon_line.text() == "":
            preview += f'icon: "truck/{self.truck_line.text().replace(".", "_")}/accessory/FOLDER/{acc_file}"\n'
        else:
            preview += f'icon: "{self.icon_line.text()}/{acc_file}"\n'

        preview += f'part_type: "factory"\n'
        preview += "\n"
        preview += f'exterior_model: "/vehicle/truck/TRUCK/accessory/FOLDER/FILE.pmd"'

        self.preview_txt.setPlainText(preview)
        self.preview_name_lbl.setText(f"{acc_file}.sii")

        # folder
        folder = f"Input accessories models folder (must be .../../vehicle/truck/xxxx_xxxx/accessory/):\n{self.INPUT}\n\n"

        folder += f"Output folder (must be .../../):\n{self.OUTPUT}\n\n"

        folder += f"Path to be make:\n.../../def/vehicle/{self.truck_line.text()}/accessory/..."

        self.folder_txt.setPlainText(folder)

    def sii_template(
        self,
        part: str,
        folder: str,
        name: str,
        price: int,
        ext_model: str,
    ):

        # header
        template = "SiiNunit\n{\n"
        template += f"accessory_addon_data : {part}.{self.truck_line.text()}.{folder}\n"

        # middle
        template += "{\n"
        template += f'	name: "{name}"\n'
        template += f"	price: {price}\n"
        template += f"	unlock: 0\n"

        if self.icon_line.text() == "":
            template += f'	icon: "truck/{self.truck_line.text().replace(".", "_")}/accessory/{folder}/{part}"\n'
        else:
            template += f'	icon: "{self.icon_line.text()}/{part}"\n'

        template += f'	part_type: "factory"\n'
        template += "\n"
        template += f'	exterior_model: "{ext_model}"\n'
        template += "}\n}\n"

        return template

    def execute(self):

        number = 1
        price = 100
        last_dir = ""

        for path, dirs, files in os.walk(self.INPUT):
            if files != []:
                for file in files:
                    if file.endswith((".pim", ".pmd")):
                        # check if current folder in accessory folder or not
                        # to prevent from other sub-folder involve
                        acc_root = os.path.split(path)
                        if acc_root[0] == self.INPUT:
                            # check if still in last folder or not
                            if acc_root[1] == last_dir:
                                number += 1
                                price += 100
                            else:
                                number = 1
                                price = 100
                            last_dir = acc_root[1]

                            # use pmd name
                            if self.filename_cmb.currentIndex() == 0:
                                acc_file = file[:-4]
                                acc_name = file[:-4].capitalize().replace("_", " ")
                                sii_filename = f"{file[:-3]}sii"

                            # use custom name
                            else:
                                acc_file = f"{self.template_line.text()}{number:0>2}"
                                acc_name = f'{self.template_line.text().capitalize().replace("_", " ")} {number:0>2}'
                                sii_filename = f"{acc_file}.sii"

                            # get (mod base folder)
                            base_path = os.path.basename(self.OUTPUT)
                            # get (model full path)
                            file_full_path = os.path.join(path, file)
                            # find (mod base folder) name in (model full path)
                            find_root = file_full_path.find(base_path) + len(base_path)
                            # remove unused address after (mod base folder) name from (model full path)
                            model_path = file_full_path[find_root:-3].replace("\\", "/")

                            # make accessories folders
                            def_dir = f"def/vehicle/truck/{self.truck_line.text()}/accessory/{acc_root[1]}"
                            sii_dir = os.path.join(self.OUTPUT, def_dir)
                            os.makedirs(sii_dir, exist_ok=True)

                            # sii template
                            acc = self.sii_template(
                                part=acc_file,
                                folder=acc_root[1],
                                name=acc_name,
                                price=price,
                                ext_model=f"{model_path}pmd",
                            )

                            # write to sii files
                            sii_file = os.path.join(sii_dir, sii_filename)
                            with open(sii_file, "w", encoding="utf-8") as f:
                                f.write(acc)

    def run(self):

        if self.truck_line.text() == "":
            Flyout.create(
                title="",
                content="Truck folder field is empty",
                icon=InfoBarIcon.ERROR,
                target=self.run_btn,
                parent=self.top_card,
            )

        elif self.filename_cmb.currentIndex() == 1 and self.template_line.text() == "":
            Flyout.create(
                title="",
                content="Name template field is empty",
                icon=InfoBarIcon.ERROR,
                target=self.run_btn,
                parent=self.top_card,
            )

        else:
            self.execute()
            scshub_infobar(
                self.INFOBAR_POS, "success_btn", self.tr("Process finished"), self.OUTPUT
            )
            logger.info("Process completed successfully")

    def get_folder(self, mode: str):

        folder_dialog = QFileDialog().getExistingDirectory(self, "Select folder")

        # only if folder selected
        if folder_dialog:
            folder_path = folder_dialog.replace("/", "\\")

            match mode:

                case "input":
                    # enable buttons after folder selected for first time
                    if self.INPUT == "":
                        self.output_btn.setEnabled(True)

                    self.INPUT = folder_path

                    self.input_btn.setToolTip(self.INPUT)

                    scshub_badge(self.top_card, self.input_btn)

                    logger.info(f'Set input folder to "{self.INPUT}"')

                case "output":
                    # enable buttons after folder selected for first time
                    if self.OUTPUT == "":
                        self.run_btn.setEnabled(True)
                        # self.run_sgmnt.setEnabled(True)
                        # self.run_sgmnt.setCurrentItem("skip")

                    self.OUTPUT = folder_path

                    self.output_btn.setToolTip(self.OUTPUT)

                    scshub_badge(self.top_card, self.output_btn)

                    logger.info(f'Set output folder to "{self.OUTPUT}"')

            self.preview()

            scshub_infobar(self.INFOBAR_POS, "success", self.tr("Folder selected"))
