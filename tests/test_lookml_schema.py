import pytest
from pydantic import ValidationError

from app.schemas import (
    GeneratedLookMLFile,
    LookMLGenerationResult,
)


def create_view_file() -> GeneratedLookMLFile:
    """
    Crée un fichier LookML de vue valide
    réutilisable dans les tests.
    """

    return GeneratedLookMLFile(
        file_name="clients.view.lkml",
        file_type="view",
        content=(
            "view: clients {\n"
            "  sql_table_name: analytics.CLIENTS ;;\n"
            "}\n"
        ),
        source_name="clients",
        warnings=[],
    )


def create_model_file() -> GeneratedLookMLFile:
    """
    Crée un fichier LookML de modèle valide.
    """

    return GeneratedLookMLFile(
        file_name="sales.model.lkml",
        file_type="model",
        content=(
            'connection: "bigquery_connection"\n\n'
            'include: "/*.view.lkml"\n\n'
            "explore: clients {\n"
            "}\n"
        ),
        source_name="sales",
        warnings=[],
    )


def test_generated_lookml_view_file_accepts_valid_data(
) -> None:
    generated_file = create_view_file()

    assert (
        generated_file.file_name
        == "clients.view.lkml"
    )

    assert generated_file.file_type == "view"
    assert generated_file.source_name == "clients"
    assert "view: clients" in generated_file.content
    assert generated_file.warnings == []


def test_generated_lookml_model_file_accepts_valid_data(
) -> None:
    generated_file = create_model_file()

    assert (
        generated_file.file_name
        == "sales.model.lkml"
    )

    assert generated_file.file_type == "model"
    assert generated_file.source_name == "sales"

    assert (
        'connection: "bigquery_connection"'
        in generated_file.content
    )


def test_generated_lookml_file_accepts_warnings(
) -> None:
    generated_file = GeneratedLookMLFile(
        file_name="orders.view.lkml",
        file_type="view",
        content="view: orders {\n}\n",
        source_name="orders",
        warnings=[
            "Mesures générées automatiquement.",
        ],
    )

    assert len(generated_file.warnings) == 1

    assert (
        generated_file.warnings[0]
        == "Mesures générées automatiquement."
    )


def test_generated_lookml_file_rejects_unknown_type(
) -> None:
    invalid_data = create_view_file().model_dump()

    invalid_data["file_type"] = "explore"

    with pytest.raises(ValidationError):
        GeneratedLookMLFile.model_validate(
            invalid_data
        )


def test_generated_lookml_file_rejects_empty_name(
) -> None:
    invalid_data = create_view_file().model_dump()

    invalid_data["file_name"] = ""

    with pytest.raises(ValidationError):
        GeneratedLookMLFile.model_validate(
            invalid_data
        )


def test_generated_lookml_file_rejects_empty_content(
) -> None:
    invalid_data = create_view_file().model_dump()

    invalid_data["content"] = ""

    with pytest.raises(ValidationError):
        GeneratedLookMLFile.model_validate(
            invalid_data
        )


def test_generated_lookml_file_rejects_empty_source_name(
) -> None:
    invalid_data = create_view_file().model_dump()

    invalid_data["source_name"] = ""

    with pytest.raises(ValidationError):
        GeneratedLookMLFile.model_validate(
            invalid_data
        )


def test_generated_lookml_file_rejects_extra_field(
) -> None:
    invalid_data = create_view_file().model_dump()

    invalid_data["unknown_field"] = (
        "not allowed"
    )

    with pytest.raises(ValidationError):
        GeneratedLookMLFile.model_validate(
            invalid_data
        )


def test_generation_result_accepts_generated_files(
) -> None:
    result = LookMLGenerationResult(
        model_name="sales",
        generation_status="generated",
        files=[
            create_view_file(),
            create_model_file(),
        ],
        output_directory="data/outputs",
        written_files=[
            "data/outputs/clients.view.lkml",
            "data/outputs/sales.model.lkml",
        ],
        missing_information=[],
        warnings=[],
    )

    assert result.model_name == "sales"

    assert (
        result.generation_status
        == "generated"
    )

    assert len(result.files) == 2
    assert len(result.written_files) == 2

    assert (
        result.output_directory
        == "data/outputs"
    )

    assert result.missing_information == []


def test_generation_result_accepts_generated_with_warnings(
) -> None:
    result = LookMLGenerationResult(
        model_name="sales",
        generation_status=(
            "generated_with_warnings"
        ),
        files=[
            create_view_file(),
        ],
        output_directory=None,
        written_files=[],
        missing_information=[],
        warnings=[
            "CLIENT_NAME est sensible.",
        ],
    )

    assert (
        result.generation_status
        == "generated_with_warnings"
    )

    assert len(result.warnings) == 1
    assert len(result.files) == 1


def test_generation_result_accepts_blocked_status(
) -> None:
    result = LookMLGenerationResult(
        model_name="sales",
        generation_status="blocked",
        files=[],
        output_directory=None,
        written_files=[],
        missing_information=[
            "Nom de la connexion Looker.",
            "Nom du schéma physique.",
        ],
        warnings=[],
    )

    assert result.generation_status == "blocked"
    assert result.files == []

    assert len(
        result.missing_information
    ) == 2


def test_generation_result_rejects_unknown_status(
) -> None:
    invalid_data = {
        "model_name": "sales",
        "generation_status": "partially_generated",
        "files": [],
        "output_directory": None,
        "written_files": [],
        "missing_information": [],
        "warnings": [],
    }

    with pytest.raises(ValidationError):
        LookMLGenerationResult.model_validate(
            invalid_data
        )


def test_generation_result_rejects_empty_model_name(
) -> None:
    invalid_data = {
        "model_name": "",
        "generation_status": "blocked",
        "files": [],
        "output_directory": None,
        "written_files": [],
        "missing_information": [],
        "warnings": [],
    }

    with pytest.raises(ValidationError):
        LookMLGenerationResult.model_validate(
            invalid_data
        )


def test_generation_result_converts_nested_files(
) -> None:
    result_data = {
        "model_name": "sales",
        "generation_status": "generated",
        "files": [
            create_view_file().model_dump(),
            create_model_file().model_dump(),
        ],
        "output_directory": None,
        "written_files": [],
        "missing_information": [],
        "warnings": [],
    }

    result = LookMLGenerationResult.model_validate(
        result_data
    )

    assert isinstance(
        result.files[0],
        GeneratedLookMLFile,
    )

    assert isinstance(
        result.files[1],
        GeneratedLookMLFile,
    )


def test_generation_result_rejects_extra_field(
) -> None:
    invalid_data = {
        "model_name": "sales",
        "generation_status": "generated",
        "files": [],
        "output_directory": None,
        "written_files": [],
        "missing_information": [],
        "warnings": [],
        "unknown_field": "not allowed",
    }

    with pytest.raises(ValidationError):
        LookMLGenerationResult.model_validate(
            invalid_data
        )
        