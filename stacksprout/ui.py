import tkinter as tk
from tkinter import ttk
from .animation import (
    sync_timeline_ui,
    animate,
    show_all_nodes_active,
)
from .interactions import on_tree_select

def set_frame_enabled(frame, enabled):
    state = "normal" if enabled else "disabled"
    for child in frame.winfo_children():
        child.configure(state=state)

def toggle_mode(context):
    """
    Toggle between animation and static views.
    This uses only the context + UI handles contained in context.ui.
    """
    if context.mode["large_graph"]:
        return

    context.mode["view_mode"] = 1 - context.mode["view_mode"]
    anim = context.mode["view_mode"] == 1

    if anim:
        # reset animation state and start animate — animate is expected to read context.animation
        context.anim.reset()
        animate(context)
    else:
        show_all_nodes_active(context.canvas, context.ui.get("graph_config", {}))
        context.anim.play(force_set=True)

    # update the toggle button text
    context.ui["toggle_mode_button"].configure(text="Static" if anim else "Animation")

    # enable/disable appropriate UI frames
    set_frame_enabled(context.ui["step_frame"], anim)
    set_frame_enabled(context.ui["playback_frame"], anim)
    context.ui["anim_speed_scale"].configure(state="normal" if anim else "disabled")
    context.ui["anim_timeline_scrub_scale"].configure(state="normal" if anim else "disabled")

def build_ui(root, context, font):
    ACCENT = "#4e9f63"
    PANEL_BG = "#484848"
    PANEL_BG_LIGHT = "#656565"
    BUTTON_BG = "#717171"
    TEXT_LIGHT = "#e6e6e6"
    TEXT_MUTED = "#b5b8b2"

    style = ttk.Style()
    style.theme_use("default")

    style.configure(
        "TFrame",
        background=PANEL_BG,
    )

    style.configure(
        "TLabel",
        background=PANEL_BG,
        foreground=TEXT_LIGHT,
    )

    style.configure(
        "Muted.TLabel",
        foreground=TEXT_MUTED,
    )

    style.configure(
        "TButton",
        padding=(10, 4),
        background=BUTTON_BG,
        foreground=TEXT_LIGHT,
    )

    style.map(
        "TButton",
        background=[
            ("active", "#575757"),
            ("pressed", "#444444"),
        ],
    )

    style.configure(
        "Accent.TButton",
        background=ACCENT,
        foreground="white",
    )

    style.map(
        "Accent.TButton",
        background=[
            ("active", "#13a635"),
            ("pressed", "#10cc3c"),
        ],
    )

    style.configure(
        "Icon.TButton",
        padding=(6, 4),
    )

    # ---- Hierarchy view (top-right) ----
    hierarchy = ttk.Treeview(root, selectmode='browse')

    stack = [(1, "")]
    while stack:
        current_node, parent = stack.pop() 
        node_id = hierarchy.insert(parent, "end", values=(current_node,), iid=f"item_{current_node}",
                    text=f"{current_node} - {context.call_info[current_node]["name"]}({context.call_info[current_node]["args"]})")
        for child, parent_of_child in context.parent.items():
            if parent_of_child == current_node:
                stack.append((child, node_id))

    hierarchy.place(relx=0.0, rely=0.0, anchor="nw")

    hierarchy.bind("<<TreeviewSelect>>", lambda e: on_tree_select(e, hierarchy, context))

    # ---- Info panel (bottom-right) ----
    info_frame = ttk.Frame(root, padding=8)
    info_frame.place(relx=1.0, rely=1.0, anchor="se", x=-12, y=-18)

    info_title = ttk.Label(
        info_frame,
        text="Call Info",
        style="Muted.TLabel",
    )
    info_title.pack(anchor="w", pady=(0, 4))

    info_text = tk.Text(
        info_frame,
        width=40,
        height=10,
        wrap="word",
        font=font,
        state="disabled",
        relief="flat",
        borderwidth=0,
        highlightthickness=0,
        background=PANEL_BG_LIGHT,
        foreground=TEXT_LIGHT,
        insertbackground=TEXT_LIGHT,
    )
    info_text.pack(fill="both", expand=True)

    # ---- Control bar (bottom) ----
    control_frame = ttk.Frame(root, padding=(12, 8))
    control_frame.pack(side="bottom", fill="x")

    left_group = ttk.Frame(control_frame)
    center_group = ttk.Frame(control_frame)
    right_group = ttk.Frame(control_frame)

    left_group.pack(side="left")
    center_group.pack(side="left", padx=16)
    right_group.pack(side="right")

    # ---- Mode toggle ----
    toggle_mode_btn = ttk.Button(
        left_group,
        text="Animation",
        command=lambda: toggle_mode(context),
    )
    if context.mode["large_graph"]:
        toggle_mode_btn.state(["disabled"])

    toggle_mode_btn.pack()

    # ---- Playback controls ----
    playback_frame = ttk.Frame(center_group)
    step_frame = ttk.Frame(center_group)

    playback_frame.pack(side="left", padx=(0, 12))
    step_frame.pack(side="left")

    reset_anim_btn = ttk.Button(
        step_frame,
        text="⏮",
        style="Icon.TButton",
        command=lambda: (context.anim.reset(), animate(context)),
    )
    step_anim_btn = ttk.Button(
        step_frame,
        text="⏵",
        style="Icon.TButton",
        command=lambda: (context.anim.step(), animate(context)),
    )
    end_anim_btn = ttk.Button(
        step_frame,
        text="⏭",
        style="Icon.TButton",
        command=lambda: (context.anim.end(), animate(context)),
    )

    reset_anim_btn.pack(side="left", padx=2)
    step_anim_btn.pack(side="left", padx=2)
    end_anim_btn.pack(side="left", padx=2)

    play_anim_btn = ttk.Button(
        playback_frame,
        text="Play",
        style="Accent.TButton",
        command=lambda: context.anim.play(),
    )
    play_anim_btn.pack()

    # ---- Speed slider ----
    anim_speed_var = tk.DoubleVar(value=context.anim.delay_ms)

    def on_anim_speed_change(_):
        context.anim.delay_ms = int(anim_speed_var.get())

    anim_speed_scale = ttk.Scale(
        right_group,
        from_=50,
        to=1000,
        orient="horizontal",
        variable=anim_speed_var,
        command=on_anim_speed_change,
    )
    anim_speed_scale.pack(fill="x", expand=True)

    speed_label = ttk.Label(
        right_group,
        text="Speed (ms)",
        style="Muted.TLabel",
    )
    speed_label.pack(anchor="e")

    # ---- Timeline scrubber ----
    anim_timeline_scrub_var = tk.DoubleVar(value=context.anim.cursor)

    def on_anim_timeline_scrub_change(_):
        new_cursor = int(anim_timeline_scrub_var.get())
        if new_cursor != context.anim.cursor:
            context.anim.cursor = new_cursor
            sync_timeline_ui(
                context.ui,
                {"cursor": context.anim.cursor, "threshold": context.anim.threshold}
            )
            context.anim.play(force_set=True)
            animate(context)

    anim_timeline_scrub_scale = ttk.Scale(
        right_group,
        from_=1,
        to=context.anim.threshold,
        orient="horizontal",
        variable=anim_timeline_scrub_var,
        command=on_anim_timeline_scrub_change,
    )
    anim_timeline_scrub_scale.pack(fill="x", expand=True)

    timeline_scrub_label = ttk.Label(
        right_group,
        text=f"Time step: {context.anim.cursor} / {context.anim.threshold}",
        style="Muted.TLabel",
    )
    timeline_scrub_label.pack(anchor="e")

    # ---- Store UI handles ----
    context.ui.update(
        {
            "toggle_mode_button": toggle_mode_btn,
            "step_frame": step_frame,
            "playback_frame": playback_frame,
            "anim_speed_scale": anim_speed_scale,
            "anim_timeline_scrub_scale": anim_timeline_scrub_scale,
            "anim_timeline_scrub_var": anim_timeline_scrub_var,
            "timeline_scrub_label": timeline_scrub_label,
            "play_button": play_anim_btn,
            "info_text": info_text,
            "hierarchy_treeview": hierarchy,
        }
    )

    # ---- Initial disabled state ----
    set_frame_enabled(step_frame, False)
    set_frame_enabled(playback_frame, False)
    anim_speed_scale.state(["disabled"])
    anim_timeline_scrub_scale.state(["disabled"])

    info_text.pack(padx=5, pady=5)