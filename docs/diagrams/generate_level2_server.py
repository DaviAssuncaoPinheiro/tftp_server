"""
C4 Model – Level 2: Container Diagram – TFTP Server
Outputs: docs/diagrams/c4_level2_container_server.png  (3840 × 2160 px, 4K)

Run:
    pip install matplotlib pillow
    python3 docs/diagrams/generate_level2_server.py
"""

import os
import sys
import matplotlib
matplotlib.use("Agg")          # headless / no display required
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ── resolve import path so c4_utils can be found from any cwd ─────────────────
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from c4_utils import (
    draw_person, draw_box, draw_cylinder,
    draw_boundary, draw_arrow, draw_arc_arrow,
    C4_COLORS
)

OUT_PATH = os.path.join(HERE, "c4_level2_container_server.png")

# ─────────────────────────────────────────────────────────────────────────────
#  Canvas  19.2 × 10.8 in  @  200 DPI  →  3 840 × 2 160 px  (4K / UHD)
# ─────────────────────────────────────────────────────────────────────────────
DPI = 200
W_IN, H_IN = 19.2, 10.8

fig, ax = plt.subplots(figsize=(W_IN, H_IN), dpi=DPI)
fig.patch.set_facecolor("#FAFAFA")
ax.set_facecolor("#FAFAFA")

# coordinate space  0..100  ×  0..56.25  (keeps 16:9 ratio, easy to reason about)
AX_W, AX_H = 100, 56.25
ax.set_xlim(0, AX_W)
ax.set_ylim(0, AX_H)
ax.set_aspect("equal")
ax.axis("off")

# ─────────────────────────────────────────────────────────────────────────────
#  Title
# ─────────────────────────────────────────────────────────────────────────────
ax.text(AX_W / 2, AX_H - 1.5,
        "TFTP Server System",
        ha="center", va="center", fontsize=20, fontweight="bold",
        color="#1168BD", family="DejaVu Sans")

ax.text(AX_W / 2, AX_H - 3.2,
        "C4 Model  ·  Level 2: Container Diagram",
        ha="center", va="center", fontsize=12,
        color="#555555", family="DejaVu Sans", style="italic")

# ─────────────────────────────────────────────────────────────────────────────
#  Outer boundary  (TFTP Server System)
# ─────────────────────────────────────────────────────────────────────────────
BOUND_X, BOUND_Y = 22, 5
BOUND_W, BOUND_H = 57, 42

draw_boundary(ax, BOUND_X, BOUND_Y, BOUND_W, BOUND_H,
              label="TFTP Server System")

# ─────────────────────────────────────────────────────────────────────────────
#  External elements  (outside boundary)
# ─────────────────────────────────────────────────────────────────────────────
# Person – System Administrator
ADMIN_CX, ADMIN_CY = 9, 40
draw_person(ax, ADMIN_CX, ADMIN_CY,
            label="System\nAdministrator",
            descr="Deploys and\nmanages the server",
            kind="person",
            w=7.5, h=6.0)

# External System – TFTP Client
CLIENT_CX, CLIENT_CY = 9, 18
draw_box(ax, CLIENT_CX, CLIENT_CY, 8.5, 5.5,
         label="TFTP Client",
         type_label="External System",
         tech="UDP / RFC 1350",
         descr="Any TFTP client\nthat sends RRQ/WRQ",
         kind="system_ext")

# ─────────────────────────────────────────────────────────────────────────────
#  Containers  (inside boundary)
# ─────────────────────────────────────────────────────────────────────────────

# 1 – CLI Interface
CLI_CX, CLI_CY = 35, 40
draw_box(ax, CLI_CX, CLI_CY, 11, 7,
         label="CLI Interface",
         type_label="Container",
         tech="Python · argparse",
         descr="Parses --host, --port,\n--directory flags.\nBootstraps the server.",
         kind="container")

# 2 – TFTP Server Core
CORE_CX, CORE_CY = 50, 27
draw_box(ax, CORE_CX, CORE_CY, 13, 8,
         label="TFTP Server Core",
         type_label="Container",
         tech="Python · threading · UDP",
         descr="TFTPServer main loop,\n_route(), session mgmt.\n_RRQSession / _WRQSession.",
         kind="container")

# 3 – Protocol Engine
PROTO_CX, PROTO_CY = 70, 40
draw_box(ax, PROTO_CX, PROTO_CY, 11, 7,
         label="Protocol Engine",
         type_label="Container",
         tech="Python · struct",
         descr="parse_packet(),\nbuild_data/ack/error().\nRFC 1350 encoding.",
         kind="container")

# 4 – File Service
FILE_SVC_CX, FILE_SVC_CY = 70, 18
draw_box(ax, FILE_SVC_CX, FILE_SVC_CY, 11, 7,
         label="File Service",
         type_label="Container",
         tech="Python · pathlib · os",
         descr="FileReader, FileWriter.\n_safe_path() – path\ntraversal protection.",
         kind="container")

# 5 – File Storage (database)
DB_CX, DB_CY = 87, 18
draw_cylinder(ax, DB_CX, DB_CY, 8, 6,
              label="File Storage",
              type_label="ContainerDb",
              tech="File System",
              descr="files/ directory.\nServed/received\nfiles at rest.",
              kind="container_db")

# ─────────────────────────────────────────────────────────────────────────────
#  Arrows
# ─────────────────────────────────────────────────────────────────────────────

# Admin → CLI Interface
draw_arrow(ax,
           ADMIN_CX + 3.8, ADMIN_CY + 0.5,
           CLI_CX - 5.5, CLI_CY + 1.0,
           label="Runs with\narguments",
           tech="CLI",
           label_offset=(0, 0.6))

# CLI Interface → TFTP Server Core
draw_arrow(ax,
           CLI_CX + 3.0, CLI_CY - 2.5,
           CORE_CX - 4.5, CORE_CY + 2.5,
           label="Creates &\nstarts",
           tech="Python call",
           label_offset=(-0.5, 0.6))

# TFTP Client → TFTP Server Core
draw_arrow(ax,
           CLIENT_CX + 4.3, CLIENT_CY + 1.2,
           CORE_CX - 6.5, CORE_CY - 0.5,
           label="RRQ / WRQ\nDATA / ACK",
           tech="UDP port 69",
           label_offset=(0, 0.7))

# TFTP Server Core → TFTP Client  (response – arc to avoid overlap)
draw_arc_arrow(ax,
               CORE_CX - 6.5, CORE_CY - 1.5,
               CLIENT_CX + 4.3, CLIENT_CY - 0.5,
               label="DATA / ACK\n/ ERROR",
               tech="UDP",
               rad=-0.25,
               label_offset=(0, -1.0))

# TFTP Server Core → Protocol Engine
draw_arrow(ax,
           CORE_CX + 5.0, CORE_CY + 2.5,
           PROTO_CX - 5.5, PROTO_CY - 1.5,
           label="parse_packet()\nbuild_*()",
           tech="Function call",
           label_offset=(0.5, 0.8))

# TFTP Server Core → File Service
draw_arrow(ax,
           CORE_CX + 4.5, CORE_CY - 2.5,
           FILE_SVC_CX - 5.5, FILE_SVC_CY + 1.5,
           label="FileReader /\nFileWriter",
           tech="Function call",
           label_offset=(0.5, -0.8))

# File Service → File Storage
draw_arrow(ax,
           FILE_SVC_CX + 5.5, FILE_SVC_CY,
           DB_CX - 4.0, DB_CY,
           label="Reads /\nwrites files",
           tech="OS I/O",
           label_offset=(0, 0.8))

# ─────────────────────────────────────────────────────────────────────────────
#  Legend (bottom-left corner)
# ─────────────────────────────────────────────────────────────────────────────
leg_x, leg_y = 1.0, 1.0
legend_items = [
    ("Person",           C4_COLORS["person"]["bg"]),
    ("External System",  C4_COLORS["system_ext"]["bg"]),
    ("Container",        C4_COLORS["container"]["bg"]),
    ("ContainerDb",      C4_COLORS["container_db"]["bg"]),
]
ax.text(leg_x, leg_y + 3.8, "Legend",
        fontsize=9, fontweight="bold", color="#333333",
        family="DejaVu Sans")

for i, (name, color) in enumerate(legend_items):
    bx = leg_x
    by = leg_y + 3.0 - i * 1.0
    rect = mpatches.FancyBboxPatch(
        (bx, by), 1.6, 0.65,
        boxstyle="round,pad=0.05",
        facecolor=color, edgecolor="#333333", linewidth=1.0, zorder=5
    )
    ax.add_patch(rect)
    ax.text(bx + 1.9, by + 0.32, name,
            va="center", fontsize=8, color="#333333", family="DejaVu Sans")

# ─────────────────────────────────────────────────────────────────────────────
#  Footer
# ─────────────────────────────────────────────────────────────────────────────
ax.text(AX_W - 1.0, 0.8,
        "https://c4model.com  ·  TFTP Server Project  ·  Level 2 Container",
        ha="right", va="bottom", fontsize=7.5,
        color="#AAAAAA", family="DejaVu Sans", style="italic")

# ─────────────────────────────────────────────────────────────────────────────
#  Save
# ─────────────────────────────────────────────────────────────────────────────
fig.savefig(OUT_PATH, dpi=DPI, facecolor=fig.get_facecolor(),
            bbox_inches=None, format="png")
plt.close(fig)

# Verify
from PIL import Image
img = Image.open(OUT_PATH)
assert img.size == (3840, 2160), f"Unexpected size: {img.size}"
print(f"✓ Saved {OUT_PATH}  ({img.size[0]}×{img.size[1]} px, 4K)")
