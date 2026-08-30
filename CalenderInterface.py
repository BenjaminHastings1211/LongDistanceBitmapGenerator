from ics import Calendar
from dotenv import load_dotenv
import requests, arrow, os

load_dotenv()


class SharedCalendar:
    def __init__(self, url=None):
        self.url = url or os.environ["CALENDER_URL"]

    def _fetch(self):
        resp = requests.get(self.url, timeout=10)
        resp.raise_for_status()
        return Calendar(resp.text)

    def next_event(self):
        try:
            cal = self._fetch()
        except (requests.RequestException, Exception):
            return None

        now = arrow.utcnow()

        # Ongoing event takes priority over future ones
        ongoing = sorted(
            (e for e in cal.events if e.begin <= now <= e.end),
            key=lambda e: e.end
        )
        if ongoing:
            e = ongoing[0]
            return {
                "name": e.name,
                "start": e.begin,
                "end": e.end,
                "duration": e.end - now,  # time remaining until it ends
                "description": e.description,
                "location": e.location,
                "ongoing": True,
            }

        upcoming = sorted(
            (e for e in cal.events if e.begin > now),
            key=lambda e: e.begin
        )
        if not upcoming:
            return None

        e = upcoming[0]
        return {
            "name": e.name,
            "start": e.begin,
            "end": e.end,
            "duration": e.begin - now,  # time remaining until it starts
            "description": e.description,
            "location": e.location,
            "ongoing": False,
        }


if __name__ == "__main__":
    cal = SharedCalendar()
    event = cal.next_event()
    if event:
        status = "ongoing, ends in" if event["ongoing"] else "starts in"
        print(event["name"], status, event["duration"])
    else:
        print("No upcoming events")