from PySide6.QtWidgets import QMainWindow

from .ui_elements import ToolButton, SmallButtonColumn, RibbonSeparator, Ribbon, RibbonGroup
from canvas import DrawingCanvas
from canvas.tools import *
from model import BeamModel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mit CAD/FEM Program")
        self.resize(800, 600)

        self.model = BeamModel()
        self.canvas = DrawingCanvas(self.model, on_change=self._update_status)
        self.setCentralWidget(self.canvas.interactor)

        self.active_button = None
        self.build_ribbon()

    def build_ribbon(self):
        ribbon = Ribbon()
        self.setMenuWidget(ribbon)

        cad_layout = ribbon.add_ribbon_tab("CAD")

        # Group 1
        group_files = RibbonGroup("Filer")

        btn_new = ToolButton(text="Ny", style=ToolButton.ButtonStyle.SMALL)
        btn_open = ToolButton(text="Åben", style=ToolButton.ButtonStyle.SMALL)
        btn_save = ToolButton(text="Save", style=ToolButton.ButtonStyle.SMALL)

        col_files = SmallButtonColumn([btn_new, btn_open, btn_save])
        group_files.add_widget(col_files)

        # Group 2
        group_elements = RibbonGroup("Elementer")

        btn_node = ToolButton(text="Knude", style=ToolButton.ButtonStyle.LARGE, checkable=True)
        btn_element = ToolButton(text="Bjælke", style=ToolButton.ButtonStyle.LARGE, checkable=True)

        btn_node.clicked.connect(lambda checked=False, b=btn_node: self.tool_button_clicked(b, NodeTool))
        btn_element.clicked.connect(lambda checked=False, b=btn_element: self.tool_button_clicked(b, BeamTool))

        group_elements.add_widget(btn_node)
        group_elements.add_widget(btn_element)

        cad_layout.addWidget(group_files)
        cad_layout.addWidget(RibbonSeparator())
        cad_layout.addWidget(group_elements)

        # Group 3
        group_loads = RibbonGroup("Laster")

        btn_point_load = ToolButton(text="Punktlast", style=ToolButton.ButtonStyle.LARGE, checkable=True)
        btn_line_load = ToolButton(text="Linjelast", style=ToolButton.ButtonStyle.LARGE, checkable=True)

        btn_point_load.clicked.connect(lambda checked=False, b=btn_point_load: self.tool_button_clicked(b, PointLoadTool))
        btn_line_load.clicked.connect(lambda checked=False, b=btn_line_load: self.tool_button_clicked(b, LineLoadTool))

        group_loads.add_widget(btn_point_load)
        group_loads.add_widget(btn_line_load)

        # Group 4
        group_boundary = RibbonGroup("Randbetingelser")

        btn_fixed = ToolButton(text="Indspænding", style=ToolButton.ButtonStyle.LARGE, checkable=True)
        btn_pinned = ToolButton(text="Fast Simpel", style=ToolButton.ButtonStyle.LARGE, checkable=True)
        btn_roller = ToolButton(text="Fri Simpel", style=ToolButton.ButtonStyle.LARGE, checkable=True)

        btn_fixed.clicked.connect(lambda checked=False, b=btn_fixed: self.tool_button_clicked(b, FixedTool))
        btn_pinned.clicked.connect(lambda checked=False, b=btn_pinned: self.tool_button_clicked(b, PinnedTool))
        btn_roller.clicked.connect(lambda checked=False, b=btn_roller: self.tool_button_clicked(b, RollerTool))

        group_boundary.add_widget(btn_fixed)
        group_boundary.add_widget(btn_pinned)
        group_boundary.add_widget(btn_roller)

        cad_layout.addWidget(group_files)
        cad_layout.addWidget(RibbonSeparator())
        cad_layout.addWidget(group_elements)
        cad_layout.addWidget(RibbonSeparator())
        cad_layout.addWidget(group_loads)
        cad_layout.addWidget(RibbonSeparator())
        cad_layout.addWidget(group_boundary)

    def tool_button_clicked(self, button, tool):
        if button is self.active_button:
            button.setChecked(False)
            self.active_button = None
            self.canvas.set_current_tool(SelectTool)
            #print(f"Tool button clicked (Deselected {button.text()})")
            return

        if self.active_button is not None:
            self.active_button.setChecked(False)

        button.setChecked(True)
        self.active_button = button
        self.canvas.set_current_tool(tool)
        #print(f"Tool button clicked (Selected {button.text()})")

    def _update_status(self):
        #print(f"Antal noder: {len(self.model.nodes)}")
        pass
