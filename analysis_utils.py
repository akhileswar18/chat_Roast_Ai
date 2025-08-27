"""
Utility functions to compute statistics from a list of WhatsApp messages.

Most functions accept a list of `Message` objects returned by
`whatsapp_parser.parse_chat` and return high level aggregates useful for
plotting or roasting.  Word and emoji statistics ignore common stop words
and treat emojis separately from plain text.
"""
from __future__ import annotations

import re
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime
from typing import Iterable, Dict, List, Tuple

from .whatsapp_parser import Message

# A small set of common English stopwords for word frequency analysis.  For a
# production system you might use nltk.corpus.stopwords instead.
STOPWORDS = set(
    [
        "the",
        "and",
        "is",
        "in",
        "to",
        "a",
        "of",
        "for",
        "on",
        "with",
        "you",
        "i",
        "it",
        "that",
        "at",
        "this",
        "my",
        "your",
        "me",
        "we",
        "our",
        "us",
        "be",
        "as",
        "are",
        "was",
        "were",
        "so",
        "but",
        "if",
        "too",
        "not",
        "or",
        "just",
        "it's",
        "its",
        "can't",
        "dont",
        "can't",
        "can't",
        "do",
        "did",
        "didn't",
        "don't",
        "u",
        "im",
        "lol",
        "haha",
        "hahaha",
    ]
)


def message_counts(messages: Iterable[Message]) -> Dict[str, int]:
    """Return a dict of sender -> number of messages sent."""
    counts = Counter()
    for msg in messages:
        counts[msg.sender] += 1
    return dict(counts)


def messages_by_day(messages: Iterable[Message]) -> Dict[str, int]:
    """Return a dict of YYYY‑MM‑DD -> message count."""
    counts = Counter()
    for msg in messages:
        key = msg.timestamp.strftime("%Y-%m-%d")
        counts[key] += 1
    return dict(counts)


def messages_by_hour(messages: Iterable[Message]) -> Dict[int, int]:
    """Return a dict of hour (0-23) -> message count."""
    counts = Counter()
    for msg in messages:
        counts[msg.timestamp.hour] += 1
    return dict(counts)


def messages_by_weekday(messages: Iterable[Message]) -> Dict[int, int]:
    """Return a dict of weekday (0=Monday) -> message count."""
    counts = Counter()
    for msg in messages:
        counts[msg.timestamp.weekday()] += 1
    return dict(counts)


_WORD_RE = re.compile(r"\b\w+\b", re.UNICODE)


def extract_words(text: str) -> List[str]:
    """Extract a list of lowercase words from a text string."""
    words = _WORD_RE.findall(text.lower())
    return [w for w in words if w and w not in STOPWORDS and len(w) > 1]


def top_words(messages: Iterable[Message], n: int = 10) -> List[Tuple[str, int]]:
    """Return the top `n` most common non‑stop words across all messages."""
    counter = Counter()
    for msg in messages:
        for word in extract_words(msg.text):
            counter[word] += 1
    return counter.most_common(n)


_EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "\U00002700-\U000027BF"  # Dingbats
    "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
    "]+",
    flags=re.UNICODE,
)


def extract_emojis(text: str) -> List[str]:
    """Return a list of emoji characters found in the text."""
    return _EMOJI_PATTERN.findall(text)


def top_emojis(messages: Iterable[Message], n: int = 5) -> List[Tuple[str, int]]:
    """Return the top `n` most common emojis across all messages."""
    counter = Counter()
    for msg in messages:
        for emoji_char in extract_emojis(msg.text):
            counter[emoji_char] += 1
    return counter.most_common(n)