"""
C4 Model Drawing Utilities
Official colors from https://c4model.com / Structurizr reference implementation
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from matplotlib.lines import Line2D
import numpy as np

# ─── Official C4 Colors ────────────────────────────────────────────────────────
C4_COLORS = {
    "person":            {"bg": "#08427B", "fg": "#FFFFFF", "border": "#052E56"},
    "system":            {"bg": "#1168BD", "fg": "#FFFFFF", "border": "#0B4884"},
    "system_ext":        {"bg": "#999999", "fg": "#FFFFFF", "border": "#6B6B6B"},
    "container":         {"bg": "#438DD5", "fg": "#FFFFFF", "border": "#2E6295"},
    "container_ext":     {"bg": "#B3B3B3", "fg": "#000000", "border": "#828282"},
    "container_db":      {"bg": "#438DD5", "fg": "#FFFFFF", "border": "#2E6295"},
    "component":         {"bg": "#85BBF0", "fg": "#000000", "border": "#5D82A8"},
    "component_ext":     {"bg": "#CCCCCC", "fg": "#000000", "border": "#AAAAAA"},
    "boundary":          {"bg": "#FFFFFF", "fg": "#444444", "border": "#888888"},
}

FONT_FAMILY = "DejaVu Sans"


# ─── Person ───────────────────────────────────────────────────────────────────
def draw_person(ax, cx, cy, label, descr="", kind="person", w=1.8, h=2.6):
    """Draw a C4 Person element (head + body + label box)."""
    colors = C4_COLORS[kind]
    bg, fg, border = colors["bg"], colors["fg"], colors["border"]

    # Head
    head_r = 0.28
    head = plt.Circle((cx, cy + h * 0.30), head_r, color=bg, zorder=3)
    ax.add_patch(head)
    head_border = plt.Circle((cx, cy + h * 0.30), head_r,
                              fill=False, edgecolor=border, linewidth=1.5, zorder=4)
    ax.add_patch(head_border)

    # Body (simple stick figure torso via rectangle)
    body_w, body_h = 0.50, 0.45
    body = FancyBboxPatch(
        (cx - body_w / 2, cy + h * 0.30 - head_r - body_h - 0.04),
        body_w, body_h,
        boxstyle="round,pad=0.02",
        facecolor=bg, edgecolor=border, linewidth=1.5, zorder=3
    )
    ax.add_patch(body)

    # Label box
    box_top = cy + h * 0.30 - head_r - body_h - 0.04
    box_h = 0.80
    box = FancyBboxPatch(
        (cx - w / 2, box_top - box_h - 0.15),
        w, box_h,
        boxstyle="round,pad=0.06",
        facecolor=bg, edgecolor=border, linewidth=1.5, zorder=3
    )
    ax.add_patch(box)

    label_y = box_top - box_h / 2 - 0.15
    ax.text(cx, label_y + 0.15, label,
            ha="center", va="center", fontsize=10, fontweight="bold",
            color=fg, fontfamily=FONT_FAMILY, zorder=5, wrap=True)
    if descr:
        ax.text(cx, label_y - 0.18, f"[Person]\n{descr}",
                ha="center", va="center", fontsize=7.5,
                color=fg, fontfamily=FONT_FAMILY, zorder=5,
                style="italic", multialignment="center")


# ─── Rectangle Box (System / Container / Component) ───────────────────────────
def draw_box(ax, cx, cy, w, h, label, type_label="", tech="", descr="",
             kind="container", dashed=False):
    """Draw a C4 rounded rectangle element."""
    colors = C4_COLORS[kind]
    bg, fg, border = colors["bg"], colors["fg"], colors["border"]

    ls = (0, (6, 3)) if dashed else "solid"

    rect = FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle="round,pad=0.08",
        facecolor=bg, edgecolor=border, linewidth=2.0,
        linestyle=ls, zorder=3
    )
    ax.add_patch(rect)

    # Header strip (darker top band with label)
    header_h = h * 0.30
    header = FancyBboxPatch(
        (cx - w / 2, cy + h / 2 - header_h), w, header_h,
        boxstyle="round,pad=0.08",
        facecolor=border, edgecolor=border, linewidth=0, zorder=4
    )
    ax.add_patch(header)

    # Type label (small, italic, inside header)
    if type_label:
        ax.text(cx, cy + h / 2 - header_h * 0.30,
                f"[{type_label}]",
                ha="center", va="center", fontsize=7.5,
                color=fg, fontfamily=FONT_FAMILY, zorder=5, style="italic")

    # Main label (bold, centered in header)
    ax.text(cx, cy + h / 2 - header_h * 0.72,
            label,
            ha="center", va="center", fontsize=10, fontweight="bold",
            color=fg, fontfamily=FONT_FAMILY, zorder=5)

    # Tech label
    if tech:
        ax.text(cx, cy - 0.05,
                f"[{tech}]",
                ha="center", va="center", fontsize=8,
                color=fg, fontfamily=FONT_FAMILY, zorder=5, style="italic")

    # Description
    if descr:
        ax.text(cx, cy - h * 0.25,
                descr,
                ha="center", va="center", fontsize=8,
                color=fg, fontfamily=FONT_FAMILY, zorder=5,
                multialignment="center", wrap=True)


# ─── Cylinder (Database) ──────────────────────────────────────────────────────
def draw_cylinder(ax, cx, cy, w, h, label, type_label="ContainerDb", tech="",
                  descr="", kind="container_db"):
    """Draw a C4 database cylinder shape."""
    colors = C4_COLORS[kind]
    bg, fg, border = colors["bg"], colors["fg"], colors["border"]

    ew = w          # ellipse width = box width
    eh = h * 0.18   # ellipse height (cap)

    # Body rectangle
    rect = mpatches.Rectangle(
        (cx - w / 2, cy - h / 2), w, h,
        facecolor=bg, edgecolor=border, linewidth=2.0, zorder=3
    )
    ax.add_patch(rect)

    # Bottom cap ellipse
    bot_ellipse = mpatches.Ellipse(
        (cx, cy - h / 2), ew, eh,
        facecolor=bg, edgecolor=border, linewidth=2.0, zorder=4
    )
    ax.add_patch(bot_ellipse)

    # Top cap ellipse
    top_ellipse = mpatches.Ellipse(
        (cx, cy + h / 2), ew, eh,
        facecolor=border, edgecolor=border, linewidth=2.0, zorder=4
    )
    ax.add_patch(top_ellipse)

    # Type label
    if type_label:
        ax.text(cx, cy + h / 2 + eh * 0.05,
                f"[{type_label}]",
                ha="center", va="center", fontsize=7.5,
                color=fg, fontfamily=FONT_FAMILY, zorder=5, style="italic")

    ax.text(cx, cy + h * 0.18,
            label,
            ha="center", va="center", fontsize=10, fontweight="bold",
            color=fg, fontfamily=FONT_FAMILY, zorder=5)

    if tech:
        ax.text(cx, cy - 0.05,
                f"[{tech}]",
                ha="center", va="center", fontsize=8,
                color=fg, fontfamily=FONT_FAMILY, zorder=5, style="italic")

    if descr:
        ax.text(cx, cy - h * 0.28,
                descr,
                ha="center", va="center", fontsize=8,
                color=fg, fontfamily=FONT_FAMILY, zorder=5,
                multialignment="center")


# ─── Dashed Boundary ──────────────────────────────────────────────────────────
def draw_boundary(ax, x, y, w, h, label=""):
    """Draw a dashed system boundary rectangle."""
    rect = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.1",
        fill=False,
        edgecolor=C4_COLORS["boundary"]["border"],
        linewidth=1.8,
        linestyle=(0, (8, 4)),
        zorder=2
    )
    ax.add_patch(rect)
    if label:
        ax.text(x + 0.20, y + h - 0.10, label,
                ha="left", va="top", fontsize=9,
                color=C4_COLORS["boundary"]["fg"],
                fontfamily=FONT_FAMILY, zorder=5,
                fontweight="bold", style="italic")


# ─── Arrow ────────────────────────────────────────────────────────────────────
def draw_arrow(ax, x1, y1, x2, y2, label="", tech="",
               color="#707070", lw=1.8, label_offset=(0, 0)):
    """Draw a directed arrow with optional label and technology."""
    ax.annotate(
        "",
        xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(
            arrowstyle="-|>",
            color=color,
            lw=lw,
            mutation_scale=16,
            connectionstyle="arc3,rad=0.0"
        ),
        zorder=6
    )
    if label or tech:
        mx = (x1 + x2) / 2 + label_offset[0]
        my = (y1 + y2) / 2 + label_offset[1]
        full = label
        if tech:
            full += f"\n[{tech}]"
        ax.text(mx, my, full,
                ha="center", va="center", fontsize=7.5,
                color="#333333",
                fontfamily=FONT_FAMILY, zorder=7,
                bbox=dict(facecolor="white", edgecolor="none",
                          alpha=0.85, boxstyle="round,pad=0.15"),
                multialignment="center")


# ─── Curved Arrow (arc) ───────────────────────────────────────────────────────
def draw_arc_arrow(ax, x1, y1, x2, y2, label="", tech="",
                   color="#707070", lw=1.8, rad=0.3, label_offset=(0, 0)):
    ax.annotate(
        "",
        xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(
            arrowstyle="-|>",
            color=color,
            lw=lw,
            mutation_scale=16,
            connectionstyle=f"arc3,rad={rad}"
        ),
        zorder=6
    )
    if label or tech:
        mx = (x1 + x2) / 2 + label_offset[0]
        my = (y1 + y2) / 2 + label_offset[1]
        full = label
        if tech:
            full += f"\n[{tech}]"
        ax.text(mx, my, full,
                ha="center", va="center", fontsize=7.5,
                color="#333333",
                fontfamily=FONT_FAMILY, zorder=7,
                bbox=dict(facecolor="white", edgecolor="none",
                          alpha=0.85, boxstyle="round,pad=0.15"),
                multialignment="center")
