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
    number_font=("default", 64),
    name_font=("default", 28),
    tiny_font=("default", 14),
    gap=10,
    margin=8,
    invert=False
):
    builder = ScreenBuilder()
    w, h = builder.canvas_size
    max_width = w - 2 * margin

    if event is None:
        lines = [
            ("No trips planned", number_font),
            ("Plan something!", tiny_font),
        ]
    elif event.get("ongoing"):
        lines = [
            (str(_days_remaining(event["duration"])), number_font),
            ("days left with you", tiny_font),
        ]
    else:
        days = str(_days_remaining(event["duration"]))

        number_w, number_h = builder.measure(
            days, font=number_font[0], size=number_font[1]
        )
        till_w, till_h = builder.measure(
            "days till", font=tiny_font[0], size=tiny_font[1]
        )

        total_w = number_w + gap + till_w
        x = (w - total_w) / 2
        bottom_y = h * 0.67

        builder.text(
            days,
            (x + number_w / 2, bottom_y - number_h / 2),
            font=number_font[0],
            size=number_font[1],
        )
        builder.text(
            "days till",
            (x + number_w + gap + till_w / 2, bottom_y - till_h / 2),
            font=tiny_font[0],
            size=tiny_font[1],
        )

        builder.text(
            event["name"],
            (w / 2, h * 0.82),
            font=name_font[0],
            size=name_font[1],
            max_width=max_width,
        )

        if invert:
            builder = builder.invert()
        return builder.render()

    heights = [
        builder.measure(text, font=font_name, size=size, max_width=max_width)[1]
        for text, (font_name, size) in lines
    ]

    block_h = sum(heights) + gap * (len(lines) - 1)
    top_y = (h - block_h) / 2 - h * 0.03

    y = top_y
    for (text, (font_name, size)), line_h in zip(lines, heights):
        builder.text(
            text,
            (w / 2, y + line_h / 2),
            font=font_name,
            size=size,
            max_width=max_width,
        )
        y += line_h + gap

    if invert:
        builder = builder.invert()

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
