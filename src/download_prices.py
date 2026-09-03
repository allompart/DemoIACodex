from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import yfinance as yf


DEFAULT_SYMBOLS_FILE = Path("config/ibex35_symbols.csv")
DEFAULT_OUTPUT_DIR = Path("data")


@dataclass(frozen=True)
class DownloadResult:
    ticker: str
    rows: int
    status: str
    message: str = ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download daily IBEX 35 prices from Yahoo Finance with yfinance."
    )
    parser.add_argument("--symbols-file", type=Path, default=DEFAULT_SYMBOLS_FILE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--start",
        default=None,
        help="Start date, YYYY-MM-DD. If omitted, downloads the full Yahoo Finance history.",
    )
    parser.add_argument("--end", default=None, help="End date, YYYY-MM-DD. Defaults to today.")
    parser.add_argument(
        "--period",
        default="max",
        help="yfinance period used when --start is omitted. Defaults to max.",
    )
    parser.add_argument(
        "--auto-adjust",
        action="store_true",
        help="Ask yfinance for adjusted OHLC prices.",
    )
    return parser.parse_args()


def load_symbols(path: Path) -> pd.DataFrame:
    symbols = pd.read_csv(path)
    required = {"name", "bme_ticker", "yahoo_ticker"}
    missing = required.difference(symbols.columns)
    if missing:
        raise ValueError(f"Missing required columns in {path}: {sorted(missing)}")
    return symbols


def normalize_prices(df: pd.DataFrame, metadata: pd.Series) -> pd.DataFrame:
    prices = df.copy()
    if isinstance(prices.columns, pd.MultiIndex):
        prices.columns = prices.columns.get_level_values(0)

    prices = prices.reset_index()
    prices.columns = [str(column).strip().lower().replace(" ", "_") for column in prices.columns]

    if "date" not in prices.columns:
        raise ValueError(f"Could not find a date column for {metadata['yahoo_ticker']}")

    prices["date"] = pd.to_datetime(prices["date"]).dt.date
    prices.insert(0, "yahoo_ticker", metadata["yahoo_ticker"])
    prices.insert(1, "bme_ticker", metadata["bme_ticker"])
    prices.insert(2, "name", metadata["name"])

    ordered = [
        "yahoo_ticker",
        "bme_ticker",
        "name",
        "date",
        "open",
        "high",
        "low",
        "close",
        "adj_close",
        "volume",
    ]
    available = [column for column in ordered if column in prices.columns]
    return prices[available].sort_values(["yahoo_ticker", "date"])


def download_symbol(
    metadata: pd.Series,
    raw_dir: Path,
    start: str | None,
    end: str | None,
    period: str,
    auto_adjust: bool,
) -> tuple[pd.DataFrame | None, DownloadResult]:
    ticker = metadata["yahoo_ticker"]
    try:
        download_kwargs = {
            "progress": False,
            "auto_adjust": auto_adjust,
            "threads": False,
        }
        if start:
            download_kwargs["start"] = start
            download_kwargs["end"] = end
        else:
            download_kwargs["period"] = period

        data = yf.download(ticker, **download_kwargs)
    except Exception as exc:  # yfinance can raise transport and parsing exceptions.
        return None, DownloadResult(ticker, 0, "error", str(exc))

    if data.empty:
        return None, DownloadResult(ticker, 0, "empty", "No rows returned")

    normalized = normalize_prices(data, metadata)
    normalized.to_csv(raw_dir / f"{ticker}.csv", index=False)
    return normalized, DownloadResult(ticker, len(normalized), "ok")


def main() -> None:
    args = parse_args()
    symbols = load_symbols(args.symbols_file)

    raw_dir = args.output_dir / "raw"
    processed_dir = args.output_dir / "processed"
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    frames: list[pd.DataFrame] = []
    results: list[DownloadResult] = []

    for _, metadata in symbols.iterrows():
        frame, result = download_symbol(
            metadata=metadata,
            raw_dir=raw_dir,
            start=args.start,
            end=args.end,
            period=args.period,
            auto_adjust=args.auto_adjust,
        )
        results.append(result)
        if frame is not None:
            frames.append(frame)
        print(f"{result.status.upper():5} {result.ticker:10} rows={result.rows} {result.message}")

    results_df = pd.DataFrame([result.__dict__ for result in results])
    results_df.to_csv(processed_dir / "download_report.csv", index=False)

    if not frames:
        raise RuntimeError("No price data downloaded. See data/processed/download_report.csv")

    prices = pd.concat(frames, ignore_index=True).sort_values(["yahoo_ticker", "date"])
    prices.to_csv(processed_dir / "ibex35_prices.csv", index=False)
    print(f"\nSaved {len(prices)} rows to {processed_dir / 'ibex35_prices.csv'}")


if __name__ == "__main__":
    main()
