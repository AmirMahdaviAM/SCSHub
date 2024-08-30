import logging
import os

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices, QFont
from PyQt5.QtWidgets import QWidget, QSizePolicy, QHBoxLayout, QVBoxLayout

from qfluentwidgets import (
    PrimaryPushSettingCard,
    ComboBoxSettingCard,
    OptionsSettingCard,
    VerticalSeparator,
    SwitchSettingCard,
    SimpleCardWidget,
    SettingCardGroup,
    ColorSettingCard,
    PushSettingCard,
    StrongBodyLabel,
    HyperlinkLabel,
    CaptionLabel,
    AvatarWidget,
    SettingCard,
    IconWidget,
    ScrollArea,
    FluentIcon,
    BodyLabel,
    setFont,
    setTheme,
    setThemeColor,
)

from ...common.tool import (
    ScsHubDialog,
    signal_bus,
    scshub_infobar,
    scshub_dir_remover,
    scshub_file_remover,
)
from ...common.config import cfg, is_win11
from ...common.info import (
    SCSHUB_FEEDBACK_URL,
    PIX_CONVERTER_INFO,
    SCS_TOOL_INFO,
    TOOLS_PATH,
    INSTAGRAM,
    TELEGRAM,
    SXC_INFO,
    VERSION,
    GITHUB,
    YEAR,
)


logger = logging.getLogger("SCSHub")


class SettingInterface(ScrollArea):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setObjectName("setting_interface")

        self.main_widget = QWidget()
        self.main_widget.setStyleSheet("background-color: transparent;")

        self.main_lyt = QVBoxLayout(self.main_widget)
        self.main_lyt.setContentsMargins(0, 0, 0, 0)
        self.main_lyt.setSpacing(30)
        self.setting_label = BodyLabel(self.tr("Settings"), self.main_widget)
        self.setting_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        setFont(self.setting_label, 33, QFont.Light)

        self.setViewportMargins(36, 36, 36, 36)
        self.setWidget(self.main_widget)
        self.setWidgetResizable(True)
        self.setStyleSheet("border: none; background-color: transparent;")

        self.cards()
        self.profile()
        self.wiki()
        self.signal_bus()

        # personalization
        self.personal_group.addSettingCard(self.mica_card)
        self.personal_group.addSettingCard(self.colorize_card)
        self.personal_group.addSettingCard(self.theme_card)
        self.personal_group.addSettingCard(self.theme_color_card)
        self.personal_group.addSettingCard(self.zoom_card)
        self.personal_group.addSettingCard(self.language_card)
        self.personal_group.addSettingCard(self.reset_card)

        # about
        self.about_group.addSettingCard(self.profile_card)
        self.about_group.addSettingCard(self.wiki_card)
        self.about_group.addSettingCard(self.feedback_card)
        self.about_group.addSettingCard(self.about_card)

        self.main_lyt.addWidget(self.setting_label)
        self.main_lyt.addWidget(self.personal_group)
        self.main_lyt.addWidget(self.about_group)
        self.main_lyt.addStretch(1)

    def edge_spacer(self, width):

        spacer_width = int((width - 1070) / 2)
        self.setViewportMargins(spacer_width, 36, spacer_width, 36)

    def cards(self):

        # personalization
        self.personal_group = SettingCardGroup(self.tr("Personalization"), self.main_widget)

        self.mica_card = SwitchSettingCard(
            FluentIcon.TRANSPARENT,
            self.tr("Mica effect"),
            self.tr("Apply semi-transparent to windows and surfaces (Win11)"),
            cfg.mica_effect,
            self.personal_group,
        )
        self.mica_card.setEnabled(is_win11())

        self.colorize_card = SwitchSettingCard(
            FluentIcon.BACKGROUND_FILL,
            self.tr("Colorize home banner"),
            self.tr("Dynamic or static color for home top banner (affect performence)"),
            cfg.colorize,
            self.personal_group,
        )

        self.theme_card = OptionsSettingCard(
            cfg.themeMode,
            FluentIcon.BRUSH,
            self.tr("Application theme"),
            self.tr("Change the theme appearance"),
            texts=[self.tr("Light"), self.tr("Dark"), self.tr("Use system setting")],
            parent=self.personal_group,
        )

        self.theme_color_card = ColorSettingCard(
            cfg.themeColor,
            FluentIcon.PALETTE,
            self.tr("Theme color"),
            self.tr("Change the theme color"),
            self.personal_group,
        )
        self.theme_color_card.colorPicker.setFixedWidth(78)

        self.zoom_card = ComboBoxSettingCard(
            cfg.dpi_scale,
            FluentIcon.ZOOM,
            self.tr("Interface zoom"),
            self.tr("Change the size of widgets and fonts"),
            texts=["100%", "125%", "150%", "175%", "200%", self.tr("Use system setting")],
            parent=self.personal_group,
        )

        self.language_card = ComboBoxSettingCard(
            cfg.language,
            FluentIcon.LANGUAGE,
            self.tr("Language"),
            self.tr("Set preferred language for UI"),
            texts=["English", self.tr("Use system setting")],
            parent=self.personal_group,
        )

        self.reset_card = PushSettingCard(
            self.tr("Reset app"),
            FluentIcon.BROOM,
            self.tr("Reset app"),
            self.tr("Delete all tools files and app config"),
            self.personal_group,
        )

        # about
        self.about_group = SettingCardGroup(self.tr("About"), self.main_widget)

        self.feedback_card = PrimaryPushSettingCard(
            self.tr("Provide feedback"),
            FluentIcon.FEEDBACK,
            self.tr("Provide feedback"),
            self.tr("Help us improve SCS Hub by providing feedback"),
            self.about_group,
        )

        self.about_card = SettingCard(
            FluentIcon.INFO,
            self.tr("About"),
            "© "
            + self.tr("Copyright")
            + f" {YEAR}, AmirMahdavi. "
            + self.tr("Version")
            + " "
            + VERSION,
            self.about_group,
        )

    def profile(self):

        self.profile_card = SimpleCardWidget(self.main_widget)
        self.profile_card.setFixedHeight(120)

        self.profile_lyt = QHBoxLayout(self.profile_card)
        self.profile_lyt.setContentsMargins(16, 0, 0, 0)
        self.profile_lyt.setSpacing(16)
        self.profile_lyt.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        # avatar
        self.avatar = AvatarWidget(self.profile_card)
        self.avatar.setObjectName("avatar")
        self.avatar.setImage(":/image/avatar.png")
        self.avatar.setRadius(40)

        # text
        self.profile_text_lyt = QVBoxLayout()
        self.profile_text_lyt.setSpacing(0)
        self.profile_text_lyt.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.profile_name_label = StrongBodyLabel(self.profile_card)
        self.profile_name_label.setText("Amir Mahdavi")
        self.profile_name_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

        self.profile_email_label = BodyLabel(self.profile_card)
        self.profile_email_label.setText("mahdaviamir33@gmail.com")
        self.profile_email_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

        # link
        self.profile_link_lyt = QHBoxLayout()
        self.profile_link_lyt.setSpacing(10)

        self.profile_github_link = HyperlinkLabel("GitHub", self.profile_card)
        self.profile_github_link.setUrl(GITHUB)

        self.profile_telegram_link = HyperlinkLabel("Telegram", self.profile_card)
        self.profile_telegram_link.setUrl(TELEGRAM)

        self.profile_instagram_ink = HyperlinkLabel("Instagram", self.profile_card)
        self.profile_instagram_ink.setUrl(INSTAGRAM)

        self.profile_link_lyt.addWidget(self.profile_github_link)
        self.profile_link_lyt.addWidget(self.profile_telegram_link)
        self.profile_link_lyt.addWidget(self.profile_instagram_ink)

        self.profile_text_lyt.addWidget(self.profile_name_label)
        self.profile_text_lyt.addWidget(self.profile_email_label)
        self.profile_text_lyt.addSpacing(5)
        self.profile_text_lyt.addLayout(self.profile_link_lyt)

        self.profile_lyt.addWidget(self.avatar)
        self.profile_lyt.addLayout(self.profile_text_lyt)

    def wiki(self):

        self.wiki_card = SimpleCardWidget(self.main_widget)
        self.wiki_card.setFixedHeight(70)

        self.wiki_ayout = QHBoxLayout(self.wiki_card)
        self.wiki_ayout.setContentsMargins(16, 0, 0, 0)
        self.wiki_ayout.setSpacing(0)
        self.wiki_ayout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        # icon
        self.wiki_con = IconWidget(FluentIcon.PEOPLE, self.wiki_card)
        self.wiki_con.setFixedSize(16, 16)

        # scs
        self.wiki_scs_lyt = QVBoxLayout()
        self.wiki_scs_lyt.setSpacing(0)

        self.wiki_scs_ink = HyperlinkLabel("SCS Tool", self.wiki_card)
        self.wiki_scs_ink.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.wiki_scs_ink.setUrl(SCS_TOOL_INFO)

        self.wiki_scs_autor = CaptionLabel(self.wiki_card)
        self.wiki_scs_autor.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.wiki_scs_autor.setText("SCS Software")

        self.wiki_scs_lyt.addWidget(self.wiki_scs_ink)
        self.wiki_scs_lyt.addWidget(self.wiki_scs_autor)

        # seprator
        self.v_seprator_1 = VerticalSeparator()

        # pix_
        self.wiki_pix_lyt = QVBoxLayout()
        self.wiki_pix_lyt.setSpacing(0)

        self.wiki_pix_link = HyperlinkLabel("PIX Converter", self.wiki_card)
        self.wiki_pix_link.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.wiki_pix_link.setUrl(PIX_CONVERTER_INFO)

        self.wiki_pix_autor = CaptionLabel(self.wiki_card)
        self.wiki_pix_autor.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.wiki_pix_autor.setText("mwl4")

        self.wiki_pix_lyt.addWidget(self.wiki_pix_link)
        self.wiki_pix_lyt.addWidget(self.wiki_pix_autor)

        # seprator
        self.v_seprator_2 = VerticalSeparator()

        # sxc
        self.wiki_sxc_lyt = QVBoxLayout()
        self.wiki_sxc_lyt.setSpacing(0)

        self.wiki_sxc_link = HyperlinkLabel("SXC Extractor", self.wiki_card)
        self.wiki_sxc_link.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.wiki_sxc_link.setUrl(SXC_INFO)

        self.wiki_sxc_autor = CaptionLabel(self.wiki_card)
        self.wiki_sxc_autor.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.wiki_sxc_autor.setText("Madman")

        self.wiki_sxc_lyt.addWidget(self.wiki_sxc_link)
        self.wiki_sxc_lyt.addWidget(self.wiki_sxc_autor)

        self.wiki_ayout.addWidget(self.wiki_con)
        self.wiki_ayout.addSpacing(16)
        self.wiki_ayout.addLayout(self.wiki_scs_lyt)
        self.wiki_ayout.addSpacing(10)
        self.wiki_ayout.addWidget(self.v_seprator_1)
        self.wiki_ayout.addSpacing(10)
        self.wiki_ayout.addLayout(self.wiki_pix_lyt)
        self.wiki_ayout.addSpacing(10)
        self.wiki_ayout.addWidget(self.v_seprator_2)
        self.wiki_ayout.addSpacing(10)
        self.wiki_ayout.addLayout(self.wiki_sxc_lyt)

    def reset_app(self):

        dialog = ScsHubDialog(
            self.tr("Reset app"),
            self.tr(
                "Are you sure want to reset app and delete all data?\nThis action is Irreversible!"
            ),
            self.window(),
        )

        if dialog.exec_():
            scshub_file_remover("config.json")
            scshub_dir_remover(TOOLS_PATH)
            os.makedirs(TOOLS_PATH)

            signal_bus.pix_exist.emit(False)
            signal_bus.sxc_exist.emit(False)
            signal_bus.scs_exist.emit(False)

            scshub_infobar(self, "success", self.tr("Configuration takes effect after restart"))
            logger.info("All tools and app config deleted")

    def signal_bus(self):

        signal_bus.window_width.connect(self.edge_spacer)

        cfg.appRestartSig.connect(
            lambda: scshub_infobar(self, "success", "Configuration takes effect after restart")
        )

        # personalization
        self.mica_card.checkedChanged.connect(signal_bus.mica_enabled)
        self.theme_color_card.colorChanged.connect(lambda c: setThemeColor(c, lazy=True))
        self.theme_card.optionChanged.connect(lambda ci: setTheme(cfg.get(ci), lazy=True))

        # app
        self.colorize_card.checkedChanged.connect(signal_bus.colorize)
        self.reset_card.clicked.connect(lambda: self.reset_app())

        # about
        self.feedback_card.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(SCSHUB_FEEDBACK_URL))
        )
