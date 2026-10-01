import pytest
from pydantic import ValidationError

from app.schemas import (
    BusinessRuleValidationResult,
    ColumnConsistencyResult,
    ConsistencyReport,
    PrimaryKeyConsistencyResult,
)


def create_valid_column_result() -> ColumnConsistencyResult:
    """
    Crée un résultat de cohérence valide pour une colonne.

    Cette fonction évite de répéter les mêmes données
    dans plusieurs tests.
    """

    return ColumnConsistencyResult(
        column_name="CLIENT_ID",
        exists_in_data=True,
        exists_in_documentation=True,
        technical_type="integer",
        documented_type="identifiant",
        type_status="consistent",
        technical_nullable=False,
        documented_required=True,
        nullability_status="consistent",
        technical_unique=True,
        documented_unique=True,
        uniqueness_status="consistent",
        overall_status="consistent",
        issues=[],
        recommendations=[],
    )


def create_valid_primary_key_result(
) -> PrimaryKeyConsistencyResult:
    """
    Crée un résultat valide de comparaison
    de clé primaire.
    """

    return PrimaryKeyConsistencyResult(
        documented_primary_key="CLIENT_ID",
        technical_candidates=[
            "CLIENT_ID",
            "CLIENT_NAME",
        ],
        recommended_technical_candidate="CLIENT_ID",
        status="consistent",
        issues=[],
        recommendations=[],
    )


def create_valid_business_rule_result(
) -> BusinessRuleValidationResult:
    """
    Crée un résultat valide de validation
    d'une règle métier.
    """

    return BusinessRuleValidationResult(
        rule_id="BR-001",
        description=(
            "CLIENT_ID doit toujours être renseigné."
        ),
        related_columns=["CLIENT_ID"],
        status="consistent",
        evidence=[
            "CLIENT_ID ne contient aucune valeur nulle."
        ],
        issues=[],
    )


def create_valid_consistency_report(
) -> ConsistencyReport:
    """
    Crée un rapport global de cohérence valide.
    """

    return ConsistencyReport(
        data_source_file="clients.csv",
        documentation_source_file=(
            "clients_documentation.md"
        ),
        technical_table_name="CLIENTS",
        documented_table_name="CLIENTS",
        table_name_status="consistent",
        consistency_score=100,
        consistency_level="excellent",
        column_results=[
            create_valid_column_result(),
        ],
        primary_key_result=(
            create_valid_primary_key_result()
        ),
        business_rule_results=[
            create_valid_business_rule_result(),
        ],
        undocumented_columns=[],
        missing_data_columns=[],
        documented_relationships=1,
        warnings=[],
        recommendations=[],
    )


def test_column_consistency_result_accepts_valid_data(
) -> None:
    result = create_valid_column_result()

    assert result.column_name == "CLIENT_ID"
    assert result.exists_in_data is True

    assert (
        result.exists_in_documentation
        is True
    )

    assert result.technical_type == "integer"
    assert result.documented_type == "identifiant"
    assert result.type_status == "consistent"

    assert (
        result.nullability_status
        == "consistent"
    )

    assert (
        result.uniqueness_status
        == "consistent"
    )

    assert result.overall_status == "consistent"
    assert result.issues == []
    assert result.recommendations == []


def test_column_consistency_result_accepts_inconsistent_status(
) -> None:
    result = ColumnConsistencyResult(
        column_name="COUNTRY",
        exists_in_data=True,
        exists_in_documentation=True,
        technical_type="string",
        documented_type="integer",
        type_status="inconsistent",
        technical_nullable=True,
        documented_required=True,
        nullability_status="inconsistent",
        technical_unique=False,
        documented_unique=False,
        uniqueness_status="consistent",
        overall_status="inconsistent",
        issues=[
            "Le type technique ne correspond pas "
            "au type documenté.",
            "La colonne obligatoire contient "
            "des valeurs nulles.",
        ],
        recommendations=[
            "Vérifier les données et la documentation.",
        ],
    )

    assert result.overall_status == "inconsistent"
    assert len(result.issues) == 2
    assert len(result.recommendations) == 1


def test_column_consistency_result_accepts_not_verifiable_status(
) -> None:
    result = ColumnConsistencyResult(
        column_name="DESCRIPTION",
        exists_in_data=True,
        exists_in_documentation=False,
        technical_type="string",
        documented_type=None,
        type_status="not_verifiable",
        technical_nullable=False,
        documented_required=None,
        nullability_status="not_verifiable",
        technical_unique=False,
        documented_unique=None,
        uniqueness_status="not_verifiable",
        overall_status="warning",
        issues=[
            "La colonne n'est pas documentée.",
        ],
        recommendations=[
            "Ajouter la colonne à la documentation.",
        ],
    )

    assert result.documented_type is None

    assert (
        result.documented_required
        is None
    )

    assert (
        result.type_status
        == "not_verifiable"
    )

    assert result.overall_status == "warning"


def test_column_consistency_result_rejects_unknown_status(
) -> None:
    invalid_data = {
        "column_name": "CLIENT_ID",
        "exists_in_data": True,
        "exists_in_documentation": True,
        "technical_type": "integer",
        "documented_type": "identifiant",
        "type_status": "unknown_status",
        "technical_nullable": False,
        "documented_required": True,
        "nullability_status": "consistent",
        "technical_unique": True,
        "documented_unique": True,
        "uniqueness_status": "consistent",
        "overall_status": "consistent",
        "issues": [],
        "recommendations": [],
    }

    with pytest.raises(ValidationError):
        ColumnConsistencyResult.model_validate(
            invalid_data
        )


def test_column_consistency_result_rejects_empty_name(
) -> None:
    invalid_data = {
        "column_name": "",
        "exists_in_data": True,
        "exists_in_documentation": True,
        "technical_type": "integer",
        "documented_type": "identifiant",
        "type_status": "consistent",
        "technical_nullable": False,
        "documented_required": True,
        "nullability_status": "consistent",
        "technical_unique": True,
        "documented_unique": True,
        "uniqueness_status": "consistent",
        "overall_status": "consistent",
        "issues": [],
        "recommendations": [],
    }

    with pytest.raises(ValidationError):
        ColumnConsistencyResult.model_validate(
            invalid_data
        )


def test_column_consistency_result_rejects_extra_field(
) -> None:
    invalid_data = (
        create_valid_column_result().model_dump()
    )

    invalid_data["unknown_field"] = (
        "not allowed"
    )

    with pytest.raises(ValidationError):
        ColumnConsistencyResult.model_validate(
            invalid_data
        )


def test_primary_key_consistency_result_accepts_valid_data(
) -> None:
    result = create_valid_primary_key_result()

    assert (
        result.documented_primary_key
        == "CLIENT_ID"
    )

    assert result.status == "consistent"

    assert (
        result.recommended_technical_candidate
        == "CLIENT_ID"
    )

    assert "CLIENT_ID" in result.technical_candidates


def test_primary_key_consistency_result_accepts_missing_documentation(
) -> None:
    result = PrimaryKeyConsistencyResult(
        documented_primary_key=None,
        technical_candidates=["CLIENT_ID"],
        recommended_technical_candidate="CLIENT_ID",
        status="not_verifiable",
        issues=[
            "Aucune clé primaire métier "
            "n'est documentée."
        ],
        recommendations=[
            "Documenter la clé primaire métier."
        ],
    )

    assert result.documented_primary_key is None
    assert result.status == "not_verifiable"
    assert len(result.issues) == 1


def test_primary_key_consistency_result_rejects_invalid_status(
) -> None:
    invalid_data = {
        "documented_primary_key": "CLIENT_ID",
        "technical_candidates": ["CLIENT_ID"],
        "recommended_technical_candidate": (
            "CLIENT_ID"
        ),
        "status": "partially_correct",
        "issues": [],
        "recommendations": [],
    }

    with pytest.raises(ValidationError):
        PrimaryKeyConsistencyResult.model_validate(
            invalid_data
        )


def test_business_rule_validation_accepts_valid_data(
) -> None:
    result = create_valid_business_rule_result()

    assert result.rule_id == "BR-001"
    assert result.status == "consistent"

    assert result.related_columns == [
        "CLIENT_ID"
    ]

    assert len(result.evidence) == 1
    assert result.issues == []


def test_business_rule_validation_accepts_not_verifiable(
) -> None:
    result = BusinessRuleValidationResult(
        rule_id="BR-002",
        description=(
            "CLIENT_ID ne doit jamais être modifié."
        ),
        related_columns=["CLIENT_ID"],
        status="not_verifiable",
        evidence=[],
        issues=[
            "Un fichier CSV unique ne permet pas "
            "de vérifier l'historique des modifications."
        ],
    )

    assert result.status == "not_verifiable"
    assert result.evidence == []
    assert len(result.issues) == 1


def test_business_rule_validation_rejects_empty_rule_id(
) -> None:
    invalid_data = {
        "rule_id": "",
        "description": "Règle de test.",
        "related_columns": [],
        "status": "not_verifiable",
        "evidence": [],
        "issues": [],
    }

    with pytest.raises(ValidationError):
        BusinessRuleValidationResult.model_validate(
            invalid_data
        )


def test_business_rule_validation_rejects_empty_description(
) -> None:
    invalid_data = {
        "rule_id": "BR-001",
        "description": "",
        "related_columns": [],
        "status": "not_verifiable",
        "evidence": [],
        "issues": [],
    }

    with pytest.raises(ValidationError):
        BusinessRuleValidationResult.model_validate(
            invalid_data
        )


def test_consistency_report_accepts_valid_data(
) -> None:
    report = create_valid_consistency_report()

    assert report.data_source_file == "clients.csv"

    assert (
        report.documentation_source_file
        == "clients_documentation.md"
    )

    assert report.technical_table_name == "CLIENTS"
    assert report.documented_table_name == "CLIENTS"

    assert (
        report.table_name_status
        == "consistent"
    )

    assert report.consistency_score == 100

    assert (
        report.consistency_level
        == "excellent"
    )

    assert len(report.column_results) == 1
    assert len(report.business_rule_results) == 1
    assert report.documented_relationships == 1


def test_consistency_report_rejects_score_over_100(
) -> None:
    invalid_data = (
        create_valid_consistency_report()
        .model_dump()
    )

    invalid_data["consistency_score"] = 101

    with pytest.raises(ValidationError):
        ConsistencyReport.model_validate(
            invalid_data
        )


def test_consistency_report_rejects_negative_score(
) -> None:
    invalid_data = (
        create_valid_consistency_report()
        .model_dump()
    )

    invalid_data["consistency_score"] = -1

    with pytest.raises(ValidationError):
        ConsistencyReport.model_validate(
            invalid_data
        )


def test_consistency_report_rejects_invalid_level(
) -> None:
    invalid_data = (
        create_valid_consistency_report()
        .model_dump()
    )

    invalid_data["consistency_level"] = (
        "perfect"
    )

    with pytest.raises(ValidationError):
        ConsistencyReport.model_validate(
            invalid_data
        )


def test_consistency_report_rejects_negative_relationship_count(
) -> None:
    invalid_data = (
        create_valid_consistency_report()
        .model_dump()
    )

    invalid_data["documented_relationships"] = -1

    with pytest.raises(ValidationError):
        ConsistencyReport.model_validate(
            invalid_data
        )


def test_consistency_report_rejects_extra_field(
) -> None:
    invalid_data = (
        create_valid_consistency_report()
        .model_dump()
    )

    invalid_data["unexpected_field"] = (
        "not allowed"
    )

    with pytest.raises(ValidationError):
        ConsistencyReport.model_validate(
            invalid_data
        )


def test_consistency_report_converts_nested_dictionaries(
) -> None:
    valid_data = (
        create_valid_consistency_report()
        .model_dump()
    )

    report = ConsistencyReport.model_validate(
        valid_data
    )

    assert isinstance(
        report.column_results[0],
        ColumnConsistencyResult,
    )

    assert isinstance(
        report.primary_key_result,
        PrimaryKeyConsistencyResult,
    )

    assert isinstance(
        report.business_rule_results[0],
        BusinessRuleValidationResult,
    )