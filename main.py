"""
Entry point for the Chat Roast analyser.

Run this script with a WhatsApp chat export to generate visual statistics and
a humorous roast.  Results will be written as PNG images into the output
directory and the roast text will be printed to the terminal.

Example:

    python main.py --input my_chat.txt --output analysis

By default the roast level is ``medium``; use ``--level mild`` or ``--level savage``
to tone it down or crank it up.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

import matplotlib

# Use the Agg backend for headless environments
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from typing import List

from .whatsapp_parser import parse_chat
from .analysis_utils import (
    message_counts,
    messages_by_day,
    messages_by_hour,
    messages_by_weekday,
    top_emojis,
    top_words,
)
from .roast_engine import generate_roast


def _ensure_output_dir(path: Path) -> None:
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)


def _plot_message_count(counts: dict, output_dir: Path) -> None:
    """Create a pie chart of messages per participant."""
    labels = list(counts.keys())
    sizes = list(counts.values())
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
    ax.set_title("Message Share by Participant")
    plt.tight_layout()
    fig.savefig(output_dir / "message_share.png")
    plt.close(fig)


def _plot_activity_over_time(day_counts: dict, output_dir: Path) -> None:
    """Create a bar chart of messages per day."""
    # Sort dates chronologically
    dates = sorted(day_counts.keys())
    counts = [day_counts[d] for d in dates]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(dates, counts, marker="o")
    ax.set_title("Messages over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Message Count")
    ax.tick_params(axis="x", rotation=45)
    plt.tight_layout()
    fig.savefig(output_dir / "activity_over_time.png")
    plt.close(fig)


def _plot_activity_by_hour(hour_counts: dict, output_dir: Path) -> None:
    """Create a bar chart of messages by hour of day."""
    hours = list(range(24))
    counts = [hour_counts.get(h, 0) for h in hours]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(hours, counts, color="#69b3a2")
    ax.set_title("Messages by Hour of Day")
    ax.set_xlabel("Hour")
    ax.set_ylabel("Message Count")
    ax.set_xticks(hours)
    plt.tight_layout()
    fig.savefig(output_dir / "activity_by_hour.png")
    plt.close(fig)


def _plot_activity_by_weekday(weekday_counts: dict, output_dir: Path) -> None:
    """Create a bar chart of messages by day of week."""
    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    counts = [weekday_counts.get(i, 0) for i in range(7)]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(weekdays, counts, color="#4071f4")
    ax.set_title("Messages by Day of Week")
    ax.set_xlabel("Day of Week")
    ax.set_ylabel("Message Count")
    plt.tight_layout()
    fig.savefig(output_dir / "activity_by_weekday.png")
    plt.close(fig)


def _plot_top_words(words: List[tuple], output_dir: Path) -> None:
    """Create a horizontal bar chart of top words."""
    if not words:
        return
    labels, values = zip(*words)
    fig, ax = plt.subplots(figsize=(6, 4))
    y_pos = list(range(len(labels)))
    ax.barh(y_pos, values, color="#e07a5f")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.set_xlabel("Count")
    ax.set_title("Top Words")
    plt.tight_layout()
    fig.savefig(output_dir / "top_words.png")
    plt.close(fig)


def _plot_top_emojis(emojis: List[tuple], output_dir: Path) -> None:
    """Create a bar chart of top emojis."""
    if not emojis:
        return
    labels, values = zip(*emojis)
    fig, ax = plt.subplots(figsize=(6, 4))
    x_pos = list(range(len(labels)))
    ax.bar(x_pos, values, color="#f2c14e")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, fontsize=16)
    ax.set_ylabel("Count")
    ax.set_title("Top Emojis")
    plt.tight_layout()
    fig.savefig(output_dir / "top_emojis.png")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyse a WhatsApp chat and generate charts + roast.")
    parser.add_argument("--input", required=True, help="Path to WhatsApp chat export (.txt)")
    parser.add_argument("--output", required=True, help="Directory to write output images")
    parser.add_argument("--level", default="medium", choices=["mild", "medium", "savage"], help="Roast intensity level")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file '{input_path}' does not exist")
    _ensure_output_dir(output_path)

    # Parse messages
    messages = parse_chat(str(input_path))
    if not messages:
        print("No messages parsed. Is the input file a valid WhatsApp export?")
        return

    # Compute statistics
    counts = message_counts(messages)
    day_counts = messages_by_day(messages)
    hour_counts = messages_by_hour(messages)
    weekday_counts = messages_by_weekday(messages)
    top_words_list = top_words(messages, n=10)
    top_emojis_list = top_emojis(messages, n=5)

    # Produce charts
    _plot_message_count(counts, output_path)
    _plot_activity_over_time(day_counts, output_path)
    _plot_activity_by_hour(hour_counts, output_path)
    _plot_activity_by_weekday(weekday_counts, output_path)
    _plot_top_words(top_words_list, output_path)
    _plot_top_emojis(top_emojis_list, output_path)

    # Generate roast
    roast_text = generate_roast(messages, level=args.level)
    print("\n====== Your Chat Roast ======\n")
    print(roast_text)


if __name__ == "__main__":
    main()