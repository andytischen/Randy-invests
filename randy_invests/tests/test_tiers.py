"""Unit tests for the seeded retail investment-tier catalogue."""

from __future__ import annotations

from randy_invests.web.tiers import (
    TIERS,
    comparison_matrix,
    get_tier,
    get_tiers,
    parse_interest_form,
    recommend_tier,
)


def test_catalogue_has_four_named_tiers():
    names = [tier.name for tier in get_tiers()]
    assert names == ["Bronze", "Silver", "Gold", "Platinum"]
    assert all(tier.minimum_usd > 0 for tier in TIERS)
    assert all(tier.benefits and tier.access for tier in TIERS)
    assert all(tier.hold_period and tier.eligibility for tier in TIERS)


def test_minimums_increase_with_tier():
    mins = [tier.minimum_usd for tier in TIERS]
    assert mins == sorted(mins)
    assert mins[0] == 1_000
    assert mins[-1] == 250_000


def test_gold_is_the_featured_tier():
    featured = [tier for tier in TIERS if tier.featured]
    assert [tier.slug for tier in featured] == ["gold"]


def test_get_tier_is_case_insensitive():
    assert get_tier("Gold").slug == "gold"
    assert get_tier(" unknown ") is None


def test_recommend_tier_picks_highest_eligible():
    assert recommend_tier(500).slug == "bronze"
    assert recommend_tier(1_000).slug == "bronze"
    assert recommend_tier(10_000).slug == "silver"
    assert recommend_tier(50_000).slug == "gold"
    assert recommend_tier(250_000).slug == "platinum"
    assert recommend_tier(1_000_000).slug == "platinum"


def test_comparison_matrix_covers_every_tier():
    rows = comparison_matrix()
    ids = [row["id"] for row in rows]
    assert "minimum" in ids
    assert "fee" in ids
    assert "hold" in ids
    for row in rows:
        assert set(row["values"]) == {"bronze", "silver", "gold", "platinum"}


def test_interest_form_validation():
    bad = parse_interest_form({"name": "A", "email": "nope", "tier": "wood"})
    assert not bad.ok
    assert len(bad.errors) >= 3

    good = parse_interest_form(
        {
            "name": "Alex Rivera",
            "email": "alex@example.com",
            "tier": "silver",
            "amount": "12,500",
            "message": "Looking for a core sleeve.",
        }
    )
    assert good.ok
    assert good.intended_amount == 12_500
    assert good.tier_slug == "silver"
