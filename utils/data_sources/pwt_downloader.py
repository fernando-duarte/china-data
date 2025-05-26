import logging
import tempfile
from pathlib import Path

import pandas as pd
import requests

from utils.caching_utils import get_cached_session
from utils.validation_utils import INDICATOR_VALIDATION_RULES, validate_dataframe_with_rules

logger = logging.getLogger(__name__)


def get_pwt_data() -> pd.DataFrame:
    """Download and process Penn World Table data for China.

    Returns:
        DataFrame with PWT data for China including year, rgdpo, rkna, pl_gdpo, cgdpo, hc columns

    Raises:
        requests.exceptions.RequestException: If download fails
        Exception: If data processing fails
    """
    logger.info("Downloading Penn World Table data...")
    excel_url = "https://dataverse.nl/api/access/datafile/354095"

    # Security improvements:
    # 1. Set timeout to prevent hanging connections
    # 2. Explicitly verify SSL certificates (handled by requests-cache session defaults or requests itself)
    # 3. Use secure temporary file handling

    try:
        # Create a cached session
        session = get_cached_session()

        response = session.get(excel_url, stream=True, timeout=30)
        response.raise_for_status()

        # Use tempfile context manager with secure permissions
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False, mode="wb") as tmp:
            # Set secure file permissions (owner read/write only)
            Path(tmp.name).chmod(0o600)

            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    tmp.write(chunk)
            tmp_path = tmp.name
            logger.debug("Downloaded PWT data to temporary file: %s", tmp_path)

        # Read the Excel file
        pwt = pd.read_excel(tmp_path, sheet_name="Data")

    except requests.exceptions.RequestException:
        logger.exception("Error occurred while downloading PWT data")
        raise
    except Exception:
        logger.exception("Unexpected error occurred while processing PWT data")
        raise
    finally:
        # Ensure temporary file is deleted
        if "tmp_path" in locals() and tmp_path and Path(tmp_path).exists():
            try:
                Path(tmp_path).unlink()
                logger.debug("Deleted temporary file: %s", tmp_path)
            except OSError as e:
                logger.warning("Failed to delete temporary file %s: %s", tmp_path, str(e))

    # Filter for China and select relevant columns in one operation
    chn_data = pwt[pwt.countrycode == "CHN"][["year", "rgdpo", "rkna", "pl_gdpo", "cgdpo", "hc"]].copy()
    chn_data["year"] = chn_data["year"].astype(int)

    # Validate PWT data
    # Rules are based on original PWT column names used in INDICATOR_VALIDATION_RULES
    validate_dataframe_with_rules(chn_data, rules=INDICATOR_VALIDATION_RULES, year_column="year")
    logger.info("Successfully downloaded and validated PWT data with %d rows for China.", len(chn_data))

    return chn_data
