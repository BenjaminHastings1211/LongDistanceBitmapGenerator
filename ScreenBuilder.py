"""
Fluent builder for hand-authored "system" screens (boot, error, WiFi setup,
etc.) — as opposed to BitmapGenerator's data-driven countdown screen.

Authored on the same landscape canvas as BitmapGenerator and rotated into the
panel's native portrait orientation the same way, so system screens look
consistent with the countdown screen.

Example:
    ScreenBuilder() \\
        .text("Booting...", (148, 50), font="abduction2002", size=32) \\
        .text("v1.0", (148, 100), font="Arial", size=14) \\
        .line((20, 80, 276, 80)) \\
        .box((10, 10, 286, 118), fill=False, width=2) \\
        .render() \\
        .save("boot.bmp")
"""

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Panel geometry
# ---------------------------------------------------------------------------
FINAL_SIZE = (128, 296)        # panel's native (w, h) — portrait, longways
TEXT_CANVAS_SIZE = (296, 128)  # authoring canvas (w, h) — landscape

WIDTH = 296
HEIGHT = 128

FONTS_DIR = "./fonts"
FALLBACK_FONT_NAME = "default"


def load_font(name, size):
    """Load `{FONTS_DIR}/{name}.ttf` at `size`. Falls back to
    `{FONTS_DIR}/{FALLBACK_FONT_NAME}.ttf` if that name isn't found."""
    try:
        return ImageFont.truetype(f"{FONTS_DIR}/{name}.ttf", size)
    except OSError:
        return ImageFont.truetype(f"{FONTS_DIR}/{FALLBACK_FONT_NAME}.ttf", size)


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


def _color(value, when_true):
    """True/False/None -> a PIL color, or None to skip drawing that part."""
    if value is False or value is None:
        return None
    if value is True:
        return when_true
    return value


def _scale_to_fit(img: Image.Image, size) -> Image.Image:
    """Scale `img` evenly (aspect ratio preserved) so it fits within `size`
    (max_width, max_height) — shrinks or grows, whichever the box calls for.

    Resizing a bilevel ("1" mode) image directly aliases badly since there's
    no interpolation between black/white, so scale in grayscale and
    re-threshold back down afterwards.
    """
    max_w, max_h = size
    scale = min(max_w / img.width, max_h / img.height)
    new_size = (max(1, round(img.width * scale)), max(1, round(img.height * scale)))

    if img.mode == "1":
        return img.convert("L").resize(new_size, Image.LANCZOS).convert("1")
    return img.resize(new_size, Image.LANCZOS)


class ScreenBuilder:
    def __init__(self, canvas_size=TEXT_CANVAS_SIZE, background=1):
        self.canvas_size = canvas_size
        self.image = Image.new("1", canvas_size, color=background)
        self.draw = ImageDraw.Draw(self.image)
        self.inverted = False

    def text(self, content, pos, font=FALLBACK_FONT_NAME, size=24, anchor="mm", fill=0,
             max_width=None, min_size=8, step=2):
        """
        Draw `content` centered on `pos` by default. `font` is a name only
        (no path/extension) looked up as `{FONTS_DIR}/{font}.ttf`. `anchor`
        is a Pillow anchor code ("mm" = center/middle, "la" = left/ascender,
        etc.) if you need something other than dead center.

        Pass `max_width` to shrink the font (down to `min_size`, in `step`
        decrements) until the text fits within that width, for content whose
        length isn't known up front (e.g. a WiFi SSID).
        """
        if max_width is not None:
            font_obj = self._fit_font(content, max_width, font, size, min_size, step)
        else:
            font_obj = load_font(font, size)

        self.draw.text(pos, content, font=font_obj, fill=fill, anchor=anchor)
        return self

    def measure(self, content, font=FALLBACK_FONT_NAME, size=24, max_width=None, min_size=8, step=2):
        """Return the (width, height) `content` would render at, without
        drawing it — useful for stacking/centering multiple lines before
        placing any of them."""
        if max_width is not None:
            font_obj = self._fit_font(content, max_width, font, size, min_size, step)
        else:
            font_obj = load_font(font, size)

        left, top, right, bottom = self.draw.textbbox((0, 0), content, font=font_obj)
        return right - left, bottom - top

    def _fit_font(self, content, max_width, font, start_size, min_size, step):
        size = start_size
        font_obj = load_font(font, size)
        while size > min_size:
            font_obj = load_font(font, size)
            left, top, right, bottom = self.draw.textbbox((0, 0), content, font=font_obj)
            if (right - left) <= max_width:
                break
            size -= step
        return font_obj

    def bmp(self, path, pos, anchor="topleft", size=None):
        """
        Paste a single-channel .bmp (mode "1" bilevel or "L" grayscale) onto
        the canvas. Rejects RGB/RGBA/palette bmps — this panel is 1-bit, and
        silently flattening a color image tends to produce garbage rather
        than what you meant.

        `pos` is placed per `anchor`: "topleft" (default) puts `pos` at the
        image's top-left corner, "center" centers the image on `pos`.

        Pass `size` as (max_width, max_height) to scale the image evenly
        (aspect ratio preserved) until it fits within that box, before
        placing it. Omit it to paste at native resolution.
        """
        img = Image.open(path)
        if img.format != "BMP":
            raise ValueError(f"{path}: expected a .bmp file, got format '{img.format}'")
        if img.mode not in ("1", "L"):
            raise ValueError(
                f"{path}: expected a single-channel bmp (mode '1' or 'L'), got mode '{img.mode}'"
            )

        if size is not None:
            img = _scale_to_fit(img, size)
        if img.mode != "1":
            img = img.convert("1")

        x, y = pos
        if anchor == "center":
            x -= img.width / 2
            y -= img.height / 2
        elif anchor != "topleft":
            raise ValueError(f"bmp(): unknown anchor '{anchor}', expected 'topleft' or 'center'")

        self.image.paste(img, (round(x), round(y)))
        return self

    def box(self, xy, outline=True, fill=False, width=1):
        """xy is (x0, y0, x1, y1) corners. outline/fill accept True (black),
        False/None (skip), or an explicit 0/1 color."""
        self.draw.rectangle(
            xy,
            outline=_color(outline, 0),
            fill=_color(fill, 0),
            width=width,
        )
        return self

    def invert(self, enabled=True):
        """Invert the final screen when rendered."""
        self.inverted = enabled
        return self

    def box_centered(self, center, size, **kwargs):
        """Same as box(), but `center` is the box's center point and `size`
        is (width, height)."""
        cx, cy = center
        w, h = size
        xy = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
        return self.box(xy, **kwargs)

    def line(self, xy, width=1, fill=True):
        """xy is (x0, y0, x1, y1), or a longer point list for a polyline."""
        self.draw.line(xy, fill=_color(fill, 0), width=width)
        return self

    def render(self, final_size=FINAL_SIZE):
        """Rotate into the panel's native portrait orientation.
        Applies inversion if enabled. Returns a PIL Image.
        """
        img = to_panel_orientation(self.image, final_size=final_size)

        if self.inverted:
            img = Image.eval(img, lambda pixel: 1 - pixel)

        return img


if __name__ == "__main__":
    ScreenBuilder() \
        .text("Booting...", (WIDTH // 2, HEIGHT // 2 - 10), font="abduction2002", size=53) \
        .text("Long Distance Tracker", (148, 95), font="Arial", size=18) \
        .line((20, 78, 276, 78)) \
        .render() \
        .save("./screens/system/boot.bmp")

    ScreenBuilder() \
        .text("Error", (WIDTH // 2, (HEIGHT // 2) - 25), font="BlueScreen", size=72) \
        .text("Please reboot", (WIDTH // 2, (HEIGHT // 2) + 25), font="default", size=24) \
        .render() \
        .save("./screens/system/error.bmp")
