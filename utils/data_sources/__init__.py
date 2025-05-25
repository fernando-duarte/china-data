"""
Data source modules for downloading and loading economic data.

This package contains modules for downloading and loading data from various sources:
- World Development Indicators (WDI) from the World Bank
- Penn World Table (PWT)
- International Monetary Fund (IMF) Fiscal Monitor
"""

from utils.data_sources.imf_loader import load_imf_tax_data
from utils.data_sources.pwt_downloader import get_pwt_data

# Import data source modules using new import structure
from utils.data_sources.wdi_downloader import download_wdi_data

__all__ = ["download_wdi_data", "get_pwt_data", "load_imf_tax_data"]
