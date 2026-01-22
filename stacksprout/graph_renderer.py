import tkinter as tk
import math
from .canvas_utils import create_circle, trim_text_to_width
from .interactions import (
    EDGE_ENDPOINTS,
    NODE_CENTER,
    NODE_RADIUS,
    NODE_ITEMS,
)

def draw_nodes(context):
    for u, (row, col) in context.pos.items():
        cx, cy = context.layout.node_center(row, col)

        circle = create_circle(
            context.canvas,
            cx,
            cy,
            context.layout.diameter / 2,
            fill=context.style["bg_color"],
            width=2,
            outline=context.ui["graph_config"]["future_node_oval"]["outline"],
            tags=("node", "future_node_oval", f"node_{u}"),
        )

        NODE_CENTER[u] = (cx, cy)
        NODE_RADIUS[u] = context.layout.diameter / 2
        NODE_ITEMS[u] = [circle]

        if not context.mode["large_graph"]:
            label1 = f"{context.call_info[u]['name']}({context.call_info[u]['args'][0]})"
            label1 = trim_text_to_width(label1, context.style["canvas_font_medium"], context.layout.diameter)
            label1_id = context.canvas.create_text(
                cx,
                cy,
                text=label1,
                font=context.style["canvas_font_medium"],
                fill=context.ui["graph_config"]["future_node_label1"]["fill"],
                justify="center",
                anchor="center",
                tags=("node", "future_node_label1", f"node_{u}"),
            )

            label2 = f"{context.call_info[u]['result']}"
            label2 = trim_text_to_width(
                label2, context.style["canvas_font_small"], math.floor(context.layout.diameter * math.sqrt(3) / 2)
            )
            label2_id = context.canvas.create_text(
                cx,
                cy + (context.layout.diameter / 4) * 1.0,  # scale is local for rendering here
                text=label2,
                font=context.style["canvas_font_small"],
                fill=context.ui["graph_config"]["future_node_label2"]["fill"],
                justify="center",
                anchor="center",
                tags=("node", "future_node_label2", f"node_{u}"),
            )
            NODE_ITEMS[u].extend([label1_id, label2_id])

def draw_edges(context):
    for u, vs in context.adj.items():
        for v in vs:
            if context.parent[u] == v:
                continue
            r = context.layout.diameter / 2

            row1, col1 = context.id_to_index[u]
            row2, col2 = context.id_to_index[v]

            x1, y1, x2, y2 = context.layout.edge_endpoints(row1, col1, row2, col2)

            dx = x2 - x1
            dy = y2 - y1
            dist = math.hypot(dx, dy) or 1.0

            x2 -= dx / dist * r
            y2 -= dy / dist * r

            edge = context.canvas.create_line(
                x1,
                y1,
                x2,
                y2,
                fill="black",
                width=2,
                arrow=tk.LAST,
                arrowshape=(10, 12, 5),
                tags=(f"edge_{v}", "edge"),
            )

            EDGE_ENDPOINTS[edge] = (u, v)