"""HTTP tests for the retail investor portal."""

from __future__ import annotations

import pytest

from randy_invests.web.app import create_app


@pytest.fixture
def client():
    app = create_app({"TESTING": True, "SECRET_KEY": "test"})
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
