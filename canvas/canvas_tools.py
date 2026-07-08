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


class SelectTool(Tool):
    name = "Select"
    pickable_targets = {"plane", "node", "beam"}

    def __init__(self, canvas):
        super().__init__(canvas)
        self.last_x = None
        self.last_y = None

    def on_left_press(self, actor, x, y):
        if actor is self.canvas.plane_actor or actor is None:
            self.canvas.set_selected(None)
            self.canvas.dragging_node_id = None
            self.canvas.dragging_beam_id = None
            return

        node_id = self.canvas.actor_to_node.get(actor)
        if node_id is not None:
            self.canvas.set_selected("node", node_id)
            self.canvas.dragging_node_id = node_id
            return

        beam_id = self.canvas.actor_to_beam.get(actor)
        if beam_id is not None:
            self.canvas.set_selected("beam", beam_id)
            self.canvas.dragging_beam_id = beam_id
            return

    def on_left_release(self, obj, event):
        if self.canvas.dragging_node_id is not None or self.canvas.dragging_beam_id is not None:
            self.canvas.dragging_node_id = None
            self.canvas.dragging_beam_id = None
            if self.canvas.on_change:
                self.canvas.on_change()

        self.last_x = None
        self.last_y = None

    def on_drag(self, actor, x, y):
        if self.last_x is None or self.last_y is None:
            self.last_x = x
            self.last_y = y
            return

        if getattr(self.canvas, "dragging_node_id", None) is not None:
            node_id = self.canvas.dragging_node_id
            self.canvas.model.nodes[node_id] = (x, y)
            self.canvas.move_node_actor(node_id, x, y)

            self.canvas.render()
        elif getattr(self.canvas, "dragging_beam_id", None) is not None:
            node1_id, node2_id = self.canvas.dragging_beam_id

            dx = x - self.last_x
            dy = y - self.last_y

            # Flyt knude 1
            x1, y1 = self.canvas.model.nodes[node1_id]
            new_x1, new_y1 = x1 + dx, y1 + dy
            self.canvas.model.nodes[node1_id] = (new_x1, new_y1)
            self.canvas.move_node_actor(node1_id, new_x1, new_y1)

            # Flyt knude 2
            x2, y2 = self.canvas.model.nodes[node2_id]
            new_x2, new_y2 = x2 + dx, y2 + dy
            self.canvas.model.nodes[node2_id] = (new_x2, new_y2)
            self.canvas.move_node_actor(node2_id, new_x2, new_y2)

            self.last_x = x
            self.last_y = y

            self.canvas.render()


class NodeTool(Tool):
    name = "Node"
    pickable_targets = {"plane"}

    def on_left_press(self, actor, x, y):
        if actor is self.canvas.plane_actor:
            node_id = self.canvas.model.add_node(x, y)
            self.canvas.draw_node(node_id, x, y)
            if self.canvas.on_change:
                self.canvas.on_change()


class ElementTool(Tool):
    name = "Element"
    pickable_targets = {"node"}

    def __init__(self, canvas):
        super().__init__(canvas)
        self.pending_node = None

    def on_left_press(self, actor, x, y):
        node_id = self.canvas.actor_to_node.get(actor)
        if node_id is None:
            return

        if self.pending_node is None:
            self.pending_node = node_id
            self.canvas.set_selected("node", node_id)
        else:
            node_id1 = self.pending_node
            node_id2 = node_id

            if node_id1 != node_id2:
                self.canvas.model.add_beam(node_id1, node_id2)
                self.canvas.draw_beam(node_id1, node_id2)
                self.canvas.set_selected(None)
                if self.canvas.on_change:
                    self.canvas.on_change()

            self.pending_node = None

    def on_hover(self, actor, x, y):
        #TODO: Add highlight til knuden musen er over
        pass


class PointLoadTool(Tool):
    name = "PointLoad"
    pickable_targets = {"node"}


class LineLoadTool(Tool):
    name = "LineLoad"
    pickable_targets = {"beam"}


class FixedTool(Tool):
    name = "Fixed"
    pickable_targets = {"node"}


class PinnedTool(Tool):
    name = "Pinned"
    pickable_targets = {"node"}


class RollerTool(Tool):
    name = "Roller"
    pickable_targets = {"node"}