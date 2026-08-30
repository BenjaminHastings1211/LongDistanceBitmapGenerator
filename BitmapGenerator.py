"""
E-paper countdown screen generator.

Display panel: 128 x 296 (portrait, width x height) — e.g. a typical
2.9" e-ink strip. Content is authored "longways" (296 x 128, landscape)
because it's much easier to lay out readable text that way, then
converted into the panel's native portrait orientation.
"""

import math
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Panel geometry
# ---------------------------------------------------------------------------
FINAL_SIZE = (128, 296)        # panel's native (w, h) — portrait, longways
TEXT_CANVAS_SIZE = (296, 128)  # authoring canvas (w, h) — landscape

FONT_BOLD_CANDIDATES = [
    "/System/Library/Fonts/HelveticaNeue.ttc",              # macOS built-in
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",     # macOS built-in
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux fallback
]
FONT_REG_CANDIDATES = [
    "/System/Library/Fonts/HelveticaNeue.ttc",              # macOS built-in
    "/System/Library/Fonts/Supplemental/Arial.ttf",          # macOS built-in
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",       # Linux fallback
]


def load_font(size, bold=True):
    candidates = FONT_BOLD_CANDIDATES if bold else FONT_REG_CANDIDATES
    for path in candidates:
        try:
            if path.endswith(".ttc"):
                # HelveticaNeue.ttc is a collection; index 1 is Bold,
                # index 0 is Regular on macOS's system copy.
                return ImageFont.truetype(path, size, index=1 if bold else 0)
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def to_panel_orientation(img: Image.Image, final_size=FINAL_SIZE) -> Image.Image:
    """
    Convert a landscape-authored image (drawn right-reading, normal
    orientation) into the panel's native portrait orientation.

    Plain `rotate(90, expand=True)` is what makes the text come out
    readable in a normal viewer/preview. Some e-paper controllers write
    their framebuffer mirrored though, so if text shows up backwards on
    your actual hardware, call this with mirror=True to pre-compensate.
    """
    img = img.convert("1") if img.mode != "1" else img

    img = img.transpose(Image.FLIP_LEFT_RIGHT)

    rotated = img.rotate(90, expand=True)

    if rotated.size != final_size:
        rotated = rotated.resize(final_size)

    return rotated


def _text_size(draw, text, font):
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    return right - left, bottom - top, left, top


def _draw_centered(draw, text, font, canvas_w, y, fill=0):
    w, h, left, top = _text_size(draw, text, font)
    x = (canvas_w - w) / 2 - left
    draw.text((x, y - top), text, font=font, fill=fill)
    return h


def _days_remaining(duration) -> int:
    """Round a timedelta up to whole days (8 days 1 hour -> 9)."""
    total_seconds = duration.total_seconds()
    return max(0, math.ceil(total_seconds / 86400))


def _fit_font(draw, text, w, start_size, bold, margin=8, min_size=8, step=2):
    """Shrink font size until `text` fits within `w - 2*margin`."""
    size = start_size
    font = load_font(size, bold=bold)
    while size > min_size:
        font = load_font(size, bold=bold)
        tw, _, _, _ = _text_size(draw, text, font)
        if tw <= w - 2 * margin:
            break
        size -= step
    return font


def make_countdown_screen(
    event: dict | None,
    canvas_size=TEXT_CANVAS_SIZE,
    number_size=64,
    name_size=28,
    tiny_size=14,
    gap=10,
) -> Image.Image:
    """
    Build a countdown screen from a `next_event()`-style dict (with
    `duration`, `ongoing`, and `name` keys), or a "nothing planned"
    placeholder if `event` is None.

    Layout for an upcoming event, top to bottom:
      1. Big bold day count (the pop) — e.g. "8"
      2. Small unbolded "days till" — smallest text on screen
      3. Bold event name, smaller than the number but bigger than #2

    Layout for an ongoing event:
      1. Big bold day count
      2. One small unbolded reminder line — "days left with you"

    Returns the final panel-ready image (portrait, rotated via
    `to_panel_orientation`) — no extra step needed from the caller.
    """
    w, h = canvas_size
    img = Image.new("1", canvas_size, color=1)  # 1 = white background
    draw = ImageDraw.Draw(img)

    if event is None:
        lines = [
            ("No trips planned", number_size, True),
            ("Plan something!", tiny_size, False),
        ]
    else:
        days = _days_remaining(event["duration"])
        number_text = str(days)
        if event.get("ongoing"):
            lines = [
                (number_text, number_size, True),
                ("days left with you", tiny_size, False),
            ]
        else:
            lines = [
                (number_text, number_size, True),
                ("days till", tiny_size, False),
                (event["name"], name_size, True),
            ]

    # Resolve fonts (shrinking any line that doesn't fit the width) and
    # measure each line's height up front so we can center the block.
    rendered = []
    for text, size, bold in lines:
        font = _fit_font(draw, text, w, size, bold)
        _, line_h, _, _ = _text_size(draw, text, font)
        rendered.append((text, font, line_h))

    block_h = sum(line_h for _, _, line_h in rendered) + gap * (len(rendered) - 1)
    # Center the block, then nudge up slightly per your call.
    top_y = (h - block_h) / 2 - h * 0.03

    y = top_y
    for text, font, line_h in rendered:
        _draw_centered(draw, text, font, w, y)
        y += line_h + gap

    return to_panel_orientation(img, final_size=FINAL_SIZE)


if __name__ == "__main__":
    # Example: ongoing visit, 4 days left
    example_ongoing = {
        "name": "Ben visiting",
        "duration": __import__("datetime").timedelta(days=3, hours=5),
        "ongoing": True,
    }
    # Example: upcoming trip, 8 days out
    example_upcoming = {
        "name": "Spring Break",
        "duration": __import__("datetime").timedelta(days=7, hours=10),
        "ongoing": False,
    }

    for name, event in [
        ("ongoing", example_ongoing),
        ("upcoming", example_upcoming),
        ("none", None),
    ]:
        make_countdown_screen(event).save(f"./server_side/countdown_{name}.bmp")

    print("saved example screens")