import pandas as pd
from utils.capital import investment, projection


def test_calculate_investment_basic():
    df = pd.DataFrame({"year": [2000, 2001, 2002], "K_USD_bn": [100.0, 110.0, 121.0]})
    result = investment.calculate_investment(df, delta=0.1)
    assert "I_USD_bn" in result.columns
    assert result["I_USD_bn"].isna().sum() >= 0


def test_project_capital_stock_basic():
    df = pd.DataFrame(
        {
            "year": [2000, 2001, 2002, 2003, 2004],
            "K_USD_bn": [100.0, 110.0, 121.0, None, None],
            "I_USD_bn": [None, 10.0, 11.0, 12.0, 13.0],
        }
    )
    out = projection.project_capital_stock(df, end_year=2004, delta=0.1)
    assert "K_USD_bn" in out.columns
