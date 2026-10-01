import re

from app.schemas import (
    BusinessDocumentationAnalysis,
    BusinessRule,
    DocumentedColumn,
    DocumentedRelationship,
    DocumentMetadata,
    SensitiveDataItem,
)


def parse_yes_no_value(
    value: str,
) -> bool | None:
    """
    Convertit une valeur textuelle oui/non en booléen.
    """

    normalized_value = value.strip().lower().rstrip(".")

    if normalized_value in {
        "oui",
        "true",
        "yes",
    }:
        return True

    if normalized_value in {
        "non",
        "false",
        "no",
    }:
        return False

    return None


def clean_markdown_list_item(
    line: str,
) -> str:
    """
    Retire les marqueurs de listes Markdown.
    """

    cleaned_line = re.sub(
        r"^\s*(?:[-*+]|\d+[.)])\s+",
        "",
        line,
    )

    return cleaned_line.strip()


def extract_table_name(
    document: DocumentMetadata,
) -> str | None:
    """
    Extrait le nom de la table depuis le titre principal.
    """

    if not document.title:
        return None

    match = re.search(
        r"\btable\s+([A-Za-z0-9_]+)\b",
        document.title,
        flags=re.IGNORECASE,
    )

    if match:
        return match.group(1).upper()

    return None


def extract_general_information(
    document: DocumentMetadata,
) -> tuple[str | None, str | None]:
    """
    Extrait la description générale et la fréquence
    de mise à jour du document.
    """

    table_description: str | None = None
    update_frequency: str | None = None

    for section in document.sections:
        if section.title.lower() != "présentation générale":
            continue

        content = section.content.strip()

        if content:
            table_description = content

        update_match = re.search(
            r"mise à jour\s+(.+?)(?:\.|\n|$)",
            content,
            flags=re.IGNORECASE,
        )

        if update_match:
            update_frequency = (
                update_match.group(1).strip()
            )

    return table_description, update_frequency


def extract_documented_primary_key(
    document: DocumentMetadata,
) -> str | None:
    """
    Extrait la clé primaire explicitement déclarée
    dans la section intitulée "Clé primaire".

    Args:
        document: document structuré à analyser.

    Returns:
        Le nom normalisé de la colonne documentée
        comme clé primaire, ou None si aucune preuve
        explicite n'est trouvée.
    """

    primary_key_patterns = [
        re.compile(
            r"\bcolonne\s+([A-Z][A-Z0-9_]*)\s+"
            r"(?:constitue|est|représente)\s+"
            r"(?:la\s+)?clé primaire\b",
            flags=re.IGNORECASE,
        ),
        re.compile(
            r"\bclé primaire(?:\s+métier)?\s*"
            r"(?:est|:)\s*([A-Z][A-Z0-9_]*)\b",
            flags=re.IGNORECASE,
        ),
        re.compile(
            r"\b([A-Z][A-Z0-9_]*)\s+"
            r"(?:constitue|est|représente)\s+"
            r"(?:la\s+)?clé primaire\b",
            flags=re.IGNORECASE,
        ),
    ]

    for section in document.sections:
        if section.title.strip().lower() != "clé primaire":
            continue

        for pattern in primary_key_patterns:
            match = pattern.search(section.content)

            if match:
                return match.group(1).upper()

    return None


def parse_documented_column(
    column_name: str,
    content: str,
) -> DocumentedColumn:
    """
    Transforme le contenu d'une section de colonne
    en objet DocumentedColumn.
    """

    description: str | None = None
    business_type: str | None = None
    expected_format: str | None = None
    required: bool | None = None
    unique: bool | None = None
    sensitive: bool | None = None
    allowed_values: list[str] = []

    for line in content.splitlines():
        cleaned_line = clean_markdown_list_item(line)

        if ":" not in cleaned_line:
            continue

        property_name, property_value = (
            cleaned_line.split(":", 1)
        )

        normalized_property = (
            property_name.strip().lower()
        )

        value = property_value.strip().rstrip(".")

        if normalized_property == "description":
            description = value

        elif normalized_property == "type métier":
            business_type = value

        elif normalized_property == "format attendu":
            expected_format = value

        elif normalized_property == "valeur obligatoire":
            required = parse_yes_no_value(value)

        elif normalized_property == "valeur unique":
            unique = parse_yes_no_value(value)

        elif normalized_property == "donnée sensible":
            sensitive = parse_yes_no_value(value)

        elif normalized_property == "valeurs autorisées":
            allowed_values = [
                item.strip()
                for item in value.split(",")
                if item.strip()
            ]

    return DocumentedColumn(
        name=column_name.upper(),
        description=description,
        business_type=business_type,
        expected_format=expected_format,
        required=required,
        unique=unique,
        sensitive=sensitive,
        allowed_values=allowed_values,
        evidence_type="explicit",
    )


def extract_documented_columns(
    document: DocumentMetadata,
) -> list[DocumentedColumn]:
    """
    Extrait les sections de niveau 3 représentant
    des colonnes documentées.
    """

    columns: list[DocumentedColumn] = []

    column_name_pattern = re.compile(
        r"^[A-Z][A-Z0-9_]*$"
    )

    for section in document.sections:
        if section.level != 3:
            continue

        column_name = section.title.strip().upper()

        if not column_name_pattern.fullmatch(
            column_name
        ):
            continue

        columns.append(
            parse_documented_column(
                column_name=column_name,
                content=section.content,
            )
        )

    return columns


def extract_business_rules(
    document: DocumentMetadata,
    documented_columns: list[DocumentedColumn],
) -> list[BusinessRule]:
    """
    Extrait les règles de la section Règles métier.
    """

    business_rules: list[BusinessRule] = []

    column_names = [
        column.name
        for column in documented_columns
    ]

    for section in document.sections:
        if section.title.lower() != "règles métier":
            continue

        rule_number = 1

        for line in section.content.splitlines():
            cleaned_line = clean_markdown_list_item(
                line
            )

            if not cleaned_line:
                continue

            related_columns = [
                column_name
                for column_name in column_names
                if re.search(
                    rf"\b{re.escape(column_name)}\b",
                    cleaned_line,
                    flags=re.IGNORECASE,
                )
            ]

            business_rules.append(
                BusinessRule(
                    rule_id=f"BR-{rule_number:03d}",
                    description=cleaned_line,
                    related_columns=related_columns,
                    evidence_type="explicit",
                )
            )

            rule_number += 1

    return business_rules


def extract_documented_relationships(
    document: DocumentMetadata,
) -> list[DocumentedRelationship]:
    """
    Extrait les relations explicitement documentées.
    """

    relationships: list[DocumentedRelationship] = []

    join_pattern = re.compile(
        r"\b([A-Z][A-Z0-9_]*)\.([A-Z][A-Z0-9_]*)"
        r"\s*=\s*"
        r"([A-Z][A-Z0-9_]*)\.([A-Z][A-Z0-9_]*)\b",
        flags=re.IGNORECASE,
    )

    for section in document.sections:
        if section.title.lower() != "relations connues":
            continue

        join_match = join_pattern.search(
            section.content
        )

        if not join_match:
            continue

        source_table = join_match.group(1).upper()
        source_column = join_match.group(2).upper()
        target_table = join_match.group(3).upper()
        target_column = join_match.group(4).upper()

        relationship_type = "unknown"

        relationship_type_match = re.search(
            r"type de relation\s*:\s*"
            r"(one-to-one|one-to-many|many-to-one|many-to-many)",
            section.content,
            flags=re.IGNORECASE,
        )

        if relationship_type_match:
            relationship_type = (
                relationship_type_match
                .group(1)
                .lower()
            )

        cardinality_description: str | None = None

        cardinality_match = re.search(
            r"cardinalité\s*:\s*(.+)",
            section.content,
            flags=re.IGNORECASE,
        )

        if cardinality_match:
            cardinality_description = (
                cardinality_match
                .group(1)
                .strip()
                .rstrip(".")
            )

        relationships.append(
            DocumentedRelationship(
                source_table=source_table,
                source_column=source_column,
                target_table=target_table,
                target_column=target_column,
                relationship_type=relationship_type,
                cardinality_description=(
                    cardinality_description
                ),
                evidence_type="explicit",
            )
        )

    return relationships


def extract_sensitive_data(
    document: DocumentMetadata,
    documented_columns: list[DocumentedColumn],
) -> list[SensitiveDataItem]:
    """
    Extrait les colonnes explicitement déclarées sensibles.
    """

    sensitive_items: list[SensitiveDataItem] = []

    precautions: list[str] = []

    for section in document.sections:
        if (
            section.title.lower()
            != "points de vigilance"
        ):
            continue

        precautions = [
            line.strip()
            for line in section.content.splitlines()
            if line.strip()
        ]

    for column in documented_columns:
        if column.sensitive is not True:
            continue

        sensitive_items.append(
            SensitiveDataItem(
                column_name=column.name,
                risk_description=(
                    column.description
                ),
                precautions=precautions,
                evidence_type="explicit",
            )
        )

    return sensitive_items


def extract_missing_information(
    document: DocumentMetadata,
) -> list[str]:
    """
    Extrait les éléments de la section
    Informations manquantes.
    """

    missing_information: list[str] = []

    for section in document.sections:
        if (
            section.title.lower()
            != "informations manquantes"
        ):
            continue

        for line in section.content.splitlines():
            cleaned_line = clean_markdown_list_item(
                line
            )

            if not cleaned_line:
                continue

            normalized_line = cleaned_line.lower()

            if normalized_line in {
                "la documentation ne précise pas :",
                "le document ne précise pas :",
            }:
                continue

            missing_information.append(
                cleaned_line.rstrip(".")
            )

    return missing_information


def parse_business_document(
    document: DocumentMetadata,
) -> BusinessDocumentationAnalysis:
    """
    Transforme un DocumentMetadata en analyse métier structurée.

    Cette extraction dépend de conventions documentaires :
    titres Markdown, propriétés sous forme clé/valeur
    et sections nommées de manière standardisée.
    """

    table_name = extract_table_name(document)

    (
        table_description,
        update_frequency,
    ) = extract_general_information(document)

    documented_primary_key = (
        extract_documented_primary_key(document)
    )

    documented_columns = (
        extract_documented_columns(document)
    )

    business_rules = extract_business_rules(
        document=document,
        documented_columns=documented_columns,
    )

    relationships = (
        extract_documented_relationships(document)
    )

    sensitive_data = extract_sensitive_data(
        document=document,
        documented_columns=documented_columns,
    )

    missing_information = (
        extract_missing_information(document)
    )

    warnings: list[str] = []

    if table_name is None:
        warnings.append(
            "Le nom de la table n'a pas pu être extrait."
        )

    if documented_primary_key is None:
        warnings.append(
            "Aucune clé primaire métier n'est "
            "explicitement documentée."
        )

    if not documented_columns:
        warnings.append(
            "Aucune colonne documentée n'a été détectée."
        )

    if not business_rules:
        warnings.append(
            "Aucune règle métier structurée "
            "n'a été détectée."
        )

    return BusinessDocumentationAnalysis(
        source_file=document.file_name,
        document_title=document.title,
        table_name=table_name,
        table_description=table_description,
        documented_primary_key=(
            documented_primary_key
        ),
        update_frequency=update_frequency,
        columns=documented_columns,
        business_rules=business_rules,
        relationships=relationships,
        sensitive_data=sensitive_data,
        missing_information=missing_information,
        warnings=warnings,
    )