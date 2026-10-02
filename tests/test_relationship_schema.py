import pytest
from pydantic import ValidationError

from app.schemas import (
    CardinalityAnalysis,
    ReferentialIntegrityResult,
    RelationshipAnalysisReport,
    RelationshipColumnValidation,
)


def create_column_validation(
) -> RelationshipColumnValidation:
    return RelationshipColumnValidation(
        source_column_exists=True,
        target_column_exists=True,
        source_column_type="integer",
        target_column_type="integer",
        types_compatible=True,
        status="valid",
        issues=[],
    )


def create_integrity_result(
) -> ReferentialIntegrityResult:
    return ReferentialIntegrityResult(
        total_foreign_key_values=6,
        matched_foreign_key_values=6,
        orphan_value_count=0,
        orphan_values=[],
        null_foreign_key_count=0,
        match_ratio=1.0,
        status="valid",
    )


def create_cardinality_analysis(
) -> CardinalityAnalysis:
    return CardinalityAnalysis(
        documented_cardinality="many-to-one",
        detected_cardinality="many-to-one",
        source_values_unique=False,
        target_values_unique=True,
        status="valid",
        explanation=(
            "Plusieurs commandes peuvent correspondre "
            "à un client unique."
        ),
    )


def test_relationship_report_accepts_valid_data() -> None:
    report = RelationshipAnalysisReport(
        source_file="orders.csv",
        target_file="clients.csv",
        source_table="ORDERS",
        source_column="CLIENT_ID",
        target_table="CLIENTS",
        target_column="CLIENT_ID",
        column_validation=create_column_validation(),
        referential_integrity=create_integrity_result(),
        cardinality_analysis=(
            create_cardinality_analysis()
        ),
        overall_status="valid",
        relationship_score=100,
        warnings=[],
        recommendations=[],
    )

    assert report.source_table == "ORDERS"
    assert report.target_table == "CLIENTS"
    assert report.relationship_score == 100
    assert report.overall_status == "valid"


def test_integrity_result_rejects_invalid_ratio() -> None:
    with pytest.raises(ValidationError):
        ReferentialIntegrityResult(
            total_foreign_key_values=6,
            matched_foreign_key_values=6,
            orphan_value_count=0,
            orphan_values=[],
            null_foreign_key_count=0,
            match_ratio=1.2,
            status="valid",
        )


def test_relationship_report_rejects_score_over_100() -> None:
    with pytest.raises(ValidationError):
        RelationshipAnalysisReport(
            source_file="orders.csv",
            target_file="clients.csv",
            source_table="ORDERS",
            source_column="CLIENT_ID",
            target_table="CLIENTS",
            target_column="CLIENT_ID",
            column_validation=create_column_validation(),
            referential_integrity=create_integrity_result(),
            cardinality_analysis=(
                create_cardinality_analysis()
            ),
            overall_status="valid",
            relationship_score=110,
            warnings=[],
            recommendations=[],
        )


def test_cardinality_rejects_unknown_value() -> None:
    invalid_data = {
        "documented_cardinality": "one-to-several",
        "detected_cardinality": "many-to-one",
        "source_values_unique": False,
        "target_values_unique": True,
        "status": "valid",
        "explanation": "Explication.",
    }

    with pytest.raises(ValidationError):
        CardinalityAnalysis.model_validate(
            invalid_data
        )


def test_relationship_schema_rejects_extra_field() -> None:
    valid_data = {
        "source_column_exists": True,
        "target_column_exists": True,
        "source_column_type": "integer",
        "target_column_type": "integer",
        "types_compatible": True,
        "status": "valid",
        "issues": [],
        "unexpected_field": "not allowed",
    }

    with pytest.raises(ValidationError):
        RelationshipColumnValidation.model_validate(
            valid_data
        )