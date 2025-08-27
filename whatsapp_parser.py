"""
Parser for exported WhatsApp chats.

This module exposes a single function, `parse_chat`, which accepts the path
to a WhatsApp text export.  It returns a list of message dictionaries with
`timestamp`, `sender` and `text` keys.

The parser supports the standard English export format:

```
12/30/24, 9:15 PM - Alice: Hey!
12/31/24, 10:00 AM - Bob: Hello
```

It also handles multi‑line messages by appending subsequent lines that do not
start with a date.

If your export uses a different locale (e.g. day/month order or a 24‑hour
time), you may need to adjust the regular expression and datetime parsing.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

# Regular expression to match the beginning of a WhatsApp message.
_MESSAGE_RE = re.compile(
    r"^(?P<date>\d{1,2}/\d{1,2}/\d{2,4}),\s*(?P<time>\d{1,2}:\d{2})\s*(?P<ampm>AM|PM)?\s*\-\s*(?P<sender>[^:]+):\s*(?P<text>.*)$"
)


@dataclass
class Message:
    timestamp: datetime
    sender: str
    text: str


def _parse_timestamp(date_str: str, time_str: str, ampm: Optional[str]) -> datetime:
    """Parse date and time strings into a datetime object.

    The function expects US style dates (month/day/year).  The year can be
    two or four digits.  If a year has two digits it is interpreted as
    2000+year (e.g. 24 -> 2024).  The time can be given with or without AM/PM.
    """
    # Normalise two‑digit years by prepending 20
    parts = date_str.split("/")
    month, day, year = parts
    if len(year) == 2:
        year = "20" + year
    date_fmt = "%m/%d/%Y"
    if ampm:
        fmt = f"{date_fmt}, %I:%M %p"
        dt_str = f"{month}/{day}/{year}, {time_str} {ampm}"
    else:
        fmt = f"{date_fmt}, %H:%M"
        dt_str = f"{month}/{day}/{year}, {time_str}"
    return datetime.strptime(dt_str, fmt)


def parse_chat(file_path: str) -> List[Message]:
    """Parse a WhatsApp chat export and return a list of Message objects.

    Lines that do not match the message pattern are treated as continuations
    of the previous message.  Empty lines are ignored.
    """
    messages: List[Message] = []
    current_msg: Optional[Message] = None
    with open(file_path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip("\n")
            if not line:
                continue
            m = _MESSAGE_RE.match(line)
            if m:
                # Save previous message before starting a new one
                if current_msg is not None:
                    messages.append(current_msg)
                date_str = m.group("date")
                time_str = m.group("time")
                ampm = m.group("ampm")
                sender = m.group("sender").strip()
                text = m.group("text")
                timestamp = _parse_timestamp(date_str, time_str, ampm)
                current_msg = Message(timestamp=timestamp, sender=sender, text=text)
            else:
                # Continuation of previous message
                if current_msg is not None:
                    current_msg.text += "\n" + line
                else:
                    # Skip lines that appear before the first message
                    continue
    # Append the last message
    if current_msg is not None:
        messages.append(current_msg)
    return messages