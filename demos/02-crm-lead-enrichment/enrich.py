"""
AI lead enrichment + risk/fit scoring.

For each inbound lead: derive firmographics from the domain, ask an LLM to produce
a one-line summary + a fit tier (A/B/C) against an ICP rubric, and emit a row ready
to write back to the CRM.

Runnable as-is with a built-in MOCK model (no API key required):
    python enrich.py

To use a real model, set USE_REAL_LLM = True and an ANTHROPIC_API_KEY env var
(the call is implemented in `_real_llm`, kept minimal and commented).
"""

from __future__ import annotations

import os
from dataclasses import dataclass

USE_REAL_LLM = False  # flip to True + set ANTHROPIC_API_KEY to use a live model

# --- Synthetic inbound leads (in production: from a webhook) ---
SAMPLE_LEADS = [
    {"name": "Dana Cole", "email": "dana@northwindmutual.com"},
    {"name": "Sam Reyes", "email": "sam@acmebakeries.com"},
    {"name": "Priya N.", "email": "priya@latticeunderwriting.com"},
]

# Stubbed firmographics by domain (in production: Clearbit / Apollo lookup).
_FIRMOGRAPHICS = {
    "northwindmutual.com": {"company": "Northwind Mutual", "size": 520, "industry": "insurance"},
    "acmebakeries.com": {"company": "Acme Bakeries", "size": 14, "industry": "food"},
    "latticeunderwriting.com": {"company": "Lattice Underwriting", "size": 85, "industry": "insurtech"},
}

ICP_RUBRIC = (
    "Ideal customer: post-revenue insurtech / embedded-insurance company, ~50-1000 staff, "
    "tech-forward. Tier A = strong fit, B = partial, C = poor fit (too small or off-industry)."
)


@dataclass
class Enriched:
    company: str
    size: int
    industry: str
    tier: str
    summary: str


def firmographics(email: str) -> dict:
    domain = email.split("@", 1)[-1].lower()
    return _FIRMOGRAPHICS.get(domain, {"company": domain, "size": 0, "industry": "unknown"})


def _mock_llm(firmo: dict) -> tuple[str, str]:
    """Deterministic stand-in for an LLM scoring call (so the demo runs offline)."""
    size, industry = firmo["size"], firmo["industry"]
    tech_ins = industry in {"insurtech", "insurance"}
    if tech_ins and 50 <= size <= 1000:
        tier = "A"
        kind = "Series-B insurtech" if industry == "insurtech" else "Mid-size insurer"
        summary = f"{kind}; {'high-intent ICP match.' if industry == 'insurtech' else 'strong embedded-API fit.'}"
    elif tech_ins:
        tier = "B"
        summary = "Insurance-adjacent but size is off-band; partial fit."
    else:
        tier = "C"
        summary = "Tiny non-tech SMB; poor fit, nurture." if size < 50 else "Off-industry; poor fit."
    return tier, summary


def _real_llm(firmo: dict) -> tuple[str, str]:  # pragma: no cover - needs network + key
    """Live scoring via Anthropic. Returns (tier, summary)."""
    import json
    import anthropic  # pip install anthropic

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    prompt = (
        f"{ICP_RUBRIC}\nCompany: {firmo}\n"
        'Reply as compact JSON: {"tier":"A|B|C","summary":"<=10 words"}.'
    )
    msg = client.messages.create(
        model="claude-fable-5",
        max_tokens=120,
        messages=[{"role": "user", "content": prompt}],
    )
    data = json.loads(msg.content[0].text)
    return data["tier"], data["summary"]


def enrich(lead: dict) -> Enriched:
    firmo = firmographics(lead["email"])
    tier, summary = (_real_llm if USE_REAL_LLM else _mock_llm)(firmo)
    return Enriched(firmo["company"], firmo["size"], firmo["industry"], tier, summary)


def main() -> None:
    rows = [enrich(lead) for lead in SAMPLE_LEADS]
    print(f"{'COMPANY':<21}{'SIZE':<9}{'INDUSTRY':<13}{'TIER':<7}SUMMARY")
    for r in rows:
        print(f"{r.company:<21}{r.size:<9}{r.industry:<13}{r.tier:<7}{r.summary}")


if __name__ == "__main__":
    main()
