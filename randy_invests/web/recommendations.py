"""Retail-structured share recommendations for the investor portal.

This module adapts the technical/ML output of the core Randy Invests pipeline
(:func:`randy_invests.main.run_pipeline`) into a plain-language shape that a
retail investor can read at a glance: a clear stance, an estimated move, and a
few de-jargoned talking points — always labelled as illustrative, never advice.

The pipeline runner is injected so the web layer (and tests) can supply a fast,
offline stand-in instead of hitting live market data and training models.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Iterable
from dataclasses import asdict, dataclass

from randy_invests.predictor import PipelineConfig

# A small, well-known demo universe. These are illustrative examples, not picks.
DEFAULT_TICKERS: tuple[str, ...] = ("AAPL", "MSFT", "NVDA")

# 730 days keeps enough history for the 200-day indicators plus the ML
# cross-validation folds (a 365-day window leaves too few rows).
DEFAULT_PERIOD_DAYS: int = 730

# How long a computed recommendation stays warm in the in-memory cache.
DEFAULT_TTL_SECONDS: int = 900

# A runner takes ``(ticker, PipelineConfig)`` and returns the run_pipeline dict.
PipelineRunner = Callable[[str, PipelineConfig], dict]

_UNAVAILABLE_NOTE = (
    "Live market data or model training was unavailable for this symbol just now. "
    "Try again shortly."
)

# signal -> (action verb, retail stance, tone class)
_SIGNAL_MAP: dict[str, tuple[str, str, str]] = {
    "BUY": ("Buy", "Buy candidate", "positive"),
    "SELL": ("Sell", "Consider reducing", "negative"),
    "HOLD": ("Hold", "Hold and watch", "neutral"),
}

_STRENGTH_MAP: dict[str, str] = {
    "STRONG": "Strong",
    "MODERATE": "Moderate",
    "WEAK": "Low-conviction",
}

_TREND_PHRASE: dict[str, str] = {
    "bullish": "trending upward",
    "bearish": "trending downward",
    "neutral": "moving sideways",
}


@dataclass(frozen=True)
class RetailShareRecommendation:
    """A single share recommendation, structured for a retail reader."""

    ticker: str
    action: str  # "Buy" / "Sell" / "Hold"
    stance: str  # retail-facing label, e.g. "Buy candidate"
    strength: str  # "Strong" / "Moderate" / "Low-conviction"
    tone: str  # "positive" / "negative" / "neutral" (drives styling)
    confidence: str  # "High" / "Medium" / "Low"
    headline: str
    plain_summary: str
    key_points: tuple[str, ...] = ()
    price: float = 0.0
    estimated_move_pct: float = 0.0
    horizon_days: int = 5
    score: float = 0.0
    available: bool = True
    note: str = ""

    # -- display helpers -------------------------------------------------
    def format_price(self) -> str:
        return f"${self.price:,.2f}"

    def format_move(self) -> str:
        return f"{self.estimated_move_pct:+.1f}%"

    def format_score(self) -> str:
        return f"{self.score:+.2f}"

    def as_dict(self) -> dict:
        """JSON-serialisable representation for the portal API."""
        data = asdict(self)
        data["key_points"] = list(self.key_points)
        return data


def unavailable(ticker: str, note: str = _UNAVAILABLE_NOTE) -> RetailShareRecommendation:
    """Return a placeholder card used when a symbol cannot be evaluated."""
    return RetailShareRecommendation(
        ticker=ticker.upper(),
        action="Hold",
        stance="No read available",
        strength="",
        tone="neutral",
        confidence="",
        headline=f"{ticker.upper()} — not available right now",
        plain_summary=note,
        key_points=(),
        available=False,
        note=note,
    )


def _key_points(result: dict, horizon_days: int) -> tuple[str, ...]:
    """Build de-jargoned talking points from a pipeline result."""
    quote = result.get("quote", {}) or {}
    patterns = result.get("patterns", {}) or {}
    prediction = result.get("prediction", {}) or {}

    points: list[str] = []

    direction = prediction.get("predicted_direction", "").upper()
    confidence = (prediction.get("confidence") or "").lower() or "low"
    if direction == "UP":
        points.append(
            f"Model's ~{horizon_days}-day outlook leans higher ({confidence} confidence)."
        )
    elif direction == "DOWN":
        points.append(
            f"Model's ~{horizon_days}-day outlook leans lower ({confidence} confidence)."
        )

    trend = patterns.get("recent_trend", "neutral")
    points.append(f"Recent price action is {_TREND_PHRASE.get(trend, 'mixed')}.")

    above_20 = patterns.get("price_above_sma20", False)
    above_50 = patterns.get("price_above_sma50", False)
    if above_20 and above_50:
        points.append("Trading above its recent averages — a supportive sign.")
    elif not above_20 and not above_50:
        points.append("Trading below its recent averages — a cautionary sign.")
    else:
        points.append("Mixed versus its recent moving averages.")

    change_pct = quote.get("change_pct")
    if isinstance(change_pct, (int, float)):
        points.append(f"Today: {change_pct:+.2f}% versus the prior close.")

    return tuple(points)


def _plain_summary(ticker: str, tone: str, strength_l: str, confidence_l: str, horizon: int) -> str:
    if tone == "positive":
        return (
            f"Randy Invests' model leans higher on {ticker} over roughly the next "
            f"{horizon} trading days ({confidence_l} confidence). Read for retail, it "
            f"looks like a {strength_l} buy candidate — an idea to research, not a promise."
        )
    if tone == "negative":
        return (
            f"The model leans lower on {ticker} over roughly the next {horizon} trading "
            f"days ({confidence_l} confidence). Read for retail, it looks like a "
            f"{strength_l} case to consider trimming or standing aside — not a directive to sell."
        )
    return (
        f"Signals on {ticker} are roughly balanced right now, so it reads as "
        f"hold-and-watch rather than act today. Revisit as fresh data arrives."
    )


def structure_for_retail(result: dict) -> RetailShareRecommendation:
    """Adapt a :func:`run_pipeline` result into a retail-structured recommendation.

    Args:
        result: The dict returned by ``run_pipeline`` (keys ``ticker``, ``quote``,
            ``patterns``, ``prediction``, ``metrics``, ``recommendation``).

    Returns:
        A :class:`RetailShareRecommendation`.
    """
    rec = result["recommendation"]
    quote = result.get("quote", {}) or {}
    prediction = result.get("prediction", {}) or {}

    action, stance, tone = _SIGNAL_MAP.get(rec.signal, ("Hold", "Hold and watch", "neutral"))
    strength_word = _STRENGTH_MAP.get(rec.strength, rec.strength.title())
    confidence = (prediction.get("confidence") or "").title()

    horizon = int(getattr(rec, "forward_days", 5) or 5)
    strength_l = strength_word.lower()
    confidence_l = confidence.lower() or "low"

    estimated_move = prediction.get("price_change_estimate_pct")
    if estimated_move is None:
        estimated_move = getattr(rec, "price_change_estimate_pct", 0.0)

    headline = f"{strength_word} {stance.lower()}" if strength_word else stance

    return RetailShareRecommendation(
        ticker=str(getattr(rec, "ticker", result.get("ticker", ""))).upper(),
        action=action,
        stance=stance,
        strength=strength_word,
        tone=tone,
        confidence=confidence,
        headline=headline,
        plain_summary=_plain_summary(
            getattr(rec, "ticker", ""), tone, strength_l, confidence_l, horizon
        ),
        key_points=_key_points(result, horizon),
        price=float(quote.get("price", getattr(rec, "price", 0.0)) or 0.0),
        estimated_move_pct=round(float(estimated_move or 0.0), 4),
        horizon_days=horizon,
        score=float(getattr(rec, "score", 0.0) or 0.0),
        available=True,
    )


def _default_runner(ticker: str, config: PipelineConfig) -> dict:
    # Imported lazily so importing this module (e.g. in tests that inject a
    # runner) does not pull in yfinance / scikit-learn unnecessarily.
    from randy_invests.main import run_pipeline

    return run_pipeline(ticker, config)


def build_one(
    ticker: str,
    *,
    runner: PipelineRunner | None = None,
    config: PipelineConfig | None = None,
) -> RetailShareRecommendation:
    """Evaluate a single ticker, returning an ``unavailable`` card on failure."""
    runner = runner or _default_runner
    config = config or PipelineConfig(period_days=DEFAULT_PERIOD_DAYS)
    try:
        result = runner(ticker, config)
        return structure_for_retail(result)
    except Exception:  # noqa: BLE001 - portal should degrade gracefully, never 500
        return unavailable(ticker)


def get_retail_recommendations(
    tickers: Iterable[str],
    *,
    runner: PipelineRunner | None = None,
    config: PipelineConfig | None = None,
    cache: dict | None = None,
    ttl: int = DEFAULT_TTL_SECONDS,
) -> list[RetailShareRecommendation]:
    """Return retail-structured recommendations for *tickers*.

    Successful results are memoised in *cache* (keyed by upper-cased ticker) for
    *ttl* seconds so repeated page loads do not re-train models. Failed lookups
    are not cached, so a transient data outage can recover on the next request.
    """
    config = config or PipelineConfig(period_days=DEFAULT_PERIOD_DAYS)
    now = time.monotonic()
    out: list[RetailShareRecommendation] = []
    for raw in tickers:
        ticker = str(raw).strip().upper()
        if not ticker:
            continue
        if cache is not None and ticker in cache:
            cached_at, cached_reco = cache[ticker]
            if now - cached_at < ttl:
                out.append(cached_reco)
                continue
        reco = build_one(ticker, runner=runner, config=config)
        if cache is not None and reco.available:
            cache[ticker] = (now, reco)
        out.append(reco)
    return out


def normalize_tickers(raw: str, *, limit: int = 6) -> list[str]:
    """Parse a comma/space separated ticker string into a clean, bounded list."""
    if not raw:
        return []
    seen: list[str] = []
    for chunk in raw.replace(",", " ").split():
        token = chunk.strip().upper()
        if token and token.isalpha() and 1 <= len(token) <= 6 and token not in seen:
            seen.append(token)
        if len(seen) >= limit:
            break
    return seen
