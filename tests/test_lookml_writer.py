from pathlib import Path

import pytest

from app.schemas import (
    GeneratedLookMLFile,
    LookMLGenerationResult,
)
from app.tools.lookml_writer import (
    resolve_output_directory,
    validate_lookml_file_name,
    validate_lookml_file_type,
    validate_unique_file_names,
    write_lookml_artifacts,
)


def create_generation_result(
) -> LookMLGenerationResult:
    """
    Crée un résultat de génération LookML valide.
    """

    return LookMLGenerationResult(
        model_name="sales",
        generation_status=(
            "generated_with_warnings"
        ),
        files=[
            GeneratedLookMLFile(
                file_name="clients.view.lkml",
                file_type="view",
                content=(
                    "view: clients {\n"
                    "  sql_table_name: "
                    "analytics.CLIENTS ;;\n"
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
                    "  sql_table_name: "
                    "analytics.ORDERS ;;\n"
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
                ),
                source_name="sales",
                warnings=[],
            ),
        ],
        output_directory=None,
        written_files=[],
        missing_information=[],
        warnings=[
            "Avertissement de test."
        ],
    )


def test_validate_lookml_file_name_accepts_view(
) -> None:
    assert (
        validate_lookml_file_name(
            "clients.view.lkml"
        )
        == "clients.view.lkml"
    )


def test_validate_lookml_file_name_accepts_model(
) -> None:
    assert (
        validate_lookml_file_name(
            "sales.model.lkml"
        )
        == "sales.model.lkml"
    )


@pytest.mark.parametrize(
    "file_name",
    [
        "../clients.view.lkml",
        "folder/clients.view.lkml",
        "folder\\clients.view.lkml",
        "clients.txt",
        "sales.lkml",
        "",
        "..",
    ],
)
def test_validate_lookml_file_name_rejects_invalid_names(
    file_name: str,
) -> None:
    with pytest.raises(ValueError):
        validate_lookml_file_name(
            file_name
        )


def test_validate_file_type_accepts_view() -> None:
    generated_file = GeneratedLookMLFile(
        file_name="clients.view.lkml",
        file_type="view",
        content="view: clients {\n}\n",
        source_name="clients",
        warnings=[],
    )

    validate_lookml_file_type(
        generated_file
    )


def test_validate_file_type_rejects_mismatch() -> None:
    generated_file = GeneratedLookMLFile(
        file_name="clients.model.lkml",
        file_type="view",
        content="view: clients {\n}\n",
        source_name="clients",
        warnings=[],
    )

    with pytest.raises(ValueError):
        validate_lookml_file_type(
            generated_file
        )


def test_validate_unique_file_names_rejects_duplicates(
) -> None:
    duplicated_file = GeneratedLookMLFile(
        file_name="clients.view.lkml",
        file_type="view",
        content="view: clients {\n}\n",
        source_name="clients",
        warnings=[],
    )

    with pytest.raises(ValueError):
        validate_unique_file_names(
            [
                duplicated_file,
                duplicated_file,
            ]
        )


def test_resolve_output_directory_accepts_child(
    tmp_path: Path,
) -> None:
    allowed_root = tmp_path / "outputs"

    output_directory = (
        allowed_root / "lookml"
    )

    resolved = resolve_output_directory(
        output_directory=str(
            output_directory
        ),
        allowed_root_directory=str(
            allowed_root
        ),
    )

    assert resolved == output_directory.resolve()


def test_resolve_output_directory_rejects_escape(
    tmp_path: Path,
) -> None:
    allowed_root = tmp_path / "outputs"

    forbidden_directory = (
        tmp_path / "outside"
    )

    with pytest.raises(ValueError):
        resolve_output_directory(
            output_directory=str(
                forbidden_directory
            ),
            allowed_root_directory=str(
                allowed_root
            ),
        )


def test_writer_writes_all_files(
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "outputs"
    output_directory = output_root / "lookml"

    result = write_lookml_artifacts(
        generation_result=(
            create_generation_result()
        ),
        output_directory=str(
            output_directory
        ),
        allowed_root_directory=str(
            output_root
        ),
        overwrite=False,
    )

    assert result.output_directory == str(
        output_directory.resolve()
    )

    assert len(result.written_files) == 3

    expected_files = [
        output_directory
        / "clients.view.lkml",
        output_directory
        / "orders.view.lkml",
        output_directory
        / "sales.model.lkml",
    ]

    for expected_file in expected_files:
        assert expected_file.exists()

        assert str(
            expected_file.resolve()
        ) in result.written_files


def test_writer_preserves_utf8_content(
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "outputs"
    output_directory = output_root / "lookml"

    generation_result = (
        create_generation_result()
    )

    generation_result.files[0].content = (
        '# Description: "Donnée sensible"\n'
        "view: clients {\n}\n"
    )

    write_lookml_artifacts(
        generation_result=generation_result,
        output_directory=str(
            output_directory
        ),
        allowed_root_directory=str(
            output_root
        ),
    )

    written_content = (
        output_directory
        / "clients.view.lkml"
    ).read_text(
        encoding="utf-8"
    )

    assert "Donnée sensible" in written_content


def test_writer_refuses_existing_files_by_default(
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "outputs"
    output_directory = output_root / "lookml"

    generation_result = (
        create_generation_result()
    )

    write_lookml_artifacts(
        generation_result=generation_result,
        output_directory=str(
            output_directory
        ),
        allowed_root_directory=str(
            output_root
        ),
    )

    with pytest.raises(FileExistsError):
        write_lookml_artifacts(
            generation_result=generation_result,
            output_directory=str(
                output_directory
            ),
            allowed_root_directory=str(
                output_root
            ),
        )


def test_writer_overwrites_when_authorized(
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "outputs"
    output_directory = output_root / "lookml"

    first_result = create_generation_result()

    write_lookml_artifacts(
        generation_result=first_result,
        output_directory=str(
            output_directory
        ),
        allowed_root_directory=str(
            output_root
        ),
    )

    second_result = create_generation_result()

    second_result.files[0].content = (
        "# Updated content\n"
        "view: clients {\n}\n"
    )

    written_result = write_lookml_artifacts(
        generation_result=second_result,
        output_directory=str(
            output_directory
        ),
        allowed_root_directory=str(
            output_root
        ),
        overwrite=True,
    )

    content = (
        output_directory
        / "clients.view.lkml"
    ).read_text(
        encoding="utf-8"
    )

    assert "# Updated content" in content
    assert len(written_result.written_files) == 3


def test_writer_rejects_blocked_generation(
    tmp_path: Path,
) -> None:
    blocked_result = LookMLGenerationResult(
        model_name="sales",
        generation_status="blocked",
        files=[],
        output_directory=None,
        written_files=[],
        missing_information=[
            "Connexion Looker manquante.",
        ],
        warnings=[],
    )

    with pytest.raises(
        ValueError,
        match="bloquée",
    ):
        write_lookml_artifacts(
            generation_result=blocked_result,
            output_directory=str(
                tmp_path / "lookml"
            ),
            allowed_root_directory=str(
                tmp_path
            ),
        )
    