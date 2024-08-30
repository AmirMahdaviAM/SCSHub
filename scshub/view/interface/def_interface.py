from qfluentwidgets import ScrollArea

from ..widget.def_creator_widget import DefCreatorWidget
from ...common.tool import signal_bus


class DefInterface(ScrollArea):

    def __init__(self):
        super().__init__()

        self.setObjectName("def_interface")

        self.def_creator = DefCreatorWidget(self)

        self.setViewportMargins(36, 36, 36, 36)
        self.setWidget(self.def_creator)
        self.setWidgetResizable(True)
        self.setStyleSheet("border: none; background: transparent;")

        signal_bus.window_width.connect(self.edge_spacer)

    def edge_spacer(self, width):

        spacer_width = int((width - 1070) / 2)
        self.setViewportMargins(spacer_width, 36, spacer_width, 36)
