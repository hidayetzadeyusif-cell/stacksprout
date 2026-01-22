class AnimationController:
    def __init__(self, context, events_len):
        self.context = context

        # previously context.timer
        self.cursor = 1
        self.threshold = events_len

        # previously context.animation
        self.playing = False
        self.after_id = None
        self.delay_ms = 300

    # ---- timeline control ----
    def step(self, backwards=False):
        if backwards:
            self.cursor = max(self.cursor - 1, 1)
        else:
            self.cursor = min(self.cursor + 1, self.threshold)

    def reset(self):
        self.cursor = 1
        self.playing = False
        self.context.ui["play_button"].configure(text="Play")

    def end(self):
        self.cursor = self.threshold
        self.playing = False
        self.context.ui["play_button"].configure(text="Play")

    def play(self, force_set=None):
        if force_set is not None:
            self.playing = force_set

        if self.playing:
            self.playing = False
            self.context.ui["play_button"].configure(text="Play")
            return

        if self.cursor >= self.threshold:
            self.cursor = 0
            animate(self.context)

        self.playing = True
        self.context.ui["play_button"].configure(text="Pause")
        self.tick()

    def tick(self):
        if not self.playing:
            return

        self.delay_ms = int(self.context.ui["anim_speed_scale"].get())

        if self.cursor >= self.threshold:
            self.playing = False
            return

        self.cursor += 1
        animate(self.context)

        self.after_id = self.context.canvas.after(
            self.delay_ms,
            self.tick
        )

def sync_timeline_ui(ui, timer):
    cursor = timer["cursor"]
    threshold = timer["threshold"]

    ui["anim_timeline_scrub_var"].set(min(max(cursor, 1), threshold))

    ui["timeline_scrub_label"].configure(
        text=f"Time step: {cursor} / {threshold}"
    )
def show_all_nodes_active(canvas, graph_config):
    # Nodes
    canvas.dtag("node", "future_node_oval")
    canvas.dtag("node", "completed_node_oval")
    canvas.dtag("node", "future_node_label1")
    canvas.dtag("node", "completed_node_label1")
    canvas.dtag("node", "future_node_label2")
    canvas.dtag("node", "completed_node_label2")

    canvas.addtag_withtag("active_node_oval", "node")
    canvas.addtag_withtag("active_node_label1", "node")
    canvas.addtag_withtag("active_node_label2", "node")

    # Edges
    canvas.dtag("edge", "future_edge")
    canvas.dtag("edge", "completed_edge")
    canvas.addtag_withtag("active_edge", "edge")

    update_animation_nodes(canvas, graph_config)
def update_animation_nodes(canvas, graph_config):
    for tag, options in graph_config.items():
        for item in canvas.find_withtag(tag):
            item_type = canvas.type(item)

            safe_options = {}
            for k, v in options.items():
                if k == "outline" and item_type == "oval":
                    safe_options[k] = v
                elif k == "fill" and item_type == "text":
                    safe_options[k] = v
                elif k == "fill" and item_type in ("text", "line"):
                    safe_options[k] = v

            if safe_options:
                canvas.itemconfigure(item, **safe_options)
def animate(context):
    p = context.anim.cursor

    for info in context.call_info.values():
        node_id = info["self_id"]
        t_in = info["in_time"]
        t_out = info["out_time"]

        if p < t_in:
            state = "future"
        elif p < t_out:
            state = "active"
        else:
            state = "completed"

        for item in context.canvas.find_withtag(f"node_{node_id}"):
            context.canvas.dtag(item, "future_node_oval")
            context.canvas.dtag(item, "active_node_oval")
            context.canvas.dtag(item, "completed_node_oval")
            context.canvas.dtag(item, "future_node_label1")
            context.canvas.dtag(item, "active_node_label1")
            context.canvas.dtag(item, "completed_node_label1")
            context.canvas.dtag(item, "future_node_label2")
            context.canvas.dtag(item, "active_node_label2")
            context.canvas.dtag(item, "completed_node_label2")

            for suffix in ("oval", "label1", "label2"):
                context.canvas.addtag_withtag(f"{state}_node_{suffix}", item)
        
        for item in context.canvas.find_withtag(f"edge_{node_id}"):
            context.canvas.dtag(item, "future_edge")
            context.canvas.dtag(item, "active_edge")
            context.canvas.dtag(item, "completed_edge")
            context.canvas.addtag_withtag(f"{state}_edge", item)

    # update timeline scrubber for sync
    sync_timeline_ui(
    context.ui,
        {"cursor": context.anim.cursor, "threshold": context.anim.threshold}
    )

    update_animation_nodes(context.canvas, context.ui["graph_config"])