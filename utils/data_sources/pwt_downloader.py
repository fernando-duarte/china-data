import logging
import os
import tempfile
import requests
import pandas as pd

logger = logging.getLogger(__name__)


def get_pwt_data():
    logger.info("Downloading Penn World Table data...")
    excel_url = "https://dataverse.nl/api/access/datafile/354095"
    
    # Security improvements:
    # 1. Set timeout to prevent hanging connections
    # 2. Explicitly verify SSL certificates
    # 3. Use secure temporary file handling
    
    try:
        # Create a session with explicit SSL verification
        session = requests.Session()
        session.verify = True  # Explicitly verify SSL certificates
        
        response = session.get(excel_url, stream=True, timeout=30)
        response.raise_for_status()
        
        # Use tempfile context manager with secure permissions
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False, mode='wb') as tmp:
            # Set secure file permissions (owner read/write only)
            os.chmod(tmp.name, 0o600)
            
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    tmp.write(chunk)
            tmp_path = tmp.name
            logger.debug("Downloaded PWT data to temporary file: %s", tmp_path)
            
        # Read the Excel file
        pwt = pd.read_excel(tmp_path, sheet_name="Data")
        
    except requests.exceptions.RequestException as e:
        logger.error("Error occurred while downloading PWT data: %s", e)
        raise
    except Exception as e:
        logger.error("Unexpected error occurred while processing PWT data: %s", e)
        raise
    finally:
        # Ensure temporary file is deleted
        if 'tmp_path' in locals() and tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
                logger.debug("Deleted temporary file: %s", tmp_path)
            except Exception as e:
                logger.warning("Failed to delete temporary file %s: %s", tmp_path, e)

    chn = pwt[pwt.countrycode == "CHN"].copy()
    chn_data = chn[["year", "rgdpo", "rkna", "pl_gdpo", "cgdpo", "hc"]].copy()
    chn_data["year"] = chn_data["year"].astype(int)
    return chn_data
