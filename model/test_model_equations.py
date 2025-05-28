"""Test script for the China Growth Model equations.

This script tests all the implemented equations with sample data
to verify they work correctly.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from model.utils.consumption import calculate_consumption
from model.utils.exports import calculate_exports
from model.utils.imports import calculate_imports
from model.utils.investment_from_saving import calculate_investment_from_saving
from model.utils.tfp_growth import calculate_tfp_growth


def test_exports():
    """Test the export equation."""
    print("Testing Export Equation:")
    print("X_t = X_0 * (e_t/e_0)^ε_x * (Y*_t/Y*_0)^μ_x")

    # Test with sample data from the model
    exports = calculate_exports(
        exchange_rate=8.0,
        foreign_income=1200.0,
        x_0=19.41,  # Initial exports from model
        e_0=1.5,    # Assumed initial exchange rate
        y_star_0=1000.0,  # Initial foreign income from model
        epsilon_x=1.5,
        mu_x=1.5
    )

    print(f"  Sample calculation: {exports:.2f} billion USD")
    print()


def test_imports():
    """Test the import equation."""
    print("Testing Import Equation:")
    print("M_t = M_0 * (e_t/e_0)^ε_m * (Y_t/Y_0)^μ_m")

    # Test with sample data from the model
    imports = calculate_imports(
        exchange_rate=8.0,
        domestic_income=500.0,
        m_0=21.84,  # Initial imports from model
        e_0=1.5,    # Assumed initial exchange rate
        y_0=300.0,  # Assumed initial GDP
        epsilon_m=-1.2,
        mu_m=1.1
    )

    print(f"  Sample calculation: {imports:.2f} billion USD")
    print()


def test_tfp_growth():
    """Test the TFP growth equation."""
    print("Testing TFP Growth Equation:")
    print("A_{t+1} = A_t * (1 + g + θ * openness_t + φ * fdi_ratio_t)")

    # Test with sample data from the model
    next_tfp = calculate_tfp_growth(
        current_tfp=1.0,
        openness_ratio=0.3,
        fdi_ratio=0.05,
        g=0.02,
        theta=0.10,
        phi=0.08
    )

    print(f"  Sample calculation: {next_tfp:.4f}")
    print()


def test_consumption():
    """Test the consumption equation."""
    print("Testing Consumption Equation:")
    print("C_t = (1 - s_t) * Y_t - G_t")

    # Test with sample data
    consumption = calculate_consumption(
        gdp=1000.0,
        saving_rate=0.3,
        government_spending=200.0
    )

    print(f"  Sample calculation: {consumption:.2f} billion USD")
    print()


def test_investment_from_saving():
    """Test the investment from saving equation."""
    print("Testing Investment from Saving Equation:")
    print("I_t = s_t * Y_t - NX_t")

    # Test with sample data
    investment = calculate_investment_from_saving(
        gdp=1000.0,
        saving_rate=0.3,
        net_exports=50.0
    )

    print(f"  Sample calculation: {investment:.2f} billion USD")
    print()


def test_with_dataframe():
    """Test all equations with a sample DataFrame."""
    print("Testing with DataFrame (time series):")

    # Create sample data
    data = {
        "year": [1980, 1985, 1990],
        "exchange_rate": [1.5, 3.2, 4.8],
        "Y_star": [1000.0, 1159.27, 1343.92],
        "GDP_USD_bn": [300.0, 400.0, 500.0],
        "saving_rate": [0.25, 0.30, 0.35],
        "G_USD_bn": [26.28, 43.99, 49.28],
        "TFP": [1.0, 1.05, 1.10],
        "Openness_Ratio": [0.15, 0.20, 0.25],
        "fdi_ratio": [0.0003, 0.0054, 0.0097]
    }

    df = pd.DataFrame(data)

    # Calculate exports
    from model.utils.exports import calculate_exports_dataframe
    df = calculate_exports_dataframe(
        df,
        exchange_rate_col="exchange_rate",
        foreign_income_col="Y_star",
        x_0=19.41,
        e_0=1.5,
        y_star_0=1000.0
    )

    # Calculate imports
    from model.utils.imports import calculate_imports_dataframe
    df = calculate_imports_dataframe(
        df,
        exchange_rate_col="exchange_rate",
        domestic_income_col="GDP_USD_bn",
        m_0=21.84,
        e_0=1.5,
        y_0=300.0
    )

    # Calculate net exports
    df["NX_USD_bn"] = df["X_USD_bn"] - df["M_USD_bn"]

    # Calculate consumption
    from model.utils.consumption import calculate_consumption_dataframe
    df = calculate_consumption_dataframe(df)

    # Calculate investment
    from model.utils.investment_from_saving import calculate_investment_from_saving_dataframe
    df = calculate_investment_from_saving_dataframe(df)

    # Calculate TFP growth
    from model.utils.tfp_growth import calculate_tfp_growth_dataframe
    df = calculate_tfp_growth_dataframe(df)

    print(df[["year", "X_USD_bn", "M_USD_bn", "NX_USD_bn", "C_USD_bn", "I_USD_bn", "TFP_next"]].round(2))
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("CHINA GROWTH MODEL EQUATIONS TEST")
    print("=" * 60)
    print()

    test_exports()
    test_imports()
    test_tfp_growth()
    test_consumption()
    test_investment_from_saving()
    test_with_dataframe()

    print("All tests completed successfully!")
    print("=" * 60)
