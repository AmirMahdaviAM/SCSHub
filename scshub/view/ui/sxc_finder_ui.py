# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\Users\Amir\Desktop\SCSHub\scshub\view\ui\sxc_finder_ui.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class SxcFinderUi(object):
    def setupUi(self, SxcFinder):
        SxcFinder.setObjectName("SxcFinder")
        SxcFinder.resize(987, 759)
        self.main_lyt = QtWidgets.QVBoxLayout(SxcFinder)
        self.main_lyt.setContentsMargins(0, 0, 0, 0)
        self.main_lyt.setObjectName("main_lyt")
        self.main_card = SimpleCardWidget(SxcFinder)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.main_card.sizePolicy().hasHeightForWidth())
        self.main_card.setSizePolicy(sizePolicy)
        self.main_card.setObjectName("main_card")
        self.main_card_lyt = QtWidgets.QVBoxLayout(self.main_card)
        self.main_card_lyt.setObjectName("main_card_lyt")
        self.finder_lbl = StrongBodyLabel(self.main_card)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.finder_lbl.sizePolicy().hasHeightForWidth())
        self.finder_lbl.setSizePolicy(sizePolicy)
        self.finder_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.finder_lbl.setObjectName("finder_lbl")
        self.main_card_lyt.addWidget(self.finder_lbl)
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
        self.download_btn = PrimaryPushButton(self.top_card)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.download_btn.sizePolicy().hasHeightForWidth())
        self.download_btn.setSizePolicy(sizePolicy)
        self.download_btn.setMinimumSize(QtCore.QSize(110, 0))
        self.download_btn.setObjectName("download_btn")
        self.top_card_lyt.addWidget(self.download_btn)
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
        self.v_separator = VerticalSeparator(self.top_card)
        self.v_separator.setObjectName("v_separator")
        self.top_card_lyt.addWidget(self.v_separator)
        spacerItem1 = QtWidgets.QSpacerItem(4, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.top_card_lyt.addItem(spacerItem1)
        self.run_btn = PrimaryPushButton(self.top_card)
        self.run_btn.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.run_btn.sizePolicy().hasHeightForWidth())
        self.run_btn.setSizePolicy(sizePolicy)
        self.run_btn.setMinimumSize(QtCore.QSize(110, 0))
        self.run_btn.setObjectName("run_btn")
        self.top_card_lyt.addWidget(self.run_btn)
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

        self.retranslateUi(SxcFinder)
        QtCore.QMetaObject.connectSlotsByName(SxcFinder)

    def retranslateUi(self, SxcFinder):
        _translate = QtCore.QCoreApplication.translate
        SxcFinder.setWindowTitle(_translate("SxcFinder", "SxcFinder"))
        self.finder_lbl.setText(_translate("SxcFinder", "Finder & Extractor"))
        self.download_btn.setText(_translate("SxcFinder", "Download"))
        self.input_btn.setText(_translate("SxcFinder", "Input"))
        self.output_btn.setText(_translate("SxcFinder", "Output"))
        self.run_btn.setText(_translate("SxcFinder", "Run"))
from qfluentwidgets import PlainTextEdit, PrimaryPushButton, PushButton, SimpleCardWidget, StrongBodyLabel, VerticalSeparator
