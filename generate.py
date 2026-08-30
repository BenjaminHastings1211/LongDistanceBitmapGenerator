from BitmapGenerator import make_countdown_screen
from CalenderInterface import SharedCalendar

cal = SharedCalendar()
event = cal.next_event()

make_countdown_screen(
    event,
    number_font=("SevenSegment", 72),
    name_font=("default", 28),
    tiny_font=("default", 14),
    gap=10,
    margin=8,
    invert=False
).save(f"./screens/main/pacific.bmp")