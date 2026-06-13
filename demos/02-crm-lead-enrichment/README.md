# Demo 02 — AI Lead Enrichment + Risk Scoring

**Stack:** n8n · Python · LLM (Anthropic/OpenAI) · CRM (HubSpot-style API)
**Type:** Self-built demonstration with synthetic data.

> A representative build of an inbound-lead pipeline that enriches each lead with an
> LLM, assigns an insurtech-style risk/fit tier, and writes the result back to the
> CRM — so sales sees a scored, summarized lead instead of a bare email. Built to
> show architecture; data and scoring are synthetic.

---

## The Challenge

Inbound leads arrive as little more than a name, email, and company. Sales then
manually researches each one — company size, industry, rough fit — before deciding
who to chase. It's slow, inconsistent, and the highest-fit leads get the same
delay as the worst ones.

## The Architecture

```mermaid
flowchart LR
  A[Webhook: new lead\n(form / CRM)] --> B[Enrich firmographics\n(domain → size, industry)]
  B --> C[LLM node\nsummary + fit + risk tier]
  C --> D{Risk/fit tier}
  D -->|High fit| E[CRM: tag + assign\nto AE, notify Slack]
  D -->|Low fit| F[CRM: nurture queue]
```

**Decisions & rationale**
- **n8n webhook** fires the moment a lead is created.
- A **firmographics step** turns the email domain into company attributes (size,
  industry) — stubbed here, swappable for Clearbit/Apollo in production.
- An **LLM step** produces a one-line summary, a fit rationale, and a risk/fit tier
  from a strict rubric. (See [`enrich.py`](./enrich.py) — runs with a built-in mock
  model so no API key is needed; a real Anthropic/OpenAI call is included, commented.)
- A **router** sends high-fit leads straight to an AE + Slack ping; low-fit leads go
  to nurture — so attention is spent where it converts.

## The Deliverable

- [`enrich.py`](./enrich.py) — enrichment + scoring. **Runnable as-is:** `python enrich.py`.
- [`workflow.n8n.json`](./workflow.n8n.json) — importable webhook → enrich → LLM → CRM router.
- This case study + diagram.

Sample output (`python enrich.py`):

```
COMPANY              SIZE     INDUSTRY     TIER   SUMMARY
Northwind Mutual     520      insurance    A      Mid-size insurer; strong embedded-API fit.
Acme Bakeries        14       food         C      Tiny non-tech SMB; poor fit, nurture.
Lattice Underwriting  85      insurtech    A      Series-B insurtech; high-intent ICP match.
```

## The Outcome (modeled)

- Manual lead research: **minutes per lead → seconds, automatic.**
- Consistent, rubric-based scoring → AEs work the **best-fit leads first.**
- Every lead lands in the CRM already summarized, tagged, and routed.
