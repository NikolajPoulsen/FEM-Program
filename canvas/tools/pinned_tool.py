from .tool import Tool


class PinnedTool(Tool):
    name = "Pinned"
    pickable_targets = {"node"}