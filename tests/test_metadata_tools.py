from pathlib import Path

import pandas as pd

from app.tools import analyze_csv_file


def test_analyze_csv_file_returns_success(
    tmp_path: Path,
) -> None:
    csv_path = tmp_path / "customers.csv"

    dataframe = pd.DataFrame(
        {
            "CUSTOMER_ID": [1, 2, 3],
            "CUSTOMER_NAME": [
                "Alice",
                "Bob",
                "Charlie",
            ],
            "COUNTRY": ["FR", "FR", "GB"],
        }
    )

    dataframe.to_csv(csv_path, index=False)

    result = analyze_csv_file(str(csv_path))

    assert result["status"] == "success"
    assert "metadata" in result

    metadata = result["metadata"]

    assert metadata["file_name"] == "customers.csv"
    assert metadata["table_name"] == "CUSTOMERS"
    assert metadata["row_count"] == 3
    assert metadata["column_count"] == 3
    assert len(metadata["columns"]) == 3
    assert "primary_key_analysis" in metadata


def test_analyze_csv_file_returns_file_not_found_error() -> None:
    result = analyze_csv_file(
        "data/inputs/missing.csv"
    )

    assert result["status"] == "error"
    assert result["error_type"] == "file_not_found"
    assert "message" in result


def test_analyze_csv_file_rejects_non_csv_file(
    tmp_path: Path,
) -> None:
    text_path = tmp_path / "customers.txt"

    text_path.write_text(
        "not a csv",
        encoding="utf-8",
    )

    result = analyze_csv_file(str(text_path))

    assert result["status"] == "error"
    assert result["error_type"] == "invalid_csv"

    assert (
        "Un fichier CSV est attendu"
        in result["message"]
    )


def test_analyze_csv_file_rejects_empty_csv(
    tmp_path: Path,
) -> None:
    csv_path = tmp_path / "empty.csv"
    csv_path.write_text("", encoding="utf-8")

    result = analyze_csv_file(str(csv_path))

    assert result["status"] == "error"
    assert result["error_type"] == "invalid_csv"
    assert "fichier CSV est vide" in result["message"]