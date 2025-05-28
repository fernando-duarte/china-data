"""Test script for model equations."""

import sys
from pathlib import Path

# Add the parent directory to the path to import model modules
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd


def test_exports() -> None:
    """Test the export equation."""
    print("Testing Export Equation:")
    print("X_t = X_0 * (e_t/e_0)^ε_x * (Y*_t/Y*_0)^μ_x")

    from model.utils.exports import calculate_exports

    # Test with sample data
    exchange_rate = 1.2  # Current exchange rate
    foreign_income = 1200.0  # Current foreign income
    x_0 = 19.41  # Initial exports
    e_0 = 1.5  # Initial exchange rate
    y_star_0 = 1000.0  # Initial foreign income

    exports = calculate_exports(
        exchange_rate=exchange_rate,
        foreign_income=foreign_income,
        x_0=x_0,
        e_0=e_0,
        y_star_0=y_star_0,
    )

    print(f"Exports: {exports:.2f} billion USD")
    print()


def test_imports() -> None:
    """Test the import equation."""
    print("Testing Import Equation:")
    print("M_t = M_0 * (e_t/e_0)^ε_m * (Y_t/Y_0)^μ_m")

    from model.utils.imports import calculate_imports

    # Test with sample data
    exchange_rate = 1.2  # Current exchange rate
    domestic_income = 350.0  # Current domestic income
    m_0 = 21.84  # Initial imports
    e_0 = 1.5  # Initial exchange rate
    y_0 = 300.0  # Initial domestic income

    imports = calculate_imports(
        exchange_rate=exchange_rate,
        domestic_income=domestic_income,
        m_0=m_0,
        e_0=e_0,
        y_0=y_0,
    )

    print(f"Imports: {imports:.2f} billion USD")
    print()


def test_tfp_growth() -> None:
    """Test the TFP growth equation."""
    print("Testing TFP Growth Equation:")
    print("TFP_{t+1} = TFP_t * (1 + g)")

    from model.utils.tfp_growth import calculate_tfp_growth

    # Test with sample data
    current_tfp = 1.0
    growth_rate = 0.03  # 3% growth

    next_tfp = calculate_tfp_growth(current_tfp=current_tfp, growth_rate=growth_rate)

    print(f"Next TFP: {next_tfp:.4f}")
    print()


def test_consumption() -> None:
    """Test the consumption equation."""
    print("Testing Consumption Equation:")
    print("C_t = (1 - s_t) * Y_t - G_t")

    from model.utils.consumption import calculate_consumption

    # Test with sample data
    gdp = 350.0  # GDP in billions
    saving_rate = 0.45  # 45% saving rate
    government_spending = 50.0  # Government spending

    consumption = calculate_consumption(gdp=gdp, saving_rate=saving_rate, government_spending=government_spending)

    print(f"Consumption: {consumption:.2f} billion USD")
    print()


def test_investment_from_saving() -> None:
    """Test the investment from saving equation."""
    print("Testing Investment from Saving Equation:")
    print("I_t = s_t * Y_t")

    from model.utils.investment_from_saving import calculate_investment_from_saving

    # Test with sample data
    gdp = 350.0  # GDP in billions
    saving_rate = 0.45  # 45% saving rate

    investment = calculate_investment_from_saving(gdp=gdp, saving_rate=saving_rate)

    print(f"Investment: {investment:.2f} billion USD")
    print()


def test_with_dataframe() -> None:
    """Test all equations with a sample DataFrame."""
    print("Testing with DataFrame (time series):")

    # Create sample data
    data = {
        "year": [2020, 2021, 2022, 2023, 2024],
        "GDP_USD_bn": [300.0, 320.0, 340.0, 360.0, 380.0],
        "exchange_rate": [1.5, 1.4, 1.3, 1.2, 1.1],
        "Y_star": [1000.0, 1050.0, 1100.0, 1150.0, 1200.0],
        "saving_rate": [0.45, 0.46, 0.47, 0.48, 0.49],
        "TFP": [1.0, 1.03, 1.06, 1.09, 1.12],
    }

    china_data = pd.DataFrame(data)

    # Calculate exports
    from model.utils.exports import calculate_exports_dataframe

    china_data = calculate_exports_dataframe(
        china_data, exchange_rate_col="exchange_rate", foreign_income_col="Y_star", x_0=19.41, e_0=1.5, y_star_0=1000.0
    )

    # Calculate imports
    from model.utils.imports import calculate_imports_dataframe

    china_data = calculate_imports_dataframe(
        china_data, exchange_rate_col="exchange_rate", domestic_income_col="GDP_USD_bn", m_0=21.84, e_0=1.5, y_0=300.0
    )

    # Calculate net exports
    china_data["NX_USD_bn"] = china_data["X_USD_bn"] - china_data["M_USD_bn"]

    # Calculate consumption
    from model.utils.consumption import calculate_consumption_dataframe

    china_data = calculate_consumption_dataframe(china_data)

    # Calculate investment
    from model.utils.investment_from_saving import calculate_investment_from_saving_dataframe

    china_data = calculate_investment_from_saving_dataframe(china_data)

    # Calculate TFP growth
    from model.utils.tfp_growth import calculate_tfp_growth_dataframe

    china_data = calculate_tfp_growth_dataframe(china_data)

    print(china_data[["year", "X_USD_bn", "M_USD_bn", "NX_USD_bn", "C_USD_bn", "I_USD_bn", "TFP_next"]].round(2))


if __name__ == "__main__":
    test_exports()
    test_imports()
    test_tfp_growth()
    test_consumption()
    test_investment_from_saving()
    test_with_dataframe()
