import logging
import os
import tempfile

import pandas as pd
import requests

from utils.caching_utils import get_cached_session
from utils.validation_utils import validate_dataframe_with_rules, INDICATOR_VALIDATION_RULES

logger = logging.getLogger(__name__)


def get_pwt_data() -> pd.DataFrame:
    logger.info("Downloading Penn World Table data...")
    excel_url = "https://dataverse.nl/api/access/datafile/354095"

    # Security improvements:
    # 1. Set timeout to prevent hanging connections
    # 2. Explicitly verify SSL certificates (handled by requests-cache session defaults or requests itself)
    # 3. Use secure temporary file handling

    try:
        # Create a cached session
        session = get_cached_session()
        # session.verify = True # requests-cache session should handle this or requests default is True

        response = session.get(excel_url, stream=True, timeout=30)
        response.raise_for_status()

        # Use tempfile context manager with secure permissions
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False, mode="wb") as tmp:
            # Set secure file permissions (owner read/write only)
            os.chmod(tmp.name, 0o600)

            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    tmp.write(chunk)
            tmp_path = tmp.name
            logger.debug(f"Downloaded PWT data to temporary file: {tmp_path}")

        # Read the Excel file
        pwt = pd.read_excel(tmp_path, sheet_name="Data")

    except requests.exceptions.RequestException as e:
        logger.error(f"Error occurred while downloading PWT data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error occurred while processing PWT data: {e}")
        raise
    finally:
        # Ensure temporary file is deleted
        if "tmp_path" in locals() and tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
                logger.debug(f"Deleted temporary file: {tmp_path}")
            except Exception as e:
                logger.warning(f"Failed to delete temporary file {tmp_path}: {e}")

    # Filter for China and select relevant columns in one operation
    chn_data = pwt[pwt.countrycode == "CHN"][["year", "rgdpo", "rkna", "pl_gdpo", "cgdpo", "hc"]].copy()
    chn_data["year"] = chn_data["year"].astype(int)
    
    # Validate PWT data
    # Rules are based on original PWT column names used in INDICATOR_VALIDATION_RULES
    validate_dataframe_with_rules(chn_data, rules=INDICATOR_VALIDATION_RULES, year_column='year')
    logger.info(f"Successfully downloaded and validated PWT data with {len(chn_data)} rows for China.")

    return chn_data
