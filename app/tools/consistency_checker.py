from app.schemas import (
    BusinessDocumentationAnalysis,
    BusinessRule,
    BusinessRuleValidationResult,
    ColumnConsistencyResult,
    ConsistencyLevel,
    ConsistencyReport,
    DocumentedColumn,
    PrimaryKeyConsistencyResult,
    TableMetadata,
)

BUSINESS_TYPE_MAPPING = {
    "identifiant": "integer",
    "entier": "integer",
    "integer": "integer",
    "nombre entier": "integer",
    "texte": "string",
    "chaîne": "string",
    "chaine": "string",
    "string": "string",
    "code pays": "string",
    "date": "date",
    "booléen": "boolean",
    "booleen": "boolean",
    "boolean": "boolean",
    "nombre décimal": "float",
    "nombre decimal": "float",
    "float": "float",
}


def normalize_documented_type(
    documented_type: str | None,
) -> str | None:
    """
    Transforme un type métier documenté
    en type sémantique comparable.
    """

    if documented_type is None:
        return None

    normalized_value = (
        documented_type
        .strip()
        .lower()
    )

    return BUSINESS_TYPE_MAPPING.get(
        normalized_value
    )

def get_consistency_level(
    score: int,
) -> ConsistencyLevel:
    """
    Convertit un score en niveau de cohérence.
    """

    if score >= 90:
        return "excellent"

    if score >= 75:
        return "good"

    if score >= 50:
        return "warning"

    return "critical"

def compare_column(
    technical_column,
    documented_column: DocumentedColumn,
) -> ColumnConsistencyResult:
    """
    Compare une colonne technique et sa définition métier.
    """

    issues: list[str] = []
    recommendations: list[str] = []

    normalized_documented_type = (
        normalize_documented_type(
            documented_column.business_type
        )
    )

    if normalized_documented_type is None:
        type_status = "not_verifiable"

        recommendations.append(
            "Préciser un type métier reconnu "
            "dans la documentation."
        )

    elif (
        technical_column.semantic_type
        == normalized_documented_type
    ):
        type_status = "consistent"

    else:
        type_status = "inconsistent"

        issues.append(
            "Le type technique détecté "
            f"'{technical_column.semantic_type}' "
            "ne correspond pas au type documenté "
            f"'{documented_column.business_type}'."
        )

        recommendations.append(
            "Vérifier le type physique de la colonne "
            "ou corriger la documentation métier."
        )

    if documented_column.required is None:
        nullability_status = "not_verifiable"

    elif (
        documented_column.required is True
        and technical_column.nullable is False
    ):
        nullability_status = "consistent"

    elif (
        documented_column.required is True
        and technical_column.nullable is True
    ):
        nullability_status = "inconsistent"

        issues.append(
            "La colonne est documentée comme obligatoire "
            "mais contient au moins une valeur nulle."
        )

        recommendations.append(
            "Corriger les valeurs nulles ou modifier "
            "la règle documentaire."
        )

    else:
        nullability_status = "consistent"

    technical_unique = (
        technical_column.unique_count
        == technical_column.sample_size
        if hasattr(technical_column, "sample_size")
        else None
    )

def compare_column(
    technical_column,
    documented_column: DocumentedColumn,
    row_count: int,
) -> ColumnConsistencyResult:
    """
    Compare une colonne technique et sa définition métier.
    """

    issues: list[str] = []
    recommendations: list[str] = []

    normalized_documented_type = (
        normalize_documented_type(
            documented_column.business_type
        )
    )

    if normalized_documented_type is None:
        type_status = "not_verifiable"

        recommendations.append(
            "Préciser un type métier reconnu "
            "dans la documentation."
        )

    elif (
        technical_column.semantic_type
        == normalized_documented_type
    ):
        type_status = "consistent"

    else:
        type_status = "inconsistent"

        issues.append(
            "Le type technique détecté "
            f"'{technical_column.semantic_type}' "
            "ne correspond pas au type documenté "
            f"'{documented_column.business_type}'."
        )

        recommendations.append(
            "Vérifier le type physique de la colonne "
            "ou corriger la documentation métier."
        )

    if documented_column.required is None:
        nullability_status = "not_verifiable"

    elif (
        documented_column.required is True
        and technical_column.nullable is False
    ):
        nullability_status = "consistent"

    elif (
        documented_column.required is True
        and technical_column.nullable is True
    ):
        nullability_status = "inconsistent"

        issues.append(
            "La colonne est documentée comme obligatoire "
            "mais contient au moins une valeur nulle."
        )

        recommendations.append(
            "Corriger les valeurs nulles ou modifier "
            "la règle documentaire."
        )

    else:
        nullability_status = "consistent"

    technical_unique = (
        technical_column.null_count == 0
        and technical_column.unique_count == row_count
    )

    if documented_column.unique is None:
        uniqueness_status = "not_verifiable"

    elif (
        documented_column.unique
        == technical_unique
    ):
        uniqueness_status = "consistent"

    else:
        uniqueness_status = "inconsistent"

        issues.append(
            "L'unicité observée dans les données "
            "ne correspond pas à l'unicité documentée."
        )

        recommendations.append(
            "Vérifier les doublons ou corriger "
            "la propriété d'unicité documentée."
        )

    statuses = {
        type_status,
        nullability_status,
        uniqueness_status,
    }

    if "inconsistent" in statuses:
        overall_status = "inconsistent"

    elif "warning" in statuses:
        overall_status = "warning"

    elif statuses == {"consistent"}:
        overall_status = "consistent"

    else:
        overall_status = "warning"

    return ColumnConsistencyResult(
        column_name=technical_column.name,
        exists_in_data=True,
        exists_in_documentation=True,
        technical_type=technical_column.semantic_type,
        documented_type=(
            documented_column.business_type
        ),
        type_status=type_status,
        technical_nullable=technical_column.nullable,
        documented_required=(
            documented_column.required
        ),
        nullability_status=nullability_status,
        technical_unique=technical_unique,
        documented_unique=documented_column.unique,
        uniqueness_status=uniqueness_status,
        overall_status=overall_status,
        issues=issues,
        recommendations=recommendations,
    )

def create_undocumented_column_result(
    technical_column,
    row_count: int,
) -> ColumnConsistencyResult:
    """
    Crée le résultat d'une colonne présente dans les données
    mais absente de la documentation.
    """

    technical_unique = (
        technical_column.null_count == 0
        and technical_column.unique_count == row_count
    )

    return ColumnConsistencyResult(
        column_name=technical_column.name,
        exists_in_data=True,
        exists_in_documentation=False,
        technical_type=technical_column.semantic_type,
        documented_type=None,
        type_status="not_verifiable",
        technical_nullable=technical_column.nullable,
        documented_required=None,
        nullability_status="not_verifiable",
        technical_unique=technical_unique,
        documented_unique=None,
        uniqueness_status="not_verifiable",
        overall_status="warning",
        issues=[
            "La colonne existe dans les données "
            "mais n'est pas documentée."
        ],
        recommendations=[
            "Ajouter la colonne à la documentation métier "
            "ou confirmer qu'elle doit être ignorée."
        ],
    )

def create_missing_data_column_result(
    documented_column: DocumentedColumn,
) -> ColumnConsistencyResult:
    """
    Crée le résultat d'une colonne documentée
    mais absente des données.
    """

    return ColumnConsistencyResult(
        column_name=documented_column.name,
        exists_in_data=False,
        exists_in_documentation=True,
        technical_type=None,
        documented_type=documented_column.business_type,
        type_status="not_verifiable",
        technical_nullable=None,
        documented_required=documented_column.required,
        nullability_status="not_verifiable",
        technical_unique=None,
        documented_unique=documented_column.unique,
        uniqueness_status="not_verifiable",
        overall_status="inconsistent",
        issues=[
            "La colonne est présente dans la documentation "
            "mais absente du fichier CSV."
        ],
        recommendations=[
            "Vérifier le schéma du fichier ou corriger "
            "la documentation métier."
        ],
    )

def compare_primary_key(
    metadata: TableMetadata,
    documentation: BusinessDocumentationAnalysis,
) -> PrimaryKeyConsistencyResult:
    """
    Compare la clé primaire documentée
    avec les candidats techniques.
    """

    documented_primary_key = (
        documentation.documented_primary_key
    )

    technical_candidates = (
        metadata.primary_key_candidates
    )

    recommended_candidate: str | None = None

    for candidate in metadata.primary_key_analysis:
        if candidate.recommended:
            recommended_candidate = (
                candidate.column_name
            )
            break

    issues: list[str] = []
    recommendations: list[str] = []

    if documented_primary_key is None:
        status = "not_verifiable"

        issues.append(
            "Aucune clé primaire métier n'est documentée."
        )

        recommendations.append(
            "Documenter explicitement la clé primaire métier."
        )

    elif documented_primary_key in technical_candidates:
        status = "consistent"

    else:
        status = "inconsistent"

        issues.append(
            "La clé primaire documentée "
            f"'{documented_primary_key}' "
            "n'est pas une candidate technique valide."
        )

        recommendations.append(
            "Vérifier les valeurs nulles, les doublons "
            "ou la documentation de la clé primaire."
        )

    if (
        documented_primary_key is not None
        and recommended_candidate is not None
        and documented_primary_key
        != recommended_candidate
    ):
        issues.append(
            "La candidate technique recommandée "
            f"'{recommended_candidate}' diffère de la clé "
            f"documentée '{documented_primary_key}'."
        )

        if status == "consistent":
            status = "warning"

    return PrimaryKeyConsistencyResult(
        documented_primary_key=(
            documented_primary_key
        ),
        technical_candidates=technical_candidates,
        recommended_technical_candidate=(
            recommended_candidate
        ),
        status=status,
        issues=issues,
        recommendations=recommendations,
    )

def validate_business_rule(
    rule: BusinessRule,
    metadata: TableMetadata,
) -> BusinessRuleValidationResult:
    """
    Évalue si une règle métier peut être vérifiée
    avec les métadonnées techniques disponibles.
    """

    technical_columns = {
        column.name: column
        for column in metadata.columns
    }

    evidence: list[str] = []
    issues: list[str] = []

    missing_columns = [
        column_name
        for column_name in rule.related_columns
        if column_name not in technical_columns
    ]

    if missing_columns:
        return BusinessRuleValidationResult(
            rule_id=rule.rule_id,
            description=rule.description,
            related_columns=rule.related_columns,
            status="inconsistent",
            evidence=[],
            issues=[
                "Les colonnes suivantes sont absentes "
                "des données : "
                + ", ".join(missing_columns)
            ],
        )

    normalized_description = (
        rule.description.lower()
    )

    if not rule.related_columns:
        return BusinessRuleValidationResult(
            rule_id=rule.rule_id,
            description=rule.description,
            related_columns=[],
            status="not_verifiable",
            evidence=[],
            issues=[
                "Aucune colonne technique n'a pu être "
                "associée automatiquement à cette règle."
            ],
        )

    statuses: list[str] = []

    for column_name in rule.related_columns:
        column = technical_columns[column_name]

        if (
            "doit toujours être renseigné"
            in normalized_description
            or "obligatoire"
            in normalized_description
        ):
            if column.null_count == 0:
                statuses.append("consistent")

                evidence.append(
                    f"{column_name} ne contient "
                    "aucune valeur nulle."
                )
            else:
                statuses.append("inconsistent")

                issues.append(
                    f"{column_name} contient "
                    f"{column.null_count} valeur(s) nulle(s)."
                )

        elif (
            "ne peuvent pas partager"
            in normalized_description
            or "unique"
            in normalized_description
        ):
            if (
                column.null_count == 0
                and column.unique_count
                == metadata.row_count
            ):
                statuses.append("consistent")

                evidence.append(
                    f"{column_name} contient uniquement "
                    "des valeurs uniques et non nulles."
                )
            else:
                statuses.append("inconsistent")

                issues.append(
                    f"{column_name} ne respecte pas "
                    "l'unicité attendue."
                )

        else:
            statuses.append("not_verifiable")

    if "inconsistent" in statuses:
        status = "inconsistent"

    elif statuses and all(
        item == "consistent"
        for item in statuses
    ):
        status = "consistent"

    else:
        status = "not_verifiable"

    return BusinessRuleValidationResult(
        rule_id=rule.rule_id,
        description=rule.description,
        related_columns=rule.related_columns,
        status=status,
        evidence=evidence,
        issues=issues,
    )

def compare_metadata_with_documentation(
    metadata: TableMetadata,
    documentation: BusinessDocumentationAnalysis,
) -> ConsistencyReport:
    """
    Compare les métadonnées techniques avec
    la documentation métier structurée.
    """

    technical_columns = {
        column.name: column
        for column in metadata.columns
    }

    documented_columns = {
        column.name: column
        for column in documentation.columns
    }

    all_column_names = sorted(
        set(technical_columns)
        | set(documented_columns)
    )

    column_results: list[
        ColumnConsistencyResult
    ] = []

    undocumented_columns: list[str] = []
    missing_data_columns: list[str] = []

    for column_name in all_column_names:
        technical_column = technical_columns.get(
            column_name
        )

        documented_column = documented_columns.get(
            column_name
        )

        if (
            technical_column is not None
            and documented_column is not None
        ):
            result = compare_column(
                technical_column=technical_column,
                documented_column=documented_column,
                row_count=metadata.row_count,
            )

        elif technical_column is not None:
            undocumented_columns.append(
                column_name
            )

            result = (
                create_undocumented_column_result(
                    technical_column=technical_column,
                    row_count=metadata.row_count,
                )
            )

        else:
            missing_data_columns.append(
                column_name
            )

            result = (
                create_missing_data_column_result(
                    documented_column=documented_column
                )
            )

        column_results.append(result)

    if documentation.table_name is None:
        table_name_status = "not_verifiable"

    elif (
        metadata.table_name
        == documentation.table_name
    ):
        table_name_status = "consistent"

    else:
        table_name_status = "inconsistent"

    primary_key_result = compare_primary_key(
        metadata=metadata,
        documentation=documentation,
    )

    business_rule_results = [
        validate_business_rule(
            rule=rule,
            metadata=metadata,
        )
        for rule in documentation.business_rules
    ]

    score = 100

    inconsistent_columns = [
        result
        for result in column_results
        if result.overall_status == "inconsistent"
    ]

    warning_columns = [
        result
        for result in column_results
        if result.overall_status == "warning"
    ]

    score -= len(inconsistent_columns) * 10
    score -= len(warning_columns) * 5

    if table_name_status == "inconsistent":
        score -= 20

    if primary_key_result.status == "inconsistent":
        score -= 20

    elif primary_key_result.status == "warning":
        score -= 10

    inconsistent_rules = [
        result
        for result in business_rule_results
        if result.status == "inconsistent"
    ]

    score -= len(inconsistent_rules) * 5

    score = max(
        0,
        min(score, 100),
    )

    warnings: list[str] = []
    recommendations: list[str] = []

    if undocumented_columns:
        warnings.append(
            "Certaines colonnes techniques ne sont "
            "pas documentées : "
            + ", ".join(undocumented_columns)
            + "."
        )

    if missing_data_columns:
        warnings.append(
            "Certaines colonnes documentées sont "
            "absentes des données : "
            + ", ".join(missing_data_columns)
            + "."
        )

    if documentation.missing_information:
        warnings.append(
            "La documentation déclare des informations "
            "manquantes."
        )

        recommendations.append(
            "Compléter les informations manquantes "
            "identifiées dans la documentation."
        )

    return ConsistencyReport(
        data_source_file=metadata.file_name,
        documentation_source_file=(
            documentation.source_file
        ),
        technical_table_name=metadata.table_name,
        documented_table_name=(
            documentation.table_name
        ),
        table_name_status=table_name_status,
        consistency_score=score,
        consistency_level=get_consistency_level(
            score
        ),
        column_results=column_results,
        primary_key_result=primary_key_result,
        business_rule_results=(
            business_rule_results
        ),
        undocumented_columns=undocumented_columns,
        missing_data_columns=missing_data_columns,
        documented_relationships=len(
            documentation.relationships
        ),
        warnings=warnings,
        recommendations=recommendations,
    )