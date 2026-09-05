from ics import Calendar
from dotenv import load_dotenv
import requests, arrow, os
from zoneinfo import ZoneInfo

load_dotenv()


class SharedCalendar:
    TIMEZONES = {
        "eastern": "America/New_York",
        "central": "America/Chicago",
        "mountain": "America/Denver",
        "pacific": "America/Los_Angeles",
    }

    def __init__(self, timezone):
        if timezone not in self.TIMEZONES:
            raise ValueError(
                f"Invalid timezone '{timezone}'. "
                f"Must be one of: {', '.join(self.TIMEZONES)}"
            )

        self.timezone = ZoneInfo(self.TIMEZONES[timezone])
        self.url = os.environ["CALENDER_URL"]

    def _fetch(self):
        resp = requests.get(self.url, timeout=10)
        resp.raise_for_status()
        return Calendar(resp.text)

    def next_event(self):
        try:
            cal = self._fetch()
        except Exception:
            return None

        now = arrow.now(self.timezone)

        events = [
            e for e in cal.events
            if e.begin and e.end
        ]

        ongoing = sorted(
            (
                e for e in events
                if e.begin.to(self.timezone) <= now <= e.end.to(self.timezone)
            ),
            key=lambda e: e.end
        )

        if ongoing:
            e = ongoing[0]
            start = e.begin.to(self.timezone)
            end = e.end.to(self.timezone)

            return {
                "name": e.name,
                "start": start,
                "end": end,
                "duration": end - now,
                "description": e.description,
                "location": e.location,
                "ongoing": True,
            }

        upcoming = sorted(
            (
                e for e in events
                if e.begin.to(self.timezone) > now
            ),
            key=lambda e: e.begin
        )

        if not upcoming:
            return None

        e = upcoming[0]
        start = e.begin.to(self.timezone)
        end = e.end.to(self.timezone)

        return {
            "name": e.name,
            "start": start,
            "end": end,
            "duration": start - now,
            "description": e.description,
            "location": e.location,
            "ongoing": False,
        }


if __name__ == "__main__":
    cal = SharedCalendar("pacific")
    event = cal.next_event()

    if event:
        status = "ongoing, ends in" if event["ongoing"] else "starts in"
        print(event["name"], status, event["duration"])
    else:
        print("No upcoming events")