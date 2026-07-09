class Tool:
    name = "Tool"
    pickable_targets: set[str] = set()

    def __init__(self, canvas):
        self.canvas = canvas

    def on_left_press(self, actor, x, y):
        pass

    def on_left_release(self, obj, event):
        pass

    def on_drag(self, actor, x, y):
        pass

    def on_hover(self, actor, x, y):
        pass