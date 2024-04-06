from PyQt5 import QtCore, QtGui, QtWidgets

from qfluentwidgets import BodyLabel, PrimaryPushButton, PushButton, StrongBodyLabel


class Ui_SCS(object):
    def setupUi(self, SCS):
        SCS.setObjectName("SCS")
        SCS.resize(910, 707)
        self.verticalLayout = QtWidgets.QVBoxLayout(SCS)
        self.verticalLayout.setObjectName("verticalLayout")
        self.buttonLayout = QtWidgets.QVBoxLayout()
        self.buttonLayout.setObjectName("buttonLayout")
        self.topButtonLayout = QtWidgets.QHBoxLayout()
        self.topButtonLayout.setObjectName("topButtonLayout")
        self.selectScsButton = PushButton(SCS)
        self.selectScsButton.setObjectName("selectScsButton")
        self.topButtonLayout.addWidget(self.selectScsButton)
        self.selectOutputButton = PushButton(SCS)
        self.selectOutputButton.setEnabled(False)
        self.selectOutputButton.setObjectName("selectOutputButton")
        self.topButtonLayout.addWidget(self.selectOutputButton)
        self.buttonLayout.addLayout(self.topButtonLayout)
        self.bottomButtonLayout = QtWidgets.QHBoxLayout()
        self.bottomButtonLayout.setObjectName("bottomButtonLayout")
        self.downloadScsButton = PrimaryPushButton(SCS)
        self.downloadScsButton.setObjectName("downloadScsButton")
        self.bottomButtonLayout.addWidget(self.downloadScsButton)
        self.runButton = PrimaryPushButton(SCS)
        self.runButton.setEnabled(False)
        self.runButton.setObjectName("runButton")
        self.bottomButtonLayout.addWidget(self.runButton)
        self.buttonLayout.addLayout(self.bottomButtonLayout)
        self.verticalLayout.addLayout(self.buttonLayout)
        self.scsFileLayout = QtWidgets.QHBoxLayout()
        self.scsFileLayout.setObjectName("scsFileLayout")
        self.scsFileLabel = BodyLabel(SCS)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scsFileLabel.sizePolicy().hasHeightForWidth())
        self.scsFileLabel.setSizePolicy(sizePolicy)
        self.scsFileLabel.setObjectName("scsFileLabel")
        self.scsFileLayout.addWidget(self.scsFileLabel)
        self.scsFilePathLabel = StrongBodyLabel(SCS)
        self.scsFilePathLabel.setObjectName("scsFilePathLabel")
        self.scsFileLayout.addWidget(self.scsFilePathLabel)
        self.verticalLayout.addLayout(self.scsFileLayout)
        self.outputLayout = QtWidgets.QHBoxLayout()
        self.outputLayout.setObjectName("outputLayout")
        self.outputLabel = BodyLabel(SCS)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.outputLabel.sizePolicy().hasHeightForWidth())
        self.outputLabel.setSizePolicy(sizePolicy)
        self.outputLabel.setObjectName("outputLabel")
        self.outputLayout.addWidget(self.outputLabel)
        self.outputPathLabel = StrongBodyLabel(SCS)
        self.outputPathLabel.setObjectName("outputPathLabel")
        self.outputLayout.addWidget(self.outputPathLabel)
        self.verticalLayout.addLayout(self.outputLayout)
        spacerItem = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(SCS)
        QtCore.QMetaObject.connectSlotsByName(SCS)

    def retranslateUi(self, SCS):
        _translate = QtCore.QCoreApplication.translate
        SCS.setWindowTitle(_translate("SCS", "Form"))
        self.selectScsButton.setText(_translate("SCS", "Select SCS Archive"))
        self.selectOutputButton.setToolTip(_translate("SCS", "Default is set to sample.scs_exp"))
        self.selectOutputButton.setText(_translate("SCS", "Select Output Folder"))
        self.downloadScsButton.setText(_translate("SCS", "Download SCS Extractor"))
        self.runButton.setText(_translate("SCS", "Run"))
        self.scsFileLabel.setText(_translate("SCS", "SCS File:"))
        self.scsFilePathLabel.setText(_translate("SCS", "-"))
        self.outputLabel.setText(_translate("SCS", "Output Folder:"))
        self.outputPathLabel.setText(_translate("SCS", "-"))
