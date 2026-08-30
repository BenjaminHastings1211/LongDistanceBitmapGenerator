"""
E-paper countdown screen generator.

Built on top of ScreenBuilder — this file only decides *what* the countdown
screen says and how its lines stack, not how text/fonts/rotation work.
"""

import math

from ScreenBuilder import ScreenBuilder


def _days_remaining(duration) -> int:
    """Round a timedelta up to whole days (8 days 1 hour -> 9)."""
    total_seconds = duration.total_seconds()
    return max(0, math.ceil(total_seconds / 86400))


def make_countdown_screen(
    event: dict | None,
    number_font=("abduction2002", 64),
    name_font=("abduction2002", 28),
    tiny_font=("Arial", 14),
    gap=10,
    margin=8,
):
    """
    Build a countdown screen from a `next_event()`-style dict (with
    `duration`, `ongoing`, and `name` keys), or a "nothing planned"
    placeholder if `event` is None.

    `number_font`/`name_font`/`tiny_font` are (font_name, size) tuples —
    `font_name` is looked up as `./fonts/{font_name}.ttf` by ScreenBuilder.

    Layout for an upcoming event, top to bottom:
      1. Big day count (the pop) — e.g. "8"
      2. Small "days till" — smallest text on screen
      3. Event name, smaller than the number but bigger than #2

    Layout for an ongoing event:
      1. Big day count
      2. One small reminder line — "days left with you"

    Returns the final panel-ready image (portrait, rotated) — no extra step
    needed from the caller beyond .save(path).
    """
    builder = ScreenBuilder()
    w, h = builder.canvas_size
    max_width = w - 2 * margin

    if event is None:
        lines = [
            ("No trips planned", number_font),
            ("Plan something!", tiny_font),
        ]
    else:
        days = _days_remaining(event["duration"])
        number_text = str(days)
        if event.get("ongoing"):
            lines = [
                (number_text, number_font),
                ("days left with you", tiny_font),
            ]
        else:
            lines = [
                (number_text, number_font),
                ("days till", tiny_font),
                (event["name"], name_font),
            ]

    # Measure each line up front (shrinking to fit the width if needed) so
    # the whole block can be centered vertically before drawing anything.
    heights = [builder.measure(text, font=font_name, size=size, max_width=max_width)[1]
               for text, (font_name, size) in lines]
    block_h = sum(heights) + gap * (len(lines) - 1)
    # Center the block, then nudge up slightly per your call.
    top_y = (h - block_h) / 2 - h * 0.03

    y = top_y
    for (text, (font_name, size)), line_h in zip(lines, heights):
        builder.text(text, (w / 2, y + line_h / 2), font=font_name, size=size, max_width=max_width)
        y += line_h + gap

    return builder.render()


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
        # ("upcoming", example_upcoming),
        # ("none", None),
    ]:
        make_countdown_screen(event, number_font=("Arasdasial", 72)).save(f"./screens/main/pacific.bmp")

    print("saved example screens")
