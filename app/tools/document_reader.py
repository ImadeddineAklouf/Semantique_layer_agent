import re
from pathlib import Path

from app.schemas import (
    DocumentFormat,
    DocumentMetadata,
    DocumentSection,
)


SUPPORTED_DOCUMENT_EXTENSIONS = {
    ".md": "markdown",
    ".txt": "text",
}


def detect_document_format(
    path: Path,
) -> DocumentFormat:
    """
    Détermine le format du document à partir de son extension.

    Args:
        path: chemin du document.

    Returns:
        Le format documentaire correspondant.

    Raises:
        ValueError: si le format n'est pas accepté.
    """

    extension = path.suffix.lower()

    document_format = SUPPORTED_DOCUMENT_EXTENSIONS.get(
        extension
    )

    if document_format is None:
        supported_formats = ", ".join(
            sorted(SUPPORTED_DOCUMENT_EXTENSIONS)
        )

        raise ValueError(
            f"Le format '{extension}' n'est pas accepté. "
            f"Formats autorisés : {supported_formats}."
        )

    return document_format


def read_document_content(
    path: Path,
) -> str:
    """
    Lit le contenu textuel d'un document en UTF-8.

    Args:
        path: chemin du document à lire.

    Returns:
        Le contenu textuel complet.

    Raises:
        ValueError: si le document ne peut pas être décodé
        ou si son contenu est vide.
    """

    try:
        content = path.read_text(
            encoding="utf-8",
        )

    except UnicodeDecodeError as error:
        raise ValueError(
            "Le document ne peut pas être lu en UTF-8 : "
            f"{path}"
        ) from error

    if not content.strip():
        raise ValueError(
            f"Le document est vide : {path}"
        )

    return content


def count_words(content: str) -> int:
    """
    Compte approximativement les mots dans un texte.

    Les mots peuvent contenir des lettres, des chiffres,
    des apostrophes et des traits d'union.
    """

    words = re.findall(
        r"\b[\wÀ-ÖØ-öø-ÿ'-]+\b",
        content,
        flags=re.UNICODE,
    )

    return len(words)


def extract_markdown_sections(
    content: str,
) -> list:
    """
    Extrait les sections d'un document Markdown.

    Une section commence par un titre Markdown compris
    entre le niveau 1 et le niveau 6.

    Args:
        content: contenu Markdown complet.

    Returns:
        La liste ordonnée des sections détectées.
    """

    heading_pattern = re.compile(
        r"^(#{1,6})\s+(.+?)\s*$"
    )

    sections: list[DocumentSection] = []

    current_title: str | None = None
    current_level: int | None = None
    current_content_lines: list[str] = []

    for line in content.splitlines():
        heading_match = heading_pattern.match(line)

        if heading_match:
            if (
                current_title is not None
                and current_level is not None
            ):
                sections.append(
                    DocumentSection(
                        title=current_title,
                        level=current_level,
                        content="\n".join(
                            current_content_lines
                        ).strip(),
                    )
                )

            heading_marks = heading_match.group(1)
            heading_title = heading_match.group(2)

            current_level = len(heading_marks)
            current_title = heading_title.strip()
            current_content_lines = []

        elif current_title is not None:
            current_content_lines.append(line)

    if (
        current_title is not None
        and current_level is not None
    ):
        sections.append(
            DocumentSection(
                title=current_title,
                level=current_level,
                content="\n".join(
                    current_content_lines
                ).strip(),
            )
        )

    return sections


def extract_text_sections(
    content: str,
) -> list:
    """
    Crée une section unique pour un document texte simple.

    Un fichier TXT ne possède pas nécessairement une
    hiérarchie explicite comme un fichier Markdown.
    """

    return [
        DocumentSection(
            title="Contenu du document",
            level=1,
            content=content.strip(),
        )
    ]


def detect_document_title(
    sections: list[DocumentSection],
    fallback_title: str,
) -> str:
    """
    Détermine le titre principal du document.

    La première section de niveau 1 est prioritaire.
    Si aucun titre de niveau 1 n'existe, le nom du fichier
    sans extension est utilisé.
    """

    for section in sections:
        if section.level == 1:
            return section.title

    return fallback_title


def read_document(
    file_path: str,
) -> DocumentMetadata:
    """
    Lit un document Markdown ou TXT et retourne
    ses métadonnées structurées.

    Args:
        file_path: chemin vers le document.

    Returns:
        Un objet DocumentMetadata validé par Pydantic.

    Raises:
        FileNotFoundError: si le document n'existe pas.
        ValueError: si le chemin n'est pas un fichier,
        si le format n'est pas accepté ou si le document
        est vide.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Le document n'existe pas : {path}"
        )

    if not path.is_file():
        raise ValueError(
            "Le chemin ne correspond pas à un fichier : "
            f"{path}"
        )

    document_format = detect_document_format(path)

    content = read_document_content(path)

    if document_format == "markdown":
        sections = extract_markdown_sections(content)
    else:
        sections = extract_text_sections(content)

    title = detect_document_title(
        sections=sections,
        fallback_title=path.stem,
    )

    return DocumentMetadata(
        file_name=path.name,
        file_path=str(path.resolve()),
        document_format=document_format,
        title=title,
        character_count=len(content),
        word_count=count_words(content),
        section_count=len(sections),
        sections=sections,
        raw_content=content,
    )