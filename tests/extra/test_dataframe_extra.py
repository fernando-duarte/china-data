from pathlib import Path

import pandas as pd

from utils.processor_dataframe import metadata_operations as meta
from utils.processor_dataframe import output_operations as out_ops


def test_get_projection_metadata_original():
    proc = pd.DataFrame({"year": [2020, 2021, 2022, 2023], "A": [1, 2, 3, 4]})
    orig = pd.DataFrame({"year": [2020, 2021], "A": [1, 2]})
    result = meta.get_projection_metadata(proc, None, orig, "A", "method", end_year=2023)
    assert result == {"method": "method", "years": [2022, 2023]}


def test_get_projection_metadata_projection_df():
    proc = pd.DataFrame({"year": [2020, 2021], "B": [1, 2]})
    proj = pd.DataFrame({"year": [2022, 2023], "B": [3, 4]})
    orig = pd.DataFrame({"year": [2020, 2021], "C": [5, 6]})
    result = meta.get_projection_metadata(proc, proj, orig, "B", "m2", end_year=2023)
    assert result == {"method": "m2", "years": [2022, 2023]}


def test_prepare_final_dataframe_and_save(tmp_path, monkeypatch):
    df = pd.DataFrame({"year": [2020, 2020, 2021], "val": [1, 1, 2]})
    output_columns = ["year", "val"]
    column_map = {"year": "Year", "val": "Value"}
    final_df = out_ops.prepare_output_data(df, output_columns, column_map)
    assert list(final_df.columns) == ["Year", "Value"]
    assert len(final_df) == 2

    called = {}

    def fake_markdown_table(df_, path, *args, **kwargs):
        called["path"] = path
        Path(path).write_text("ok")

    monkeypatch.setattr(out_ops, "create_markdown_table", fake_markdown_table)
    success = out_ops.save_output_files(
        final_df,
        str(tmp_path),
        "data",
        {},
        end_year=2021,
    )
    assert success
    assert (tmp_path / "data.csv").exists()
    assert (tmp_path / "data.md").exists()
