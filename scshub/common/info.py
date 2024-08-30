import os
from sys import platform, maxsize


# scshub
YEAR = 2024
VERSION = "1.3"
SCSHUB_GITHUB_URL = "https://github.com/AmirMahdaviAM/SCSHub/"
SCSHUB_FEEDBACK_URL = "https://github.com/AmirMahdaviAM/SCSHub/issues"
SCSHUB_FORUM_URL = "https://forum.scssoft.com/viewtopic.php?t=328411"
GITHUB = "https://github.com/AmirMahdaviAM/"
TELEGRAM = "https://t.me/amirmdvi"
INSTAGRAM = "https://instagram.com/amirmdvl"


# tools path
TOOLS_PATH = os.path.join(os.getcwd(), "tools")
MAIN_LOG = "scshub.log"

# create tool path if not exist
if not os.path.isdir(TOOLS_PATH):
    os.makedirs(TOOLS_PATH, exist_ok=True)


# scs
SCS_TOOL_INFO = "https://modding.scssoft.com/wiki/Documentation/Tools/Game_Archive_Packer"
SCS_TOOL_URL = "https://download.eurotrucksimulator2.com/scs_packer_1_50.zip"
SCS_TOOL_ZIP = os.path.join(TOOLS_PATH, "scs_packer.zip")
SCS_TOOL_UNZIP = TOOLS_PATH
SCS_TOOL_PATH = os.path.join(TOOLS_PATH, "scs_packer.exe")
SCS_PACKER_LOG = "scs_packer.log"
SCS_EXTRACTOR_LOG = "scs_extractor.log"


# pix
PIX_CONVERTER_INFO = "https://github.com/mwl4/ConverterPIX/"
if platform == "linux":
    PIX_CONVERTER_URL = "https://github.com/mwl4/ConverterPIX/raw/master/bin/linux/converter_pix"
    PIX_CONVERTER_PATH = os.path.join(TOOLS_PATH, "converter_pix")
elif platform == "darwin":
    PIX_CONVERTER_URL = (
        "https://github.com/theHarven/ConverterPIX/raw/MacOS_binary/bin/macos/converter_pix"
    )
    PIX_CONVERTER_PATH = os.path.join(TOOLS_PATH, "converter_pix")
else:
    PIX_CONVERTER_URL = (
        "https://github.com/mwl4/ConverterPIX/raw/master/bin/win_x86/converter_pix.exe"
    )
    PIX_CONVERTER_PATH = os.path.join(TOOLS_PATH, "converter_pix.exe")
PIX_CONVERTER_LOG = "pix_converter.log"
PIX_FINDER_LOG = "pix_finder.log"


# sxc
SXC_INFO = "https://forum.scssoft.com/viewtopic.php?t=276948"
SXC_URL = "https://drive.google.com/uc?export=download&id=1rbRkKGICeQ8wwTnLKgs2cbBlpDx865X2"
SXC_ZIP = os.path.join(TOOLS_PATH, "sxc_extractor.zip")
SXC_UNZIP = os.path.join(TOOLS_PATH, "sxc_extractor")
SXC_HDB_URL = "https://drive.google.com/uc?export=download&id=1xDwb0pTZZ_Z2CqK9YrVPAd1DEJ2Vua4N"
SXC_HDB_PATH = os.path.join(SXC_UNZIP, "sxc.hdb")
if maxsize < 2**32:  # 32-bit
    SXC_EXTRACTOR_PATH = os.path.join(SXC_UNZIP, "sxc.exe")
    SXC_FINDER_PATH = os.path.join(SXC_UNZIP, "addons", "pathfinder", "sxclist.exe")
    SXC_PACKER_PATH = os.path.join(SXC_UNZIP, "addons", "packer", "sxcpack.exe")
elif maxsize > 2**32:  # 64-bit
    SXC_EXTRACTOR_PATH = os.path.join(SXC_UNZIP, "sxc64.exe")
    SXC_FINDER_PATH = os.path.join(SXC_UNZIP, "addons", "pathfinder", "sxclist64.exe")
    SXC_PACKER_PATH = os.path.join(SXC_UNZIP, "addons", "packer", "sxcpack64.exe")
SXC_EXTRACTOR_LOG = "sxc_extractor.log"
SXC_FINDER_LOG = "sxc_finder.log"
SXC_PACKER_LOG = "sxc_packer.log"
