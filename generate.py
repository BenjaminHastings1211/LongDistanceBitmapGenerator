from BitmapGenerator import make_countdown_screen
from CalenderInterface import SharedCalendar

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
        number_font=("2k12", 92),
        name_font=("default", 28),
        tiny_font=("default", 14),
        gap=5,
        margin=8,
        invert=False
    ).save(f"./screens/main/%s.bmp"%tz)