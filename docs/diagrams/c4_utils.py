"""
C4 Model Drawing Utilities
Official colors from https://c4model.com / Structurizr reference implementation
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from matplotlib.patches import Rectangle

# ─── Official C4 Colors ────────────────────────────────────────────────────────
C4_COLORS = {
    "person":        {"bg": "#08427B", "fg": "#FFFFFF", "border": "#052E56"},
    "system":        {"bg": "#1168BD", "fg": "#FFFFFF", "border": "#0B4884"},
    "system_ext":    {"bg": "#999999", "fg": "#FFFFFF", "border": "#6B6B6B"},
    "container":     {"bg": "#438DD5", "fg": "#FFFFFF", "border": "#2E6295"},
    "container_ext": {"bg": "#B3B3B3", "fg": "#000000", "border": "#828282"},
    "container_db":  {"bg": "#438DD5", "fg": "#FFFFFF", "border": "#2E6295"},
    "component":     {"bg": "#85BBF0", "fg": "#000000", "border": "#5D82A8"},
    "boundary":      {"bg": "#FFFFFF", "fg": "#444444", "border": "#888888"},
}

FONT = "DejaVu Sans"


# ─── Person ───────────────────────────────────────────────────────────────────
def draw_person(ax, cx, cy, label, descr="", kind="person", w=9.0, h=6.0):
    """
    C4 Person: rounded rectangle with a circle head protruding above.
    All text is placed INSIDE the rectangle — no overlaps.
    cy = vertical centre of the ENTIRE element (head + box).
    """
    c = C4_COLORS[kind]
    bg, fg, border = c["bg"], c["fg"], c["border"]

    head_r = w * 0.13           # radius of head circle
    gap    = head_r * 0.4       # gap between head bottom and box top
    box_h  = h - 2 * head_r - gap   # box occupies the lower part

    # Vertical positions
    box_bot = cy - h / 2
    box_top = box_bot + box_h
    head_cy = box_top + gap + head_r   # head centre

    # ── Box ──
    rect = FancyBboxPatch(
        (cx - w / 2, box_bot), w, box_h,
        boxstyle="round,pad=0.07",
        facecolor=bg, edgecolor=border, linewidth=2.0, zorder=3
    )
    ax.add_patch(rect)

    # ── Head ──
    head = plt.Circle((cx, head_cy), head_r, color=bg, zorder=4)
    ax.add_patch(head)
    ring = plt.Circle((cx, head_cy), head_r,
                       fill=False, edgecolor=border, linewidth=2.0, zorder=5)
    ax.add_patch(ring)

    # ── Text inside box ──
    # [Person] italic tag near top of box
    ax.text(cx, box_bot + box_h * 0.82,
            "[Person]",
            ha="center", va="center",
            fontsize=8.5, color=fg, fontfamily=FONT,
            style="italic", zorder=6)

    # Name bold in middle
    ax.text(cx, box_bot + box_h * 0.52,
            label,
            ha="center", va="center",
            fontsize=11, fontweight="bold",
            color=fg, fontfamily=FONT,
            multialignment="center", zorder=6)

    # Description italic at bottom
    if descr:
        ax.text(cx, box_bot + box_h * 0.20,
                descr,
                ha="center", va="center",
                fontsize=8.5, color=fg, fontfamily=FONT,
                style="italic", multialignment="center", zorder=6)


# ─── Rectangle Box ────────────────────────────────────────────────────────────
def draw_box(ax, cx, cy, w, h, label, type_label="", tech="", descr="",
             kind="container"):
    """
    C4 rectangular element with a darker header band.
    Text layout:
      header  → [type_label]  (italic, small)
                label         (bold)
      body    → [tech]        (italic)
                descr         (regular, multi-line)
    All positions are computed from the actual box geometry — no magic fractions.
    """
    c = C4_COLORS[kind]
    bg, fg, border = c["bg"], c["fg"], c["border"]

    box_l = cx - w / 2
    box_b = cy - h / 2
    box_t = cy + h / 2

    header_h = max(h * 0.28, 2.2)   # header band height (min 2.2 units)
    body_top = box_t - header_h      # top of the white-ish body area

    # ── Outer box ──
    rect = FancyBboxPatch(
        (box_l, box_b), w, h,
        boxstyle="round,pad=0.09",
        facecolor=bg, edgecolor=border, linewidth=2.0, zorder=3
    )
    ax.add_patch(rect)

    # ── Header band (darker shade) ──
    # Use a plain Rectangle clipped to the top portion; overlay on rounded rect
    header = FancyBboxPatch(
        (box_l, body_top), w, header_h,
        boxstyle="round,pad=0.09",
        facecolor=border, edgecolor=border, linewidth=0, zorder=4
    )
    ax.add_patch(header)

    # ── Header text ──
    if type_label:
        ax.text(cx, body_top + header_h * 0.75,
                f"[{type_label}]",
                ha="center", va="center",
                fontsize=8, color=fg, fontfamily=FONT,
                style="italic", zorder=6)

    ax.text(cx, body_top + header_h * 0.32,
            label,
            ha="center", va="center",
            fontsize=11, fontweight="bold",
            color=fg, fontfamily=FONT, zorder=6)

    # ── Body text ──
    # Available body height from box_b to body_top
    body_h = body_top - box_b

    # Tech label — placed in upper quarter of body
    if tech:
        ax.text(cx, box_b + body_h * 0.78,
                f"[{tech}]",
                ha="center", va="center",
                fontsize=8.5, color=fg, fontfamily=FONT,
                style="italic", zorder=6)

    # Description — centred in lower part of body
    if descr:
        ax.text(cx, box_b + body_h * 0.38,
                descr,
                ha="center", va="center",
                fontsize=8.5, color=fg, fontfamily=FONT,
                multialignment="center", zorder=6)


# ─── Cylinder (Database / ContainerDb) ───────────────────────────────────────
def draw_cylinder(ax, cx, cy, w, h, label, type_label="ContainerDb",
                  tech="", descr="", kind="container_db"):
    """C4 database cylinder: rectangle body + ellipse caps."""
    c = C4_COLORS[kind]
    bg, fg, border = c["bg"], c["fg"], c["border"]

    eh = h * 0.16          # ellipse cap height
    body_h = h - eh / 2

    # Body
    rect = Rectangle(
        (cx - w / 2, cy - h / 2), w, body_h,
        facecolor=bg, edgecolor=border, linewidth=2.0, zorder=3
    )
    ax.add_patch(rect)

    # Bottom cap
    ax.add_patch(mpatches.Ellipse(
        (cx, cy - h / 2 + eh / 2), w, eh,
        facecolor=bg, edgecolor=border, linewidth=2.0, zorder=4
    ))

    # Top cap (darker = header)
    ax.add_patch(mpatches.Ellipse(
        (cx, cy - h / 2 + body_h), w, eh,
        facecolor=border, edgecolor=border, linewidth=2.0, zorder=4
    ))

    # Type label inside top cap
    if type_label:
        ax.text(cx, cy - h / 2 + body_h,
                f"[{type_label}]",
                ha="center", va="center",
                fontsize=8, color=fg, fontfamily=FONT,
                style="italic", zorder=6)

    # Label
    ax.text(cx, cy + h * 0.10,
            label,
            ha="center", va="center",
            fontsize=11, fontweight="bold",
            color=fg, fontfamily=FONT, zorder=6)

    if tech:
        ax.text(cx, cy - h * 0.10,
                f"[{tech}]",
                ha="center", va="center",
                fontsize=8.5, color=fg, fontfamily=FONT,
                style="italic", zorder=6)

    if descr:
        ax.text(cx, cy - h * 0.35,
                descr,
                ha="center", va="center",
                fontsize=8, color=fg, fontfamily=FONT,
                multialignment="center", zorder=6)


# ─── Dashed Boundary ──────────────────────────────────────────────────────────
def draw_boundary(ax, x, y, w, h, label=""):
    """Dashed system-boundary rectangle."""
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.12",
        fill=False,
        edgecolor=C4_COLORS["boundary"]["border"],
        linewidth=1.8,
        linestyle=(0, (8, 4)),
        zorder=2
    ))
    if label:
        ax.text(x + 0.3, y + h - 0.15, label,
                ha="left", va="top",
                fontsize=9.5, fontweight="bold", style="italic",
                color=C4_COLORS["boundary"]["fg"],
                fontfamily=FONT, zorder=5)


# ─── Straight Arrow ───────────────────────────────────────────────────────────
def draw_arrow(ax, x1, y1, x2, y2, label="", tech="",
               color="#606060", lw=1.8, label_offset=(0, 0)):
    ax.annotate("",
        xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                        mutation_scale=16,
                        connectionstyle="arc3,rad=0.0"),
        zorder=6)
    _arrow_label(ax, x1, y1, x2, y2, label, tech, label_offset)


# ─── Arc Arrow ────────────────────────────────────────────────────────────────
def draw_arc_arrow(ax, x1, y1, x2, y2, label="", tech="",
                   color="#606060", lw=1.8, rad=0.25, label_offset=(0, 0)):
    ax.annotate("",
        xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                        mutation_scale=16,
                        connectionstyle=f"arc3,rad={rad}"),
        zorder=6)
    _arrow_label(ax, x1, y1, x2, y2, label, tech, label_offset)


def _arrow_label(ax, x1, y1, x2, y2, label, tech, label_offset):
    if not label and not tech:
        return
    mx = (x1 + x2) / 2 + label_offset[0]
    my = (y1 + y2) / 2 + label_offset[1]
    text = label + (f"\n[{tech}]" if tech else "")
    ax.text(mx, my, text,
            ha="center", va="center",
            fontsize=8, color="#222222", fontfamily=FONT,
            multialignment="center", zorder=7,
            bbox=dict(facecolor="white", edgecolor="none",
                      alpha=0.88, boxstyle="round,pad=0.2"))
