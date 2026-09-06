"""Unit tests for the retail-structured share recommendation layer."""

from __future__ import annotations

from randy_invests.predictor import PipelineConfig
from randy_invests.recommender import Recommendation
from randy_invests.web.recommendations import (
    build_one,
    get_retail_recommendations,
    normalize_tickers,
    structure_for_retail,
    unavailable,
)


def _result(
    ticker="AAPL",
    signal="BUY",
    strength="MODERATE",
    score=0.42,
    direction="UP",
    confidence="MEDIUM",
    change_pct=0.74,
    trend="bullish",
):
    """Build a synthetic run_pipeline-style result dict."""
    rec = Recommendation(
        ticker=ticker,
        signal=signal,
        strength=strength,
        score=score,
        reasons=["ML ensemble predicts UP with MEDIUM confidence (prob=0.62)"],
        price=189.30,
        price_change_estimate_pct=1.23,
        forward_days=5,
    )
    return {
        "ticker": ticker,
        "quote": {"price": 189.30, "change_pct": change_pct},
        "patterns": {
            "recent_trend": trend,
            "price_above_sma20": True,
            "price_above_sma50": True,
        },
        "prediction": {
            "predicted_direction": direction,
            "confidence": confidence,
            "direction_probability": 0.62,
            "price_change_estimate_pct": 1.23,
        },
        "metrics": {"ensemble_accuracy": 0.55},
        "recommendation": rec,
    }


def test_structure_buy_is_positive_and_plain():
    reco = structure_for_retail(_result())
    assert reco.ticker == "AAPL"
    assert reco.action == "Buy"
    assert reco.tone == "positive"
    assert reco.strength == "Moderate"
    assert reco.confidence == "Medium"
    assert reco.price == 189.30
    assert reco.horizon_days == 5
    assert reco.format_move() == "+1.2%"
    assert reco.format_price() == "$189.30"
    # Plain-language, retail-facing summary — no raw indicator jargon.
    assert "buy candidate" in reco.plain_summary.lower()
    assert reco.key_points  # has talking points
    assert any("outlook" in p.lower() for p in reco.key_points)


def test_structure_sell_is_negative():
    reco = structure_for_retail(
        _result(signal="SELL", strength="STRONG", score=-0.6, direction="DOWN", trend="bearish")
    )
    assert reco.action == "Sell"
    assert reco.tone == "negative"
    assert reco.strength == "Strong"
    assert "trimming" in reco.plain_summary.lower() or "standing aside" in reco.plain_summary.lower()


def test_structure_hold_is_neutral():
    reco = structure_for_retail(
        _result(signal="HOLD", strength="WEAK", score=0.05, direction="UP", trend="neutral")
    )
    assert reco.action == "Hold"
    assert reco.tone == "neutral"
    assert reco.strength == "Low-conviction"
    assert "hold-and-watch" in reco.plain_summary.lower()


def test_as_dict_is_json_friendly():
    data = structure_for_retail(_result()).as_dict()
    assert data["ticker"] == "AAPL"
    assert data["action"] == "Buy"
    assert isinstance(data["key_points"], list)
    assert data["available"] is True


def test_unavailable_card():
    reco = unavailable("TSLA")
    assert reco.available is False
    assert reco.ticker == "TSLA"
    assert reco.note


def test_build_one_uses_injected_runner():
    reco = build_one("MSFT", runner=lambda t, c: _result(ticker=t), config=PipelineConfig())
    assert reco.ticker == "MSFT"
    assert reco.available is True


def test_build_one_degrades_gracefully_on_error():
    def boom(ticker, config):
        raise ValueError("no data")

    reco = build_one("BADX", runner=boom, config=PipelineConfig())
    assert reco.available is False
    assert reco.ticker == "BADX"


def test_get_recommendations_caches_successful_results():
    calls = {"n": 0}

    def counting_runner(ticker, config):
        calls["n"] += 1
        return _result(ticker=ticker)

    cache: dict = {}
    first = get_retail_recommendations(
        ["AAPL", "MSFT"], runner=counting_runner, cache=cache, ttl=1000
    )
    assert [r.ticker for r in first] == ["AAPL", "MSFT"]
    assert calls["n"] == 2

    # Second call is served entirely from cache — runner not invoked again.
    again = get_retail_recommendations(
        ["AAPL", "MSFT"], runner=counting_runner, cache=cache, ttl=1000
    )
    assert calls["n"] == 2
    assert [r.ticker for r in again] == ["AAPL", "MSFT"]


def test_failed_lookups_are_not_cached():
    def boom(ticker, config):
        raise RuntimeError("down")

    cache: dict = {}
    get_retail_recommendations(["AAPL"], runner=boom, cache=cache, ttl=1000)
    assert cache == {}


def test_normalize_tickers_cleans_and_bounds():
    assert normalize_tickers("aapl, msft nvda") == ["AAPL", "MSFT", "NVDA"]
    assert normalize_tickers("AAPL AAPL") == ["AAPL"]  # de-duplicated
    assert normalize_tickers("A123 $$$ TSLA") == ["TSLA"]  # drops non-alpha
    assert len(normalize_tickers("a b c d e f g h", limit=6)) == 6
    assert normalize_tickers("") == []
