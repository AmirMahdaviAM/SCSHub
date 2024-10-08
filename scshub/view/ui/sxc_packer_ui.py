# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\Users\Amir\Desktop\SCSHub\scshub\view\ui\sxc_packer_ui.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class SxcPackerUi(object):
    def setupUi(self, SxcPacker):
        SxcPacker.setObjectName("SxcPacker")
        SxcPacker.resize(1057, 759)
        self.main_lyt = QtWidgets.QVBoxLayout(SxcPacker)
        self.main_lyt.setContentsMargins(0, 0, 0, 0)
        self.main_lyt.setObjectName("main_lyt")
        self.main_card = SimpleCardWidget(SxcPacker)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.main_card.sizePolicy().hasHeightForWidth())
        self.main_card.setSizePolicy(sizePolicy)
        self.main_card.setObjectName("main_card")
        self.main_card_lyt = QtWidgets.QVBoxLayout(self.main_card)
        self.main_card_lyt.setObjectName("main_card_lyt")
        self.packer_lbl = StrongBodyLabel(self.main_card)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.packer_lbl.sizePolicy().hasHeightForWidth())
        self.packer_lbl.setSizePolicy(sizePolicy)
        self.packer_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.packer_lbl.setObjectName("packer_lbl")
        self.main_card_lyt.addWidget(self.packer_lbl)
        self.top_card = SimpleCardWidget(self.main_card)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.top_card.sizePolicy().hasHeightForWidth())
        self.top_card.setSizePolicy(sizePolicy)
        self.top_card.setMinimumSize(QtCore.QSize(0, 60))
        self.top_card.setMaximumSize(QtCore.QSize(16777215, 60))
        self.top_card.setObjectName("top_card")
        self.top_card_lyt = QtWidgets.QHBoxLayout(self.top_card)
        self.top_card_lyt.setObjectName("top_card_lyt")
        self.input_btn = PushButton(self.top_card)
        self.input_btn.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.input_btn.sizePolicy().hasHeightForWidth())
        self.input_btn.setSizePolicy(sizePolicy)
        self.input_btn.setMinimumSize(QtCore.QSize(110, 0))
        self.input_btn.setObjectName("input_btn")
        self.top_card_lyt.addWidget(self.input_btn)
        self.output_btn = PushButton(self.top_card)
        self.output_btn.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.output_btn.sizePolicy().hasHeightForWidth())
        self.output_btn.setSizePolicy(sizePolicy)
        self.output_btn.setMinimumSize(QtCore.QSize(110, 0))
        self.output_btn.setObjectName("output_btn")
        self.top_card_lyt.addWidget(self.output_btn)
        spacerItem = QtWidgets.QSpacerItem(4, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.top_card_lyt.addItem(spacerItem)
        self.v_separator_1 = VerticalSeparator(self.top_card)
        self.v_separator_1.setObjectName("v_separator_1")
        self.top_card_lyt.addWidget(self.v_separator_1)
        spacerItem1 = QtWidgets.QSpacerItem(4, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.top_card_lyt.addItem(spacerItem1)
        self.pack_btn = PrimaryPushButton(self.top_card)
        self.pack_btn.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pack_btn.sizePolicy().hasHeightForWidth())
        self.pack_btn.setSizePolicy(sizePolicy)
        self.pack_btn.setMinimumSize(QtCore.QSize(110, 0))
        self.pack_btn.setObjectName("pack_btn")
        self.top_card_lyt.addWidget(self.pack_btn)
        spacerItem2 = QtWidgets.QSpacerItem(4, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.top_card_lyt.addItem(spacerItem2)
        self.v_separator_2 = VerticalSeparator(self.top_card)
        self.v_separator_2.setObjectName("v_separator_2")
        self.top_card_lyt.addWidget(self.v_separator_2)
        spacerItem3 = QtWidgets.QSpacerItem(4, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.top_card_lyt.addItem(spacerItem3)
        self.hidden_chk = CheckBox(self.top_card)
        self.hidden_chk.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.hidden_chk.sizePolicy().hasHeightForWidth())
        self.hidden_chk.setSizePolicy(sizePolicy)
        self.hidden_chk.setMinimumSize(QtCore.QSize(29, 22))
        self.hidden_chk.setMaximumSize(QtCore.QSize(22, 22))
        self.hidden_chk.setText("")
        self.hidden_chk.setObjectName("hidden_chk")
        self.top_card_lyt.addWidget(self.hidden_chk)
        self.hidden_btn = PushButton(self.top_card)
        self.hidden_btn.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.hidden_btn.sizePolicy().hasHeightForWidth())
        self.hidden_btn.setSizePolicy(sizePolicy)
        self.hidden_btn.setMinimumSize(QtCore.QSize(100, 0))
        self.hidden_btn.setObjectName("hidden_btn")
        self.top_card_lyt.addWidget(self.hidden_btn)
        spacerItem4 = QtWidgets.QSpacerItem(4, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.top_card_lyt.addItem(spacerItem4)
        self.exclude_chk = CheckBox(self.top_card)
        self.exclude_chk.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.exclude_chk.sizePolicy().hasHeightForWidth())
        self.exclude_chk.setSizePolicy(sizePolicy)
        self.exclude_chk.setMinimumSize(QtCore.QSize(29, 22))
        self.exclude_chk.setMaximumSize(QtCore.QSize(22, 22))
        self.exclude_chk.setText("")
        self.exclude_chk.setObjectName("exclude_chk")
        self.top_card_lyt.addWidget(self.exclude_chk)
        self.exclude_btn = PushButton(self.top_card)
        self.exclude_btn.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.exclude_btn.sizePolicy().hasHeightForWidth())
        self.exclude_btn.setSizePolicy(sizePolicy)
        self.exclude_btn.setMinimumSize(QtCore.QSize(100, 0))
        self.exclude_btn.setObjectName("exclude_btn")
        self.top_card_lyt.addWidget(self.exclude_btn)
        spacerItem5 = QtWidgets.QSpacerItem(4, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.top_card_lyt.addItem(spacerItem5)
        self.encrypt_chk = CheckBox(self.top_card)
        self.encrypt_chk.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.encrypt_chk.sizePolicy().hasHeightForWidth())
        self.encrypt_chk.setSizePolicy(sizePolicy)
        self.encrypt_chk.setMinimumSize(QtCore.QSize(29, 22))
        self.encrypt_chk.setMaximumSize(QtCore.QSize(22, 22))
        self.encrypt_chk.setText("")
        self.encrypt_chk.setObjectName("encrypt_chk")
        self.top_card_lyt.addWidget(self.encrypt_chk)
        self.encrypt_btn = PushButton(self.top_card)
        self.encrypt_btn.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.encrypt_btn.sizePolicy().hasHeightForWidth())
        self.encrypt_btn.setSizePolicy(sizePolicy)
        self.encrypt_btn.setMinimumSize(QtCore.QSize(100, 0))
        self.encrypt_btn.setObjectName("encrypt_btn")
        self.top_card_lyt.addWidget(self.encrypt_btn)
        spacerItem6 = QtWidgets.QSpacerItem(4, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.top_card_lyt.addItem(spacerItem6)
        self.stored_chk = CheckBox(self.top_card)
        self.stored_chk.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stored_chk.sizePolicy().hasHeightForWidth())
        self.stored_chk.setSizePolicy(sizePolicy)
        self.stored_chk.setMinimumSize(QtCore.QSize(29, 22))
        self.stored_chk.setMaximumSize(QtCore.QSize(22, 22))
        self.stored_chk.setText("")
        self.stored_chk.setObjectName("stored_chk")
        self.top_card_lyt.addWidget(self.stored_chk)
        self.stored_btn = PushButton(self.top_card)
        self.stored_btn.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stored_btn.sizePolicy().hasHeightForWidth())
        self.stored_btn.setSizePolicy(sizePolicy)
        self.stored_btn.setMinimumSize(QtCore.QSize(100, 0))
        self.stored_btn.setObjectName("stored_btn")
        self.top_card_lyt.addWidget(self.stored_btn)
        self.main_card_lyt.addWidget(self.top_card)
        self.log_txt = PlainTextEdit(self.main_card)
        self.log_txt.setMinimumSize(QtCore.QSize(0, 170))
        self.log_txt.setMaximumSize(QtCore.QSize(16777215, 170))
        self.log_txt.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.log_txt.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.log_txt.setReadOnly(True)
        self.log_txt.setObjectName("log_txt")
        self.main_card_lyt.addWidget(self.log_txt)
        self.main_lyt.addWidget(self.main_card)

        self.retranslateUi(SxcPacker)
        QtCore.QMetaObject.connectSlotsByName(SxcPacker)

    def retranslateUi(self, SxcPacker):
        _translate = QtCore.QCoreApplication.translate
        SxcPacker.setWindowTitle(_translate("SxcPacker", "SxcPacker"))
        self.packer_lbl.setText(_translate("SxcPacker", "Packer"))
        self.input_btn.setText(_translate("SxcPacker", "Input"))
        self.output_btn.setText(_translate("SxcPacker", "Output"))
        self.pack_btn.setText(_translate("SxcPacker", "Pack"))
        self.hidden_chk.setToolTip(_translate("SxcPacker", "-h List of files/directories to be hidden"))
        self.hidden_btn.setText(_translate("SxcPacker", "Hidden file"))
        self.exclude_chk.setToolTip(_translate("SxcPacker", "-x  List of files/directories to be excluded"))
        self.exclude_btn.setText(_translate("SxcPacker", "Exclude file"))
        self.encrypt_chk.setToolTip(_translate("SxcPacker", "-e List of unit files (.sii) to be encrypted"))
        self.encrypt_btn.setText(_translate("SxcPacker", "Encryp file"))
        self.stored_chk.setToolTip(_translate("SxcPacker", "-s  List of files/directories to be stored"))
        self.stored_btn.setText(_translate("SxcPacker", "Stored file"))
from qfluentwidgets import CheckBox, PlainTextEdit, PrimaryPushButton, PushButton, SimpleCardWidget, StrongBodyLabel, VerticalSeparator
