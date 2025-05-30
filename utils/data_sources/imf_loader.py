"""TODO: Add module docstring."""

import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

# Import required modules using new import structure
from utils import find_file
from utils.path_constants import get_search_locations_relative_to_root
from utils.validation_utils import INDICATOR_VALIDATION_RULES, validate_dataframe_with_rules

logger = logging.getLogger(__name__)


def _read_metadata_file(date_file_path: Path) -> dict[str, str]:
    """Read metadata from download_date.txt file.

    Args:
        date_file_path: Path to the metadata file

    Returns:
        Dictionary of metadata key-value pairs

    Raises:
        OSError: If file cannot be read
    """
    metadata = {}
    lines = date_file_path.read_text(encoding="utf-8").splitlines()

    for raw_line in lines:
        line = raw_line.strip()
        if line and ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip()

    return metadata


def check_and_update_hash() -> bool:
    """Update download_date.txt if the IMF CSV file hash has changed.

    This function:
    - Calculates the SHA-256 hash of the IMF CSV file
    - Reads the current hash from download_date.txt
    - Updates the file with the new hash and current date if the hash has changed or
      download_date.txt doesn't exist
    - Takes no action if the hash is the same

    Returns:
        bool: True if the hash was updated, False otherwise
    """
    # Find the IMF file
    imf_filename = "dataset_DEFAULT_INTEGRATION_IMF.FAD_FM_5.0.0.csv"
    search_locations = get_search_locations_relative_to_root()
    possible_locations_relative = search_locations["input_files"]
    imf_file = find_file(imf_filename, possible_locations_relative)

    if not imf_file:
        logger.error("IMF Fiscal Monitor file not found, cannot check hash")
        return False

    # Find the download_date.txt file
    date_file = find_file("download_date.txt", possible_locations_relative)

    # Calculate the current hash of the IMF file
    imf_path = Path(imf_file)
    current_hash = hashlib.sha256(imf_path.read_bytes()).hexdigest()

    # Check if we need to update the hash
    hash_changed = True
    if date_file and Path(date_file).exists():
        # Read the current metadata
        try:
            metadata = _read_metadata_file(Path(date_file))

            # Check if the hash has changed
            if "hash" in metadata and metadata["hash"] == current_hash:
                hash_changed = False
                logger.info("IMF file hash unchanged, no need to update download_date.txt")
        except OSError:
            logger.exception("Error reading download_date.txt")

    # Update the download_date.txt file if the hash has changed
    if hash_changed:
        logger.info("IMF file hash has changed, updating download_date.txt")
        today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")

        # Create the new content
        content = f"download_date: {today}\n"
        content += f"file: {imf_filename}\n"
        content += "hash_algorithm: SHA-256\n"
        content += f"hash: {current_hash}\n"

        # Determine where to save the file
        output_path = Path(date_file) if date_file else imf_path.parent / "download_date.txt"

        # Write the new content
        try:
            output_path.write_text(content, encoding="utf-8")
            logger.info("Updated download_date.txt at %s", output_path)
        except OSError:
            logger.exception("Error updating download_date.txt")
            return False

        return True

    return False


def load_imf_tax_data() -> pd.DataFrame:
    """Load IMF Fiscal Monitor tax revenue data for China.

    This function also checks if the IMF file hash has changed and updates
    the download_date.txt file if necessary.

    Returns:
        pandas.DataFrame: DataFrame containing tax revenue data with columns 'year'
                         and 'TAX_pct_GDP'.
                         Returns an empty DataFrame if the file is not found.
    """
    # Check if the IMF file hash has changed and update download_date.txt if needed
    check_and_update_hash()

    imf_filename = "dataset_DEFAULT_INTEGRATION_IMF.FAD_FM_5.0.0.csv"
    # Get the standard input file locations
    search_locations = get_search_locations_relative_to_root()
    possible_locations_relative = search_locations["input_files"]
    imf_file = find_file(imf_filename, possible_locations_relative)

    if imf_file:
        logger.info("Found IMF Fiscal Monitor file at: %s", imf_file)
        imf_data = pd.read_csv(imf_file)
        # Filter for China annual tax revenue data
        china_filter = (
            (imf_data["COUNTRY"] == "CHN")
            & (imf_data["FREQUENCY"] == "A")
            & (imf_data["INDICATOR"] == "G1_S13_POGDP_PT")
        )
        imf_data = imf_data[china_filter]

        # Rename columns to standard format
        tax_data = imf_data[["TIME_PERIOD", "OBS_VALUE"]].rename(
            columns={"TIME_PERIOD": "year", "OBS_VALUE": "TAX_pct_GDP"}
        )
        tax_data["year"] = tax_data["year"].astype(int)
        tax_data["TAX_pct_GDP"] = pd.to_numeric(tax_data["TAX_pct_GDP"], errors="coerce")

        # Validate IMF tax data (rules are based on the final column name 'TAX_pct_GDP')
        validate_dataframe_with_rules(
            tax_data, rules=INDICATOR_VALIDATION_RULES, year_column="year"
        )
        logger.info("Successfully loaded and validated IMF tax data with %d rows.", len(tax_data))

        return tax_data

    logger.error("IMF Fiscal Monitor file not found in any of the expected locations")
    # Return an empty DataFrame with the expected columns
    return pd.DataFrame(columns=["year", "TAX_pct_GDP"])
