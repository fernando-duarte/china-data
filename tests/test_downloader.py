"""Test suite for the china_data_downloader.py functionality.

This module tests the data downloading functionality including:
- World Bank WDI data retrieval
- Penn World Table data retrieval
- Error handling for failed downloads
- Data format validation
"""

import pandas as pd
import pytest

# Use updated import structure
from utils.data_sources import download_wdi_data, get_pwt_data
from utils.error_handling import DataDownloadError


# Create module-like objects for backward compatibility with the test code
class WdiDownloader:
    download_wdi_data = download_wdi_data
    wb = __import__("pandas_datareader", fromlist=["wb"]).wb
    time = __import__("time")


class PwtDownloader:
    get_pwt_data = get_pwt_data
    pd = __import__("pandas", fromlist=["pd"])
    requests = __import__("requests")


# Create instances for backward compatibility
wdi_downloader = WdiDownloader()
pwt_downloader = PwtDownloader()


class DummySession:
    """Simple session mock returning a dummy response."""

    def get(self, url, stream=True, timeout=30):
        return DummyResponse()


def make_df(rows):
    return pd.DataFrame(rows)


def test_download_wdi_data_success(monkeypatch):
    sample = pd.DataFrame({"country": ["CN"], "year": [2020], "NY_GDP_MKTP_CD": [1.0]})

    def fake_download(country, indicator, start, end):
        return sample

    monkeypatch.setattr(wdi_downloader.wb, "download", fake_download)
    monkeypatch.setattr(wdi_downloader.time, "sleep", lambda s: None)
    df = wdi_downloader.download_wdi_data("NY.GDP.MKTP.CD", end_year=2022)
    assert not df.empty
    assert list(df.columns) == ["country", "year", "NY_GDP_MKTP_CD"]
    assert "China" in df["country"].unique()
    assert df["year"].max() <= 2022


def test_download_wdi_data_failure(monkeypatch):
    def fail(*a, **k):
        msg = "fail"
        raise RuntimeError(msg)

    monkeypatch.setattr(wdi_downloader.wb, "download", fail)
    monkeypatch.setattr(wdi_downloader.time, "sleep", lambda s: None)
    with pytest.raises(DataDownloadError):
        wdi_downloader.download_wdi_data("BAD")


class DummyResponse:
    def __init__(self):
        self.content = b"dummy"

    def raise_for_status(self):
        pass

    def iter_content(self, chunk_size=8192):
        yield b"data"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        pass


def test_get_pwt_data_success(monkeypatch, tmp_path):
    monkeypatch.setattr("utils.data_sources.pwt_downloader.get_cached_session", lambda: DummySession())
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
    monkeypatch.setattr(pwt_downloader.pd, "read_excel", lambda path, sheet_name="Data": expected)
    df = get_pwt_data()
    assert list(df.columns) == ["year", "rgdpo", "rkna", "pl_gdpo", "cgdpo", "hc"]
    assert df.iloc[0]["year"] == 2017


def test_get_pwt_data_error(monkeypatch):
    class ErrorSession(DummySession):
        def get(self, url, stream=True, timeout=30):
            msg = "bad"
            raise pwt_downloader.requests.exceptions.HTTPError(msg)

    monkeypatch.setattr("utils.data_sources.pwt_downloader.get_cached_session", lambda: ErrorSession())
    with pytest.raises(pwt_downloader.requests.exceptions.HTTPError):
        get_pwt_data()
