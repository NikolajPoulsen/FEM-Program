from .tool import Tool


class LineLoadTool(Tool):
    name = "LineLoad"
    pickable_targets = {"beam", "plane"}

    def on_hover(self, actor, x, y):
        if actor is self.canvas.plane_actor or actor is None:
            self.canvas.set_hovered(None)
            return

        beam_id = self.canvas.actor_to_beam.get(actor)
        if beam_id is not None:
            self.canvas.set_hovered("beam", beam_id)
            return