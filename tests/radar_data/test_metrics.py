from scripts.radar_data.metrics import (
    classify_signal,
    compute_pe,
    percentile_rank,
    relative_volume,
    simple_moving_average,
)


def test_sma200_uses_latest_200_valid_values():
    values = [0.0, None] + [float(value) for value in range(1, 201)]

    assert simple_moving_average(values, 200) == 100.5


def test_sma_returns_none_when_valid_sample_is_too_short():
    assert simple_moving_average([1.0] * 199, 200) is None


def test_empirical_percentile_is_inclusive():
    assert percentile_rank(list(range(1, 11)), 1, min_samples=10) == 10.0
    assert percentile_rank(list(range(1, 11)), 10, min_samples=10) == 100.0


def test_percentile_returns_none_when_sample_is_too_short():
    assert percentile_rank([1.0] * 9, 1.0, min_samples=10) is None


def test_relative_volume_uses_prior_twenty_sessions():
    assert relative_volume(200.0, [100.0] * 20) == 2.0


def test_company_pe_requires_positive_eps():
    assert compute_pe(120.0, 6.0, "stock") == 20.0
    assert compute_pe(120.0, 0.0, "stock") is None
    assert compute_pe(120.0, -2.0, "stock") is None


def test_etf_never_receives_company_pe():
    assert compute_pe(500.0, 20.0, "etf") is None


def test_signal_requires_technical_and_dual_low_percentiles():
    result = classify_signal(
        price=80.0,
        sma200=100.0,
        price_percentile=8.0,
        pe_percentile=7.0,
    )

    assert result.signal_a is True
    assert result.signal_b is True
    assert result.level == "review"
    assert result.label == "人工复核"


def test_single_signal_is_only_watch():
    result = classify_signal(
        price=80.0,
        sma200=100.0,
        price_percentile=40.0,
        pe_percentile=50.0,
    )

    assert result.signal_a is True
    assert result.signal_b is False
    assert result.level == "watch"


def test_missing_or_stale_data_never_generates_review_signal():
    missing = classify_signal(
        price=80.0,
        sma200=100.0,
        price_percentile=8.0,
        pe_percentile=None,
    )
    stale = classify_signal(
        price=80.0,
        sma200=100.0,
        price_percentile=8.0,
        pe_percentile=7.0,
        stale=True,
    )

    assert missing.level == "unknown"
    assert stale.level == "unknown"
