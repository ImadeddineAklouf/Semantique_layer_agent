from pathlib import Path

import pandas as pd

from app.tools import analyze_table_relationship


def test_analyze_table_relationship_returns_success() -> None:
    result = analyze_table_relationship(
        source_file_path="data/inputs/orders.csv",
        source_column="CLIENT_ID",
        target_file_path="data/inputs/clients.csv",
        target_column="CLIENT_ID",
        documented_cardinality="many-to-one",
    )

    assert result["status"] == "success"

    assert "relationship_report" in result

    report = result["relationship_report"]

    assert report["source_table"] == "ORDERS"
    assert report["source_column"] == "CLIENT_ID"
    assert report["target_table"] == "CLIENTS"
    assert report["target_column"] == "CLIENT_ID"

    assert report["overall_status"] == "valid"
    assert report["relationship_score"] == 100

    assert (
        report["column_validation"]["types_compatible"]
        is True
    )

    assert (
        report["referential_integrity"]
        ["orphan_value_count"]
        == 0
    )

    assert (
        report["referential_integrity"]["match_ratio"]
        == 1.0
    )

    assert (
        report["cardinality_analysis"]
        ["detected_cardinality"]
        == "many-to-one"
    )


def test_analyze_table_relationship_detects_orphans(
    tmp_path: Path,
) -> None:
    clients_path = tmp_path / "clients.csv"
    orders_path = tmp_path / "orders.csv"

    pd.DataFrame(
        {
            "CLIENT_ID": [1, 2, 3],
        }
    ).to_csv(
        clients_path,
        index=False,
    )

    pd.DataFrame(
        {
            "ORDER_ID": [1001, 1002, 1003],
            "CLIENT_ID": [1, 2, 999],
        }
    ).to_csv(
        orders_path,
        index=False,
    )

    result = analyze_table_relationship(
        source_file_path=str(orders_path),
        source_column="CLIENT_ID",
        target_file_path=str(clients_path),
        target_column="CLIENT_ID",
        documented_cardinality="many-to-one",
    )

    assert result["status"] == "success"

    report = result["relationship_report"]

    assert report["overall_status"] == "invalid"

    assert (
        report["referential_integrity"]
        ["orphan_value_count"]
        == 1
    )

    assert (
        report["referential_integrity"]
        ["orphan_values"]
        == ["999"]
    )


def test_analyze_table_relationship_returns_source_error(
) -> None:
    result = analyze_table_relationship(
        source_file_path="data/inputs/missing.csv",
        source_column="CLIENT_ID",
        target_file_path="data/inputs/clients.csv",
        target_column="CLIENT_ID",
        documented_cardinality="many-to-one",
    )

    assert result["status"] == "error"
    assert result["error_type"] == "file_not_found"


def test_analyze_table_relationship_returns_target_error(
) -> None:
    result = analyze_table_relationship(
        source_file_path="data/inputs/orders.csv",
        source_column="CLIENT_ID",
        target_file_path="data/inputs/missing.csv",
        target_column="CLIENT_ID",
        documented_cardinality="many-to-one",
    )

    assert result["status"] == "error"
    assert result["error_type"] == "file_not_found"


def test_analyze_table_relationship_reports_missing_column(
) -> None:
    result = analyze_table_relationship(
        source_file_path="data/inputs/orders.csv",
        source_column="UNKNOWN_ID",
        target_file_path="data/inputs/clients.csv",
        target_column="CLIENT_ID",
        documented_cardinality="many-to-one",
    )

    assert result["status"] == "success"

    report = result["relationship_report"]

    assert report["overall_status"] == "invalid"

    assert (
        report["column_validation"]
        ["source_column_exists"]
        is False
    )