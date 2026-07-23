# vince-portfolio

Monorepo for Vince Macaraig's public-facing work. Structured so the deployed site is decoupled from the tooling behind it.

## Structure

```
/web        → the deployed portfolio site (Vercel deploys THIS folder)
            currently plain static HTML/CSS/JS (no build step)
/           → repo root: docs, experiments, and future automation demos
```

Future folders (planned):
```
/demos      → n8n / Python automation demos (workflow JSON exports + READMEs)
              — the credibility artifacts for AI-automation freelance work
```

## Deploy (Vercel)

| Setting | Value |
|---|---|
| **Root Directory** | `web` |
| **Framework Preset** | `Other` (static — no build) |
| **Build / Output / Install** | leave empty |

Auto-deploys on every push to `main`.

### Upgrade path (when richer animation / components are wanted)
Convert `web/` into a Vite or Next app. The **only** Vercel setting that changes is the
build command (e.g. Vite → `npm run build`, output `dist`). Root Directory stays `web`,
so nothing else breaks. For light animation, GSAP via CDN needs no build at all.

## Site sections (as of claude/portfolio-refresh)
- **Case studies** — 3 anonymized production systems (real workflow logic, no client
  data) with n8n canvas screenshots + report mockups in `web/assets/`
- **Spec demos** — the 3 runnable synthetic demos in `/demos`
- **Fixed-scope offer** — automated weekly report setup, $400 / 5 days

## TODO before sharing the link widely
- ~~Replace `LINKEDIN-URL-TBD`~~ done · ~~contact email button~~ done
- Optional: refresh `og.png` to feature a case-study visual
- Optional: record 1–2 Loom walkthroughs of the case-study workflows
