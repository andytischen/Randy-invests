"""HTTP tests for the retail investor portal."""

from __future__ import annotations

import pytest

from randy_invests.recommender import Recommendation
from randy_invests.web.app import create_app


def _fake_runner(ticker, config):
    """Offline stand-in for run_pipeline used by portal recommendation tests."""
    rec = Recommendation(
        ticker=ticker,
        signal="BUY",
        strength="MODERATE",
        score=0.42,
        reasons=["ML ensemble predicts UP with MEDIUM confidence"],
        price=100.0,
        price_change_estimate_pct=1.5,
        forward_days=5,
    )
    return {
        "ticker": ticker,
        "quote": {"price": 100.0, "change_pct": 0.5},
        "patterns": {
            "recent_trend": "bullish",
            "price_above_sma20": True,
            "price_above_sma50": True,
        },
        "prediction": {
            "predicted_direction": "UP",
            "confidence": "MEDIUM",
            "direction_probability": 0.62,
            "price_change_estimate_pct": 1.5,
        },
        "metrics": {"ensemble_accuracy": 0.55},
        "recommendation": rec,
    }


@pytest.fixture
def client():
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test",
            "RECOMMENDATION_RUNNER": _fake_runner,
            "RECOMMENDATION_TICKERS": ["AAPL", "MSFT"],
        }
    )
    with app.test_client() as client:
        yield client, app


def test_home_and_tiers_render(client):
    http, _app = client
    home = http.get("/")
    assert home.status_code == 200
    body = home.get_data(as_text=True)
    assert "Investment access" in body
    assert "Bronze" in body
    assert "not financial" in body.lower() or "not an offer" in body.lower()

    tiers = http.get("/tiers")
    assert tiers.status_code == 200
    page = tiers.get_data(as_text=True)
    assert "Bronze" in page
    assert "Silver" in page
    assert "Gold" in page
    assert "Platinum" in page
    assert "$1,000" in page
    assert "$250,000" in page
    assert "Side-by-side comparison" in page
    assert "Express interest" in page
    assert "illustrative" in page.lower()
    assert "Educational recaps" in page
    assert "Named liaison" in page
    assert "Dedicated analyst" in page


def test_alias_routes_redirect_to_tiers(client):
    http, _app = client
    for path in ("/portal", "/invest"):
        response = http.get(path)
        assert response.status_code in {301, 302}
        assert response.headers["Location"].endswith("/tiers")


def test_tier_detail_and_404(client):
    http, _app = client
    gold = http.get("/tiers/gold")
    assert gold.status_code == 200
    assert "Gold access" in gold.get_data(as_text=True)
    assert http.get("/tiers/wood").status_code == 404


def test_fit_highlighter_query(client):
    http, _app = client
    page = http.get("/tiers?amount=60000").get_data(as_text=True)
    assert "maps to" in page
    assert "Gold" in page
    assert "is-highlighted" in page


def test_interest_form_round_trip(client):
    http, app = client
    blank = http.get("/interest?tier=bronze")
    assert blank.status_code == 200
    assert "Bronze" in blank.get_data(as_text=True)

    rejected = http.post(
        "/interest",
        data={"name": "", "email": "bad", "tier": ""},
    )
    assert rejected.status_code == 400
    assert app.interest_inbox == []

    accepted = http.post(
        "/interest",
        data={
            "name": "Jordan Chen",
            "email": "jordan@example.com",
            "tier": "platinum",
            "amount": "300000",
        },
        follow_redirects=True,
    )
    assert accepted.status_code == 200
    text = accepted.get_data(as_text=True)
    assert "Thank you, Jordan Chen" in text
    assert "Platinum" in text
    assert len(app.interest_inbox) == 1
    assert app.interest_inbox[0].tier_slug == "platinum"


def test_separate_marketing_pages(client):
    http, _app = client
    about = http.get("/about")
    assert about.status_code == 200
    assert "Meet Randy" in about.get_data(as_text=True)
    assert "middle-class" in about.get_data(as_text=True)

    learn = http.get("/learn")
    assert learn.status_code == 200
    assert "How the desk works" in learn.get_data(as_text=True)

    channel = http.get("/channel")
    assert channel.status_code == 200
    body = channel.get_data(as_text=True)
    assert "@RandyInvests" in body
    assert "kitchen table" in body.lower()
    assert http.get("/youtube").status_code == 200

    advertise = http.get("/advertise")
    assert advertise.status_code == 200
    ad = advertise.get_data(as_text=True)
    assert "Ready-to-run snippets" in ad
    assert "utm_source=youtube" in ad


def test_partner_form_round_trip(client):
    http, app = client
    rejected = http.post(
        "/advertise",
        data={"name": "", "email": "bad", "organization": "", "channel": ""},
    )
    assert rejected.status_code == 400
    assert app.partner_inbox == []

    accepted = http.post(
        "/advertise",
        data={
            "name": "Sam Ortiz",
            "email": "sam@example.com",
            "organization": "Oak Street Investment Club",
            "channel": "investment-club",
            "message": "Can we walk through the fee table?",
        },
        follow_redirects=True,
    )
    assert accepted.status_code == 200
    assert "Partner note received" in accepted.get_data(as_text=True)
    assert len(app.partner_inbox) == 1
    assert app.partner_inbox[0].channel == "investment-club"


def test_randy_icon_is_served(client):
    http, _app = client
    icon = http.get("/static/img/randy_invests_icon.png")
    banner = http.get("/static/img/randy_invests_channel_banner.png")
    assert icon.status_code == 200
    assert icon.mimetype == "image/png"
    assert banner.status_code == 200


def test_recommendations_page_renders_retail_cards(client):
    http, _app = client
    page = http.get("/recommendations").get_data(as_text=True)
    assert "Share recommendations, in plain language." in page
    assert "AAPL" in page and "MSFT" in page
    # Retail framing and stance, not raw indicator jargon.
    assert "buy candidate" in page.lower()
    assert "not investment advice" in page.lower()


def test_recommendations_custom_ticker_query(client):
    http, _app = client
    page = http.get("/recommendations?tickers=tsla goog").get_data(as_text=True)
    assert "TSLA" in page
    assert "GOOG" in page


def test_api_recommendations_json(client):
    http, _app = client
    payload = http.get("/api/recommendations").get_json()
    slugs = [row["ticker"] for row in payload["recommendations"]]
    assert slugs == ["AAPL", "MSFT"]
    first = payload["recommendations"][0]
    assert first["action"] == "Buy"
    assert first["tone"] == "positive"
    assert isinstance(first["key_points"], list)


def test_nav_links_to_share_ideas(client):
    http, _app = client
    page = http.get("/").get_data(as_text=True)
    assert 'href="/recommendations"' in page
    assert "Share ideas" in page


def test_api_tiers_json(client):
    http, _app = client
    payload = http.get("/api/tiers").get_json()
    assert [row["slug"] for row in payload["tiers"]] == [
        "bronze",
        "silver",
        "gold",
        "platinum",
    ]
    assert payload["tiers"][0]["minimum_usd"] == 1000
