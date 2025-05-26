import logging

import pandas as pd
import pytest

from utils.error_handling import decorators


def test_handle_data_operation_return_on_error(monkeypatch):
    monkeypatch.setattr(decorators.logger, "log", lambda *a, **k: None)

    @decorators.handle_data_operation("divide", return_on_error="err")
    def divide(a, b):
        return a / b

    assert divide(4, 2) == 2
    assert divide(4, 0) == "err"


def test_handle_data_operation_reraise(monkeypatch):
    monkeypatch.setattr(decorators.logger, "log", lambda *a, **k: None)

    @decorators.handle_data_operation("boom", reraise=True)
    def boom():
        msg = "bad"
        raise ValueError(msg)

    with pytest.raises(ValueError, match="bad"):
        boom()


def test_safe_dataframe_operation_returns_df():
    @decorators.safe_dataframe_operation("process")
    def good(df):
        return df * 2

    df = pd.DataFrame({"a": [1, 2]})
    result = good(df)
    pd.testing.assert_frame_equal(result, df * 2)


def test_safe_dataframe_operation_on_error():
    @decorators.safe_dataframe_operation("process")
    def bad(df):
        msg = "fail"
        raise RuntimeError(msg)

    df = pd.DataFrame({"a": [1]})
    result = bad(df)
    assert result.empty


def test_retry_on_exception(monkeypatch):
    calls = {"n": 0}

    @decorators.retry_on_exception(max_attempts=3, delay=0)
    def flaky():
        calls["n"] += 1
        if calls["n"] < 2:
            msg = "try again"
            raise ValueError(msg)
        return "ok"

    assert flaky() == "ok"
    assert calls["n"] == 2


def test_log_execution_time(caplog):
    caplog.set_level(logging.INFO)

    @decorators.log_execution_time
    def work(x):
        return x * 2

    assert work(3) == 6
    assert any("work took" in rec.message for rec in caplog.records)
