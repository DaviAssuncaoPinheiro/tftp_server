"""
C4 Level 2 – Container Diagram (Server) — Google Slides–ready PowerPoint
Produces: c4_server_level2_presentation.pptx  (project root)

Slide structure (9 slides):
  1  –  Diagram (4K PNG full-bleed)
  2  –  Explanation: System Administrator
  3  –  Explanation: TFTP Client
  4  –  Explanation: CLI Interface
  5  –  Explanation: TFTP Server Core
  6  –  Explanation: Protocol Engine
  7  –  Explanation: File Service
  8  –  Explanation: File Storage (DB)
  9  –  Explanation: Relationships / Arrows

Run:
    pip install python-pptx
    python3 docs/diagrams/generate_presentation.py
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

HERE    = os.path.dirname(os.path.abspath(__file__))
ROOT    = os.path.join(HERE, "..", "..")
PNG     = os.path.join(HERE, "c4_level2_container_server.png")
OUT     = os.path.join(ROOT, "c4_server_level2_presentation.pptx")

# ─── Helpers ──────────────────────────────────────────────────────────────────
def hex2rgb(h):
    h = h.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

C4 = {
    "person":       {"bg": "#08427B", "fg": "#FFFFFF"},
    "system_ext":   {"bg": "#999999", "fg": "#FFFFFF"},
    "container":    {"bg": "#438DD5", "fg": "#FFFFFF"},
    "container_db": {"bg": "#438DD5", "fg": "#FFFFFF"},
    "arrow":        {"bg": "#F0F0F0", "fg": "#333333"},
}

# 16:9 widescreen dimensions
SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)


def new_prs():
    prs = Presentation()
    prs.slide_width  = SLIDE_W
    prs.slide_height = SLIDE_H
    return prs


def blank_slide(prs):
    layout = prs.slide_layouts[6]   # completely blank
    return prs.slides.add_slide(layout)


def set_bg(slide, hex_color="#FFFFFF"):
    from pptx.oxml.ns import qn
    from lxml import etree
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = hex2rgb(hex_color)


def add_text_box(slide, text, left, top, width, height,
                 font_size=14, bold=False, italic=False,
                 color="#000000", align=PP_ALIGN.LEFT,
                 bg_color=None, wrap=True):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf    = txBox.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size   = Pt(font_size)
    run.font.bold   = bold
    run.font.italic = italic
    run.font.color.rgb = hex2rgb(color)
    if bg_color:
        from pptx.oxml.ns import qn
        from lxml import etree
        spPr = txBox._element.spPr
        solidFill = etree.SubElement(spPr, qn("a:solidFill"))
        srgbClr   = etree.SubElement(solidFill, qn("a:srgbClr"))
        srgbClr.set("val", bg_color.lstrip("#"))
    return txBox


def add_colored_rect(slide, left, top, width, height, bg_hex, border_hex=None):
    shape = slide.shapes.add_shape(
        1,  # MSO_SHAPE_TYPE.RECTANGLE
        left, top, width, height
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = hex2rgb(bg_hex)
    if border_hex:
        shape.line.color.rgb = hex2rgb(border_hex)
        shape.line.width = Pt(1.5)
    else:
        shape.line.fill.background()
    return shape


# ─── Slide 1 — Diagram PNG full-bleed ────────────────────────────────────────
def slide_diagram(prs, png_path):
    slide = blank_slide(prs)
    set_bg(slide, "#1A1A2E")
    slide.shapes.add_picture(png_path, 0, 0, SLIDE_W, SLIDE_H)
    return slide


# ─── Explanation slide factory ───────────────────────────────────────────────
def slide_explanation(prs, element_name, c4_type, c4_kind,
                      description, technology, code_ref,
                      extra_bullets=None):
    """
    One slide per C4 element with:
     - colored header strip (C4 element colour)
     - element name + type badge
     - description, technology, code reference
     - optional extra bullet points
    """
    slide = blank_slide(prs)
    set_bg(slide, "#FAFAFA")

    COLORS = C4[c4_kind]
    header_h = Inches(1.55)

    # ── Header strip ──────────────────────────────────────────────────────────
    add_colored_rect(slide, 0, 0, SLIDE_W, header_h, COLORS["bg"])

    # Type badge (small rounded rect inside header)
    badge_w, badge_h = Inches(2.2), Inches(0.35)
    badge = slide.shapes.add_shape(
        1, Inches(0.35), Inches(0.22), badge_w, badge_h
    )
    badge.fill.solid()
    badge.fill.fore_color.rgb = hex2rgb("#FFFFFF")
    badge.fill.fore_color.theme_color  # ignore – just set directly
    badge.line.fill.background()
    tf = badge.text_frame
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    run = tf.paragraphs[0].add_run()
    run.text = c4_type
    run.font.size  = Pt(10)
    run.font.italic = True
    run.font.color.rgb = hex2rgb(COLORS["bg"])

    # Element name
    add_text_box(slide, element_name,
                 Inches(0.35), Inches(0.62),
                 SLIDE_W - Inches(0.7), Inches(0.85),
                 font_size=26, bold=True,
                 color=COLORS["fg"],
                 align=PP_ALIGN.LEFT)

    # ── Body ──────────────────────────────────────────────────────────────────
    body_top = header_h + Inches(0.25)
    col_l    = Inches(0.5)
    col_r    = Inches(7.0)
    row_h    = Inches(0.95)
    lbl_w    = Inches(2.2)
    val_w    = Inches(5.8)
    lbl_font = 11
    val_font = 12

    rows = [
        ("Description", description),
        ("Technology",  technology),
        ("Code File",   code_ref),
    ]
    if extra_bullets:
        rows.append(("Key Details", "\n".join(f"• {b}" for b in extra_bullets)))

    for i, (lbl, val) in enumerate(rows):
        top_i = body_top + Inches(0.05) + i * row_h

        # Separator line
        if i > 0:
            line = slide.shapes.add_shape(1,
                col_l, top_i - Inches(0.08),
                SLIDE_W - col_l - Inches(0.5), Pt(1)
            )
            line.fill.solid()
            line.fill.fore_color.rgb = hex2rgb("#DDDDDD")
            line.line.fill.background()

        add_text_box(slide, lbl,
                     col_l, top_i, lbl_w, row_h,
                     font_size=lbl_font, bold=True,
                     color="#555555")

        add_text_box(slide, val,
                     col_l + lbl_w, top_i, val_w, row_h,
                     font_size=val_font,
                     color="#111111")

    # C4 colour swatch bottom-right
    sw_size = Inches(0.6)
    swatch = add_colored_rect(slide,
        SLIDE_W - sw_size - Inches(0.3),
        SLIDE_H - sw_size - Inches(0.3),
        sw_size, sw_size,
        COLORS["bg"]
    )

    # Footer
    add_text_box(slide,
                 "C4 Model · Level 2 Container Diagram · TFTP Server  |  c4model.com",
                 Inches(0.5), SLIDE_H - Inches(0.4),
                 SLIDE_W - Inches(1.0), Inches(0.35),
                 font_size=8, italic=True,
                 color="#AAAAAA", align=PP_ALIGN.CENTER)

    return slide


# ─── Relationships slide ─────────────────────────────────────────────────────
def slide_relationships(prs):
    slide = blank_slide(prs)
    set_bg(slide, "#FAFAFA")

    # Header strip
    add_colored_rect(slide, 0, 0, SLIDE_W, Inches(1.4), "#2E2E2E")
    add_text_box(slide, "Relationships  ·  Arrows",
                 Inches(0.35), Inches(0.40),
                 SLIDE_W - Inches(0.7), Inches(0.7),
                 font_size=26, bold=True, color="#FFFFFF")
    add_text_box(slide, "[Container → Container  |  C4 Level 2]",
                 Inches(0.35), Inches(0.10),
                 SLIDE_W - Inches(0.7), Inches(0.40),
                 font_size=10, italic=True, color="#CCCCCC")

    rels = [
        ("System Administrator",  "CLI Interface",        "Runs with arguments",      "CLI / shell"),
        ("CLI Interface",         "TFTP Server Core",     "Creates & starts server",  "Python function call"),
        ("TFTP Client",           "TFTP Server Core",     "RRQ / WRQ / DATA / ACK",   "UDP port 69 (RFC 1350)"),
        ("TFTP Server Core",      "TFTP Client",          "DATA / ACK / ERROR",       "UDP"),
        ("TFTP Server Core",      "Protocol Engine",      "parse_packet() / build_*()", "Python function call"),
        ("TFTP Server Core",      "File Service",         "FileReader / FileWriter",  "Python function call"),
        ("File Service",          "File Storage",         "Reads / writes files",     "OS I/O (pathlib)"),
    ]

    col_w = [Inches(2.8), Inches(2.8), Inches(4.2), Inches(2.8)]
    headers = ["From", "To", "Label", "Technology"]
    header_bg = "#438DD5"
    row_bgs   = ["#EFF6FF", "#FAFAFA"]

    top = Inches(1.6)
    row_h = Inches(0.58)
    left = Inches(0.4)

    # Header row
    x = left
    for j, (hdr, cw) in enumerate(zip(headers, col_w)):
        cell = add_colored_rect(slide, x, top, cw - Inches(0.05), row_h,
                                header_bg)
        add_text_box(slide, hdr,
                     x + Inches(0.08), top + Inches(0.10),
                     cw - Inches(0.15), row_h - Inches(0.08),
                     font_size=10, bold=True, color="#FFFFFF")
        x += cw

    for i, (frm, to, lbl, tech) in enumerate(rels):
        y = top + (i + 1) * row_h
        x = left
        for j, (val, cw) in enumerate(zip([frm, to, lbl, tech], col_w)):
            bg = row_bgs[i % 2] if j < len(col_w) - 1 else row_bgs[i % 2]
            add_colored_rect(slide, x, y, cw - Inches(0.05), row_h, bg,
                             border_hex="#CCCCCC")
            add_text_box(slide, val,
                         x + Inches(0.08), y + Inches(0.08),
                         cw - Inches(0.18), row_h - Inches(0.10),
                         font_size=9, color="#111111")
            x += cw

    add_text_box(slide,
                 "C4 Model · Level 2 Container Diagram · TFTP Server  |  c4model.com",
                 Inches(0.5), SLIDE_H - Inches(0.4),
                 SLIDE_W - Inches(1.0), Inches(0.35),
                 font_size=8, italic=True,
                 color="#AAAAAA", align=PP_ALIGN.CENTER)
    return slide


# ─── Build presentation ───────────────────────────────────────────────────────
prs = new_prs()

# Slide 1 – Diagram
slide_diagram(prs, PNG)

# Slide 2 – Person: System Administrator
slide_explanation(prs,
    element_name  = "System Administrator",
    c4_type       = "[Person]",
    c4_kind       = "person",
    description   = (
        "The human actor who deploys, configures, and operates the TFTP Server. "
        "Interacts exclusively through the CLI Interface."
    ),
    technology    = "Terminal / SSH",
    code_ref      = "server.py  (entry point, main())",
    extra_bullets = [
        "Provides --host, --port, --directory flags at startup",
        "Monitors server log output on stdout",
        "Stops the server via KeyboardInterrupt (Ctrl+C)",
    ]
)

# Slide 3 – External System: TFTP Client
slide_explanation(prs,
    element_name  = "TFTP Client",
    c4_type       = "[External System]",
    c4_kind       = "system_ext",
    description   = (
        "Any external application that implements the TFTP protocol (RFC 1350). "
        "Initiates file transfers by sending RRQ (read) or WRQ (write) datagrams "
        "to the server's UDP port."
    ),
    technology    = "UDP / RFC 1350",
    code_ref      = "External – not part of this codebase",
    extra_bullets = [
        "Examples: tftp(1) CLI, curl --tftp-*, network boot loaders (PXE)",
        "Connects to UDP port 69 by default (configurable)",
        "Session TID (Transfer ID) is a random ephemeral port per transfer",
    ]
)

# Slide 4 – Container: CLI Interface
slide_explanation(prs,
    element_name  = "CLI Interface",
    c4_type       = "[Container · Python / argparse]",
    c4_kind       = "container",
    description   = (
        "Parses command-line arguments, validates the root directory, "
        "initialises the Python logger and instantiates TFTPServer. "
        "Acts as the application entry point and lifecycle manager."
    ),
    technology    = "Python 3 · argparse · logging",
    code_ref      = "server.py  ·  src/cli.py",
    extra_bullets = [
        "parse_args() → Namespace(host, port, directory)",
        "validate_directory() raises ArgumentTypeError on invalid path",
        "main() wires logging, args and TFTPServer.start()",
        "Catches KeyboardInterrupt for graceful shutdown",
    ]
)

# Slide 5 – Container: TFTP Server Core
slide_explanation(prs,
    element_name  = "TFTP Server Core",
    c4_type       = "[Container · Python / threading]",
    c4_kind       = "container",
    description   = (
        "The central container of the system. Runs a UDP socket loop, "
        "routes incoming datagrams to existing sessions or spawns new ones, "
        "and manages concurrent transfers via a thread-per-session model."
    ),
    technology    = "Python 3 · socket · threading · queue",
    code_ref      = "src/tftp_server.py",
    extra_bullets = [
        "TFTPServer.start() — binds UDP socket, receives datagrams in a loop",
        "_route(data, addr) — dispatches packets: new session or queued message",
        "_RRQSession.run() — handles file downloads (send DATA, wait ACK)",
        "_WRQSession.run() — handles file uploads (receive DATA, send ACK)",
        "MAX_RETRIES=5, SESSION_TIMEOUT=5 s per block",
        "Thread-safe session registry: dict[addr → Queue] + threading.Lock",
    ]
)

# Slide 6 – Container: Protocol Engine
slide_explanation(prs,
    element_name  = "Protocol Engine",
    c4_type       = "[Container · Python / struct]",
    c4_kind       = "container",
    description   = (
        "Encodes and decodes all TFTP binary packets according to RFC 1350. "
        "Stateless pure-function module; contains all opcode constants and "
        "error code definitions."
    ),
    technology    = "Python 3 · struct (binary packing)",
    code_ref      = "src/protocol.py",
    extra_bullets = [
        "Opcodes: OP_RRQ=1, OP_WRQ=2, OP_DATA=3, OP_ACK=4, OP_ERROR=5",
        "parse_packet(data) → dict dispatches to _parse_request/data/ack/error",
        "build_rrq/wrq/data/ack/error() return bytes ready to sendto()",
        "BLOCK_SIZE = 512 bytes; is_last_block() checks len < 512",
        "Supported modes: netascii · octet · mail",
        "Custom TFTPError exception carries RFC error codes",
    ]
)

# Slide 7 – Container: File Service
slide_explanation(prs,
    element_name  = "File Service",
    c4_type       = "[Container · Python / pathlib]",
    c4_kind       = "container",
    description   = (
        "Provides safe, validated file I/O for the server. "
        "FileReader streams a file in 512-byte blocks for RRQ transfers. "
        "FileWriter atomically persists received blocks for WRQ transfers. "
        "_safe_path() prevents path-traversal attacks."
    ),
    technology    = "Python 3 · pathlib · os",
    code_ref      = "src/file_service.py",
    extra_bullets = [
        "FileReader.next_block() → (block_num, bytes≤512); supports context mgr",
        "FileWriter.write_block(payload); abort() deletes partial file on error",
        "_safe_path() resolves symlinks and rejects paths outside root_dir",
        "Raises TFTPError(ERR_ACCESS_VIOLATION) on traversal attempt",
        "Raises TFTPError(ERR_FILE_NOT_FOUND / ERR_FILE_EXISTS) as appropriate",
        "Raises TFTPError(ERR_DISK_FULL) when OSError occurs during write",
    ]
)

# Slide 8 – ContainerDb: File Storage
slide_explanation(prs,
    element_name  = "File Storage",
    c4_type       = "[ContainerDb · File System]",
    c4_kind       = "container_db",
    description   = (
        "The persistent data store. A directory on the local file system "
        "designated at startup via --directory. Files within this directory "
        "can be downloaded (RRQ) or uploaded (WRQ) by TFTP clients."
    ),
    technology    = "File System  (ext4 / any POSIX FS)",
    code_ref      = "files/  (default directory; configurable)",
    extra_bullets = [
        "Read by FileReader during RRQ (download) sessions",
        "Written by FileWriter during WRQ (upload) sessions",
        "No file may be overwritten — FileWriter enforces no-clobber policy",
        "Symlinks are resolved before path validation (no escaping root)",
        "Permissions checked at open-time (read/write access)",
    ]
)

# Slide 9 – Relationships
slide_relationships(prs)

# ─── Save ─────────────────────────────────────────────────────────────────────
prs.save(OUT)
print(f"✓ Saved {OUT}")
print(f"  Slides: {len(prs.slides)}")
print()
print("  Import into Google Slides:")
print("  File → Import slides → Upload → select .pptx")
