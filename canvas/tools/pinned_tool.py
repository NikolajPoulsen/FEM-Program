from .tool import Tool


class PinnedTool(Tool):
    name = "Pinned"
    pickable_targets = {"node", "plane"}

    def on_left_press(self, actor, x, y):
        node_id = self.canvas.actor_to_node.get(actor)
        if node_id is not None:
            node = self.canvas.node_model.nodes[node_id]

            if not node.is_constrained:
                node.is_constrained = True
                node.locked_dofs.update({1, 2})  # Lås u, v

                self.canvas.draw_constraint(node_id, "pinned")

                if self.canvas.on_change:
                    self.canvas.on_change()

    def on_hover(self, actor, x, y):
        if actor is self.canvas.plane_actor or actor is None:
            self.canvas.set_hovered(None)
            return

        node_id = self.canvas.actor_to_node.get(actor)
        if node_id is not None:
            self.canvas.set_hovered("node", node_id)
            return