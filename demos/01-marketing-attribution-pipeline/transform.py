"""
Marketing attribution normalizer + ROAS calculator.

Takes raw ad-spend rows and attribution events from multiple platforms (each with
its own schema), normalizes them into one shape, de-duplicates events, joins spend
to conversions by channel, and prints ROAS by channel.

Runnable as-is with bundled synthetic data:
    python transform.py

No external services or credentials required. In production the SAMPLE_SPEND /
generated-events blocks are replaced by n8n HTTP + webhook nodes feeding this same
logic (see workflow.n8n.json).
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

# --- Synthetic spend (in production: pulled from Meta / Google Ads APIs) ---
# Platform-native schemas differ on purpose, to show normalization.
SAMPLE_SPEND = [
    {"source": "meta", "campaign_id": "c1", "date": "2026-06-12", "spend_cents": 70000},
    {"source": "meta", "campaign_id": "c2", "date": "2026-06-12", "spend_cents": 50000},
    {"source": "google_ads", "campaignId": "g1", "day": "2026-06-12", "cost": 980.00},
]

CHANNEL_ALIASES = {"meta": "meta", "facebook": "meta", "google_ads": "google", "google": "google"}

# Conversion volume + per-conversion revenue per channel (synthetic but realistic).
_EVENT_SPEC = [
    ("meta", "c1", 90, 30.00),
    ("meta", "c2", 66, 30.00),
    ("google", "g1", 133, 28.00),
    ("referral", "organic", 43, 30.00),
]


def generate_events() -> list[dict]:
    """Build a deterministic synthetic postback stream (with one duplicate)."""
    events: list[dict] = []
    n = 0
    for channel, campaign, count, rev in _EVENT_SPEC:
        for _ in range(count):
            n += 1
            events.append({"event_id": f"e{n}", "channel": channel,
                           "campaign": campaign, "date": "2026-06-12", "revenue": rev})
    # Duplicate the first postback to prove idempotent de-duplication works.
    events.append(dict(events[0]))
    return events


@dataclass
class ChannelStats:
    spend: float = 0.0
    revenue: float = 0.0
    conversions: int = 0

    @property
    def roas(self) -> float | None:
        return round(self.revenue / self.spend, 2) if self.spend else None


def normalize_spend(rows: list[dict]) -> dict[str, float]:
    """Collapse each platform's spend schema into {channel: spend_dollars}."""
    out: dict[str, float] = defaultdict(float)
    for r in rows:
        channel = CHANNEL_ALIASES.get(r.get("source", ""), r.get("source", ""))
        if "spend_cents" in r:
            out[channel] += r["spend_cents"] / 100.0
        elif "cost" in r:
            out[channel] += float(r["cost"])
    return dict(out)


def dedupe_events(events: list[dict]) -> list[dict]:
    """Drop duplicate attribution postbacks by event_id (idempotency)."""
    seen: set[str] = set()
    unique = []
    for e in events:
        if e["event_id"] in seen:
            continue
        seen.add(e["event_id"])
        unique.append(e)
    return unique


def build_channel_stats(spend: dict[str, float], events: list[dict]) -> dict[str, ChannelStats]:
    stats: dict[str, ChannelStats] = defaultdict(ChannelStats)
    for ch, amt in spend.items():
        stats[ch].spend += amt
    for e in events:
        ch = CHANNEL_ALIASES.get(e["channel"], e["channel"])
        stats[ch].revenue += float(e["revenue"])
        stats[ch].conversions += 1
    return dict(stats)


def render(stats: dict[str, ChannelStats]) -> str:
    lines = [f"{'channel':<9} {'spend':>8} {'revenue':>9} {'conversions':>12} {'ROAS':>6}"]
    for ch in sorted(stats):
        s = stats[ch]
        roas = f"{s.roas:.2f}" if s.roas is not None else "n/a"
        lines.append(f"{ch:<9} {s.spend:>8.2f} {s.revenue:>9.2f} {s.conversions:>12} {roas:>6}")
    return "\n".join(lines)


def main() -> None:
    spend = normalize_spend(SAMPLE_SPEND)
    raw_events = generate_events()
    events = dedupe_events(raw_events)
    print(f"# ingested {len(raw_events)} postbacks, {len(events)} after de-dup")
    print(render(build_channel_stats(spend, events)))


if __name__ == "__main__":
    main()
