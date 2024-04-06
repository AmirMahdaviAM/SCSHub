import os, logging
from subprocess import Popen
from sys import platform
from random import randint
from enum import Enum

from PyQt5.QtCore import Qt, QProcess
from PyQt5.QtWidgets import QWidget, QFileDialog, QListWidgetItem

from qfluentwidgets import (InfoBar, InfoBarPosition, InfoBarIcon, IndeterminateProgressRing,
                            PushButton, ToolTipFilter, FluentIcon, InfoLevel, FluentIconBase,
                            ListWidget, InfoBadge)

from scshub.view.ui.pix_ui import Ui_PIX
from scshub.common.tool import ScsHubIcon, downloader, PIX_URL, PIX_PATH


# set logger
logger = logging.getLogger("ConverterPIX")


class Argument(Enum):
    EXP = "-e"
    BASE = "-b"
    MODEL = "-m"
    TOBJ = "-t"
    EXT_FILE = "-extract_f"
    EXT_DIR = "-extract_d"
    NEW_MAT = "-matFormat147"
    LISTDIR = "-listdir"

    def __str__(self):
        return str(self.value)


class PixInterface(QWidget, Ui_PIX):

    def __init__(self):
        super().__init__()

        #check for log file and delete it
        if os.path.isfile("pix.log"):
            os.remove("pix.log")
            logger.info("Delete last pix.log file")

        self.SCS_FILES = []
        self.EXPORT_PATH = ""

        self.PIX_MODE = ""
        self.MODE = "-extract_f"
        
        self.SUB_PATH = "/"
        self.ANIM_PATH = "/"
        self.SUFFIX_END = ""

        self.MATERIAL147 = False
        self.ANIMMODE = False

        self.LAST_SELECTED_FOLDER = ""
        self.LAST_SELECTED_FILE = ""
        self.SELECTED_ANIM_FILES = []

        # first set process to none to pervent from repeated run
        self.mainProcess = None
        self.animProcess = None

        # setup ui from pix_ui.py
        self.setupUi(self)
        self.initUi()

    def initUi(self):

        # create badge for run button
        self.runErrorBadge = InfoBadge()
        self.runSuccessBadge = InfoBadge()

        # checking for converter pix file and download it if not exist
        if os.path.isfile(PIX_PATH):
            self.runSuccessBadge = InfoBadge.success("", self, self.runButton)
            self.runSuccessBadge.setFixedSize(9, 9)
            self.downloadPixButton.hide()
            logger.info("ConverterPIX exist")
        else:
            self.runErrorBadge = InfoBadge.error("", self, self.runButton)
            self.runErrorBadge.setFixedSize(9, 9)
            self.runErrorBadge.show()
            self.selectScsButton.setDisabled(True)
            self.downloadPixButton.clicked.connect(lambda: self.donwloadPix())
            logger.info("ConverterPIX not exist")

        # create badge for run button
        self.openScsErrorBadge = InfoBadge.error("", self, self.selectScsButton)
        self.openScsErrorBadge.setFixedSize(9, 9)
        self.openScsErrorBadge.show()

        self.radioGroup.buttonClicked.connect(lambda button: self.selectMode(button.text()))

        self.modelRadio.installEventFilter(ToolTipFilter(self.modelRadio))
        self.tobjRadio.installEventFilter(ToolTipFilter(self.tobjRadio))
        self.extdirRadio.installEventFilter(ToolTipFilter(self.extdirRadio))
        self.extfileRadio.installEventFilter(ToolTipFilter(self.extfileRadio))
        
        self.materialCheckbox.stateChanged.connect(lambda: self.materialOption())
        self.materialCheckbox.installEventFilter(ToolTipFilter(self.materialCheckbox))

        self.animCheckBox.stateChanged.connect(lambda: self.animOption())
        self.animCheckBox.installEventFilter(ToolTipFilter(self.animCheckBox))
        
        self.animListCard.hide()
        self.animList.setSelectionMode(ListWidget.MultiSelection)
        self.animList.currentTextChanged.connect(self.indexAnimFolder)
        self.animList.itemClicked.connect(self.indexAnimFile)

        self.folderList.currentTextChanged.connect(self.indexDir)

        self.fileList.currentTextChanged.connect(self.indexFile)

        self.folderCountBadge.setLevel(InfoLevel.INFOAMTION)
        self.fileCountBadge.setLevel(InfoLevel.INFOAMTION)
        self.animCountBadge.setLevel(InfoLevel.INFOAMTION)

        self.resetButton.setIcon(FluentIcon.HOME)
        self.resetButton.installEventFilter(ToolTipFilter(self.resetButton))
        self.resetButton.clicked.connect(lambda: self.resetSubPath())

        self.refreshButton.setIcon(FluentIcon.UPDATE)
        self.refreshButton.installEventFilter(ToolTipFilter(self.refreshButton))
        self.refreshButton.clicked.connect(lambda: self.refreshSubPath())

        self.navigationBar.setSpacing(10)
        self.navigationBar.setFixedHeight(19)
        self.navigationBar.currentItemChanged.connect(lambda objectName: self.switchDir(objectName))

        self.selectScsButton.clicked.connect(lambda: self.getScsFiles())

        self.selectOutputButton.clicked.connect(lambda: self.getExportPath())
        self.selectOutputButton.installEventFilter(ToolTipFilter(self.selectOutputButton))

        self.runButton.clicked.connect(lambda: self.customMode())


    def listdirMode(self):
        """Run ConverterPIX to create directory and file lists"""

        # set mode to listdir to detect in handleOutput()
        self.PIX_MODE = "listdir"

        # set argument
        args = ""
        for file_path in self.SCS_FILES:
            args += f'{Argument.BASE} "{file_path}" '
        args += f'{Argument.LISTDIR} {self.SUB_PATH}'

        logger.info(f"Change process to listdir mode with these argument: ({args})")

        # run converter pix
        self.pixMainProcess(args)

    def customMode(self):
        """Run ConverterPIX to exucute selected mode and argument"""

        self.PIX_MODE = "custom"

        # set argument
        args = ""
        for file_path in self.SCS_FILES:
            args += f'{Argument.BASE} "{file_path}" '

        if self.MATERIAL147 and self.materialCheckbox.isEnabled():
            args += f'{Argument.NEW_MAT} '
        args += f'{self.MODE} '

        if self.MODE == "-m":
            args += f'{self.SUB_PATH[:-4]} '
        else:
            args += f'{self.SUB_PATH} '

        if self.ANIMMODE and self.animCheckBox.isEnabled() and self.SELECTED_ANIM_FILES != []:
            for file in self.SELECTED_ANIM_FILES:
                anim = os.path.join(self.SUB_PATH.replace(self.LAST_SELECTED_FILE, ""), file[:-4]).replace("\\", "/")
                args += f'{anim} '

        args += f'{Argument.EXP} "{self.EXPORT_PATH}"'

        logger.info(f"Change process to custom mode with these argument: ({args})")
        
        # run converter pix
        self.pixMainProcess(args)

    def animMode(self):
        """Run ConverterPIX to create directory and file lists only for anim"""

        # set argument
        args = ""
        for file_path in self.SCS_FILES:
            args += f'{Argument.BASE} "{file_path}" '
        args += f'{Argument.LISTDIR} {self.ANIM_PATH}'

        logger.info(f"Change process to anim mode with these argument: ({args})")

        # run converter pix
        self.pixAnimProcess(args)


    def selectMode(self, mode):
        """Change argument with selected modes"""

        match mode:
            case "Model":
                self.MODE = str(Argument.MODEL)
                self.materialCheckbox.setEnabled(True)
                self.animCheckBox.setEnabled(True)
                if self.animCheckBox.isEnabled() and self.animCheckBox.isChecked():
                    self.animListCard.show()
                self.fileListCard.show()
                self.SUFFIX_END = ".pmd"
                self.fileLabel.setText(self.tr("Model"))
                self.refreshSubPath()
            case "TOBJ":
                self.MODE = str(Argument.TOBJ)
                self.materialCheckbox.setDisabled(True)
                self.animCheckBox.setDisabled(True)
                self.animListCard.hide()
                self.fileListCard.show()
                self.SUFFIX_END = ".tobj"
                self.fileLabel.setText(self.tr("TOBJ"))
                self.refreshSubPath()
            case "Extract File":
                self.MODE = str(Argument.EXT_FILE)
                self.materialCheckbox.setDisabled(True)
                self.animCheckBox.setDisabled(True)
                self.animListCard.hide()
                self.fileListCard.show()
                self.SUFFIX_END = ""
                self.fileLabel.setText(self.tr("File"))
                self.refreshSubPath()
            case "Extract Folder":
                self.MODE = str(Argument.EXT_DIR)
                self.materialCheckbox.setDisabled(True)
                self.animCheckBox.setDisabled(True)
                self.animListCard.hide()
                self.fileListCard.hide()
                self.refreshSubPath()

        logger.info(f"Change mode to ({mode})")

    def materialOption(self):
        """Change material conversion to past 1.47 version"""

        if self.materialCheckbox.isChecked():
            self.MATERIAL147 = True
        else:
            self.MATERIAL147 = False
        
        logger.info(f"Change past 1.47 material option state to {self.MATERIAL147}")

    def animOption(self):
        """Enable anim include"""

        if self.animCheckBox.isChecked():
            self.ANIMMODE = True
            self.animListCard.show()
        else:
            self.ANIMMODE = False
            self.animListCard.hide()
        
        logger.info(f"Enable anim state to {self.ANIMMODE}") 


    def pixMainProcess(self, args):
        """Main process to run Convertex PIX exe file (Main)"""
        
        # check if scs path is not empty
        if self.SCS_FILES == "":
            logger.error("SCS file path is not set and operation canceled")
            InfoBar.error("Failed", "SCS file path is not set", duration=3000, parent=self)
        else:
            if self.mainProcess == None:
                self.mainProcess = QProcess()
                self.mainProcess.readyReadStandardOutput.connect(self.handleMainOutput)
                self.mainProcess.stateChanged.connect(self.handleMainState)
                self.mainProcess.finished.connect(self.handleMainFinish)

                finalCommand = f'"{PIX_PATH}" {args}'
                self.mainProcess.start(finalCommand)
                self.mainProcess.waitForReadyRead(1)
                # print(finalCommand)
                logger.info(f"Main Process: ({finalCommand})")

    def handleMainOutput(self):
        """Handle output of ConverterPIX (Main)"""
    
        # get output data from process and decode it
        data = self.mainProcess.readAllStandardOutput()
        decoded = bytes(data).decode("utf-8")
        output = decoded.splitlines()
        # print(decoded)

        # handle listdir mode
        if self.PIX_MODE == "listdir":
            
            if output[-1] == "-- done --":
                # add root item to navigation bar
                if len(self.SCS_FILES) < 2:
                    self.navigationBar.addItem("root", f"{os.path.split(self.SCS_FILES[0])[1]}")
                else:
                    self.navigationBar.addItem("root", "multi-archive")

                # clear previous list and selection from view
                self.fileList.clearSelection()
                self.folderList.clear()
                self.fileList.clear()

                folder = []
                file = []

                for line in output:
                    # create directory list
                    if line.startswith("[D] "):
                        folder.append(os.path.relpath(line[4:], self.SUB_PATH))

                    # create file list
                    elif line.startswith("[F] "):
                        # cheack suffix and only include specified in list26
                        if line.endswith(self.SUFFIX_END) and not line.endswith((".pmg", ".pmc", ".pma")):
                            file.append(os.path.relpath(line[4:], self.SUB_PATH))

                # set list count to badges
                self.folderCountBadge.setText(str(len(folder)))
                self.fileCountBadge.setText(str(len(file)))

                # add items in list to list view
                for dir in folder:
                    self.folderList.addItem(QListWidgetItem(FluentIconBase.qicon(ScsHubIcon.FOLDER), dir))
                
                # add items in list to list view and ignore it if in (-extract_d) mode
                if self.MODE != str(Argument.EXT_DIR):
                    for file in file:
                        if file.endswith(".pmd"):
                            self.fileList.addItem(QListWidgetItem(FluentIconBase.qicon(ScsHubIcon.MODEL), file))

                        elif file.endswith(".ppd"):
                            self.fileList.addItem(QListWidgetItem(FluentIconBase.qicon(ScsHubIcon.PREFAB), file))

                        elif file.endswith(".tobj"):
                            self.fileList.addItem(QListWidgetItem(FluentIconBase.qicon(ScsHubIcon.TOBJ), file))

                        elif file.endswith((".dds", ".png", ".jpg", ".mask")):
                            self.fileList.addItem(QListWidgetItem(FluentIconBase.qicon(ScsHubIcon.TEXTURE), file))

                        elif file.endswith((".sii", ".sui", ".txt", ".cfg", ".dat", ".soundref")):
                            self.fileList.addItem(QListWidgetItem(FluentIconBase.qicon(ScsHubIcon.TEXT), file))

                        else:
                            self.fileList.addItem(QListWidgetItem(FluentIconBase.qicon(ScsHubIcon.FILE), file))

        # handle custom mode
        elif self.PIX_MODE == "custom":

            # write output to pix.log
            f = open("pix.log", "a")
            f.write("=====  Start  =====")
            for line in output[5:]:
                f.write(f"{line}\n")            
            f.write("=====   End   =====\n\n")
            f.close()

            # handle warning and error and show infobar
            if "<warning>" in decoded: self.infoBar("warning")
            elif "<error>" in decoded: self.infoBar("error")
            elif "No" in decoded: self.infoBar("error")
            elif "Unable" in decoded: self.infoBar("error")
            elif "Cannot" in decoded: self.infoBar("error")
            elif "Failed" in decoded: self.infoBar("error")
            elif "readDir" in decoded: self.infoBar("error")
            elif "Invalid parameters" in decoded: self.infoBar("error")
            elif "Unknown filesystem type" in decoded: self.infoBar("error")
            else: self.infoBar("success")
        
            logger.info("Pix process ended and output saved in pix.log file")

    def handleMainState(self, state):
        """Handle diffrent states of ConverterPIX process (Main)"""

        # diffrent states
        states = {
            QProcess.NotRunning: "NotRunning",
            QProcess.Starting: "Starting",
            QProcess.Running: "Running",
        }
        state_name = states[state]

        if self.PIX_MODE == "custom":

            # running state
            if state_name == "Running":
                # show working infobar
                self.workingInfobar = InfoBar.new(InfoBarIcon.INFORMATION, "Working", "Executing task", Qt.Horizontal,
                                                False, -1, InfoBarPosition.TOP, self)
                workingWgt = IndeterminateProgressRing(self)
                workingWgt.setFixedSize(22, 22)
                workingWgt.setStrokeWidth(4)
                self.workingInfobar.addWidget(workingWgt)

                # disable buttons and lists to prevent from repeated executation
                self.runButton.setDisabled(True)
                self.fileList.setDisabled(True)
                self.folderList.setDisabled(True)

                logger.info("Pix Process Running")
        
            # finish state
            elif state_name == "NotRunning":
                # close working infobar
                self.workingInfobar.close()
                
                # enable back, buttons and lists again
                self.runButton.setEnabled(True)
                self.fileList.setEnabled(True)
                self.folderList.setEnabled(True)

                logger.info("Pix Process Finished")

    def handleMainFinish(self):

        self.mainProcess = None


    def pixAnimProcess(self, args):
        """Main process to run Convertex PIX exe file (Anim)"""
        
        # check if scs path is not empty
        if self.SCS_FILES == "":
            logger.error("SCS file path is not set and operation canceled")
            InfoBar.error("Failed", "SCS file path is not set", duration=3000, parent=self)
        else:
            if self.animProcess == None:
                self.animProcess = QProcess()
                self.animProcess.readyReadStandardOutput.connect(self.handleAnimOutput)
                self.animProcess.finished.connect(self.handleAnimFinish)

                finalCommand = f'"{PIX_PATH}" {args}'
                self.animProcess.start(finalCommand)
                self.animProcess.waitForReadyRead(1)
                # print(finalCommand)
                logger.info(f"Anim Process: ({finalCommand})")

    def handleAnimOutput(self):
        """Handle output of ConverterPIX (Anim)"""

        # get output data from process and decode it
        data = self.animProcess.readAllStandardOutput()
        decoded = bytes(data).decode("utf-8")
        output = decoded.splitlines()

        # clear previous list and selection from view
        self.animList.clearSelection()
        self.animList.clear()
        self.SELECTED_ANIM_FILES = []
        
        self.animList.addItem(QListWidgetItem(FluentIconBase.qicon(FluentIcon.UP), ".."))

        folder = []
        anim = []

        for line in output:
            # create directory list
            if line.startswith("[D] "):
                folder.append(os.path.relpath(line[4:], self.ANIM_PATH))

            # create file list
            elif line.startswith("[F] "):

                # cheack suffix and only include pma file
                if line.endswith(".pma"):
                    anim.append(os.path.relpath(line[4:], self.ANIM_PATH))

        # set list count to badges
        self.animCountBadge.setText(str(len(anim)))

        # add items in list to list view
        for dir in folder:
            self.animList.addItem(QListWidgetItem(FluentIconBase.qicon(ScsHubIcon.FOLDER), dir))
        
        for anim in anim:
            self.animList.addItem(QListWidgetItem(FluentIconBase.qicon(ScsHubIcon.ANIM), anim))

    def handleAnimFinish(self):

        self.animProcess = None


    def removeSubPathEnd(self):
        """Check and remove last selected filename in subpath if it exist"""

        if self.SUB_PATH.endswith(self.LAST_SELECTED_FILE):
            self.SUB_PATH = self.SUB_PATH.replace(self.LAST_SELECTED_FILE, "")
        logger.info(f"Check and remove last selected file:({self.LAST_SELECTED_FILE}) in subpath if it exist and refresh list")

    def resetSubPath(self):
        """Reset subpath to / and run again and go back to the root of scs file"""

        logger.info("Reset subpath to / root and refresh list")

        self.SUB_PATH = "/"
        self.ANIM_PATH = "/"
        self.navigationBar.clear()
        self.listdirMode()
        self.animMode()

    def refreshSubPath(self):
        """Refresh current subpath without going to root of scs file"""
        
        logger.info("Refresh curent subpath without reset and refresh list")

        # check and remove last selected filename in subpath if it exist
        self.removeSubPathEnd()
            
        self.fileList.clearSelection()
        self.animList.clearSelection()
        self.listdirMode()
        self.animMode()


    def switchDir(self, selected):
        """Switch to chosen directory in navigation bar"""

        # back to root of scs file if (/) item selected in navigation bar
        if selected == "root":
            self.SUB_PATH = "/"

        # find selected item index in saved subpath string and
        # delete all after item name itself and update new subpath
        if self.SUB_PATH != "/":
            newDir = self.SUB_PATH[0:self.SUB_PATH.rfind(selected[:-2])+len(selected[:-2])].replace("\\", "/")
            self.SUB_PATH = newDir

        self.listdirMode()

        logger.info("Switch to chosen directory item in navigation bar and refresh list")

    def indexDir(self, selected):
        """Add selected folder and update subpath"""

        # check if not empty and add last item to navigation bar
        if selected != "":
            # check and remove last selected filename in subpath if it exist
            self.removeSubPathEnd()
                
            # update subpath and add selected folder name to end of it
            self.SUB_PATH = os.path.join(self.SUB_PATH, selected).replace("\\", "/")
            self.LAST_SELECTED_FOLDER = self.SUB_PATH

            navi = os.path.split(self.SUB_PATH)
            self.navigationBar.addItem(f"{selected}{randint(10, 99)}", navi[1])
            # self.navigationBar.addItem(selected, navi[1])

            self.listdirMode()

            logger.info(f'Add ({selected}) to subpath and new subpath is "{self.SUB_PATH}"')

    def indexFile(self, selected):
        """Add selected file and update subpath"""
        
        # check and remove last selected filename in subpath if it exist
        self.removeSubPathEnd()

        # update subpath and add file name to it
        newPath = os.path.join(self.SUB_PATH, selected).replace("\\", "/")
        self.SUB_PATH = newPath

        self.LAST_SELECTED_FILE = selected

        logger.info(f'Add ({self.LAST_SELECTED_FILE}) to subpath and new subpath is "{self.SUB_PATH}"')

    def indexAnimFolder(self, selected):
        """Add selected anim folder and update anim path"""

        if selected != "" and not selected.endswith(".pma"):
            if selected == "..":
                if self.ANIM_PATH != "/":
                    backPath = os.path.split(self.ANIM_PATH)
                    self.ANIM_PATH = backPath[0].replace("\\", "/")
            else:
                self.ANIM_PATH = os.path.join(self.ANIM_PATH, selected).replace("\\", "/")
                self.SELECTED_ANIM_FILES = []

            self.animMode()

        logger.info(f'Add ({selected}) to animpath and new animpath is "{self.ANIM_PATH}"')

    def indexAnimFile(self):
        """Add selected anim files to a lsit for convert"""

        selection = self.animList.selectedItems()

        selectedList = []

        count = 0
        for anim in selection:
            if anim.text() != "..":
                if anim.text().endswith(".pma"):
                    selectedList.append(str(selection[count].text()))
                    count += 1

        self.SELECTED_ANIM_FILES = selectedList

        logger.info(f'Current anim list is ({self.SELECTED_ANIM_FILES})')
        

    def getScsFiles(self):
        """Get SCS file paths"""

        filePaths = QFileDialog().getOpenFileNames(self, "Select SCS Archives", filter="SCS Archives (*.zip *.scs)")
        if filePaths[0]:
            self.SCS_FILES = filePaths[0]
            InfoBar.success("Success", "SCS Archives selected", duration=1500, parent=self)
            logger.info(f'Set scs file paths to "{str(filePaths[0])}"')
            self.resetSubPath()
        
        # enable function after file selected
        if not self.SCS_FILES == []:
            self.selectOutputButton.setEnabled(True)
            self.runButton.setEnabled(True)
            self.refreshButton.setEnabled(True)
            self.resetButton.setEnabled(True)
            self.modelRadio.setEnabled(True)
            self.tobjRadio.setEnabled(True)
            self.extdirRadio.setEnabled(True)
            self.extfileRadio.setEnabled(True)

            self.openScsErrorBadge.hide()
            self.openScsSuccessBadge = InfoBadge.success("", self, self.selectScsButton)
            self.openScsSuccessBadge.setFixedSize(9, 9)
            self.openScsSuccessBadge.show()
    
    def getExportPath(self):
        """Get Export path"""

        dirPath = QFileDialog().getExistingDirectory(self, "Select Output")
        if dirPath:
            self.EXPORT_PATH = dirPath
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
                    openRoot = PushButton("Open Root")

                    # check export path and if it is empty, replace it with scs path with "_exp" suffix
                    if self.EXPORT_PATH == "":
                        outPath = f'{self.SCS_FILES[0]}_exp'
                        rootPath = outPath.replace("/", "\\")
                    else:
                        outPath = self.EXPORT_PATH
                        rootPath = outPath.replace("/", "\\")
                    subPath = self.LAST_SELECTED_FOLDER
                    folderPath = f'{outPath}{subPath}'.replace("/", "\\")

                    openFolder.clicked.connect(lambda: Popen(f"explorer.exe {folderPath}"))
                    openRoot.clicked.connect(lambda: Popen(f"explorer.exe {rootPath}"))
                    success.addWidget(openFolder)
                    success.addWidget(openRoot)

            case "error":   
                error = InfoBar.error("Failed", "There is error in process\nCheck log file.",
                                      Qt.Vertical, True, 4000, InfoBarPosition.TOP_RIGHT, self)
                logger.error("Operation completed with error, check pix.log file")
                if platform == "win32":
                    openLog = PushButton("Open Log")
                    openLog.clicked.connect(lambda: Popen("notepad.exe pix.log"))
                    error.addWidget(openLog)

            case "warning":
                warning = InfoBar.warning("Failed", "There is warning in process\nCheck log file.",
                                      Qt.Vertical, True, 4000, InfoBarPosition.TOP_RIGHT, self)
                logger.error("Operation completed with error, check pix.log file")
                if platform == "win32":
                    openLog = PushButton("Open Log")
                    openLog.clicked.connect(lambda: Popen("notepad.exe pix.log"))
                    warning.addWidget(openLog)


    def donwloadPix(self):

        downloader.start()
        downloader.URL = PIX_URL
        downloader.PATH = PIX_PATH
        downloader.started.connect(self.downloadPixStart)
        downloader.result.connect(self.downloadPixFinish)

    def downloadPixStart(self):

        self.downloadPixButton.setDisabled(True)

        self.downloadInfobar = InfoBar.new(InfoBarIcon.INFORMATION, "Working", "Downloading ConverterPIX", Qt.Horizontal,
                                            False, -1, InfoBarPosition.TOP, self)
        downloadWgt = IndeterminateProgressRing(self)
        downloadWgt.setFixedSize(22, 22)
        downloadWgt.setStrokeWidth(4)
        self.downloadInfobar.addWidget(downloadWgt)
            
    def downloadPixFinish(self, result):

        self.downloadInfobar.close()

        match result:
            case 0:
                self.runErrorBadge.hide()
                self.runSuccessBadge = InfoBadge.success("", self, self.runButton)
                self.runSuccessBadge.setFixedSize(9, 9)
                self.runSuccessBadge.show()
                self.downloadPixButton.hide()
                self.downloadPixButton.setDisabled(True)
                self.selectScsButton.setEnabled(True)
                
                InfoBar.success("Success", "ConverterPIX downloaded", duration=2000, parent=self)

                logger.info("ConverterPix updated!")

            case 1:
                self.downloadPixButton.setEnabled(True)
                InfoBar.error("Failed", "Error during downloading\nCheck internet", duration=2000, parent=self)