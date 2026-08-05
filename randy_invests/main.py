"""Main entry point for the Randy-Invests stock market predictor."""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from pathlib import Path

from randy_invests.data_fetcher import fetch_historical_data, fetch_realtime_quote
from randy_invests.predictor import PipelineConfig, StockPredictor
from randy_invests.recommender import Recommendation, generate_recommendation
from randy_invests.technical_analysis import add_indicators, identify_patterns

_DISCLAIMER = (
    "\n⚠  DISCLAIMER: Randy-Invests is for informational and educational purposes only."
    "\n   Nothing in this output constitutes financial advice, a recommendation to buy or"
    "\n   sell any security, or an offer or solicitation to trade. Always do your own"
    "\n   research and consult a qualified financial professional before investing.\n"
)


# ---------------------------------------------------------------------------
# Pure pipeline (no I/O side effects)
# ---------------------------------------------------------------------------


def run_pipeline(ticker: str, config: PipelineConfig) -> dict:
    """Run the full analysis pipeline for *ticker* and return structured results.

    This function has no side effects (no printing).  It is the testable core
    of the CLI — :func:`analyse` wraps it and handles all output formatting.

    Args:
        ticker: Stock ticker symbol (e.g. ``'AAPL'``).
        config: :class:`~randy_invests.predictor.PipelineConfig` controlling
            all pipeline parameters.

    Returns:
        Dictionary with keys:
            ``ticker``, ``quote``, ``patterns``, ``metrics``,
            ``prediction``, ``recommendation``
            (a :class:`~randy_invests.recommender.Recommendation` instance).

    Raises:
        ValueError: If data cannot be fetched or is insufficient.
        RuntimeError: If the predictor is in an invalid state.
    """
    df = fetch_historical_data(
        ticker,
        period_days=config.period_days,
        use_cache=config.use_cache,
        cache_ttl_seconds=config.cache_ttl_seconds,
    )
    quote = fetch_realtime_quote(ticker)
    df_ind = add_indicators(df)
    patterns = identify_patterns(df_ind)

    predictor = StockPredictor(config=config)
    metrics = predictor.train(df_ind)
    prediction = predictor.predict(df_ind)

    rec = generate_recommendation(
        ticker=ticker,
        quote=quote,
        prediction=prediction,
        patterns=patterns,
        training_metrics=metrics,
        forward_days=config.forward_days,
    )

    return {
        "ticker": ticker.upper(),
        "quote": quote,
        "patterns": patterns,
        "metrics": metrics,
        "prediction": prediction,
        "recommendation": rec,
    }


# ---------------------------------------------------------------------------
# Output formatting helpers
# ---------------------------------------------------------------------------


def _print_patterns(patterns: dict) -> None:
    """Print a compact summary of detected patterns."""
    labels = {
        "golden_cross":            "Golden Cross (SMA-20 > SMA-50)",
        "death_cross":             "Death Cross (SMA-20 < SMA-50)",
        "macd_bullish_crossover":  "MACD Bullish Crossover",
        "macd_bearish_crossover":  "MACD Bearish Crossover",
        "price_above_sma20":       "Above SMA-20",
        "price_above_sma50":       "Above SMA-50",
        "price_above_sma200":      "Above SMA-200",
        "rsi_overbought":          "RSI Overbought (>70)",
        "rsi_oversold":            "RSI Oversold (<30)",
        "stoch_overbought":        "Stochastic Overbought (>80)",
        "stoch_oversold":          "Stochastic Oversold (<20)",
        "williams_r_overbought":   "Williams %R Overbought (>-20)",
        "williams_r_oversold":     "Williams %R Oversold (<-80)",
        "cci_overbought":          "CCI Overbought (>100)",
        "cci_oversold":            "CCI Oversold (<-100)",
        "bollinger_squeeze":       "Bollinger Band Squeeze",
        "bb_above_upper":          "Price Above BB Upper Band",
        "bb_below_lower":          "Price Below BB Lower Band",
        "kc_above_upper":          "Price Above Keltner Upper Band",
        "kc_below_lower":          "Price Below Keltner Lower Band",
        "dc_breakout_up":          "Donchian Breakout Up (new 20-day high)",
        "dc_breakout_down":        "Donchian Breakout Down (new 20-day low)",
        "strong_trend":            "Strong Trend (ADX > 25)",
        "weak_trend":              "Weak Trend (ADX < 20)",
        "adx_bullish":             "ADX Bullish (+DI > -DI)",
        "vortex_bullish":          "Vortex Bullish (VI+ > VI-)",
        "psar_bullish":            "Parabolic SAR Bullish",
        "psar_bearish":            "Parabolic SAR Bearish",
        "aroon_bullish":           "Aroon Bullish",
        "aroon_bearish":           "Aroon Bearish",
        "mfi_overbought":          "MFI Overbought (>80)",
        "mfi_oversold":            "MFI Oversold (<20)",
    }
    active = [label for key, label in labels.items() if patterns.get(key)]
    trend = patterns.get("recent_trend", "neutral")
    print(f"      Recent trend: {trend.upper()}")
    if active:
        for label in active:
            print(f"      ✓ {label}")
    else:
        print("      No strong pattern signals detected.")


def _print_summary_table(results: list[dict]) -> None:
    """Print a compact summary table for multiple tickers."""
    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    header = f"{'Ticker':<8} {'Price':>8} {'Change%':>9} {'Signal':<16} {'Score':>7} {'CV RF%':>7} {'CV GB%':>7}"
    print(header)
    print("-" * 70)
    for r in results:
        rec: Recommendation = r["recommendation"]
        q = r["quote"]
        m = r["metrics"]
        signal_str = f"{rec.strength} {rec.signal}"
        cv_rf = f"{m.get('cv_rf_accuracy', 0):.1%}"
        cv_gb = f"{m.get('cv_gb_accuracy', 0):.1%}"
        print(
            f"{rec.ticker:<8} {q['price']:>8.2f} {q['change_pct']:>+9.2f}%"
            f" {signal_str:<16} {rec.score:>+7.3f} {cv_rf:>7} {cv_gb:>7}"
        )
    print("=" * 70)


def _results_to_json(results: list[dict]) -> str:
    """Serialise pipeline results to a JSON string."""
    out = []
    for r in results:
        rec: Recommendation = r["recommendation"]
        out.append({
            "ticker": r["ticker"],
            "quote": r["quote"],
            "metrics": r["metrics"],
            "prediction": r["prediction"],
            "recommendation": {
                "signal": rec.signal,
                "strength": rec.strength,
                "score": rec.score,
                "price": rec.price,
                "price_change_estimate_pct": rec.price_change_estimate_pct,
                "forward_days": rec.forward_days,
                "reasons": rec.reasons,
            },
        })
    return json.dumps(out, indent=2, default=str)


def _results_to_csv(results: list[dict]) -> str:
    """Serialise pipeline results to a CSV string."""
    buf = io.StringIO()
    fieldnames = [
        "ticker", "price", "change_pct", "signal", "strength", "score",
        "price_change_estimate_pct", "forward_days",
        "rf_accuracy", "gb_accuracy", "ensemble_accuracy",
        "cv_rf_accuracy", "cv_gb_accuracy",
    ]
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    for r in results:
        rec: Recommendation = r["recommendation"]
        q = r["quote"]
        m = r["metrics"]
        writer.writerow({
            "ticker": r["ticker"],
            "price": q["price"],
            "change_pct": q["change_pct"],
            "signal": rec.signal,
            "strength": rec.strength,
            "score": rec.score,
            "price_change_estimate_pct": rec.price_change_estimate_pct,
            "forward_days": rec.forward_days,
            "rf_accuracy": m.get("rf_accuracy", ""),
            "gb_accuracy": m.get("gb_accuracy", ""),
            "ensemble_accuracy": m.get("ensemble_accuracy", ""),
            "cv_rf_accuracy": m.get("cv_rf_accuracy", ""),
            "cv_gb_accuracy": m.get("cv_gb_accuracy", ""),
        })
    return buf.getvalue()


# ---------------------------------------------------------------------------
# High-level analyse (with I/O)
# ---------------------------------------------------------------------------


def analyse(ticker: str, config: PipelineConfig) -> dict:
    """Run the full analysis pipeline for *ticker* and print formatted output.

    Args:
        ticker: Stock ticker symbol (e.g. ``'AAPL'``).
        config: :class:`~randy_invests.predictor.PipelineConfig` instance.

    Returns:
        The structured results dictionary from :func:`run_pipeline`.
    """
    print(f"\n{'='*60}")
    print(f"  Randy-Invests Stock Market Predictor: {ticker.upper()}")
    print(f"{'='*60}")

    print(f"\n[1/4] Fetching historical data ({config.period_days} days)...")
    # We call run_pipeline which re-fetches; print steps inline for UX
    print("\n[2/4] Fetching real-time quote...")
    print("\n[3/4] Computing technical indicators and patterns...")
    print("\n[4/4] Training ML models and generating prediction...")

    result = run_pipeline(ticker, config)
    q = result["quote"]
    m = result["metrics"]
    rec: Recommendation = result["recommendation"]

    print(f"\n      {ticker.upper()} @ ${q['price']:.2f}  ({q['change_pct']:+.2f}% today)")
    _print_patterns(result["patterns"])
    print(
        f"      Model accuracy — RF: {m['rf_accuracy']:.1%}  "
        f"GB: {m['gb_accuracy']:.1%}  "
        f"Ensemble: {m['ensemble_accuracy']:.1%}  "
        f"(CV RF: {m.get('cv_rf_accuracy', 0):.1%}  CV GB: {m.get('cv_gb_accuracy', 0):.1%})"
    )
    print(f"\n{rec}\n")
    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="randy-invests",
        description="Randy-Invests: ML-powered stock market predictor with buy/sell recommendations.",
    )
    parser.add_argument(
        "tickers",
        nargs="*",
        metavar="TICKER",
        help="One or more stock ticker symbols to analyse (e.g. AAPL MSFT TSLA).",
    )
    parser.add_argument(
        "--watchlist",
        metavar="FILE",
        help="Path to a plain-text file with one ticker per line.",
    )
    parser.add_argument(
        "--period",
        type=int,
        default=365,
        metavar="DAYS",
        help="Days of historical data to use for training (default: 365).",
    )
    parser.add_argument(
        "--forward",
        type=int,
        default=5,
        metavar="DAYS",
        help="Prediction horizon in trading days (default: 5).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="output_json",
        help="Output results as JSON (suppresses human-readable output).",
    )
    parser.add_argument(
        "--csv",
        action="store_true",
        dest="output_csv",
        help="Output results as CSV (suppresses human-readable output).",
    )
    parser.add_argument(
        "--no-cache",
        action="store_false",
        dest="use_cache",
        help="Disable the local parquet data cache.",
    )

    args = parser.parse_args()

    # Collect tickers
    tickers: list[str] = list(args.tickers)
    if args.watchlist:
        wl = Path(args.watchlist)
        if not wl.exists():
            print(f"[ERROR] Watchlist file not found: {wl}", file=sys.stderr)
            sys.exit(1)
        for line in wl.read_text().splitlines():
            t = line.strip()
            if t and not t.startswith("#"):
                tickers.append(t)

    if not tickers:
        parser.print_help()
        sys.exit(1)

    config = PipelineConfig(
        period_days=args.period,
        forward_days=args.forward,
        use_cache=args.use_cache,
    )

    machine_output = args.output_json or args.output_csv
    if not machine_output:
        print(_DISCLAIMER)

    results: list[dict] = []
    errors: list[str] = []
    for ticker in tickers:
        try:
            if machine_output:
                result = run_pipeline(ticker, config)
            else:
                result = analyse(ticker, config)
            results.append(result)
        except Exception as exc:  # noqa: BLE001
            print(f"\n[ERROR] {ticker.upper()}: {exc}", file=sys.stderr)
            errors.append(ticker)

    # Machine-readable outputs
    if args.output_json and results:
        print(_results_to_json(results))
    elif args.output_csv and results:
        print(_results_to_csv(results), end="")
    elif results and len(results) > 1:
        _print_summary_table(results)

    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
