import os, logging
from subprocess import Popen
from sys import platform

from PyQt5.QtCore import Qt, QProcess
from PyQt5.QtWidgets import QWidget, QFileDialog, QVBoxLayout

from qfluentwidgets import (InfoBar, InfoBarPosition, InfoBarIcon, IndeterminateProgressRing,
                            PushButton, ToolTipFilter, FluentIcon, FluentIconBase, InfoBadge)

from ..ui.scs_ui import Ui_SCS
from ...common.tool import ScsHubIcon, downloader, SCS_URL, SCS_PATH


# set logger
logger = logging.getLogger("SCSExtractor")


class ScsInterface(QWidget, Ui_SCS):

    def __init__(self):
        super().__init__()

        #check for log file and delete it
        if os.path.isfile("scs.log"):
            os.remove("scs.log")
            logger.info("Delete last scs.log file")

        self.SCS_FILE = []
        self.EXPORT_PATH = ""

        # first set process to none to pervent from repeated run
        self.mainProcess = None

        # setup ui from pix_ui.py
        self.setupUi(self)
        self.initUi()

    def initUi(self):

        # create badge for run button
        self.runErrorBadge = InfoBadge()
        self.runSuccessBadge = InfoBadge()

        # checking for converter pix file and download it if not exist
        if os.path.isfile(SCS_PATH):
            self.runSuccessBadge = InfoBadge.success("", self, self.runButton)
            self.runSuccessBadge.setFixedSize(9, 9)
            self.downloadScsButton.hide()
            logger.info("SCSExtractor exist")
        else:
            self.runErrorBadge = InfoBadge.error("", self, self.runButton)
            self.runErrorBadge.setFixedSize(9, 9)
            self.runErrorBadge.show()
            self.selectScsButton.setDisabled(True)
            self.downloadScsButton.clicked.connect(lambda: self.donwloadScs())
            logger.info("SCSExtractor not exist")

        # create badge for open scs file button
        self.selectScsErrorBadge = InfoBadge.error("", self, self.selectScsButton)
        self.selectScsErrorBadge.setFixedSize(9, 9)
        self.selectScsErrorBadge.show()

        self.selectScsSuccessBadge = InfoBadge()        

        self.selectScsButton.clicked.connect(lambda: self.getScsFile())

        self.selectOutputButton.clicked.connect(lambda: self.getExportPath())
        self.selectOutputButton.installEventFilter(ToolTipFilter(self.selectOutputButton))

        self.runButton.clicked.connect(lambda: self.runScsExtractor())


    def runScsExtractor(self):
        """Run SCSExtractor"""

        # set command to execute
        command = f'"{SCS_PATH}" "{self.SCS_FILE}" "{self.EXPORT_PATH}"'
        print(command)
        logger.info(command)

        # run scs extractor
        if self.mainProcess == None:
            self.mainProcess = QProcess()
            self.mainProcess.readyReadStandardOutput.connect(self.handleOutput)
            self.mainProcess.stateChanged.connect(self.handleState)
            self.mainProcess.finished.connect(self.handleFinish)

            self.mainProcess.start(command)
            self.mainProcess.waitForReadyRead(1)


    def handleOutput(self):
        """Handle output of SCSExtractor"""
    
        # get output data from process and decode it
        data = self.mainProcess.readAllStandardOutput()
        decoded = bytes(data).decode("utf-8")
        output = decoded.splitlines()
        print(decoded)

        # write output to scs.log
        f = open("scs.log", "a")
        f.write("=====  Start  =====\n")
        for line in output:
            f.write(f"{line}\n")            
        f.write("=====   End   =====\n\n")
        f.close()

        # handle error and show infobar
        if "*** ERROR ***" in decoded: self.infoBar("error")
        else: self.infoBar("success")
    
        logger.info("SCSExtractor ended and output saved in scs.log file")

    def handleState(self, state):
        """Handle diffrent states of SCSExtractor process"""

        # diffrent states
        states = {
            QProcess.NotRunning: "NotRunning",
            QProcess.Starting: "Starting",
            QProcess.Running: "Running",
        }
        state_name = states[state]

        # running state
        if state_name == "Running":
            # show working infobar
            self.workingInfobar = InfoBar.new(InfoBarIcon.INFORMATION, "Working", "Exracting files", Qt.Horizontal,
                                            False, -1, InfoBarPosition.TOP, self)
            workingWgt = IndeterminateProgressRing(self)
            workingWgt.setFixedSize(22, 22)
            workingWgt.setStrokeWidth(4)
            self.workingInfobar.addWidget(workingWgt)

            # disable buttons and lists to prevent from repeated executation
            self.runButton.setDisabled(True)

            logger.info("SCSExtractor Running")
    
        # finish state
        elif state_name == "NotRunning":
            # close working infobar
            self.workingInfobar.close()
            
            # enable back, buttons and lists again
            self.runButton.setEnabled(True)

            logger.info("SCSExtractor Finished")

    def handleFinish(self):

        self.mainProcess = None


    def getScsFile(self):
        """Get SCS file path"""

        if platform == "win32":
            filePath = QFileDialog().getOpenFileName(self, "Select SCS Archive", filter="SCS Archive (*.zip *.scs)")
            if filePath[0]:
                self.SCS_FILE = filePath[0]

                # set export path to (sample_exp)
                exportPath = f"{self.SCS_FILE[:-4]}_exp"
                if not os.path.isdir(exportPath):
                    os.makedirs(exportPath, exist_ok=True)
                self.EXPORT_PATH = exportPath

                self.scsFilePathLabel.setText(self.SCS_FILE)
                self.outputPathLabel.setText(self.EXPORT_PATH)

                InfoBar.success("Success", "SCS Archives selected", duration=1500, parent=self)
                logger.info(f'Set scs file paths to "{str(filePath[0])}"')
            
            # enable function after file selected
            if not self.SCS_FILE == []:
                self.selectOutputButton.setEnabled(True)
                self.runButton.setEnabled(True)

                self.selectScsErrorBadge.hide()
                self.selectScsSuccessBadge = InfoBadge.success("", self, self.selectScsButton)
                self.selectScsSuccessBadge.setFixedSize(9, 9)
                self.selectScsSuccessBadge.show()
        else:
            self.infoBar("platform")
    
    def getExportPath(self):
        """Get Export path"""

        dirPath = QFileDialog().getExistingDirectory(self, "Select Output")
        if dirPath:
            self.EXPORT_PATH = dirPath

            self.outputPathLabel.setText(self.EXPORT_PATH)
            
            logger.info(f'Set export path to "{dirPath}"')


    def infoBar(self, type):
        """Show info bar"""

        match type:
            case "success":
                success = InfoBar.success("Success", "Finished succesfully",
                                      Qt.Vertical, True, 3000, InfoBarPosition.TOP_RIGHT, self)
                logger.info("Operation completed successfully")
                # if windows, show open button
                if platform == "win32":
                    openFolder = PushButton("Open Folder")
                    folderPath = self.EXPORT_PATH.replace("/", "\\")
                    openFolder.clicked.connect(lambda: Popen(f"explorer.exe {folderPath}"))
                    success.addWidget(openFolder)

            case "error":   
                error = InfoBar.error("Failed", "There is error in process\nCheck log file.",
                                      Qt.Vertical, True, 4000, InfoBarPosition.TOP_RIGHT, self)
                logger.error("Operation completed with error, check scs.log file")
                if platform == "win32":
                    openLog = PushButton("Open Log")
                    openLog.clicked.connect(lambda: Popen("notepad.exe scs.log"))
                    error.addWidget(openLog)

            case "warning":
                warning = InfoBar.warning("Failed", "There is warning in process\nCheck log file.",
                                      Qt.Vertical, True, 4000, InfoBarPosition.TOP_RIGHT, self)
                logger.error("Operation completed with error, check scs.log file")
                if platform == "win32":
                    openLog = PushButton("Open Log")
                    openLog.clicked.connect(lambda: Popen("notepad.exe pix.log"))
                    warning.addWidget(openLog)
            case "platform":
                InfoBar.error("Error", f"Not work in {platform}\nSCS extractor only work in windows", duration=4000, parent=self)


    def donwloadScs(self):
        if platform == "win32":
            downloader.start()
            downloader.URL = SCS_URL
            downloader.PATH = SCS_PATH
            downloader.started.connect(self.donwloadScsStart)
            downloader.result.connect(self.donwloadScsFinish)
        else:
            self.infoBar("platform")

    def donwloadScsStart(self):

        self.downloadScsButton.setDisabled(True)

        self.downloadInfobar = InfoBar.new(InfoBarIcon.INFORMATION, "Working", "Downloading SCSExtractor", Qt.Horizontal,
                                            False, -1, InfoBarPosition.TOP, self)
        downloadWgt = IndeterminateProgressRing(self)
        downloadWgt.setFixedSize(22, 22)
        downloadWgt.setStrokeWidth(4)
        self.downloadInfobar.addWidget(downloadWgt)
            
    def donwloadScsFinish(self, result):

        self.downloadInfobar.close()

        match result:
            case 0:
                self.runErrorBadge.hide()
                self.runSuccessBadge = InfoBadge.success("", self, self.runButton)
                self.runSuccessBadge.setFixedSize(9, 9)
                self.runSuccessBadge.show()
                self.downloadScsButton.hide()
                self.downloadScsButton.setDisabled(True)
                self.selectScsButton.setEnabled(True)
                
                InfoBar.success("Success", "SCSExtractor downloaded", duration=2000, parent=self)

                logger.info("SCSExtractor updated!")

            case 1:
                self.downloadScsButton.setEnabled(True)
                InfoBar.error("Failed", "Error during downloading\nCheck internet", duration=2000, parent=self)