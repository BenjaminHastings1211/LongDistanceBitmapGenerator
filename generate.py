from BitmapGenerator import make_countdown_screen
from CalenderInterface import SharedCalendar
from ProvisioningScreen import make_provisioning_screen
from ScreenBuilder import ScreenBuilder, WIDTH, HEIGHT

# Construct Time Cards
timezones = [
    'eastern',
    'pacific',
    'mountain',
    'central'
]

for tz in timezones:
    cal = SharedCalendar(tz)
    event = cal.next_event()


    make_countdown_screen(
        event,
        number_font=("YellowBanana", 92),
        name_font=("Retrotech", 32),
        tiny_font=("default", 14),
        gap=5,
        margin=8,
        invert=False
    ).save(f"./screens/main/%s.bmp"%tz)

# Update System Screens

# Wifi Screen

make_provisioning_screen().save("./screens/system/qr.bmp")

# Boot Sreen

ScreenBuilder() \
    .text("Booting...", (WIDTH // 2, HEIGHT // 2 - 10), font="abduction2002", size=53) \
    .text("Long Distance Tracker", (148, 95), font="Retrotech", size=22) \
    .line((20, 78, 276, 78)) \
    .save("./screens/system/boot.bmp")

# Error Screen

ScreenBuilder() \
    .text("ERROR", (WIDTH // 2, 38), font="BlueScreen", size=62) \
    .line((28, 68, 268, 68), width=1) \
    .text("Something went wrong.", (WIDTH // 2, 82), font="Retrotech", size=16) \
    .text("Please reboot.", (WIDTH // 2, 100), font="Retrotech", size=16) \
    .save("./screens/system/error.bmp")