from .tree_to_grid import generate_tree_grid
from .graph_renderer import draw_nodes, draw_edges
from .ui import build_ui
from .layout import LayoutEngine
from .animation import show_all_nodes_active, AnimationController
from .interactions import bind_keys

import tkinter as tk
import tkinter.font as tkfont
import ctypes

class _VisualizationContext:
    """
    Minimal shared state used by callbacks and helpers.
    Keep only truly shared / mutable state here.
    """

    def __init__(self):
        self.canvas = None
        self.call_info = None
        self.parent = None

        # layout engine
        self.layout = None 

        # mode + animation state
        self.mode = {"view_mode": 0, "large_graph": False}  # 0 = static, 1 = animation
        self.anim = None

        # UI handles so callbacks can update UI
        self.ui = {}

        # style constants
        self.style = {}

        # selection + lookup tables
        self.selected_node = {"id": None}
        self.id_to_index = {}

        # graph structure (handy to have on context)
        self.tree_grid = None
        self.adj = None
        self.pos = None
    
def visualize_tree(func):
    if not hasattr(func, "parent") or not hasattr(func, "call_info"):
        raise RuntimeError("Function is not traced. Use decorator 'trace'.")
    if not func.parent or not func.call_info:
        print("No calls were traced. Try running the function.")
        return

    # attempt dpi awareness on Windows (harmless if fails)
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    root = tk.Tk()
    root.tk.call("tk", "scaling", 1.5)
    root.title(f"StackSprout - Recursion Tree for {func.__name__}")

    # Create context
    context = _VisualizationContext()
    
    # -------------------------
    # Local layout / style constants (keep them local)
    # -------------------------
    cell_offset, diameter = 30, 50
    context.style["canvas_font_medium"] = tkfont.Font(
        family="Segoe UI", size=diameter // 5
    )
    context.style["canvas_font_small"] = tkfont.Font(
        family="Segoe UI", size=diameter // 7
    )

    context.style["bg_color"] = "#f2f2ff"

    context.style["ui_font_medium"] = tkfont.Font(family="Segoe UI", size=10)
    context.style["base_font_medium"] = context.style["canvas_font_medium"].cget("size")
    context.style["base_font_small"] = context.style["canvas_font_small"].cget("size")

    canvas_width, canvas_height = 800, 600

    # -------------------------
    # Fill context and populate shared state
    # -------------------------
    context.canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg=context.style["bg_color"])
    context.call_info = func.call_info
    context.parent = func.parent

    # Build grid/graph and keep it on context (these are structural, not UI constants)
    tree_grid, adj, pos = generate_tree_grid(context.parent, context.call_info, center=True)
    context.tree_grid = tree_grid
    context.adj = adj
    context.pos = pos

    # Layout engine
    layout = LayoutEngine(tree_grid, diameter, cell_offset)
    layout.compute_centering(canvas_width, canvas_height)
    context.layout = layout

    # Zoom / drawing limits (locals)
    zoom_config = {
        "max_draw_nodes": 5000,
        "min_scale": 0.3,
        "max_scale": 3.0,
        "step": 1.1
    }

    # Large graph detection
    n = len(context.call_info)
    if n > zoom_config["max_draw_nodes"]:
        context.mode["large_graph"] = True

    # Build animation events if graph small enough
    events = []
    if not context.mode["large_graph"]:
        for info in context.call_info.values():
            events.append({"time": info["in_time"], "type": 0, "info": info})
            events.append({"time": info["out_time"], "type": 1, "info": info})
        events.sort(key=lambda e: e["time"])

    context.anim = AnimationController(context, len(events))

    # keep graph_config accessible to callbacks via context.ui
    context.ui["graph_config"] = {
        "active_node_oval": {"outline": "#333"},
        "active_node_label1": {"fill": "black"},
        "active_node_label2": {"fill": "black"},
        "completed_node_oval": {"outline": "#999"},
        "completed_node_label1": {"fill": "#666"},
        "completed_node_label2": {"fill": "#666"},
        "future_node_oval": {"outline": context.style["bg_color"]},
        "future_node_label1": {"fill": context.style["bg_color"]},
        "future_node_label2": {"fill": context.style["bg_color"]},
        "active_edge": {"fill": "black"},
        "completed_edge": {"fill": "#999"},
        "future_edge": {"fill": context.style["bg_color"]},
    }

    # selection lookup (id -> grid coordinate)
    for row in range(1, len(tree_grid)):
        for col in range(len(tree_grid[row])):
            context.id_to_index[tree_grid[row][col].id] = (row, col)

    # -------------------------
    # Draw graph
    # -------------------------
    draw_edges(context)
    draw_nodes(context)
    show_all_nodes_active(context.canvas, context.ui["graph_config"])
    
    # -------------------------
    # UI (clean ttk-based)
    # -------------------------
    build_ui(root, context, context.style["ui_font_medium"])

    # keybinds
    bind_keys(root, context, zoom_config)

    # pack canvas
    context.canvas.pack()

    root.mainloop()