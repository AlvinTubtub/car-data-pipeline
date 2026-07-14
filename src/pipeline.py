import argparse
import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict

import polars as pl

# --- CONFIGURATION ---

@dataclass
class PipelineConfig:
    """
    Centralized configuration for the ETL pipeline.
    """
    input_path: Path
    output_path: Path
    usd_to_php_rate: float = 58.0  # Approximate/illustrative FX rate

    # Price Quality Gates
    min_price: float = 100_000.0
    max_price_multiplier: float = 10.0
    price_scale_threshold: float = 5_000_000.0

    # Mileage Quality Gates (rejects missing/garbled/unrealistic values)
    min_mileage: float = 500.0
    max_mileage: float = 300_000.0

    # Canonical Mapping (common abbreviations -> canonical model names)
    synonyms: Dict[str, str] = field(default_factory=lambda: {
        "crv": "cr-v",
        "hrv": "hr-v",
        "mux": "mu-x",
        "dmax": "d-max",
        "brv": "br-v",
        "montero": "montero sport",
    })

# --- LOGGING ---

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# --- ETL FUNCTIONS (Pure Functions) ---

def load_lazy_data(source: Path) -> pl.LazyFrame:
    if not source.exists():
        raise FileNotFoundError(f"Input file not found: {source}")
    logger.info(f"Scanning source: {source}")
    return pl.scan_csv(
        source,
        has_header=False,
        new_columns=["id", "raw_name", "raw_price", "source", "date", "raw_mileage"]
    )

def normalize_pricing(lf: pl.LazyFrame, config: PipelineConfig) -> pl.LazyFrame:
    """Cleans raw strings, handles USD conversion, and fixes scaling errors."""
    return (
        lf
        .with_columns([
            pl.col("raw_price").str.contains(r"\$").alias("is_usd"),
            pl.col("raw_price")
              .str.replace_all(r"[^0-9,.]", "")
              .str.replace(",", ".")
              .cast(pl.Float64, strict=False)
              .alias("raw_float"),
        ])
        .with_columns([
            pl.when(pl.col("raw_float") > config.price_scale_threshold)
              .then(pl.col("raw_float") / 100)
              .otherwise(pl.col("raw_float"))
              .alias("corrected_float")
        ])
        .with_columns([
            pl.when(pl.col("is_usd"))
              .then(pl.col("corrected_float") / config.usd_to_php_rate)
              .otherwise(pl.col("corrected_float"))
              .round(2)
              .alias("price_final")
        ])
    )

def normalize_mileage(lf: pl.LazyFrame) -> pl.LazyFrame:
    """Extracts the numeric km value from the dirty raw_mileage string.

    Handles variants like '45000 km', '45000km', '45,000 KM', '45000 kms',
    and missing/empty values (which become null).
    """
    return lf.with_columns([
        pl.col("raw_mileage")
          .str.replace_all(",", "")
          .str.extract(r"(\d+)", 1)
          .cast(pl.Float64, strict=False)
          .alias("mileage_final")
    ])

def generate_fingerprints(lf: pl.LazyFrame, synonyms: Dict[str, str]) -> pl.LazyFrame:
    """Generates a normalized 'fingerprint' for fuzzy grouping."""
    keys = list(synonyms.keys())
    vals = list(synonyms.values())

    return lf.with_columns([
        pl.col("raw_name")
          .str.to_lowercase()
          .str.replace_many(keys, vals)
          .str.replace_all(r"\b(rush|nego|negotiable|urgent|preowned|certified|forsale|fs)\b", "")
          .str.replace_all(r"[^a-z0-9\s]", " ")
          .str.replace_all(r"\s+", " ")
          .str.strip_chars()
          .str.split(" ")
          .list.sort()
          .list.join(" ")
          .alias("fingerprint")
    ])

def filter_anomalies(lf: pl.LazyFrame, config: PipelineConfig) -> pl.LazyFrame:
    """Filters outliers based on robust group statistics and quality gates.

    Uses the group median instead of the mean so extreme price outliers
    do not inflate the threshold and escape filtering.
    """
    return (
        lf
        .with_columns([
            pl.col("price_final").median().over("fingerprint").alias("group_median")
        ])
        .filter(
            (pl.col("price_final") >= config.min_price) &
            (
                pl.col("price_final")
                <= (pl.col("group_median") * config.max_price_multiplier)
            ) &
            (pl.col("fingerprint").str.len_chars() > 1) &
            (pl.col("mileage_final").is_not_null()) &
            (pl.col("mileage_final") >= config.min_mileage) &
            (pl.col("mileage_final") <= config.max_mileage)
        )
    )

def aggregate_products(lf: pl.LazyFrame) -> pl.LazyFrame:
    """Aggregates metrics by fingerprint."""
    return (
        lf
        .group_by("fingerprint")
        .agg([
            pl.col("raw_name")
              .sort_by(pl.col("raw_name").str.len_chars(), descending=True)
              .first()
              .alias("display_title"),
            pl.col("price_final").mean().round(2).alias("avg_price"),
            pl.col("mileage_final").mean().round(1).alias("avg_mileage"),
            pl.len().alias("occurrence_count")
        ])
        .sort("occurrence_count", descending=True)
        .select(["display_title", "avg_price", "avg_mileage", "occurrence_count"])
    )

# --- CLI & EXECUTION ---

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clean and aggregate used car listings.")
    parser.add_argument("--input", "-i", type=Path, required=True, help="Path to raw CSV file")
    parser.add_argument("--output", "-o", type=Path, required=True, help="Path to output CSV file")
    parser.add_argument("--rate", "-r", type=float, default=58.0, help="USD to PHP exchange rate (approximate, default: 58.0)")
    return parser.parse_args()

def main():
    args = parse_arguments()

    config = PipelineConfig(
        input_path=args.input,
        output_path=args.output,
        usd_to_php_rate=args.rate
    )

    try:
        pipeline = (
            load_lazy_data(config.input_path)
            .pipe(normalize_pricing, config)
            .pipe(normalize_mileage)
            .pipe(generate_fingerprints, config.synonyms)
            .pipe(filter_anomalies, config)
            .pipe(aggregate_products)
        )

        logger.info(f"Starting pipeline. Input: {config.input_path} | Rate: {config.usd_to_php_rate}")
        pipeline.sink_csv(config.output_path, separator=",")
        logger.info(f"Success. Output written to: {config.output_path}")

    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()