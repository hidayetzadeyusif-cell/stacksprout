import tkinter as tk
from .canvas_utils import get_node_circle
from .animation import animate

# store graph geometry
VIEW = {
    "scale": 1.0,
    "tx": 0.0,
    "ty": 0.0,
}
EDGE_ENDPOINTS = {}
NODE_CENTER = {}  # node_id -> (cx, cy)
NODE_RADIUS = {}  # node_id -> r
NODE_ITEMS = {}  # node_id -> list of canvas item IDs

def keybind_gate(event, view_mode, func):
    """Only run func if we're in animation view (same behaviour as before)."""
    if view_mode == 1:
        func()

def cull_nodes(canvas, margin=300):
    """
    Hide node items that are outside the viewport + margin.
    Uses NODE_CENTER / NODE_RADIUS in canvas coordinates.
    """
    vx0 = canvas.canvasx(0)
    vy0 = canvas.canvasy(0)
    vx1 = vx0 + canvas.winfo_width()
    vy1 = vy0 + canvas.winfo_height()

    for u, (wx, wy) in NODE_CENTER.items():
        cx = wx * VIEW["scale"] + VIEW["tx"]
        cy = wy * VIEW["scale"] + VIEW["ty"]
        r  = NODE_RADIUS[u] * VIEW["scale"]

        offscreen = (
            cx + r < vx0 - margin
            or cx - r > vx1 + margin
            or cy + r < vy0 - margin
            or cy - r > vy1 + margin
        )

        for item in NODE_ITEMS[u]:
            canvas.itemconfigure(item, state="hidden" if offscreen else "normal")
def cull_edges(canvas, margin=300):
    """
    Hide edges where both endpoints are offscreen.
    Uses NODE_CENTER / NODE_RADIUS in canvas coordinates.
    """
    vx0 = canvas.canvasx(0) - margin
    vy0 = canvas.canvasy(0) - margin
    vx1 = vx0 + canvas.winfo_width() + margin
    vy1 = vy0 + canvas.winfo_height() + margin

    for edge_id, (u, v) in EDGE_ENDPOINTS.items():
        wx0, wy0 = NODE_CENTER[u]
        wx1, wy1 = NODE_CENTER[v]

        cx0 = wx0 * VIEW["scale"] + VIEW["tx"]
        cy0 = wy0 * VIEW["scale"] + VIEW["ty"]
        cx1 = wx1 * VIEW["scale"] + VIEW["tx"]
        cy1 = wy1 * VIEW["scale"] + VIEW["ty"]

        r0 = NODE_RADIUS[u] * VIEW["scale"]
        r1 = NODE_RADIUS[v] * VIEW["scale"]

        u_off = (
            cx0 + r0 < vx0
            or cx0 - r0 > vx1
            or cy0 + r0 < vy0
            or cy0 - r0 > vy1
        )

        v_off = (
            cx1 + r1 < vx0
            or cx1 - r1 > vx1
            or cy1 + r1 < vy0
            or cy1 - r1 > vy1
        )

        canvas.itemconfigure(edge_id, state="hidden" if (u_off and v_off) else "normal")
def cull_canvas(canvas, margin=300):
    """Run both node and edge culling."""
    cull_nodes(canvas, margin=margin)
    cull_edges(canvas, margin=margin)

def select_node(canvas, context, node_id, toggle=True):
    selected_id = context.selected_node["id"]

    # Deselect if clicking the already-selected node
    if selected_id == node_id and toggle:
        node_tag = f"node_{node_id}"
        circle = get_node_circle(canvas, node_tag)
        if circle:
            canvas.itemconfig(circle, width=2)

        context.selected_node["id"] = None

        info_text = context.ui["info_text"]
        info_text.config(state="normal")
        info_text.delete("1.0", tk.END)
        info_text.config(state="disabled")
        return

    # Unhighlight previously selected node
    if selected_id is not None:
        old_tag = f"node_{selected_id}"
        old_circle = get_node_circle(canvas, old_tag)
        if old_circle:
            canvas.itemconfig(old_circle, width=2)

    # Highlight newly selected node
    node_tag = f"node_{node_id}"
    circle = get_node_circle(canvas, node_tag)
    if circle:
        canvas.itemconfig(circle, width=4)
    
    # Select newly selected node in TreeView
    iid = f"item_{node_id}"
    context.ui["hierarchy_treeview"].selection_set(iid)
    context.ui["hierarchy_treeview"].see(iid)

    context.selected_node["id"] = node_id
    info = context.call_info[node_id]

    info_text = context.ui["info_text"]
    info_text.config(state="normal")
    info_text.delete("1.0", tk.END)

    info_text.insert(tk.END, f"Call ID: {node_id}\n")
    info_text.insert(tk.END, f"Function: {info['name']}\n")
    info_text.insert(tk.END, f"Arguments: {info['args']}\n")
    info_text.insert(tk.END, f"Result: {info['result']}\n")
    info_text.insert(tk.END, f"Depth: {info['depth']}\n")
    info_text.insert(tk.END, f"In Time: {info['in_time']}\n")
    info_text.insert(tk.END, f"Out Time: {info['out_time']}\n")

    info_text.config(state="disabled")

def on_tree_select(event, tree, context):
    selection = tree.selection()
    if not selection:
        return

    iid = selection[0]
    node_id = int(iid.split("_")[1])

    if context.selected_node["id"] == node_id:
        return

    select_node(context.canvas, context, node_id, toggle=False)
def on_node_click(event, context):
    canvas = event.widget

    item = canvas.find_withtag("current")[0]
    tags = canvas.gettags(item)

    if "future_node_oval" in tags:
        return

    node_tag = next(t for t in tags if t.startswith("node_"))
    node_id = int(node_tag[5:])

    select_node(canvas, context, node_id)
def enable_canvas_pan(canvas, on_pan_end=None):
    """
    Simple middle-button pan: moves all canvas items and schedules an optional
    on_pan_end callback after motion stops (debounced).
    """
    pan = {"x": 0, "y": 0}
    pan_job = {"id": None}

    def start(event):
        pan["x"] = event.x
        pan["y"] = event.y

    def drag(event):
        dx = event.x - pan["x"]
        dy = event.y - pan["y"]
        canvas.move("all", dx, dy)
        VIEW["tx"] += dx
        VIEW["ty"] += dy
        pan["x"] = event.x
        pan["y"] = event.y

        if on_pan_end:
            if pan_job["id"] is not None:
                canvas.after_cancel(pan_job["id"])
            pan_job["id"] = canvas.after(80, on_pan_end)

    canvas.bind("<ButtonPress-2>", start)
    canvas.bind("<B2-Motion>", drag)
def on_zoom(
    event,
    context,
    zoom_config,
    on_zoom_end=None,
):
    """
    Zoom handler that mutates a provided `scale` dict with key "value".
    Also scales canvas items and adjusts font sizes.
    """
    if event.delta > 0 or getattr(event, "num", None) == 4:
        factor = zoom_config["step"]
    else:
        factor = 1 / zoom_config["step"]

    new_scale = VIEW["scale"] * factor
    if not (zoom_config["min_scale"] <= new_scale <= zoom_config["max_scale"]):
        return

    x = context.canvas.canvasx(event.x)
    y = context.canvas.canvasy(event.y)
    context.canvas.scale("all", x, y, factor, factor)

    VIEW["tx"] = x + (VIEW["tx"] - x) * factor
    VIEW["ty"] = y + (VIEW["ty"] - y) * factor
    VIEW["scale"] *= factor

    context.style["canvas_font_medium"].configure(size=max(2, int(context.style["base_font_medium"] * new_scale)))
    context.style["canvas_font_small"].configure(size=max(1, int(context.style["base_font_small"] * new_scale)))

    if on_zoom_end:
        if hasattr(context.canvas, "_zoom_job"):
            context.canvas.after_cancel(context.canvas._zoom_job)
        context.canvas._zoom_job = context.canvas.after(80, on_zoom_end)

def bind_keys(root, context, zoom_config):
    # -- Bind zoom/pan. Pass local fonts/base sizes to on_zoom where needed --
    context.canvas.bind(
        "<MouseWheel>",
        lambda e: on_zoom(
            e,
            context,
            zoom_config,
            on_zoom_end=lambda: cull_canvas(context.canvas),
        ),
    )
    context.canvas.bind(
        "<Button-4>",
        lambda e: on_zoom(
            e,
            context,
            zoom_config,
            on_zoom_end=lambda: cull_canvas(context.canvas),
        ),
    )
    context.canvas.bind(
        "<Button-5>",
        lambda e: on_zoom(
            e,
            context,
            zoom_config,
            on_zoom_end=lambda: cull_canvas(context.canvas),
        ),
    )

    # Panning
    enable_canvas_pan(context.canvas, on_pan_end=lambda: cull_canvas(context.canvas))

    # Node click handler receives context (so it can show info, highlight, etc.)
    context.canvas.tag_bind("node", "<Button-1>", lambda event: on_node_click(event, context))

    # Keybinds use the simple context-based gate above
    root.bind_all("<KeyPress-space>", lambda e: keybind_gate(e, context.mode["view_mode"], context.anim.play))
    root.bind_all(
        "<KeyPress-Left>",
        lambda e: keybind_gate(
            e, context.mode["view_mode"], lambda: (context.anim.step(backwards=True), animate(context))
        ),
    )
    root.bind_all(
        "<KeyPress-Right>",
        lambda e: keybind_gate(e, context.mode["view_mode"], lambda: (context.anim.step(), animate(context))),
    )
    root.bind_all(
        "<KeyPress-Home>",
        lambda e: keybind_gate(e, context.mode["view_mode"], lambda: (context.anim.reset(), animate(context))),
    )
    root.bind_all(
        "<KeyPress-End>",
        lambda e: keybind_gate(e, context.mode["view_mode"], lambda: (context.anim.end(), animate(context))),
    )