"""Configuration settings for China Data Processing.

This module centralizes all configuration settings, constants, and parameters
used throughout the China data processing pipeline.
"""

from pathlib import Path
from typing import Optional


class Config:
    """Central configuration for the China data processing pipeline."""

    # Project paths
    PROJECT_ROOT = Path(__file__).parent
    INPUT_DIR = PROJECT_ROOT / "input"
    OUTPUT_DIR = PROJECT_ROOT / "output"
    PARAMETERS_DIR = PROJECT_ROOT / "parameters_info"

    # Data processing parameters
    DEFAULT_ALPHA = 0.33
    DEFAULT_CAPITAL_OUTPUT_RATIO = 3.0
    DEFAULT_END_YEAR = 2050
    DEFAULT_DEPRECIATION_RATE = 0.05

    # Network and retry configuration
    MAX_RETRIES = 3
    RETRY_DELAY_SECONDS = 5
    REQUEST_TIMEOUT_SECONDS = 30
    DOWNLOAD_DELAY_SECONDS = 1  # Delay between WDI downloads

    # Data validation thresholds
    MIN_DATA_POINTS_FOR_REGRESSION = 2
    MIN_DATA_POINTS_FOR_ARIMA = 5
    OUTLIER_Z_SCORE_THRESHOLD = 3.0
    
    # Growth rate defaults for extrapolation
    DEFAULT_GROWTH_RATE = 0.05  # 5% default growth rate
    DEFAULT_INVESTMENT_GROWTH_RATE = 0.05  # 5% for investment estimation
    DEFAULT_HC_GROWTH_RATE = 0.01  # 1% for human capital
    
    # ARIMA model parameters
    DEFAULT_ARIMA_ORDER = (1, 1, 1)
    
    # File operation parameters
    MAX_LOG_ERRORS_DISPLAYED = 5  # Maximum parse errors to show in logs
    
    # Data range validation
    MIN_YEAR = 1960
    MAX_REASONABLE_YEAR = 2100
    
    # Numeric precision
    DECIMAL_PLACES_CURRENCY = 2  # For USD billions
    DECIMAL_PLACES_RATIOS = 4    # For TFP, ratios, etc.
    DECIMAL_PLACES_PROJECTIONS = 4  # For projected values

    # Column mappings for output
    OUTPUT_COLUMN_MAP = {
        "year": "Year",
        "GDP_USD_bn": "GDP",
        "C_USD_bn": "Consumption",
        "G_USD_bn": "Government",
        "I_USD_bn": "Investment",
        "X_USD_bn": "Exports",
        "M_USD_bn": "Imports",
        "NX_USD_bn": "Net Exports",
        "T_USD_bn": "Tax Revenue (bn USD)",
        "Openness_Ratio": "Openness Ratio",
        "S_USD_bn": "Saving (bn USD)",
        "S_priv_USD_bn": "Private Saving (bn USD)",
        "S_pub_USD_bn": "Public Saving (bn USD)",
        "Saving_Rate": "Saving Rate",
        "POP_mn": "Population",
        "LF_mn": "Labor Force",
        "K_USD_bn": "Physical Capital",
        "TFP": "TFP",
        "FDI_pct_GDP": "FDI (% of GDP)",
        "TAX_pct_GDP": "Tax Revenue (% of GDP)",
        "hc": "Human Capital",
    }

    # World Bank indicators
    WDI_INDICATORS = {
        "NY.GDP.MKTP.CD": "GDP_USD",
        "NE.CON.PRVT.CD": "C_USD",
        "NE.CON.GOVT.CD": "G_USD",
        "NE.GDI.TOTL.CD": "I_USD",
        "NE.EXP.GNFS.CD": "X_USD",
        "NE.IMP.GNFS.CD": "M_USD",
        "BX.KLT.DINV.WD.GD.ZS": "FDI_pct_GDP",
        "SP.POP.TOTL": "POP",
        "SL.TLF.TOTL.IN": "LF",
    }

    # Extrapolation methods
    EXTRAPOLATION_METHODS = {
        "GDP_USD_bn": "arima",
        "C_USD_bn": "arima",
        "G_USD_bn": "arima",
        "I_USD_bn": "arima",
        "X_USD_bn": "arima",
        "M_USD_bn": "arima",
        "FDI_pct_GDP": "average_growth_rate",
        "POP_mn": "linear_regression",
        "LF_mn": "linear_regression",
    }

    # Logging configuration
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    @classmethod
    def get_output_directory(cls) -> Path:
        """Get the output directory, creating it if necessary."""
        cls.OUTPUT_DIR.mkdir(exist_ok=True)
        return cls.OUTPUT_DIR

    @classmethod
    def get_input_file_path(cls, filename: str) -> Optional[Path]:
        """Get the full path for an input file."""
        path = cls.INPUT_DIR / filename
        return path if path.exists() else None
