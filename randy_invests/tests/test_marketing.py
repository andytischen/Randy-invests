"""Unit tests for YouTube-channel and advertising catalogue helpers."""

from __future__ import annotations

from randy_invests.web.marketing import (
    CHANNEL_HANDLE,
    get_ad_snippets,
    get_episodes,
    get_market_channels,
    get_share_links,
    parse_partner_form,
)


def test_channel_handle_and_episode_slate():
    assert CHANNEL_HANDLE == "@RandyInvests"
    titles = [episode.title for episode in get_episodes()]
    assert any("kitchen table" in title.lower() for title in titles)
    assert any("Bronze vs Silver" in title for title in titles)
    assert all(episode.duration and episode.summary for episode in get_episodes())


def test_market_channels_and_snippets_are_retail_safe():
    names = [item.name for item in get_market_channels()]
    assert "YouTube education series" in names
    assert all(item.first_move for item in get_market_channels())
    snippets = get_ad_snippets()
    assert snippets
    assert all(snippet.destination.startswith("/") for snippet in snippets)
    assert all(snippet.headline and snippet.body for snippet in snippets)


def test_share_links_carry_utm_tags():
    paths = [link["path"] for link in get_share_links()]
    assert any("utm_source=youtube" in path for path in paths)
    assert any(path.startswith("/tiers") for path in paths)


def test_partner_form_validation():
    bad = parse_partner_form({"name": "A", "email": "x", "organization": "", "channel": "billboard"})
    assert not bad.ok
    good = parse_partner_form(
        {
            "name": "Riley Patel",
            "email": "riley@example.com",
            "organization": "Tuesday Night Club",
            "channel": "youtube",
        }
    )
    assert good.ok
    assert good.channel == "youtube"
