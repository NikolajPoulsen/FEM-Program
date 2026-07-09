from .tool import Tool


class PointLoadTool(Tool):
    name = "PointLoad"
    pickable_targets = {"node"}