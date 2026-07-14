import pytest
import polars as pl
from pathlib import Path
from src.pipeline import (
    normalize_pricing,
    normalize_mileage,
    generate_fingerprints,
    filter_anomalies,
    PipelineConfig,
)

# --- FIXTURES ---

@pytest.fixture
def config():
    """Returns a standard config for testing."""
    return PipelineConfig(
        input_path=Path("dummy_in.csv"),
        output_path=Path("dummy_out.csv"),
        usd_to_php_rate=58.0
    )

# --- TESTS ---

def test_normalize_pricing_logic(config):
    """
    Test 1: Check USD -> PHP conversion.
    Test 2: Check scaling fix (150,000,000 -> 1,500,000.00).
    Test 3: Check standard cleaning (comma decimal separator).
    Test 4: Check invalid input -> null.
    """
    data = pl.DataFrame({
        "raw_price": ["$1160.00", "150000000", "50,00", "invalid"]
    }).lazy()

    # Execution
    result = normalize_pricing(data, config).collect()

    # Assertions
    # 1. $1160 / 58.0 = 20.0
    assert result["price_final"][0] == 20.0
    # 2. 150,000,000 > 5,000,000 threshold -> divide by 100 -> 1,500,000.0
    assert result["price_final"][1] == 1500000.0
    # 3. "50,00" -> 50.0
    assert result["price_final"][2] == 50.0
    # 4. "invalid" -> null
    assert result["price_final"][3] is None

def test_normalize_mileage_logic():
    """
    Test 1: Standard 'km' with space.
    Test 2: No space before unit ('45000km').
    Test 3: Comma-formatted + capitalized unit ('45,000 KM').
    Test 4: Plural unit ('120000 kms').
    Test 5: Missing/empty value -> null.
    """
    data = pl.DataFrame({
        "raw_mileage": ["45000 km", "60000km", "45,000 KM", "120000 kms", ""]
    }).lazy()

    result = normalize_mileage(data).collect()

    assert result["mileage_final"][0] == 45000.0
    assert result["mileage_final"][1] == 60000.0
    assert result["mileage_final"][2] == 45000.0
    assert result["mileage_final"][3] == 120000.0
    assert result["mileage_final"][4] is None

def test_fingerprint_generation():
    """
    Test 1: Synonym replacement (crv -> cr-v).
    Test 2: Token sorting (A B == B A).
    Test 3: Listing filler word removal.
    """
    synonyms = {"crv": "cr-v"}

    data = pl.DataFrame({
        "raw_name": [
            "Honda CRV RUSH!!",     # Should become: cr honda v
            "Rush Honda CR-V",      # Should become: cr honda v
        ]
    }).lazy()

    # Execution
    result = generate_fingerprints(data, synonyms).collect()

    fp1 = result["fingerprint"][0]
    fp2 = result["fingerprint"][1]

    # Assertions
    assert "rush" not in fp1     # Filler word removed
    assert "rush" not in fp2     # Filler word removed
    assert fp1 == fp2            # Both should result in same fingerprint (sorted tokens)
    assert fp1 == "cr honda v"   # Alphabetical order, hyphen normalized to space

def test_filter_anomalies_mileage_gate(config):
    """
    Ensures rows with missing, zero, or out-of-range mileage are dropped,
    even when the price is perfectly valid.
    """
    data = pl.DataFrame({
        "fingerprint": ["toyota vios", "toyota vios", "toyota vios", "toyota vios"],
        "price_final": [500000.0, 500000.0, 500000.0, 500000.0],
        "mileage_final": [45000.0, None, 0.0, 900000.0],  # valid, null, zero, absurd
    }).lazy()

    result = filter_anomalies(data, config).collect()

    # Only the first row (valid mileage) should survive
    assert result.height == 1
    assert result["mileage_final"][0] == 45000.0

def test_filter_anomalies_price_gate_still_works(config):
    """
    Ensures the price anomaly logic (min price, group-relative max) still
    filters correctly alongside the mileage gate.
    """
    data = pl.DataFrame({
        "fingerprint": ["toyota vios", "toyota vios", "toyota vios"],
        "price_final": [500000.0, 20000.0, 50000000.0],  # valid, below min, absurd vs group
        "mileage_final": [45000.0, 45000.0, 45000.0],
    }).lazy()

    result = filter_anomalies(data, config).collect()

    assert result.height == 1
    assert result["price_final"][0] == 500000.0

def test_config_immutability(config):
    """Ensure config preserves critical financial and mileage thresholds."""
    assert config.usd_to_php_rate == 58.0
    assert config.min_price == 100_000.0
    assert config.min_mileage == 500.0
    assert config.max_mileage == 300_000.0