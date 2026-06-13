# Demos — marketing-data automation

Self-built, runnable demonstrations of the kind of marketing-data and automation
work I do for growth / RevOps teams. **All use synthetic data** — they're built to
show architecture and execution, not to expose any client's systems.

| # | Demo | What it shows | Stack |
|---|------|---------------|-------|
| 01 | [Marketing Attribution Pipeline](./01-marketing-attribution-pipeline) | Ingest ad + analytics events → normalize → ROAS by channel, no manual exports | n8n · Python · SQL |
| 02 | [CRM Lead Enrichment (AI)](./02-crm-lead-enrichment) | Inbound leads → LLM enrichment + risk scoring → write back to CRM | n8n · Python · LLM |
| 03 | [RevOps KPI Model + Dashboard](./03-revops-kpi-dashboard) | Clean data model + SQL behind a CAC/ROAS/LTV dashboard stakeholders trust | SQL · Metabase |

Each folder has a case-study README, the workflow/code, and an architecture diagram.

> These are demonstrations with dummy data. Real client work is under NDA and not published.
