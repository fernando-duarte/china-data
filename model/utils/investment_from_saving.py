"""Investment from saving calculation module for the China Growth Model.

This module implements the current account balance equation:
I_t = sY_t + CA_t

Where:
- I_t: Investment in period t
- s: Savings rate
- Y_t: GDP in period t
- CA_t: Current account balance in period t

The current account balance is calculated as:
CA_t = -NX_t (negative of net exports)

Net exports (NX_t) = Exports - Imports
"""

import logging

import pandas as pd

logger = logging.getLogger(__name__)


def _validate_positive_gdp(gdp: float) -> float:
    """Validate that GDP is positive."""
    if gdp <= 0:
        msg = f"GDP must be positive, got {gdp}"
        raise ValueError(msg)
    return gdp


def _validate_savings_rate(s: float) -> float:
    """Validate that savings rate is between 0 and 1."""
    if not 0 <= s <= 1:
        msg = f"Savings rate must be between 0 and 1, got {s}"
        raise ValueError(msg)
    return s


def _calculate_scalar_investment(
    gdp: float, savings_rate: float, net_exports: float
) -> tuple[float, float, float, float]:
    """Calculate investment from scalar inputs."""
    domestic_savings = savings_rate * gdp
    current_account = -net_exports
    investment = domestic_savings + current_account

    logger.debug("Calculated investment: I=%.2f from S=%.2f, CA=%.2f", investment, domestic_savings, current_account)

    return investment, domestic_savings, current_account, net_exports


def _calculate_series_investment(
    gdp: pd.Series[float], savings_rate: pd.Series[float], net_exports: pd.Series[float]
) -> tuple[pd.Series[float], pd.Series[float], pd.Series[float], pd.Series[float]]:
    """Calculate investment from series inputs."""
    domestic_savings = savings_rate * gdp
    current_account = -net_exports
    investment = domestic_savings + current_account

    logger.debug("Calculated investment series for %d periods", len(gdp))

    return investment, domestic_savings, current_account, net_exports


def calculate_investment_from_saving(
    gdp: float | pd.Series[float],
    savings_rate: float | pd.Series[float],
    net_exports: float | pd.Series[float],
) -> float | pd.Series[float]:
    """Calculate investment using the current account balance equation.

    Investment is determined by domestic savings plus the current account balance.
    The current account balance equals the negative of net exports (trade balance).

    Args:
        gdp: GDP in current period (Y_t)
        savings_rate: Savings rate (s, between 0 and 1)
        net_exports: Net exports (exports - imports)

    Returns:
        Investment level (I_t)

    Raises:
        ValueError: If GDP is non-positive or savings rate is not in [0, 1]

    Example:
        >>> investment = calculate_investment_from_saving(gdp=1000.0, savings_rate=0.3, net_exports=50.0)
        >>> print(f"Investment: {investment:.2f}")
        Investment: 250.00
    """
    # Handle series input
    if isinstance(gdp, pd.Series) or isinstance(savings_rate, pd.Series) or isinstance(net_exports, pd.Series):
        # Convert all to series for consistent handling
        if not isinstance(gdp, pd.Series):
            if isinstance(savings_rate, pd.Series):
                series_len = len(savings_rate)
            elif isinstance(net_exports, pd.Series):
                series_len = len(net_exports)
            else:
                # All are scalars, shouldn't reach here but handle it
                series_len = 1
            gdp = pd.Series([gdp] * series_len, dtype=float)
        if not isinstance(savings_rate, pd.Series):
            series_len = len(gdp)  # gdp is now guaranteed to be a Series
            savings_rate = pd.Series([savings_rate] * series_len, dtype=float)
        if not isinstance(net_exports, pd.Series):
            series_len = len(gdp)  # gdp is now guaranteed to be a Series
            net_exports = pd.Series([net_exports] * series_len, dtype=float)

        # Validate series inputs
        if (gdp <= 0).any():
            logger.warning("Some GDP values are non-positive")
            gdp = gdp.clip(lower=1e-6)

        if ((savings_rate < 0) | (savings_rate > 1)).any():
            logger.warning("Some savings rates are outside [0, 1]")
            savings_rate = savings_rate.clip(lower=0, upper=1)

        investment, _, _, _ = _calculate_series_investment(gdp, savings_rate, net_exports)
        return investment

    # Handle scalar input
    assert isinstance(gdp, float)  # Type narrowing for MyPy
    validated_gdp = _validate_positive_gdp(gdp)
    assert isinstance(savings_rate, float)  # Type narrowing for MyPy
    validated_savings_rate = _validate_savings_rate(savings_rate)
    assert isinstance(net_exports, float)  # Type narrowing for MyPy

    scalar_investment, _, _, _ = _calculate_scalar_investment(validated_gdp, validated_savings_rate, net_exports)
    return scalar_investment


def calculate_investment_breakdown(gdp: float, savings_rate: float, net_exports: float) -> dict[str, float]:
    """Calculate investment with detailed breakdown of components.

    Args:
        gdp: GDP in current period
        savings_rate: Savings rate (between 0 and 1)
        net_exports: Net exports (exports - imports)

    Returns:
        Dictionary containing:
        - investment: Total investment
        - domestic_savings: Domestic savings (s*Y)
        - current_account: Current account balance (-NX)
        - net_exports: Net exports (NX)
        - investment_rate: Investment as share of GDP

    Raises:
        ValueError: If inputs are invalid
    """
    gdp = _validate_positive_gdp(gdp)
    savings_rate = _validate_savings_rate(savings_rate)

    investment, domestic_savings, current_account, net_exports = _calculate_scalar_investment(
        gdp, savings_rate, net_exports
    )

    return {
        "investment": investment,
        "domestic_savings": domestic_savings,
        "current_account": current_account,
        "net_exports": net_exports,
        "investment_rate": investment / gdp,
    }


def calculate_investment_dataframe(
    df: pd.DataFrame,
    *,
    gdp_col: str = "gdp",
    savings_rate_col: str = "savings_rate",
    net_exports_col: str = "net_exports",
    output_col: str = "investment",
    add_components: bool = False,
) -> pd.DataFrame:
    """Calculate investment for a DataFrame with time series data.

    Args:
        df: DataFrame containing GDP, savings rate, and net exports data
        gdp_col: Column name for GDP data
        savings_rate_col: Column name for savings rate data
        net_exports_col: Column name for net exports data
        output_col: Column name for calculated investment
        add_components: Whether to add component columns (savings, CA)

    Returns:
        DataFrame with investment column(s) added

    Raises:
        ValueError: If required columns are missing
    """
    # Validate required columns
    required_cols = [gdp_col, savings_rate_col, net_exports_col]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        msg = f"Missing required columns: {missing_cols}"
        raise ValueError(msg)

    result_df = df.copy()

    # Calculate investment
    result_df[output_col] = calculate_investment_from_saving(
        gdp=df[gdp_col], savings_rate=df[savings_rate_col], net_exports=df[net_exports_col]
    )

    if add_components:
        result_df["domestic_savings"] = df[savings_rate_col] * df[gdp_col]
        result_df["current_account"] = -df[net_exports_col]
        result_df["investment_rate"] = result_df[output_col] / df[gdp_col]

    logger.info("Calculated investment for %d periods", len(result_df))

    return result_df


def analyze_investment_dynamics(
    gdp_series: pd.Series[float],
    savings_rate_series: pd.Series[float],
    net_exports_series: pd.Series[float],
) -> pd.DataFrame:
    """Analyze investment dynamics over time.

    Args:
        gdp_series: Time series of GDP
        savings_rate_series: Time series of savings rates
        net_exports_series: Time series of net exports

    Returns:
        DataFrame with investment analysis including:
        - investment: Total investment
        - domestic_savings: Domestic savings
        - current_account: Current account balance
        - investment_rate: Investment/GDP ratio
        - ca_gdp_ratio: Current account/GDP ratio

    Raises:
        ValueError: If series have different lengths
    """
    if len(gdp_series) != len(savings_rate_series) or len(gdp_series) != len(net_exports_series):
        msg = "All series must have the same length"
        raise ValueError(msg)

    investment, domestic_savings, current_account, _ = _calculate_series_investment(
        gdp_series, savings_rate_series, net_exports_series
    )

    analysis_df = pd.DataFrame(
        {
            "gdp": gdp_series,
            "savings_rate": savings_rate_series,
            "net_exports": net_exports_series,
            "investment": investment,
            "domestic_savings": domestic_savings,
            "current_account": current_account,
            "investment_rate": investment / gdp_series,
            "ca_gdp_ratio": current_account / gdp_series,
        }
    )

    logger.info("Analyzed investment dynamics for %d periods", len(analysis_df))

    return analysis_df
