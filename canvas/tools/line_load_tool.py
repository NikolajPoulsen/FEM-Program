from .tool import Tool


class LineLoadTool(Tool):
    name = "LineLoad"
    pickable_targets = {"beam"}