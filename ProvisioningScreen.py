"""
Builds the screen shown on the panel while the device is in WiFi
provisioning mode: a QR code (joins the device's own setup AP) on the left,
instructions on the right.

Two-step pipeline, same split as BitmapGenerator.py building on ScreenBuilder:
  1. QrGenerator renders the raw QR code into ./media (a staging area, not
     served directly).
  2. This file composes that QR bitmap with text via ScreenBuilder and saves
     the result to ./screens/system/qr.bmp, which the device downloads
     during system_reset() and shows via qr_screen().
"""

from QrGenerator import create_wifi_qr
from ScreenBuilder import ScreenBuilder, WIDTH, HEIGHT

# Must match the embedded project's Kconfig defaults (main/Kconfig.projbuild:
# DEVICE_NAME / DEVICE_PASSWORD) -- there's no automatic link between the two,
# so re-run this whenever those change.
DEVICE_NAME = "LongDistanceTracker"
DEVICE_PASSWORD = "password"

MEDIA_QR_PATH = "./media/qr.bmp"
OUTPUT_PATH = "./screens/system/qr.bmp"

MARGIN = 8
GAP = 12

HEADING = "Setup Mode"
BODY = "Scan to connect, then follow the prompts to finish setup."

HEADING_FONT = ("Arial Bold", 22)
BODY_FONT = ("default", 14)
LINE_GAP = 4


def _wrap_text(builder, text, font, size, max_width):
    """Greedy word-wrap: pack as many words per line as fit under max_width."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        width, _ = builder.measure(candidate, font=font, size=size)
        if width <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def make_provisioning_screen(
    ssid=DEVICE_NAME,
    password=DEVICE_PASSWORD,
    heading=HEADING,
    body=BODY,
    heading_font=HEADING_FONT,
    body_font=BODY_FONT,
):
    """Generate the QR code at exactly the size it'll be shown at (avoids a
    second resize pass over the code, which risks blurring/dithering it into
    something a phone camera won't scan), then compose the final screen."""
    qr_size = HEIGHT - 2 * MARGIN
    create_wifi_qr(ssid, password, qr_size, MEDIA_QR_PATH)

    builder = ScreenBuilder()
    builder.bmp(MEDIA_QR_PATH, (MARGIN, MARGIN))

    text_x = MARGIN * 2 + qr_size + GAP
    text_width = WIDTH - text_x - MARGIN

    heading_name, heading_size = heading_font
    body_name, body_size = body_font

    y = MARGIN + 6
    builder.text(heading, (text_x, y), font=heading_name, size=heading_size,
                 anchor="la", max_width=text_width)
    y += builder.measure(heading, font=heading_name, size=heading_size,
                          max_width=text_width)[1] + GAP

    for line in _wrap_text(builder, body, body_name, body_size, text_width):
        builder.text(line, (text_x, y), font=body_name, size=body_size, anchor="la")
        y += builder.measure(line, font=body_name, size=body_size)[1] + LINE_GAP

    return builder.invert().render()


if __name__ == "__main__":
    make_provisioning_screen().save(OUTPUT_PATH)
    print(f"saved provisioning screen to {OUTPUT_PATH}")
