from pathlib import Path

from app.tools import analyze_documentation_file


def test_analyze_documentation_file_returns_success(
    tmp_path: Path,
) -> None:
    document_path = tmp_path / "customers.md"

    document_path.write_text(
        """# Documentation CUSTOMERS

## Présentation

La table contient les clients.

## Clé primaire

CUSTOMER_ID est la clé primaire métier.
""",
        encoding="utf-8",
    )

    result = analyze_documentation_file(
        str(document_path)
    )

    assert result["status"] == "success"
    assert "document" in result

    document = result["document"]

    assert document["file_name"] == "customers.md"
    assert document["document_format"] == "markdown"
    assert document["title"] == (
        "Documentation CUSTOMERS"
    )

    assert document["section_count"] == 3
    assert len(document["sections"]) == 3
    assert document["character_count"] > 0
    assert document["word_count"] > 0


def test_analyze_documentation_file_returns_missing_error() -> None:
    result = analyze_documentation_file(
        "data/documentation/missing.md"
    )

    assert result["status"] == "error"
    assert result["error_type"] == "file_not_found"
    assert "message" in result


def test_analyze_documentation_file_rejects_format(
    tmp_path: Path,
) -> None:
    document_path = tmp_path / "customers.pdf"

    document_path.write_text(
        "Fake PDF content",
        encoding="utf-8",
    )

    result = analyze_documentation_file(
        str(document_path)
    )

    assert result["status"] == "error"
    assert result["error_type"] == "invalid_document"

    assert (
        "n'est pas accepté"
        in result["message"]
    )


def test_analyze_documentation_file_rejects_empty_file(
    tmp_path: Path,
) -> None:
    document_path = tmp_path / "empty.md"

    document_path.write_text(
        "",
        encoding="utf-8",
    )

    result = analyze_documentation_file(
        str(document_path)
    )

    assert result["status"] == "error"
    assert result["error_type"] == "invalid_document"

    assert (
        "Le document est vide"
        in result["message"]
    )


def test_analyze_text_document_returns_single_section(
    tmp_path: Path,
) -> None:
    document_path = tmp_path / "customers.txt"

    document_path.write_text(
        "Documentation simple de la table CUSTOMERS.",
        encoding="utf-8",
    )

    result = analyze_documentation_file(
        str(document_path)
    )

    assert result["status"] == "success"

    document = result["document"]

    assert document["document_format"] == "text"
    assert document["section_count"] == 1
    assert len(document["sections"]) == 1

    assert (
        document["sections"][0]["title"]
        == "Contenu du document"
    )