from app.tools import analyze_csv_file


def test_clients_fixture_returns_expected_metadata() -> None:
    result = analyze_csv_file(
        "data/inputs/clients.csv"
    )

    assert result["status"] == "success"

    metadata = result["metadata"]

    assert metadata["file_name"] == "clients.csv"
    assert metadata["table_name"] == "CLIENTS"
    assert metadata["row_count"] == 4
    assert metadata["column_count"] == 5

    column_names = [
        column["name"]
        for column in metadata["columns"]
    ]

    assert column_names == [
        "CLIENT_ID",
        "CLIENT_NAME",
        "COUNTRY",
        "CREATION_DATE",
        "IS_ACTIVE",
    ]

    semantic_types = {
        column["name"]: column["semantic_type"]
        for column in metadata["columns"]
    }

    assert semantic_types == {
        "CLIENT_ID": "integer",
        "CLIENT_NAME": "string",
        "COUNTRY": "string",
        "CREATION_DATE": "date",
        "IS_ACTIVE": "boolean",
    }

    quality_report = metadata["quality_report"]

    assert quality_report["quality_score"] == 95
    assert quality_report["quality_level"] == "excellent"
    assert quality_report["total_null_values"] == 0
    assert quality_report["duplicate_row_count"] == 0