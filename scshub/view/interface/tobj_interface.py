from qfluentwidgets import ScrollArea

from ..widget.tobj_editor_widget import TobjEditorWidget
from ...common.tool import signal_bus


class TobjInterface(ScrollArea):

    def __init__(self):
        super().__init__()

        self.setObjectName("tobj_interface")

        self.tobj_editor = TobjEditorWidget(self)

        self.setViewportMargins(36, 36, 36, 36)
        self.setWidget(self.tobj_editor)
        self.setWidgetResizable(True)
        self.setStyleSheet("border: none; background: transparent;")

        signal_bus.window_width.connect(self.edge_spacer)

    def edge_spacer(self, width):

        spacer_width = int((width - 1070) / 2)
        self.setViewportMargins(spacer_width, 36, spacer_width, 36)
