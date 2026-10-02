import re

from app.schemas import (
    BusinessDocumentationAnalysis,
    ConsistencyReport,
    RelationshipAnalysisReport,
    SemanticDimension,
    SemanticFieldType,
    SemanticJoin,
    SemanticJoinRelationship,
    SemanticMeasure,
    SemanticModelSpecification,
    SemanticViewSpecification,
    TableMetadata,
)

SEMANTIC_FIELD_TYPE_MAPPING: dict[
    str,
    SemanticFieldType,
] = {
    "integer": "number",
    "float": "number",
    "number": "number",
    "string": "string",
    "boolean": "yesno",
    "date": "date",
    "datetime": "date_time",
    "timestamp": "date_time",
}

RELATIONSHIP_MAPPING: dict[
    str,
    SemanticJoinRelationship,
] = {
    "one-to-one": "one_to_one",
    "one-to-many": "one_to_many",
    "many-to-one": "many_to_one",
    "many-to-many": "many_to_many",
    "unknown": "unknown",
}

def normalize_semantic_name(
    value: str,
) -> str:
    """
    Transforme un nom technique en nom sémantique snake_case.

    Exemples :
        CLIENT_ID -> client_id
        Creation Date -> creation_date
        CUSTOMER-NAME -> customer_name
    """

    normalized_value = value.strip().lower()

    normalized_value = re.sub(
        r"[^a-z0-9]+",
        "_",
        normalized_value,
    )

    normalized_value = re.sub(
        r"_+",
        "_",
        normalized_value,
    )

    return normalized_value.strip("_")

def create_field_label(
    column_name: str,
) -> str:
    """
    Transforme un nom de colonne technique
    en libellé lisible.

    Exemple :
        CLIENT_ID -> Client ID
    """

    words = column_name.split("_")

    formatted_words = [
        word.upper()
        if word in {"ID", "URL", "API"}
        else word.capitalize()
        for word in words
    ]

    return " ".join(formatted_words)


def map_semantic_field_type(
    technical_type: str,
) -> SemanticFieldType:
    """
    Convertit le type sémantique technique
    vers le type de la spécification sémantique.
    """

    normalized_type = technical_type.strip().lower()

    return SEMANTIC_FIELD_TYPE_MAPPING.get(
        normalized_type,
        "unknown",
    )

def map_join_relationship(
    relationship: str,
) -> SemanticJoinRelationship:
    """
    Convertit une cardinalité du moteur relationnel
    vers la représentation sémantique.
    """

    normalized_relationship = (
        relationship.strip().lower()
    )

    return RELATIONSHIP_MAPPING.get(
        normalized_relationship,
        "unknown",
    )

def create_documented_column_index(
    documentation: BusinessDocumentationAnalysis,
) -> dict:
    """
    Indexe les colonnes documentées par leur nom.
    """

    return {
        column.name: column
        for column in documentation.columns
    }

def create_consistency_column_index(
    consistency_report: ConsistencyReport,
) -> dict:
    """
    Indexe les résultats de cohérence par colonne.
    """

    return {
        result.column_name: result
        for result in consistency_report.column_results
    }

def build_semantic_dimension(
    technical_column,
    documented_column,
    consistency_result,
    validated_primary_key: str | None,
) -> SemanticDimension:
    """
    Construit une dimension à partir des informations
    techniques, documentaires et de cohérence.
    """

    source_column = technical_column.name

    dimension_name = normalize_semantic_name(
        source_column
    )

    field_type = map_semantic_field_type(
        technical_column.semantic_type
    )

    is_primary_key = (
        validated_primary_key is not None
        and source_column == validated_primary_key
    )

    description: str | None = None
    required: bool | None = None
    unique: bool | None = None
    sensitive = False
    allowed_values: list[str] = []

    warnings: list[str] = []

    if documented_column is not None:
        description = documented_column.description
        required = documented_column.required
        unique = documented_column.unique
        sensitive = (
            documented_column.sensitive is True
        )
        allowed_values = (
            documented_column.allowed_values
        )
    else:
        warnings.append(
            "La colonne existe techniquement mais "
            "n'est pas documentée."
        )

    validation_status = "validated"

    if consistency_result is None:
        validation_status = "requires_review"

        warnings.append(
            "Aucun résultat de cohérence n'est disponible."
        )

    elif (
        consistency_result.overall_status
        == "inconsistent"
    ):
        validation_status = "requires_review"

        warnings.extend(
            consistency_result.issues
        )

    elif consistency_result.overall_status in {
        "warning",
        "not_verifiable",
    }:
        validation_status = "warning"

        warnings.extend(
            consistency_result.issues
        )

    if field_type == "unknown":
        validation_status = "requires_review"

        warnings.append(
            "Le type de la dimension n'a pas pu "
            "être déterminé."
        )

    if sensitive:
        warnings.append(
            "Cette dimension contient une donnée sensible."
        )

        if validation_status == "validated":
            validation_status = "warning"

    return SemanticDimension(
        name=dimension_name,
        source_column=source_column,
        label=create_field_label(source_column),
        description=description,
        field_type=field_type,
        sql_expression=(
            f"${{TABLE}}.{source_column}"
        ),
        primary_key=is_primary_key,
        hidden=False,
        sensitive=sensitive,
        required=required,
        unique=unique,
        allowed_values=allowed_values,
        validation_status=validation_status,
        warnings=list(dict.fromkeys(warnings)),
    )

def is_identifier_column(
    column_name: str,
) -> bool:
    """
    Détermine si une colonne ressemble à un identifiant.
    """

    normalized_name = column_name.upper()

    return (
        normalized_name == "ID"
        or normalized_name.endswith("_ID")
    )

def build_count_measure(
    view_name: str,
) -> SemanticMeasure:
    """
    Crée la mesure de comptage standard.
    """

    singular_label = (
        view_name[:-1]
        if view_name.endswith("s")
        else view_name
    )

    return SemanticMeasure(
        name="count",
        label="Count",
        description=(
            f"Nombre total d'enregistrements "
            f"de la vue {view_name}."
        ),
        measure_type="count",
        source_column=None,
        sql_expression=None,
        value_format=None,
        validation_status="validated",
        warnings=[],
    )

def build_numeric_measures(
    metadata: TableMetadata,
) -> list[SemanticMeasure]:
    """
    Crée des mesures pour les colonnes numériques
    qui ne représentent pas des identifiants.
    """

    measures: list[SemanticMeasure] = []

    for column in metadata.columns:
        if column.semantic_type not in {
            "integer",
            "float",
            "number",
        }:
            continue

        if is_identifier_column(column.name):
            continue

        normalized_name = normalize_semantic_name(
            column.name
        )

        label = create_field_label(
            column.name
        )

        for measure_type, prefix in [
            ("sum", "total"),
            ("average", "average"),
            ("min", "minimum"),
            ("max", "maximum"),
        ]:
            measures.append(
                SemanticMeasure(
                    name=(
                        f"{prefix}_{normalized_name}"
                    ),
                    label=(
                        f"{prefix.capitalize()} {label}"
                    ),
                    description=(
                        f"{measure_type.capitalize()} "
                        f"de la colonne {column.name}."
                    ),
                    measure_type=measure_type,
                    source_column=column.name,
                    sql_expression=(
                        f"${{{normalized_name}}}"
                    ),
                    value_format=None,
                    validation_status="warning",
                    warnings=[
                        "Mesure générée automatiquement. "
                        "La pertinence métier doit être validée."
                    ],
                )
            )

    return measures

def build_semantic_join(
    relationship_report: RelationshipAnalysisReport,
) -> SemanticJoin:
    """
    Transforme un rapport relationnel validé
    en jointure sémantique.
    """

    target_view_name = normalize_semantic_name(
        relationship_report.target_table
    )

    relationship = map_join_relationship(
        relationship_report
        .cardinality_analysis
        .detected_cardinality
    )

    warnings: list[str] = list(
        relationship_report.warnings
    )

    if relationship_report.overall_status == "valid":
        validation_status = "validated"

    elif relationship_report.overall_status == "warning":
        validation_status = "warning"

    else:
        validation_status = "requires_review"

    return SemanticJoin(
        name=target_view_name,
        source_table=relationship_report.source_table,
        source_column=relationship_report.source_column,
        target_table=relationship_report.target_table,
        target_column=relationship_report.target_column,
        relationship=relationship,
        sql_on=(
            f"${{{normalize_semantic_name(relationship_report.source_table)}."
            f"{normalize_semantic_name(relationship_report.source_column)}}} "
            f"= "
            f"${{{target_view_name}."
            f"{normalize_semantic_name(relationship_report.target_column)}}}"
        ),
        foreign_key_match_ratio=(
            relationship_report
            .referential_integrity
            .match_ratio
        ),
        orphan_value_count=(
            relationship_report
            .referential_integrity
            .orphan_value_count
        ),
        validation_status=validation_status,
        warnings=warnings,
    )

def determine_validated_primary_key(
    consistency_report: ConsistencyReport,
) -> str | None:
    """
    Retourne la clé primaire si elle est suffisamment validée.
    """

    primary_key_result = (
        consistency_report.primary_key_result
    )

    if primary_key_result.status not in {
        "consistent",
        "warning",
    }:
        return None

    return (
        primary_key_result.documented_primary_key
    )

def build_semantic_view(
    metadata: TableMetadata,
    documentation: BusinessDocumentationAnalysis,
    consistency_report: ConsistencyReport,
    relationship_reports: list[
        RelationshipAnalysisReport
    ] | None = None,
) -> SemanticViewSpecification:
    """
    Construit une spécification de vue sémantique.
    """

    relationship_reports = (
        relationship_reports or []
    )

    documented_columns = (
        create_documented_column_index(
            documentation
        )
    )

    consistency_columns = (
        create_consistency_column_index(
            consistency_report
        )
    )

    validated_primary_key = (
        determine_validated_primary_key(
            consistency_report
        )
    )

    dimensions: list[SemanticDimension] = []

    for technical_column in metadata.columns:
        dimensions.append(
            build_semantic_dimension(
                technical_column=technical_column,
                documented_column=(
                    documented_columns.get(
                        technical_column.name
                    )
                ),
                consistency_result=(
                    consistency_columns.get(
                        technical_column.name
                    )
                ),
                validated_primary_key=(
                    validated_primary_key
                ),
            )
        )

    view_name = normalize_semantic_name(
        metadata.table_name
    )

    measures = [
        build_count_measure(view_name)
    ]

    measures.extend(
        build_numeric_measures(metadata)
    )

    joins: list[SemanticJoin] = []

    for relationship_report in relationship_reports:
        if (
            relationship_report.source_table
            != metadata.table_name
        ):
            continue

        joins.append(
            build_semantic_join(
                relationship_report
            )
        )

    sensitive_fields = [
        dimension.source_column
        for dimension in dimensions
        if dimension.sensitive
    ]

    documented_rules = [
        rule.description
        for rule in documentation.business_rules
    ]

    warnings: list[str] = []
    recommendations: list[str] = []

    dimension_statuses = {
        dimension.validation_status
        for dimension in dimensions
    }

    measure_statuses = {
        measure.validation_status
        for measure in measures
    }

    join_statuses = {
        join.validation_status
        for join in joins
    }

    component_statuses = (
        dimension_statuses
        | measure_statuses
        | join_statuses
    )

    if "requires_review" in component_statuses:
        validation_status = "requires_review"

    elif "warning" in component_statuses:
        validation_status = "warning"

    else:
        validation_status = "validated"

    if validated_primary_key is None:
        validation_status = "requires_review"

        warnings.append(
            "Aucune clé primaire suffisamment validée "
            "n'est disponible."
        )

        recommendations.append(
            "Confirmer la clé primaire avant "
            "la génération LookML."
        )

    warnings.extend(
        consistency_report.warnings
    )

    recommendations.extend(
        consistency_report.recommendations
    )

    return SemanticViewSpecification(
        view_name=view_name,
        source_table_name=metadata.table_name,
        source_file=metadata.file_name,
        label=create_field_label(
            metadata.table_name
        ),
        description=(
            documentation.table_description
        ),
        primary_key=validated_primary_key,
        dimensions=dimensions,
        measures=measures,
        joins=joins,
        sensitive_fields=sensitive_fields,
        documented_rules=documented_rules,
        validation_status=validation_status,
        warnings=list(dict.fromkeys(warnings)),
        recommendations=list(
            dict.fromkeys(recommendations)
        ),
    )

def build_semantic_model(
    model_name: str,
    project_name: str,
    views: list[SemanticViewSpecification],
    connection_name: str | None = None,
    default_schema: str | None = None,
) -> SemanticModelSpecification:
    """
    Construit la spécification sémantique globale.
    """

    missing_information: list[str] = []
    warnings: list[str] = []

    if not connection_name:
        missing_information.append(
            "Nom de la connexion Looker."
        )

    if not default_schema:
        missing_information.append(
            "Nom du schéma ou dataset physique."
        )

    views_requiring_review = [
        view.view_name
        for view in views
        if (
            view.validation_status
            == "requires_review"
        )
    ]

    if views_requiring_review:
        missing_information.append(
            "Validation humaine requise pour les vues : "
            + ", ".join(views_requiring_review)
            + "."
        )

    warning_views = [
        view.view_name
        for view in views
        if view.validation_status == "warning"
    ]

    if warning_views:
        warnings.append(
            "Certaines vues comportent des avertissements : "
            + ", ".join(warning_views)
            + "."
        )

    generation_ready = (
        len(missing_information) == 0
    )

    return SemanticModelSpecification(
        model_name=normalize_semantic_name(
            model_name
        ),
        project_name=normalize_semantic_name(
            project_name
        ),
        connection_name=connection_name,
        default_schema=default_schema,
        views=views,
        generation_ready=generation_ready,
        missing_information=missing_information,
        warnings=warnings,
        metadata={
            "view_count": len(views),
            "builder_version": "0.1.0",
        },
    )

