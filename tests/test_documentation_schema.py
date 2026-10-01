import pytest
from pydantic import ValidationError

from app.schemas import (
    DocumentMetadata,
    DocumentSection,
)


def test_document_section_accepts_valid_data() -> None:
    section = DocumentSection(
        title="Règles métier",
        level=2,
        content="CLIENT_ID est obligatoire.",
    )

    assert section.title == "Règles métier"
    assert section.level == 2
    assert section.content == "CLIENT_ID est obligatoire."


def test_document_section_rejects_invalid_level() -> None:
    with pytest.raises(ValidationError):
        DocumentSection(
            title="Section invalide",
            level=7,
            content="Contenu.",
        )


def test_document_metadata_accepts_valid_data() -> None:
    document = DocumentMetadata(
        file_name="clients_documentation.md",
        file_path="data/documentation/clients_documentation.md",
        document_format="markdown",
        title="Documentation métier de la table CLIENTS",
        character_count=100,
        word_count=20,
        section_count=1,
        sections=[
            {
                "title": "Présentation générale",
                "level": 2,
                "content": "Présentation de la table.",
            }
        ],
        raw_content="# Documentation",
    )

    assert document.document_format == "markdown"
    assert document.section_count == 1
    assert isinstance(
        document.sections[0],
        DocumentSection,
    )


def test_document_metadata_rejects_unknown_format() -> None:
    with pytest.raises(ValidationError):
        DocumentMetadata(
            file_name="document.pdf",
            file_path="document.pdf",
            document_format="pdf",
            title=None,
            character_count=100,
            word_count=20,
            section_count=0,
            sections=[],
            raw_content="Contenu",
        )


def test_document_metadata_rejects_extra_field() -> None:
    invalid_document = {
        "file_name": "document.md",
        "file_path": "document.md",
        "document_format": "markdown",
        "title": "Document",
        "character_count": 10,
        "word_count": 2,
        "section_count": 0,
        "sections": [],
        "raw_content": "# Document",
        "unknown_field": "not allowed",
    }

    with pytest.raises(ValidationError):
        DocumentMetadata.model_validate(
            invalid_document
        )