# Card History Killfeed

A semi-transparent overlay that displays your recent review history during Anki review sessions.

## Use Case

The card info screen (shown when pressing 'i' in the reviewer) is pretty nice, but the only really interesting information for me was the review history, because it helps me make a decision as to whether I should change something about my cards (if I have a huge streak of pressing "again" something is wrong; leech monitoring can do this too, but this is helpful live).


## What It Shows

Each line displays:
- Date and time of review
- Review type (Learn/Review/Relearn)
- Button pressed (1-4, with "1" highlighted in red)
- Interval given

## Configuration

Access via **Tools → Card History Killfeed Config...**

- **Corner position**: Choose where the killfeed appears (top-left, top-right, bottom-left, bottom-right)
- **Maximum lines**: Set how many review entries to display (1-100, default 10)

**Note:** When your window is ≤50% of screen width, the killfeed shows only 1 line and centers at the top, pushing card content down. This hopefully makes it not cover up your card content if your window is small.