from .tool import Tool


class FixedTool(Tool):
    name = "Fixed"
    pickable_targets = {"node"}