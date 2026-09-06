"""Flask application for the Randy Invests retail investor portal."""

from __future__ import annotations

import os
from datetime import datetime, timezone

from flask import Flask, abort, flash, redirect, render_template, request, session, url_for

from randy_invests.web.tiers import (
    comparison_matrix,
    get_tier,
    get_tiers,
    parse_interest_form,
    recommend_tier,
)

DEFAULT_SECRET = "randy-invests-portal-demo-only"


def create_app(test_config: dict | None = None) -> Flask:
    """Application factory used by tests and ``python -m randy_invests.web``."""
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )
    app.config.update(
        SECRET_KEY=os.environ.get("RANDY_INVESTS_SECRET", DEFAULT_SECRET),
        TEMPLATES_AUTO_RELOAD=True,
    )
    if test_config:
        app.config.update(test_config)

    # In-memory demo inbox. Replaced per process; never a payment ledger.
    app.interest_inbox = []

    @app.context_processor
    def _globals():
        return {
            "now": datetime.now(timezone.utc),
            "nav_tiers": get_tiers(),
        }

    @app.get("/")
    def home():
        return render_template("home.html", tiers=get_tiers(), page="home")

    @app.get("/tiers")
    def tiers_index():
        selected = (request.args.get("highlight") or "").strip().lower()
        highlighted = get_tier(selected)
        amount_raw = (request.args.get("amount") or "").strip()
        recommended = None
        parsed_amount = None
        if amount_raw:
            try:
                parsed_amount = float(amount_raw.replace(",", "").replace("$", ""))
                recommended = recommend_tier(parsed_amount)
                highlighted = recommended
            except ValueError:
                parsed_amount = None
        return render_template(
            "tiers.html",
            tiers=get_tiers(),
            rows=comparison_matrix(),
            highlighted=highlighted,
            recommended=recommended,
            parsed_amount=parsed_amount,
            page="tiers",
        )

    @app.get("/tiers/<slug>")
    def tier_detail(slug: str):
        tier = get_tier(slug)
        if tier is None:
            abort(404)
        return render_template(
            "tier_detail.html",
            tier=tier,
            tiers=get_tiers(),
            page="tiers",
        )

    @app.get("/interest")
    def interest_get():
        preset = get_tier(request.args.get("tier") or "")
        return render_template(
            "interest.html",
            tiers=get_tiers(),
            preset=preset,
            form={},
            errors=[],
            page="interest",
        )

    @app.post("/interest")
    def interest_post():
        inquiry = parse_interest_form(request.form)
        if not inquiry.ok:
            flash("Please correct the highlighted fields.", "error")
            return render_template(
                "interest.html",
                tiers=get_tiers(),
                preset=get_tier(inquiry.tier_slug),
                form=request.form,
                errors=inquiry.errors,
                page="interest",
            ), 400

        app.interest_inbox.append(inquiry)
        session["last_interest_tier"] = inquiry.tier_slug
        session["demo_investor_name"] = inquiry.name
        if inquiry.intended_amount is not None:
            session["demo_investor_amount"] = inquiry.intended_amount
        flash(
            "Thank you. This is a demonstration inbox — no payment was taken "
            "and no account was opened.",
            "success",
        )
        return redirect(url_for("interest_thanks", tier=inquiry.tier_slug))

    @app.get("/interest/thanks")
    def interest_thanks():
        tier = get_tier(request.args.get("tier") or session.get("last_interest_tier") or "")
        return render_template(
            "thanks.html",
            tier=tier,
            investor_name=session.get("demo_investor_name"),
            page="interest",
        )

    @app.get("/api/tiers")
    def api_tiers():
        payload = []
        for tier in get_tiers():
            payload.append(
                {
                    "slug": tier.slug,
                    "name": tier.name,
                    "minimum_usd": tier.minimum_usd,
                    "annual_fee_pct": tier.annual_fee_pct,
                    "hold_period": tier.hold_period,
                    "featured": tier.featured,
                }
            )
        return {"tiers": payload}

    @app.get("/portal")
    @app.get("/invest")
    def aliases():
        return redirect(url_for("tiers_index"))

    return app


def main() -> None:
    """CLI / console-script entry point."""
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    create_app().run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()
