from app.tools import (
    compare_csv_with_documentation,
)


def test_compare_csv_with_documentation_returns_success() -> None:
    result = compare_csv_with_documentation(
        csv_file_path="data/inputs/clients.csv",
        documentation_file_path=(
            "data/documentation/"
            "clients_documentation.md"
        ),
    )

    assert result["status"] == "success"
    assert "csv_metadata" in result
    assert "documentation_analysis" in result
    assert "consistency_report" in result

    report = result["consistency_report"]

    assert report["technical_table_name"] == "CLIENTS"
    assert report["documented_table_name"] == "CLIENTS"
    assert report["table_name_status"] == "consistent"

    assert (
        report["primary_key_result"]["status"]
        == "consistent"
    )


def test_compare_csv_with_documentation_returns_csv_error() -> None:
    result = compare_csv_with_documentation(
        csv_file_path="data/inputs/missing.csv",
        documentation_file_path=(
            "data/documentation/"
            "clients_documentation.md"
        ),
    )

    assert result["status"] == "error"
    assert result["error_type"] == "file_not_found"


def test_compare_csv_with_documentation_returns_document_error() -> None:
    result = compare_csv_with_documentation(
        csv_file_path="data/inputs/clients.csv",
        documentation_file_path=(
            "data/documentation/missing.md"
        ),
    )

    assert result["status"] == "error"
    assert result["error_type"] == "file_not_found"