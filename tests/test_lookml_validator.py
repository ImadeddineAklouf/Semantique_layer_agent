import pytest

from app.schemas import (
    GeneratedLookMLFile,
    LookMLGenerationResult,
)
from app.tools.lookml_validator import (
    extract_field_references,
    extract_object_names,
    validate_lookml_artifacts,
)


def create_valid_generation(
) -> LookMLGenerationResult:
    return LookMLGenerationResult(
        model_name="sales",
        generation_status="generated",
        files=[
            GeneratedLookMLFile(
                file_name="clients.view.lkml",
                file_type="view",
                content=(
                    "view: clients {\n"
                    "  sql_table_name: analytics.CLIENTS ;;\n"
                    "  dimension: client_id {\n"
                    "    type: number\n"
                    "    primary_key: yes\n"
                    "    sql: ${TABLE}.CLIENT_ID ;;\n"
                    "  }\n"
                    "  measure: count {\n"
                    "    type: count\n"
                    "  }\n"
                    "}\n"
                ),
                source_name="clients",
                warnings=[],
            ),
            GeneratedLookMLFile(
                file_name="orders.view.lkml",
                file_type="view",
                content=(
                    "view: orders {\n"
                    "  sql_table_name: analytics.ORDERS ;;\n"
                    "  dimension: order_id {\n"
                    "    type: number\n"
                    "    primary_key: yes\n"
                    "    sql: ${TABLE}.ORDER_ID ;;\n"
                    "  }\n"
                    "  dimension: client_id {\n"
                    "    type: number\n"
                    "    sql: ${TABLE}.CLIENT_ID ;;\n"
                    "  }\n"
                    "}\n"
                ),
                source_name="orders",
                warnings=[],
            ),
            GeneratedLookMLFile(
                file_name="sales.model.lkml",
                file_type="model",
                content=(
                    'connection: "connection"\n'
                    'include: "/*.view.lkml"\n'
                    "explore: clients {\n"
                    "}\n"
                    "explore: orders {\n"
                    "  join: clients {\n"
                    "    type: left_outer\n"
                    "    relationship: many_to_one\n"
                    "    sql_on: ${orders.client_id} = "
                    "${clients.client_id} ;;\n"
                    "  }\n"
                    "}\n"
                ),
                source_name="sales",
                warnings=[],
            ),
        ],
        output_directory=None,
        written_files=[],
        missing_information=[],
        warnings=[],
    )


def test_extract_object_names() -> None:
    content = (
        "dimension: client_id {\n}\n"
        "dimension: client_name {\n}\n"
    )

    assert extract_object_names(
        content,
        "dimension",
    ) == [
        "client_id",
        "client_name",
    ]


def test_extract_field_references() -> None:
    references = extract_field_references(
        "sql: ${orders.client_id} "
        "= ${clients.client_id} ;;"
    )

    assert references == [
        "orders.client_id",
        "clients.client_id",
    ]


def test_validate_valid_generation() -> None:
    report = validate_lookml_artifacts(
        create_valid_generation()
    )

    assert report.valid is True
    assert report.error_count == 0

    assert (
        report.validated_file_count
        == 3
    )


def test_validator_detects_unbalanced_braces() -> None:
    generation = create_valid_generation()

    generation.files[0].content = (
        "view: clients {\n"
    )

    report = validate_lookml_artifacts(
        generation
    )

    issue_codes = {
        issue.code
        for issue in report.issues
    }

    assert report.valid is False

    assert (
        "UNBALANCED_BRACES"
        in issue_codes
    )


def test_validator_detects_missing_primary_key(
) -> None:
    generation = create_valid_generation()

    generation.files[0].content = (
        generation.files[0].content.replace(
            "primary_key: yes\n",
            "",
        )
    )

    report = validate_lookml_artifacts(
        generation
    )

    issue_codes = {
        issue.code
        for issue in report.issues
    }

    assert "MISSING_PRIMARY_KEY" in issue_codes
    assert report.warning_count >= 1


def test_validator_detects_unknown_join_view(
) -> None:
    generation = create_valid_generation()

    generation.files[2].content = (
        generation.files[2].content.replace(
            "join: clients",
            "join: unknown_view",
        )
    )

    report = validate_lookml_artifacts(
        generation
    )

    issue_codes = {
        issue.code
        for issue in report.issues
    }

    assert report.valid is False

    assert (
        "UNKNOWN_JOIN_VIEW"
        in issue_codes
    )


def test_validator_rejects_blocked_generation(
) -> None:
    blocked_result = LookMLGenerationResult(
        model_name="sales",
        generation_status="blocked",
        files=[],
        output_directory=None,
        written_files=[],
        missing_information=[
            "Connexion manquante.",
        ],
        warnings=[],
    )

    with pytest.raises(ValueError):
        validate_lookml_artifacts(
            blocked_result
        )