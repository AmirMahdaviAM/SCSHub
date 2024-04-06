from PyQt5.QtCore import Qt, QUrl, QSize, QRect
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QWidget, QLabel, QSizePolicy, QSpacerItem, QHBoxLayout, QVBoxLayout

from qfluentwidgets import (SettingCardGroup, SettingCard, CustomColorSettingCard,
                            PrimaryPushSettingCard, OptionsSettingCard, HyperlinkLabel,
                            ComboBoxSettingCard, SwitchSettingCard, SimpleCardWidget,
                            ExpandLayout, ScrollArea, InfoBar, FluentIcon, AvatarWidget,
                            BodyLabel, StrongBodyLabel, setTheme, setThemeColor)

from ...common.config import cfg, isWin11
from ...common.tool import StyleSheet, signalBus, VERSION, YEAR, SCSHUB_FEEDBACK_URL, GITHUB, TELEGRAM, INSTAGRAM


class SettingInterface(ScrollArea):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # setting label
        self.settingLabel = QLabel(self.tr("Settings"), self)

        self.cards()
        self.profile()
        self.initUi()
        self.connectSignalToSlot()

    def cards(self):

        self.personalGroup = SettingCardGroup(self.tr("Personalization"), self.scrollWidget)
        
        self.micaCard = SwitchSettingCard(
            FluentIcon.TRANSPARENT,
            self.tr("Mica effect"),
            self.tr("Apply semi transparent to windows and surfaces"),
            cfg.micaEnabled,
            self.personalGroup
        )
        self.themeCard = OptionsSettingCard(
            cfg.themeMode,
            FluentIcon.BRUSH,
            self.tr("Application theme"),
            self.tr("Change the appearance of your application"),
            texts=[
                self.tr("Light"), self.tr("Dark"),
                self.tr("Use system setting")
            ],
            parent=self.personalGroup
        )
        self.themeColorCard = CustomColorSettingCard(
            cfg.themeColor,
            FluentIcon.PALETTE,
            self.tr("Theme color"),
            self.tr("Change the theme color of you application"),
            self.personalGroup
        )
        self.zoomCard = ComboBoxSettingCard(
            cfg.dpiScale,
            FluentIcon.ZOOM,
            self.tr("Interface zoom"),
            self.tr("Change the size of widgets and fonts"),
            texts=[
                "100%", "125%", "150%", "175%", "200%",
                self.tr("Use system setting")],
            parent=self.personalGroup
        )
        self.languageCard = ComboBoxSettingCard(
            cfg.language,
            FluentIcon.LANGUAGE,
            self.tr("Language"),
            self.tr("Set your preferred language for UI"),
            texts=['English', self.tr('Use system setting')],
            parent=self.personalGroup
        )

        self.aboutGroup = SettingCardGroup(self.tr("About"), self.scrollWidget)
        
        self.feedbackCard = PrimaryPushSettingCard(
            self.tr("Provide feedback"),
            FluentIcon.FEEDBACK,
            self.tr("Provide feedback"),
            self.tr("Help us improve SCS Hub by providing feedback"),
            self.aboutGroup
        )
        self.aboutCard = SettingCard(
            FluentIcon.INFO,
            self.tr("About"),
            "© " + self.tr("Copyright") + f" {YEAR}, AmirMahdavi. " + self.tr("Version") + " " + VERSION,
            self.aboutGroup
        )

    def profile(self):
        self.profileCard = SimpleCardWidget(self.scrollWidget)
        self.profileCard.setMinimumSize(QSize(16777215, 130))
        self.profileCard.setMaximumSize(QSize(16777215, 130))
        self.profileCard.setObjectName("profileCard")

        self.profileLayout = QHBoxLayout(self.profileCard)
        self.profileLayout.setContentsMargins(16, 0, 0, 0)
        self.profileLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.profileLayout.setObjectName("profileLayout")

        self.avatar = AvatarWidget(self.profileCard)
        self.avatar.setObjectName("avatar")
        self.avatar.setImage(":/SCSHub/image/avatar.png")
        self.avatar.setRadius(48)

        spacerItem = QSpacerItem(16, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.textLayout = QVBoxLayout()
        self.textLayout.setObjectName("textLayout")

        spacerItem1 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Minimum)
        
        self.nameLabel = StrongBodyLabel(self.profileCard)
        self.nameLabel.setObjectName("nameLabel")
        self.nameLabel.setText("Amir Mahdavi")

        self.emailLabel = BodyLabel(self.profileCard)
        self.emailLabel.setObjectName("emailLabel")
        self.emailLabel.setText("mahdaviamir33@gmail.com")

        self.linkLayout = QHBoxLayout()
        self.linkLayout.setObjectName("linkLayout")
        self.linkLayout.setSpacing(16)
        
        self.githubLink = HyperlinkLabel("GitHub", self.profileCard)
        self.githubLink.setObjectName("githubLink")
        self.githubLink.setUrl(GITHUB)

        self.telegramLink = HyperlinkLabel("Telegram", self.profileCard)
        self.telegramLink.setObjectName("telegramLink")
        self.telegramLink.setUrl(TELEGRAM)

        self.instagramLink = HyperlinkLabel("Instagram",self.profileCard)
        self.instagramLink.setObjectName("instagramLink")
        self.instagramLink.setUrl(INSTAGRAM)

        spacerItem2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.linkLayout.addWidget(self.githubLink)
        self.linkLayout.addWidget(self.telegramLink)
        self.linkLayout.addWidget(self.instagramLink)

        self.textLayout.addItem(spacerItem1)
        self.textLayout.addWidget(self.nameLabel)
        self.textLayout.addWidget(self.emailLabel)
        self.textLayout.addLayout(self.linkLayout)
        self.textLayout.addItem(spacerItem2)

        self.profileLayout.addWidget(self.avatar)
        self.profileLayout.addItem(spacerItem)
        self.profileLayout.addLayout(self.textLayout)

    def initUi(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 80, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName("settingInterface")

        self.scrollWidget.setObjectName("scrollWidget")

        self.settingLabel.setObjectName("settingLabel")
        self.settingLabel.move(36, 30)

        self.micaCard.setEnabled(isWin11())

        # set custom stylesheet
        StyleSheet.SETTING_INTERFACE.apply(self)

        # add cards to group
        self.personalGroup.addSettingCard(self.micaCard)
        self.personalGroup.addSettingCard(self.themeCard)
        self.personalGroup.addSettingCard(self.themeColorCard)
        self.personalGroup.addSettingCard(self.zoomCard)
        self.personalGroup.addSettingCard(self.languageCard)

        self.aboutGroup.addSettingCard(self.profileCard)
        self.aboutGroup.addSettingCard(self.feedbackCard)
        self.aboutGroup.addSettingCard(self.aboutCard)

        # add setting card group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)
        self.expandLayout.addWidget(self.personalGroup)
        self.expandLayout.addWidget(self.aboutGroup)

    def restartInfoBar(self):
        """Show restart tooltip"""

        InfoBar.success(
            self.tr("Success"),
            self.tr("Configuration takes effect after restart"),
            duration=1500,
            parent=self
        )

    def connectSignalToSlot(self):
        """Connect signal to slot"""

        cfg.appRestartSig.connect(self.restartInfoBar)

        # personalization
        self.themeCard.optionChanged.connect(lambda ci: setTheme(cfg.get(ci), lazy=True))
        self.themeColorCard.colorChanged.connect(lambda c: setThemeColor(c, lazy=True))
        self.micaCard.checkedChanged.connect(signalBus.micaEnableChanged)

        # about
        self.feedbackCard.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(SCSHUB_FEEDBACK_URL)))
