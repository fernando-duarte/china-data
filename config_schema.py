"""Pydantic configuration schema for China Data Processing.

This module defines validated configuration schemas using Pydantic for type safety
and validation of configuration settings.
"""

from pathlib import Path

from pydantic import BaseModel, Field, field_validator


class PathConfig(BaseModel):  # type: ignore[misc]
    """Configuration for project paths."""

    project_root: Path = Field(default_factory=lambda: Path(__file__).parent)
    input_dir: Path = Field(default_factory=lambda: Path(__file__).parent / "input")
    output_dir: Path = Field(default_factory=lambda: Path(__file__).parent / "output")
    parameters_dir: Path = Field(default_factory=lambda: Path(__file__).parent / "parameters_info")

    @field_validator("input_dir", "output_dir", "parameters_dir")
    @classmethod
    def ensure_directories_exist(cls, v: Path) -> Path:
        """Ensure directories exist."""
        v.mkdir(exist_ok=True, parents=True)
        return v


class ProcessingConfig(BaseModel):  # type: ignore[misc]
    """Configuration for data processing parameters."""

    default_alpha: float = Field(default=0.33, ge=0, le=1, description="Capital share parameter")
    default_capital_output_ratio: float = Field(
        default=3.0, gt=0, description="Capital to output ratio"
    )
    default_end_year: int = Field(
        default=2050, ge=2024, le=2100, description="End year for projections"
    )
    default_depreciation_rate: float = Field(
        default=0.05, ge=0, le=1, description="Depreciation rate"
    )


class NetworkConfig(BaseModel):  # type: ignore[misc]
    """Configuration for network and retry settings."""

    max_retries: int = Field(default=3, ge=1, le=10, description="Maximum retry attempts")
    retry_delay_seconds: int = Field(default=5, ge=1, le=60, description="Delay between retries")
    request_timeout_seconds: int = Field(default=30, ge=10, le=300, description="Request timeout")
    download_delay_seconds: int = Field(
        default=1, ge=0, le=10, description="Delay between downloads"
    )


class ValidationConfig(BaseModel):  # type: ignore[misc]
    """Configuration for data validation thresholds."""

    min_data_points_for_regression: int = Field(
        default=2, ge=2, description="Min points for regression"
    )
    min_data_points_for_arima: int = Field(default=5, ge=3, description="Min points for ARIMA")
    outlier_z_score_threshold: float = Field(default=3.0, ge=2.0, description="Z-score threshold")
    negative_investment_threshold: float = Field(
        default=0.1, ge=0, le=1, description="Negative investment threshold"
    )
    min_years_for_investment_stats: int = Field(
        default=5, ge=3, description="Min years for investment stats"
    )


class GrowthRateConfig(BaseModel):  # type: ignore[misc]
    """Configuration for growth rate defaults."""

    default_growth_rate: float = Field(
        default=0.05, ge=-0.5, le=0.5, description="Default growth rate"
    )
    default_investment_growth_rate: float = Field(
        default=0.05, ge=-0.5, le=0.5, description="Investment growth rate"
    )
    default_hc_growth_rate: float = Field(
        default=0.01, ge=-0.1, le=0.1, description="Human capital growth rate"
    )


class LoggingConfig(BaseModel):  # type: ignore[misc]
    """Configuration for logging settings."""

    log_file: str = Field(default="china_data.log", description="Log file path")
    log_level: str = Field(
        default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$", description="Logging level"
    )
    log_format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    log_date_format: str = Field(default="%Y-%m-%d %H:%M:%S")
    structured_logging_enabled: bool = Field(default=True, description="Enable structured logging")
    structured_logging_json_format: bool = Field(
        default=False, description="Use JSON format for logs"
    )
    structured_logging_include_process_info: bool = Field(
        default=True, description="Include process info in logs"
    )


class CacheConfig(BaseModel):  # type: ignore[misc]
    """Configuration for caching settings."""

    cache_name: str = Field(default="china_data_cache", description="Cache database name")
    cache_backend: str = Field(default="sqlite", description="Cache backend type")
    cache_expire_after_days: int = Field(
        default=7, ge=1, le=30, description="Cache expiration in days"
    )


class ChinaDataConfig(BaseModel):  # type: ignore[misc]
    """Main configuration schema for China Data Processor."""

    # Sub-configurations
    paths: PathConfig = Field(default_factory=PathConfig)
    processing: ProcessingConfig = Field(default_factory=ProcessingConfig)
    network: NetworkConfig = Field(default_factory=NetworkConfig)
    validation: ValidationConfig = Field(default_factory=ValidationConfig)
    growth_rates: GrowthRateConfig = Field(default_factory=GrowthRateConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)

    # Data range validation
    min_year: int = Field(default=1960, ge=1900, le=2000)
    max_reasonable_year: int = Field(default=2100, ge=2050, le=2200)
    baseline_year: int = Field(default=2017, ge=2000, le=2030)
    baseline_year_range_min: int = Field(default=2010, ge=2000)
    baseline_year_range_max: int = Field(default=2020, le=2030)
    imf_projection_start_year: int = Field(default=2023, ge=2020, le=2030)

    # Data validation ranges
    population_min: int = Field(default=1000, ge=100)
    labor_force_min: int = Field(default=1000, ge=100)
    fdi_pct_gdp_min: float = Field(default=-100, le=0)
    fdi_pct_gdp_max: float = Field(default=200, ge=0)
    human_capital_min: float = Field(default=0.5, ge=0)
    human_capital_max: float = Field(default=5.0, le=10)
    tax_pct_gdp_min: float = Field(default=0, ge=0)
    tax_pct_gdp_max: float = Field(default=100, le=100)

    # Numeric precision
    decimal_places_currency: int = Field(default=2, ge=0, le=6)
    decimal_places_ratios: int = Field(default=4, ge=0, le=8)
    decimal_places_projections: int = Field(default=4, ge=0, le=8)
    decimal_places_investment: int = Field(default=2, ge=0, le=6)

    # Unit conversion
    billion_divisor: int = Field(default=1000, description="Convert millions to billions")

    # File operation parameters
    max_log_errors_displayed: int = Field(default=5, ge=1, le=100)
    file_encoding: str = Field(default="utf-8")

    # ARIMA model parameters
    default_arima_order: tuple[int, int, int] = Field(default=(1, 1, 1))

    class Config:
        """Pydantic configuration."""

        validate_assignment = True
        extra = "forbid"
