"""
Simple roast engine for WhatsApp chats.

The goal of this module is to transform plain statistics into witty commentary.
Roasts are light‑hearted and never personal – they focus on observable chat
behaviour (who talks a lot, who lurks, when the conversation happens, etc.).

The roast intensity can be tweaked via the `level` argument.  Three levels
are supported:

* ``mild`` – friendly observations with almost no sarcasm
* ``medium`` – balanced snark with a cheeky tone (default)
* ``savage`` – extra spicy remarks that still avoid being truly mean
"""
from __future__ import annotations

from typing import Iterable, List, Tuple
import math

from whatsapp_parser import Message
from analysis_utils import (
    message_counts,
    messages_by_hour,
    messages_by_weekday,
    top_emojis,
    top_words,
)


_WEEKDAY_NAMES = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
}


def _percentage(part: int, whole: int) -> int:
    return int(round(part / whole * 100)) if whole else 0


def _format_hour(hour: int) -> str:
    """Return an hour in human friendly 12‑hour format."""
    suffix = "AM" if hour < 12 else "PM"
    h = hour % 12
    if h == 0:
        h = 12
    return f"{h}{suffix}"


def generate_roast(messages: Iterable[Message], level: str = "medium") -> str:
    """Generate a roast paragraph based on the chat messages.

    :param messages: An iterable of Message objects
    :param level: 'mild', 'medium' or 'savage'
    :return: A multi‑line string with witty commentary
    """
    level = level.lower()
    if level not in {"mild", "medium", "savage"}:
        level = "medium"

    msgs = list(messages)
    total_messages = len(msgs)
    if total_messages == 0:
        return "No messages to roast."

    counts = message_counts(msgs)
    # Determine talkative vs silent participants
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    top_sender, top_count = sorted_counts[0]
    top_pct = _percentage(top_count, total_messages)
    bottom_sender, bottom_count = sorted_counts[-1]
    bottom_pct = _percentage(bottom_count, total_messages)

    hour_counts = messages_by_hour(msgs)
    peak_hour = max(hour_counts.items(), key=lambda x: x[1])[0]
    weekday_counts = messages_by_weekday(msgs)
    peak_weekday = max(weekday_counts.items(), key=lambda x: x[1])[0]

    emojis = top_emojis(msgs, n=1)
    top_emoji, emoji_count = (emojis[0] if emojis else (None, 0))

    words = top_words(msgs, n=1)
    top_word, word_count = (words[0] if words else (None, 0))

    lines: List[str] = []

    # Template for talkative user
    if level == "mild":
        lines.append(
            f"{top_sender} sent the most messages at {top_pct}% of the chat. Quite the social butterfly!"
        )
        lines.append(
            f"{bottom_sender} only contributed {bottom_pct}% of messages. Lurking is an art form, after all."
        )
    elif level == "medium":
        lines.append(
            f"{top_sender} dominated the chat with {top_pct}% of the messages. Maybe let someone else get a word in?"
        )
        lines.append(
            f"{bottom_sender} clocked in at just {bottom_pct}% of messages. Do you even know this chat exists?"
        )
    else:  # savage
        lines.append(
            f"{top_sender} hogged {top_pct}% of the conversation. Ever heard of a hobby outside this chat?"
        )
        lines.append(
            f"{bottom_sender} barely registered at {bottom_pct}% of messages. Silent member or professional ghoster?"
        )

    # Template for peak activity time
    peak_hour_str = _format_hour(peak_hour)
    weekday_name = _WEEKDAY_NAMES.get(peak_weekday, "Unknown day")
    if level == "mild":
        lines.append(
            f"Most chatting happens around {peak_hour_str} on {weekday_name}. Night owls with a schedule, perhaps?"
        )
    elif level == "medium":
        lines.append(
            f"Peak chat time is {peak_hour_str} on {weekday_name}. Who needs sleep when you have memes?"
        )
    else:
        lines.append(
            f"You lot blow up the chat at {peak_hour_str} on {weekday_name}. Congratulations on never respecting bed time."
        )

    # Template for favourite emoji
    if top_emoji:
        if level == "mild":
            lines.append(
                f"Your favourite emoji appears to be {top_emoji}, used {emoji_count} times. Expressive bunch!"
            )
        elif level == "medium":
            lines.append(
                f"Top emoji award goes to {top_emoji} – dropped {emoji_count} times. Maybe diversify your feelings?"
            )
        else:
            lines.append(
                f"{top_emoji} shows up {emoji_count} times. Ever considered using words like a normal human?"
            )

    # Template for most common word
    if top_word:
        if level == "mild":
            lines.append(
                f"The word '{top_word}' comes up a lot ({word_count} times). Looks like a favourite topic!"
            )
        elif level == "medium":
            lines.append(
                f"You say '{top_word}' {word_count} times. Is that a cry for help or just laziness?"
            )
        else:
            lines.append(
                f"'{top_word}' appears {word_count} times. We get it, you have a limited vocabulary."
            )

    return "\n".join(lines)