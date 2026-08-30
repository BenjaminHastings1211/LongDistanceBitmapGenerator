import argparse
import os

import qrcode

# Staging area for raw generated assets that get composed into a screen by
# another script (e.g. ProvisioningScreen.py) rather than served directly.
MEDIA_DIR = "./media"
DEFAULT_OUTPUT = f"{MEDIA_DIR}/qr.bmp"


def create_wifi_qr(ssid, password, size, output=DEFAULT_OUTPUT):
    # Standard Wi-Fi QR code format
    data = f"WIFI:T:WPA;S:{ssid};P:{password};;"

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=1,
        border=0,
    )

    qr.add_data(data)
    qr.make(fit=True)

    # Generate the QR code
    img = qr.make_image(fill_color="black", back_color="white")

    # Resize to the exact requested size. box_size=1 above means the raw
    # image is exactly one pixel per module, so this is a clean integer
    # nearest-neighbor upscale (Pillow forces NEAREST for mode "1"/"L"
    # regardless of the requested filter) -- no blurring or dithering that
    # would make the code harder to scan.
    img = img.resize((size, size))

    # Ensure 1-bit image, which is useful for e-paper
    img = img.convert("1")

    out_dir = os.path.dirname(output)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    img.save(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a Wi-Fi QR code."
    )

    parser.add_argument("ssid", help="Wi-Fi network name")
    parser.add_argument("password", help="Wi-Fi password")
    parser.add_argument(
        "--size",
        type=int,
        default=128,
        help="QR code size in pixels (default: 128)",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help=f"Output image path (default: {DEFAULT_OUTPUT})",
    )

    args = parser.parse_args()

    create_wifi_qr(
        args.ssid,
        args.password,
        args.size,
        args.output,
    )

    print(f"Saved QR code to {args.output}")
