---
name: retail-investor-portal
description: Extends the Randy Invests Flask retail portal — investment tiers, share ideas, YouTube/marketing pages, and conservative finance copy. Use when changing randy_invests/web, /tiers, /recommendations, /channel, /advertise, or portal UI/copy.
---

# Retail investor portal

Python 3.9+ Flask app in `randy_invests/web`. Extend this stack. Do not add a second frontend.

## Run and verify

```bash
pip install -e ".[dev]" pyarrow
python -m randy_invests.web          # or: randy-invests-portal
# HOST=0.0.0.0 PORT=5000 for remote browsers
pytest randy_invests/tests/ -q
ruff check randy_invests/            # CI runs this on the whole package
```

Canonical product URL: `http://127.0.0.1:5000/tiers`.

## Routes

| Path | Role |
|------|------|
| `/tiers` | Comparison (cards + table). `/portal` and `/invest` redirect here |
| `/tiers/<slug>` | Single program |
| `/recommendations` | ML buy/hold/sell restated for retail. `?tickers=AAPL+MSFT` (max 6) |
| `/interest` | Mocked express-interest form (no payments) |
| `/channel` (`/youtube`) | YouTube brand home |
| `/advertise` | Marketing playbook + partner form |
| `/about` | Meet Randy |
| `/learn` | How the desk works |
| `/api/tiers`, `/api/recommendations` | JSON |

Wire a live YouTube subscribe URL with `YOUTUBE_CHANNEL_URL`. Session secret: `RANDY_INVESTS_SECRET`.

## Layout

```
randy_invests/web/
├── app.py              # Flask factory and routes
├── tiers.py            # Bronze–Platinum catalogue + interest validation
├── recommendations.py  # Retail restatement of ML signals
├── marketing.py        # Channel episodes, ad snippets, partner form
├── templates/          # Jinja; extend base.html
└── static/             # css/portal.css, js/portal.js, img/Randy icon+banner
```

Keep CSS/JS in the existing portal files. Reuse `base.html` nav/footer.

## Tiers

Seeded demo data in `TIERS` (`tiers.py`). Order is lowest minimum → highest: Bronze, Silver, Gold, Platinum. Gold is `featured`.

Each tier needs: name, minimum USD, annual fee, hold/liquidity, eligibility, benefits, access, CTA. Prefer editing the catalogue over hardcoding copy in templates.

Fit highlighter: `recommend_tier(amount)` returns the highest tier whose minimum is met; amounts below Bronze still map to Bronze. Label it **illustrative, not advice**.

**Jinja:** dicts expose `.values` as `dict.values`. Use `row['values'][tier.slug]`, never `row.values[...]`.

## Brand

Randy is a **middle-class member of the investment community** — kitchen-table research, not a hedge-fund character. Icon/banner: `randy_invests/web/static/img/randy_invests_icon.png` and `randy_invests_channel_banner.png`. Use that portrait as avatar, favicon, and header mark.

Channel handle: `@RandyInvests`. Episodes and ads send people to `/tiers` or `/learn`; they do not sell a security on camera.

## Copy rules

- Every public page keeps the footer disclaimer (illustrative; not advice; not an offer).
- No guaranteed returns, “lock it in,” or crystal-ball claims.
- ML labels are research signals, not recommendations to trade.
- Forms are demonstration inboxes (`app.interest_inbox`, `app.partner_inbox`). Do not add real payments.
- No auth yet. Public pages are enough; note personalization as later work.

## Tests and lint

Add HTTP coverage in `randy_invests/tests/test_web.py`. Catalogue/form helpers: `test_tiers.py`, `test_marketing.py`. Ruff config is in `pyproject.toml` (`E,F,W,I,UP`, py39). `X | None` is fine with `from __future__ import annotations`. Do not commit `__pycache__` or `*.egg-info`.
