from pathlib import Path

from app.tools.lookml_generation_tools import (
    generate_lookml_project,
)


def run_complete_pipeline(
    tmp_path: Path,
    write_files: bool = True,
    overwrite: bool = False,
):
    """
    Exécute tout le pipeline déterministe :

    - lecture des CSV ;
    - analyse documentaire ;
    - cohérence ;
    - relation ;
    - modèle sémantique ;
    - rendu LookML ;
    - validation locale ;
    - écriture facultative.
    """

    output_root = tmp_path / "outputs"
    output_directory = output_root / "lookml"

    return generate_lookml_project(
        model_name="sales",
        project_name="semantic_layer_builder",
        clients_csv_path=(
            "data/inputs/clients.csv"
        ),
        clients_documentation_path=(
            "data/documentation/"
            "clients_documentation.md"
        ),
        orders_csv_path=(
            "data/inputs/orders.csv"
        ),
        orders_documentation_path=(
            "data/documentation/"
            "orders_documentation.md"
        ),
        relationship_source_column="CLIENT_ID",
        relationship_target_column="CLIENT_ID",
        documented_cardinality="many-to-one",
        connection_name="bigquery_connection",
        default_schema="analytics",
        output_directory=str(output_directory),
        allowed_root_directory=str(output_root),
        write_files=write_files,
        overwrite=overwrite,
    )


def get_written_files_by_name(
    result: dict,
) -> dict[str, Path]:
    """
    Indexe les fichiers écrits par leur nom.
    """

    return {
        Path(file_path).name: Path(file_path)
        for file_path in result["written_files"]
    }


def test_complete_pipeline_returns_success(
    tmp_path: Path,
) -> None:
    result = run_complete_pipeline(tmp_path)

    assert result["status"] == "success"
    assert result["pipeline_stage"] == "completed"

    assert (
        result["message"]
        == (
            "Le projet LookML a été construit, "
            "validé et écrit avec succès."
        )
    )


def test_complete_pipeline_builds_ready_semantic_model(
    tmp_path: Path,
) -> None:
    result = run_complete_pipeline(tmp_path)

    semantic_model = result["semantic_model"]

    assert semantic_model["model_name"] == "sales"

    assert (
        semantic_model["project_name"]
        == "semantic_layer_builder"
    )

    assert (
        semantic_model["connection_name"]
        == "bigquery_connection"
    )

    assert (
        semantic_model["default_schema"]
        == "analytics"
    )

    assert semantic_model["generation_ready"] is True
    assert semantic_model["missing_information"] == []


def test_complete_pipeline_builds_two_views(
    tmp_path: Path,
) -> None:
    result = run_complete_pipeline(tmp_path)

    views = result["semantic_model"]["views"]

    view_names = [
        view["view_name"]
        for view in views
    ]

    assert view_names == [
        "clients",
        "orders",
    ]


def test_complete_pipeline_validates_primary_keys(
    tmp_path: Path,
) -> None:
    result = run_complete_pipeline(tmp_path)

    views = {
        view["view_name"]: view
        for view in result["semantic_model"]["views"]
    }

    assert (
        views["clients"]["primary_key"]
        == "CLIENT_ID"
    )

    assert (
        views["orders"]["primary_key"]
        == "ORDER_ID"
    )

    client_primary_dimensions = [
        dimension
        for dimension
        in views["clients"]["dimensions"]
        if dimension["primary_key"]
    ]

    order_primary_dimensions = [
        dimension
        for dimension
        in views["orders"]["dimensions"]
        if dimension["primary_key"]
    ]

    assert len(client_primary_dimensions) == 1
    assert len(order_primary_dimensions) == 1

    assert (
        client_primary_dimensions[0]["source_column"]
        == "CLIENT_ID"
    )

    assert (
        order_primary_dimensions[0]["source_column"]
        == "ORDER_ID"
    )


def test_complete_pipeline_validates_relationship(
    tmp_path: Path,
) -> None:
    result = run_complete_pipeline(tmp_path)

    relationship = result["relationship_report"]

    assert relationship["overall_status"] == "valid"

    assert (
        relationship["relationship_score"]
        == 100
    )

    assert (
        relationship["referential_integrity"]
        ["orphan_value_count"]
        == 0
    )

    assert (
        relationship["referential_integrity"]
        ["match_ratio"]
        == 1.0
    )

    assert (
        relationship["cardinality_analysis"]
        ["detected_cardinality"]
        == "many-to-one"
    )


def test_complete_pipeline_validates_generated_lookml(
    tmp_path: Path,
) -> None:
    result = run_complete_pipeline(tmp_path)

    validation_report = (
        result["validation_report"]
    )

    assert validation_report["valid"] is True
    assert validation_report["error_count"] == 0

    assert (
        validation_report["validated_file_count"]
        == 3
    )

    invalid_files = [
        file_result["file_name"]
        for file_result
        in validation_report["file_results"]
        if not file_result["valid"]
    ]

    assert invalid_files == []


def test_complete_pipeline_writes_three_files(
    tmp_path: Path,
) -> None:
    result = run_complete_pipeline(tmp_path)

    assert len(result["written_files"]) == 3

    written_files = get_written_files_by_name(
        result
    )

    assert set(written_files) == {
        "clients.view.lkml",
        "orders.view.lkml",
        "sales.model.lkml",
    }

    for file_path in written_files.values():
        assert file_path.exists()
        assert file_path.is_file()


def test_complete_pipeline_clients_view_content(
    tmp_path: Path,
) -> None:
    result = run_complete_pipeline(tmp_path)

    written_files = get_written_files_by_name(
        result
    )

    content = written_files[
        "clients.view.lkml"
    ].read_text(
        encoding="utf-8"
    )

    assert "view: clients {" in content

    assert (
        "sql_table_name: analytics.CLIENTS ;;"
        in content
    )

    assert "dimension: client_id {" in content
    assert "dimension: client_name {" in content
    assert "dimension: country {" in content
    assert "dimension: creation_date {" in content
    assert "dimension: is_active {" in content

    assert content.count(
        "primary_key: yes"
    ) == 1

    assert "measure: count {" in content


def test_complete_pipeline_orders_view_content(
    tmp_path: Path,
) -> None:
    result = run_complete_pipeline(tmp_path)

    written_files = get_written_files_by_name(
        result
    )

    content = written_files[
        "orders.view.lkml"
    ].read_text(
        encoding="utf-8"
    )

    assert "view: orders {" in content

    assert (
        "sql_table_name: analytics.ORDERS ;;"
        in content
    )

    assert "dimension: order_id {" in content
    assert "dimension: client_id {" in content
    assert "dimension: order_date {" in content
    assert "dimension: amount {" in content
    assert "dimension: status {" in content

    assert content.count(
        "primary_key: yes"
    ) == 1

    expected_measures = [
        "count",
        "total_amount",
        "average_amount",
        "minimum_amount",
        "maximum_amount",
    ]

    for measure_name in expected_measures:
        assert (
            f"measure: {measure_name} {{"
            in content
        )


def test_complete_pipeline_model_content(
    tmp_path: Path,
) -> None:
    result = run_complete_pipeline(tmp_path)

    written_files = get_written_files_by_name(
        result
    )

    content = written_files[
        "sales.model.lkml"
    ].read_text(
        encoding="utf-8"
    )

    assert (
        'connection: "bigquery_connection"'
        in content
    )

    assert (
        'include: "/*.view.lkml"'
        in content
    )

    assert "explore: clients {" in content
    assert "explore: orders {" in content
    assert "join: clients {" in content

    assert (
        "relationship: many_to_one"
        in content
    )

    assert (
        "sql_on: ${orders.client_id} "
        "= ${clients.client_id} ;;"
        in content
    )


def test_complete_pipeline_does_not_generate_id_measures(
    tmp_path: Path,
) -> None:
    result = run_complete_pipeline(tmp_path)

    written_files = get_written_files_by_name(
        result
    )

    orders_content = written_files[
        "orders.view.lkml"
    ].read_text(
        encoding="utf-8"
    )

    forbidden_measures = [
        "total_order_id",
        "average_order_id",
        "minimum_order_id",
        "maximum_order_id",
        "total_client_id",
        "average_client_id",
        "minimum_client_id",
        "maximum_client_id",
    ]

    for measure_name in forbidden_measures:
        assert measure_name not in orders_content


def test_complete_pipeline_preserves_sensitive_warning(
    tmp_path: Path,
) -> None:
    result = run_complete_pipeline(tmp_path)

    written_files = get_written_files_by_name(
        result
    )

    content = written_files[
        "clients.view.lkml"
    ].read_text(
        encoding="utf-8"
    )

    assert "# Sensitive field:" in content

    clients_view = next(
        view
        for view
        in result["semantic_model"]["views"]
        if view["view_name"] == "clients"
    )

    assert "CLIENT_NAME" in (
        clients_view["sensitive_fields"]
    )


def test_complete_pipeline_can_run_without_writing(
    tmp_path: Path,
) -> None:
    result = run_complete_pipeline(
        tmp_path=tmp_path,
        write_files=False,
    )

    assert result["status"] == "success"

    assert (
        result["pipeline_stage"]
        == "lookml_validation"
    )

    assert result["written_files"] == []

    assert (
        result["validation_report"]["valid"]
        is True
    )

    assert len(
        result["generation_result"]["files"]
    ) == 3