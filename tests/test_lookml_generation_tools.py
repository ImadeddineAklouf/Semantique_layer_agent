from pathlib import Path

from app.tools import generate_lookml_project


def generate_valid_project(
    tmp_path: Path,
    write_files: bool,
    overwrite: bool = False,
):
    """
    Exécute le pipeline avec les sources réelles.
    """

    output_root = tmp_path / "outputs"

    output_directory = (
        output_root / "lookml"
    )

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
        relationship_source_column=(
            "CLIENT_ID"
        ),
        relationship_target_column=(
            "CLIENT_ID"
        ),
        documented_cardinality=(
            "many-to-one"
        ),
        connection_name=(
            "bigquery_connection"
        ),
        default_schema="analytics",
        output_directory=str(
            output_directory
        ),
        allowed_root_directory=str(
            output_root
        ),
        write_files=write_files,
        overwrite=overwrite,
    )


def test_final_tool_generates_and_validates_in_memory(
    tmp_path: Path,
) -> None:
    result = generate_valid_project(
        tmp_path=tmp_path,
        write_files=False,
    )

    assert result["status"] == "success"

    assert (
        result["pipeline_stage"]
        == "lookml_validation"
    )

    assert (
        result["validation_report"]["valid"]
        is True
    )

    assert (
        result["validation_report"]["error_count"]
        == 0
    )

    assert result["written_files"] == []

    generated_file_names = [
        generated_file["file_name"]
        for generated_file
        in result["generation_result"]["files"]
    ]

    assert generated_file_names == [
        "clients.view.lkml",
        "orders.view.lkml",
        "sales.model.lkml",
    ]


def test_final_tool_writes_validated_files(
    tmp_path: Path,
) -> None:
    result = generate_valid_project(
        tmp_path=tmp_path,
        write_files=True,
    )

    assert result["status"] == "success"
    assert result["pipeline_stage"] == "completed"

    assert (
        result["validation_report"]["valid"]
        is True
    )

    assert len(result["written_files"]) == 3

    for file_path in result["written_files"]:
        assert Path(file_path).exists()


def test_final_tool_writes_expected_content(
    tmp_path: Path,
) -> None:
    result = generate_valid_project(
        tmp_path=tmp_path,
        write_files=True,
    )

    file_paths = {
        Path(file_path).name: Path(file_path)
        for file_path in result["written_files"]
    }

    clients_content = file_paths[
        "clients.view.lkml"
    ].read_text(
        encoding="utf-8"
    )

    orders_content = file_paths[
        "orders.view.lkml"
    ].read_text(
        encoding="utf-8"
    )

    model_content = file_paths[
        "sales.model.lkml"
    ].read_text(
        encoding="utf-8"
    )

    assert "view: clients {" in clients_content

    assert (
        "sql_table_name: analytics.CLIENTS ;;"
        in clients_content
    )

    assert "view: orders {" in orders_content

    assert (
        "measure: total_amount {"
        in orders_content
    )

    assert (
        'connection: "bigquery_connection"'
        in model_content
    )

    assert "join: clients {" in model_content


def test_final_tool_refuses_overwrite_by_default(
    tmp_path: Path,
) -> None:
    first_result = generate_valid_project(
        tmp_path=tmp_path,
        write_files=True,
    )

    assert first_result["status"] == "success"

    second_result = generate_valid_project(
        tmp_path=tmp_path,
        write_files=True,
        overwrite=False,
    )

    assert second_result["status"] == "error"

    assert (
        second_result["pipeline_stage"]
        == "lookml_writing"
    )

    assert (
        second_result["error_type"]
        == "file_exists"
    )


def test_final_tool_allows_explicit_overwrite(
    tmp_path: Path,
) -> None:
    first_result = generate_valid_project(
        tmp_path=tmp_path,
        write_files=True,
    )

    assert first_result["status"] == "success"

    second_result = generate_valid_project(
        tmp_path=tmp_path,
        write_files=True,
        overwrite=True,
    )

    assert second_result["status"] == "success"
    assert len(second_result["written_files"]) == 3


def test_final_tool_returns_missing_file_error(
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "outputs"

    result = generate_lookml_project(
        model_name="sales",
        project_name="semantic_layer_builder",
        clients_csv_path=(
            "data/inputs/missing.csv"
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
        relationship_source_column=(
            "CLIENT_ID"
        ),
        relationship_target_column=(
            "CLIENT_ID"
        ),
        documented_cardinality="many-to-one",
        connection_name="connection",
        default_schema="analytics",
        output_directory=str(
            output_root / "lookml"
        ),
        allowed_root_directory=str(
            output_root
        ),
    )

    assert result["status"] == "error"

    assert result["error_type"] == (
        "file_not_found"
    )


def test_final_tool_rejects_unsafe_output_directory(
    tmp_path: Path,
) -> None:
    allowed_root = tmp_path / "outputs"

    forbidden_directory = (
        tmp_path / "outside"
    )

    result = generate_lookml_project(
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
        relationship_source_column=(
            "CLIENT_ID"
        ),
        relationship_target_column=(
            "CLIENT_ID"
        ),
        documented_cardinality="many-to-one",
        connection_name="connection",
        default_schema="analytics",
        output_directory=str(
            forbidden_directory
        ),
        allowed_root_directory=str(
            allowed_root
        ),
        write_files=True,
    )

    assert result["status"] == "error"

    assert (
        result["error_type"]
        == "invalid_input"
    )

    assert (
        result["pipeline_stage"]
        == "pipeline_validation"
    )

def test_final_tool_returns_dictionary(
    tmp_path: Path,
) -> None:
    result = generate_valid_project(
        tmp_path=tmp_path,
        write_files=False,
    )

    assert isinstance(result, dict)

def test_preview_result_contains_analysis_reports(
    tmp_path: Path,
) -> None:
    result = generate_valid_project(
        tmp_path=tmp_path,
        write_files=False,
    )

    assert "relationship_report" in result
    assert "consistency_reports" in result

    assert result["relationship_report"] is not None

    assert (
        result["relationship_report"]
        ["overall_status"]
        == "valid"
    )

    assert (
        set(result["consistency_reports"])
        == {"clients", "orders"}
    )