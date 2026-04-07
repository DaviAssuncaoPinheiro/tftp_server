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
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from c4_utils import (
    draw_person, draw_box, draw_cylinder,
    draw_boundary, draw_arrow, draw_arc_arrow,
    C4_COLORS
)

OUT_PATH = os.path.join(HERE, "c4_level2_container_server.png")

# ─── Canvas: 19.2 × 10.8 in @ 200 DPI = 3840 × 2160 px (4K) ─────────────────
DPI = 200
fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=DPI)
fig.patch.set_facecolor("#F8F9FA")
ax.set_facecolor("#F8F9FA")

# Logical coordinate space: 0–100 × 0–56.25  (preserves 16:9)
W, H = 100.0, 56.25
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.set_aspect("equal")
ax.axis("off")

# ─── Title ────────────────────────────────────────────────────────────────────
ax.text(W / 2, H - 1.4,
        "TFTP Server System",
        ha="center", va="top",
        fontsize=22, fontweight="bold",
        color="#1168BD", fontfamily="DejaVu Sans")

ax.text(W / 2, H - 3.0,
        "C4 Model  ·  Level 2: Container Diagram",
        ha="center", va="top",
        fontsize=12, color="#555555",
        fontfamily="DejaVu Sans", style="italic")

# ─── System boundary ──────────────────────────────────────────────────────────
# Spans from x=18 to x=97, y=3 to y=50
BX, BY, BW, BH = 18.0, 3.0, 79.0, 47.0
draw_boundary(ax, BX, BY, BW, BH, label="TFTP Server System")

# ─── External elements (left side, outside boundary) ─────────────────────────

# Person – System Administrator
ADMIN_CX, ADMIN_CY = 8.5, 40.5
draw_person(ax, ADMIN_CX, ADMIN_CY,
            label="System\nAdministrator",
            descr="Deploys and\nmanages the server",
            kind="person",
            w=10.0, h=7.0)

# External System – TFTP Client
CLIENT_CX, CLIENT_CY = 8.5, 20.0
draw_box(ax, CLIENT_CX, CLIENT_CY, 10.5, 7.0,
         label="TFTP Client",
         type_label="External System",
         tech="UDP / RFC 1350",
         descr="Any RFC 1350 client\nthat sends RRQ / WRQ",
         kind="system_ext")

# ─── Containers (inside boundary) ────────────────────────────────────────────

# 1 – CLI Interface  (top-left inside boundary)
CLI_CX, CLI_CY = 34.0, 43.5
draw_box(ax, CLI_CX, CLI_CY, 14.0, 9.0,
         label="CLI Interface",
         type_label="Container",
         tech="Python · argparse",
         descr="Parses --host, --port,\n--directory flags.\nBootstraps the server.",
         kind="container")

# 2 – TFTP Server Core  (centre — primary element, larger)
CORE_CX, CORE_CY = 54.5, 27.5
draw_box(ax, CORE_CX, CORE_CY, 19.0, 14.0,
         label="TFTP Server Core",
         type_label="Container",
         tech="Python · threading · socket",
         descr="TFTPServer UDP main loop\n_route() · session dispatch\n_RRQSession · _WRQSession\nMAX_RETRIES=5 · TIMEOUT=5s",
         kind="container")

# 3 – Protocol Engine  (top-right)
PROTO_CX, PROTO_CY = 77.0, 43.5
draw_box(ax, PROTO_CX, PROTO_CY, 14.0, 9.0,
         label="Protocol Engine",
         type_label="Container",
         tech="Python · struct",
         descr="parse_packet()\nbuild_data / ack / error()\nRFC 1350 binary encoding",
         kind="container")

# 4 – File Service  (bottom-right)
FSVC_CX, FSVC_CY = 77.0, 18.5
draw_box(ax, FSVC_CX, FSVC_CY, 14.0, 9.0,
         label="File Service",
         type_label="Container",
         tech="Python · pathlib · os",
         descr="FileReader · FileWriter\n_safe_path() prevents\npath traversal attacks",
         kind="container")

# 5 – File Storage  (far right, database cylinder)
DB_CX, DB_CY = 93.5, 18.5
draw_cylinder(ax, DB_CX, DB_CY, 10.5, 9.0,
              label="File Storage",
              type_label="ContainerDb",
              tech="File System",
              descr="files/ directory\nServed & received\nfiles at rest",
              kind="container_db")

# ─── Arrows ───────────────────────────────────────────────────────────────────

# Admin → CLI Interface
draw_arrow(ax,
           ADMIN_CX + 5.1, ADMIN_CY + 1.0,
           CLI_CX - 7.1,  CLI_CY + 1.5,
           label="Runs with\narguments",
           tech="CLI",
           label_offset=(0, 0.9))

# CLI Interface → TFTP Server Core
draw_arrow(ax,
           CLI_CX + 3.5,  CLI_CY - 3.5,
           CORE_CX - 7.5, CORE_CY + 4.5,
           label="Creates &\nstarts",
           tech="Python call",
           label_offset=(-0.5, 0.9))

# TFTP Client → TFTP Server Core  (requests)
draw_arrow(ax,
           CLIENT_CX + 5.3, CLIENT_CY + 1.5,
           CORE_CX - 9.6,   CORE_CY - 1.0,
           label="RRQ / WRQ / DATA / ACK",
           tech="UDP port 69",
           label_offset=(0, 1.1))

# TFTP Server Core → TFTP Client  (responses — arc below to avoid overlap)
draw_arc_arrow(ax,
               CORE_CX - 9.6, CORE_CY - 2.5,
               CLIENT_CX + 5.3, CLIENT_CY - 1.0,
               label="DATA / ACK / ERROR",
               tech="UDP",
               rad=-0.22,
               label_offset=(0, -1.3))

# TFTP Server Core → Protocol Engine
draw_arrow(ax,
           CORE_CX + 6.0,  CORE_CY + 4.0,
           PROTO_CX - 7.1, PROTO_CY - 2.5,
           label="parse_packet()\nbuild_*()",
           tech="Function call",
           label_offset=(0.8, 0.9))

# TFTP Server Core → File Service
draw_arrow(ax,
           CORE_CX + 6.0,  CORE_CY - 4.5,
           FSVC_CX - 7.1,  FSVC_CY + 2.0,
           label="FileReader /\nFileWriter",
           tech="Function call",
           label_offset=(0.8, -0.9))

# File Service → File Storage
draw_arrow(ax,
           FSVC_CX + 7.1, FSVC_CY,
           DB_CX - 5.3,   DB_CY,
           label="Reads /\nwrites",
           tech="OS I/O",
           label_offset=(0, 0.9))

# ─── Legend ───────────────────────────────────────────────────────────────────
LX, LY = 1.0, 1.2
legend_items = [
    ("Person",          C4_COLORS["person"]["bg"]),
    ("External System", C4_COLORS["system_ext"]["bg"]),
    ("Container",       C4_COLORS["container"]["bg"]),
    ("ContainerDb",     C4_COLORS["container_db"]["bg"]),
]

ax.text(LX, LY + 5.2, "Legend",
        fontsize=10, fontweight="bold", color="#333333",
        fontfamily="DejaVu Sans")

for i, (name, color) in enumerate(legend_items):
    by = LY + 4.2 - i * 1.15
    ax.add_patch(mpatches.FancyBboxPatch(
        (LX, by), 1.8, 0.72,
        boxstyle="round,pad=0.05",
        facecolor=color, edgecolor="#444444", linewidth=1.0, zorder=5
    ))
    ax.text(LX + 2.1, by + 0.36, name,
            va="center", fontsize=9, color="#333333",
            fontfamily="DejaVu Sans")

# ─── Footer ───────────────────────────────────────────────────────────────────
ax.text(W - 0.8, 0.7,
        "https://c4model.com  ·  TFTP Server Project  ·  Level 2 Container Diagram",
        ha="right", va="bottom",
        fontsize=8, color="#AAAAAA",
        fontfamily="DejaVu Sans", style="italic")

# ─── Save ─────────────────────────────────────────────────────────────────────
fig.savefig(OUT_PATH, dpi=DPI, facecolor=fig.get_facecolor(),
            bbox_inches=None, format="png")
plt.close(fig)

from PIL import Image
img = Image.open(OUT_PATH)
assert img.size == (3840, 2160), f"Unexpected size: {img.size}"
print(f"✓ {OUT_PATH}  ({img.size[0]}×{img.size[1]} px, 4K)")
