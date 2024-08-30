import sys
from enum import Enum

from PyQt5.QtCore import QLocale

from qfluentwidgets import (
    OptionsConfigItem,
    OptionsValidator,
    ConfigSerializer,
    BoolValidator,
    ConfigItem,
    QConfig,
    Theme,
    qconfig,
)


def is_win11():
    return sys.platform == "win32" and sys.getwindowsversion().build >= 22000


class Language(Enum):

    ENGLISH = QLocale(QLocale.English)
    AUTO = QLocale()


class LanguageSerializer(ConfigSerializer):

    def serialize(self, language):
        return language.value.name() if language != Language.AUTO else "Auto"

    def deserialize(self, value: str):
        return Language(QLocale(value)) if value != "Auto" else Language.AUTO


class Config(QConfig):

    mica_effect = ConfigItem("QFluentWidgets", "MicaEnabled", False, BoolValidator())

    dpi_scale = OptionsConfigItem(
        "QFluentWidgets",
        "DpiScale",
        "Auto",
        OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]),
        restart=True,
    )

    language = OptionsConfigItem(
        "QFluentWidgets",
        "Language",
        Language.ENGLISH,
        OptionsValidator(Language),
        LanguageSerializer(),
        restart=True,
    )

    colorize = ConfigItem("SCSHub", "ColorizeBanner", False, BoolValidator())


cfg = Config()
cfg.themeMode.value = Theme.AUTO

qconfig.load("config.json", cfg)
