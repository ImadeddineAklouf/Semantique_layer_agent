import pytest
from pydantic import ValidationError

from app.schemas import (
    ColumnMetadata,
    DataQualityReport,
    PrimaryKeyCandidate,
    TableMetadata,
)


def create_valid_column() -> ColumnMetadata:
    return ColumnMetadata(
        name="CUSTOMER_ID",
        pandas_type="int64",
        semantic_type="integer",
        nullable=False,
        null_count=0,
        unique_count=3,
        sample_values=[1, 2, 3],
    )


def test_column_metadata_accepts_valid_data() -> None:
    column = create_valid_column()

    assert column.name == "CUSTOMER_ID"
    assert column.semantic_type == "integer"
    assert column.null_count == 0


def test_column_metadata_rejects_invalid_semantic_type() -> None:
    with pytest.raises(ValidationError):
        ColumnMetadata(
            name="CUSTOMER_ID",
            pandas_type="int64",
            semantic_type="number",  # type: ignore[arg-type]
            nullable=False,
            null_count=0,
            unique_count=3,
            sample_values=[1, 2, 3],
        )


def test_column_metadata_rejects_negative_null_count() -> None:
    with pytest.raises(ValidationError):
        ColumnMetadata(
            name="CUSTOMER_ID",
            pandas_type="int64",
            semantic_type="integer",
            nullable=False,
            null_count=-1,
            unique_count=3,
            sample_values=[1, 2, 3],
        )


def test_column_metadata_rejects_more_than_three_samples() -> None:
    with pytest.raises(ValidationError):
        ColumnMetadata(
            name="CUSTOMER_ID",
            pandas_type="int64",
            semantic_type="integer",
            nullable=False,
            null_count=0,
            unique_count=4,
            sample_values=[1, 2, 3, 4],
        )


def test_primary_key_candidate_rejects_score_over_100() -> None:
    with pytest.raises(ValidationError):
        PrimaryKeyCandidate(
            column_name="CUSTOMER_ID",
            score=110,
            confidence="high",
            reasons=[],
            warnings=[],
            recommended=True,
        )


def test_table_metadata_converts_nested_column_dictionary() -> None:
    table = TableMetadata(
        file_name="customers.csv",
        table_name="CUSTOMERS",
        file_path="customers.csv",
        row_count=3,
        column_count=1,
        primary_key_candidates=["CUSTOMER_ID"],
        primary_key_analysis=[],
        quality_report=create_valid_quality_report(),
        columns=[
            {
                "name": "CUSTOMER_ID",
                "pandas_type": "int64",
                "semantic_type": "integer",
                "nullable": False,
                "null_count": 0,
                "unique_count": 3,
                "sample_values": [1, 2, 3],
            }
        ],
    )

    assert isinstance(table.columns[0], ColumnMetadata)
    assert table.columns[0].name == "CUSTOMER_ID"


def test_table_metadata_rejects_inconsistent_column_count() -> None:
    with pytest.raises(
        ValidationError,
        match="column_count",
    ):
        TableMetadata(
            file_name="customers.csv",
            table_name="CUSTOMERS",
            file_path="customers.csv",
            row_count=3,
            column_count=2,
            primary_key_candidates=["CUSTOMER_ID"],
            primary_key_analysis=[],
            quality_report=create_valid_quality_report(),
            columns=[create_valid_column()],
        )


def test_table_metadata_rejects_unknown_key_candidate() -> None:
    with pytest.raises(
        ValidationError,
        match="aucune colonne",
    ):
        TableMetadata(
            file_name="customers.csv",
            table_name="CUSTOMERS",
            file_path="customers.csv",
            row_count=3,
            column_count=1,
            primary_key_candidates=["UNKNOWN_ID"],
            primary_key_analysis=[],
            quality_report=create_valid_quality_report(),
            columns=[create_valid_column()],
        )


def test_table_metadata_rejects_unknown_field() -> None:
    valid_table = {
        "file_name": "customers.csv",
        "table_name": "CUSTOMERS",
        "file_path": "customers.csv",
        "row_count": 3,
        "column_count": 1,
        "primary_key_candidates": ["CUSTOMER_ID"],
        "primary_key_analysis": [],
        "columns": [create_valid_column()],
        "unexpected_field": "not allowed",
    }

    with pytest.raises(ValidationError):
        TableMetadata.model_validate(valid_table)

def create_valid_quality_report() -> DataQualityReport:
    return DataQualityReport(
        quality_score=100,
        quality_level="excellent",
        total_null_values=0,
        duplicate_row_count=0,
        duplicate_row_ratio=0.0,
        constant_columns=[],
        high_null_columns=[],
        warnings=[],
        recommendations=[],
    )