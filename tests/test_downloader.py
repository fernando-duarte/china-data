"""Test suite for the china_data_downloader.py functionality.

This module tests the data downloading functionality including:
- World Bank WDI data retrieval
- Penn World Table data retrieval
- Error handling for failed downloads
- Data format validation
"""

import time

import pandas as pd
import pytest
import requests
from pandas_datareader import wb

# Use updated import structure
from utils.data_sources import download_wdi_data, get_pwt_data
from utils.error_handling import DataDownloadError


class DummySession:
    """Simple session mock returning a dummy response."""

    def get(self, url, stream=True, timeout=30):
        return DummyResponse(b"dummy content")


class DummyResponse:
    def __init__(self, content):
        self.content = content
        self.raw = self

    def raise_for_status(self):
        pass

    def read(self):
        connection_failed_msg = "Connection failed"
        raise requests.exceptions.RequestException(connection_failed_msg)

    def close(self):
        pass

    def iter_content(self, chunk_size=None):
        yield self.content


def test_download_wdi_data_success(monkeypatch):
    sample = pd.DataFrame({"country": ["CN"], "year": [2020], "NY_GDP_MKTP_CD": [1.0]})

    def fake_download(country, indicator, start, end):
        return sample

    # Patch at the module level where it's actually called
    monkeypatch.setattr(wb, "download", fake_download)
    monkeypatch.setattr(time, "sleep", lambda s: None)

    # Patch WorldBankReader to return mock data
    class MockReader:
        def __init__(self, *args, **kwargs):
            self.timeout = 30

        def read(self):
            # Return data with MultiIndex like the real API
            idx = pd.MultiIndex.from_tuples([("China", 2020)], names=["country", "year"])
            return pd.DataFrame({"NY.GDP.MKTP.CD": [1.0]}, index=idx)

        def close(self):
            pass

    monkeypatch.setattr(wb, "WorldBankReader", MockReader)

    df = download_wdi_data("NY.GDP.MKTP.CD", end_year=2022)
    assert not df.empty
    assert list(df.columns) == ["country", "year", "NY_GDP_MKTP_CD"]
    assert df["country"].iloc[0] == "China"
    assert df["year"].max() <= 2022


def test_download_wdi_data_failure(monkeypatch):
    import requests

    # Patch WorldBankReader to fail
    class FailingReader:
        def __init__(self, *args, **kwargs):
            self.timeout = 30

        def read(self):
            error_msg = "Connection failed"
            raise requests.exceptions.RequestException(error_msg)

        def close(self):
            pass

    monkeypatch.setattr(wb, "WorldBankReader", FailingReader)
    monkeypatch.setattr(time, "sleep", lambda s: None)

    with pytest.raises(DataDownloadError):
        download_wdi_data("BAD")


def make_df(rows):
    return pd.DataFrame(rows)


def test_get_pwt_data_success(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "utils.data_sources.pwt_downloader.get_cached_session", lambda: DummySession()
    )
    expected = pd.DataFrame(
        {
            "countrycode": ["CHN"],
            "year": [2017],
            "rgdpo": [1],
            "rkna": [2],
            "pl_gdpo": [3],
            "cgdpo": [4],
            "hc": [5],
        }
    )
    monkeypatch.setattr(pd, "read_excel", lambda path, sheet_name="Data": expected)
    df = get_pwt_data()
    assert list(df.columns) == ["year", "rgdpo", "rkna", "pl_gdpo", "cgdpo", "hc"]
    assert df.iloc[0]["year"] == 2017


def test_get_pwt_data_error(monkeypatch):
    import requests

    class ErrorSession(DummySession):
        def get(self, url, stream=True, timeout=30):
            msg = "bad"
            raise requests.exceptions.HTTPError(msg)

    monkeypatch.setattr(
        "utils.data_sources.pwt_downloader.get_cached_session", lambda: ErrorSession()
    )
    with pytest.raises(requests.exceptions.HTTPError):
        get_pwt_data()
