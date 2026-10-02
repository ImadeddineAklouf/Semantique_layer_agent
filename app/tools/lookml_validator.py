import re

from app.schemas import (
    GeneratedLookMLFile,
    LookMLFileValidationResult,
    LookMLGenerationResult,
    LookMLValidationIssue,
    LookMLValidationReport,
)

def validate_balanced_braces(
    generated_file: GeneratedLookMLFile,
) -> list[LookMLValidationIssue]:
    """
    Vérifie que les accolades LookML
    sont correctement équilibrées.
    """

    issues: list[LookMLValidationIssue] = []

    opening_count = (
        generated_file.content.count("{")
    )

    closing_count = (
        generated_file.content.count("}")
    )

    if opening_count != closing_count:
        issues.append(
            LookMLValidationIssue(
                file_name=generated_file.file_name,
                severity="error",
                code="UNBALANCED_BRACES",
                message=(
                    "Le nombre d'accolades ouvrantes "
                    "et fermantes est différent : "
                    f"{opening_count} ouvrante(s), "
                    f"{closing_count} fermante(s)."
                ),
                object_name=None,
            )
        )

    return issues

def extract_object_names(
    content: str,
    object_type: str,
) -> list[str]:
    """
    Extrait les noms des objets LookML.

    Exemples :
        view: clients
        dimension: client_id
        measure: count
        explore: orders
        join: clients
    """

    pattern = re.compile(
        rf"^\s*{re.escape(object_type)}"
        r":\s*([a-z][a-z0-9_]*)\s*\{",
        flags=re.MULTILINE,
    )

    return pattern.findall(content)

def find_duplicates(
    values: list[str],
) -> list[str]:
    """
    Retourne les valeurs présentes plusieurs fois.
    """

    return sorted(
        {
            value
            for value in values
            if values.count(value) > 1
        }
    )

def validate_view_file(
    generated_file: GeneratedLookMLFile,
) -> list[LookMLValidationIssue]:
    """
    Vérifie la structure principale
    d'un fichier .view.lkml.
    """

    issues: list[LookMLValidationIssue] = []

    content = generated_file.content

    view_names = extract_object_names(
        content,
        "view",
    )

    if len(view_names) == 0:
        issues.append(
            LookMLValidationIssue(
                file_name=generated_file.file_name,
                severity="error",
                code="MISSING_VIEW",
                message=(
                    "Aucune déclaration view "
                    "n'a été trouvée."
                ),
            )
        )

    elif len(view_names) > 1:
        issues.append(
            LookMLValidationIssue(
                file_name=generated_file.file_name,
                severity="error",
                code="MULTIPLE_VIEWS",
                message=(
                    "Un fichier de vue doit contenir "
                    "une seule déclaration view."
                ),
            )
        )

    expected_view_name = (
        generated_file.file_name
        .removesuffix(".view.lkml")
    )

    if (
        len(view_names) == 1
        and view_names[0] != expected_view_name
    ):
        issues.append(
            LookMLValidationIssue(
                file_name=generated_file.file_name,
                severity="error",
                code="VIEW_NAME_MISMATCH",
                message=(
                    "Le nom de la vue ne correspond "
                    "pas au nom du fichier."
                ),
                object_name=view_names[0],
            )
        )

    if "sql_table_name:" not in content:
        issues.append(
            LookMLValidationIssue(
                file_name=generated_file.file_name,
                severity="error",
                code="MISSING_SQL_TABLE_NAME",
                message=(
                    "La vue ne contient aucun "
                    "sql_table_name."
                ),
                object_name=(
                    view_names[0]
                    if view_names
                    else None
                ),
            )
        )

    dimension_names = extract_object_names(
        content,
        "dimension",
    )

    for duplicate_name in find_duplicates(
        dimension_names
    ):
        issues.append(
            LookMLValidationIssue(
                file_name=generated_file.file_name,
                severity="error",
                code="DUPLICATE_DIMENSION",
                message=(
                    "La dimension est déclarée "
                    "plusieurs fois."
                ),
                object_name=duplicate_name,
            )
        )

    measure_names = extract_object_names(
        content,
        "measure",
    )

    for duplicate_name in find_duplicates(
        measure_names
    ):
        issues.append(
            LookMLValidationIssue(
                file_name=generated_file.file_name,
                severity="error",
                code="DUPLICATE_MEASURE",
                message=(
                    "La mesure est déclarée "
                    "plusieurs fois."
                ),
                object_name=duplicate_name,
            )
        )

    primary_key_count = content.count(
        "primary_key: yes"
    )

    if primary_key_count == 0:
        issues.append(
            LookMLValidationIssue(
                file_name=generated_file.file_name,
                severity="warning",
                code="MISSING_PRIMARY_KEY",
                message=(
                    "Aucune clé primaire LookML "
                    "n'est déclarée."
                ),
                object_name=(
                    view_names[0]
                    if view_names
                    else None
                ),
            )
        )

    elif primary_key_count > 1:
        issues.append(
            LookMLValidationIssue(
                file_name=generated_file.file_name,
                severity="error",
                code="MULTIPLE_PRIMARY_KEYS",
                message=(
                    "Plusieurs dimensions sont marquées "
                    "comme clés primaires."
                ),
                object_name=(
                    view_names[0]
                    if view_names
                    else None
                ),
            )
        )

    return issues

def extract_field_references(
    content: str,
) -> list[str]:
    """
    Extrait les références ${...} du LookML.
    """

    return re.findall(
        r"\$\{([^}]+)\}",
        content,
    )

def validate_local_field_references(
    generated_file: GeneratedLookMLFile,
) -> list[LookMLValidationIssue]:
    """
    Vérifie les références locales utilisées
    dans un fichier de vue.

    Les références ${TABLE}.COLONNE sont toujours
    autorisées.

    Les références ${dimension_name} doivent pointer
    vers une dimension déclarée dans le fichier.
    """

    issues: list[LookMLValidationIssue] = []

    dimension_names = set(
        extract_object_names(
            generated_file.content,
            "dimension",
        )
    )

    references = extract_field_references(
        generated_file.content
    )

    for reference in references:
        if reference == "TABLE":
            continue

        if "." in reference:
            continue

        if reference not in dimension_names:
            issues.append(
                LookMLValidationIssue(
                    file_name=(
                        generated_file.file_name
                    ),
                    severity="error",
                    code="UNKNOWN_LOCAL_FIELD",
                    message=(
                        "Une expression référence "
                        "un champ local inconnu."
                    ),
                    object_name=reference,
                )
            )

    return issues

def validate_model_file(
    generated_file: GeneratedLookMLFile,
    available_view_names: set[str],
) -> list[LookMLValidationIssue]:
    """
    Vérifie la structure d'un fichier .model.lkml.
    """

    issues: list[LookMLValidationIssue] = []

    content = generated_file.content

    if "connection:" not in content:
        issues.append(
            LookMLValidationIssue(
                file_name=generated_file.file_name,
                severity="error",
                code="MISSING_CONNECTION",
                message=(
                    "Le modèle ne contient aucune "
                    "connexion Looker."
                ),
            )
        )

    if "include:" not in content:
        issues.append(
            LookMLValidationIssue(
                file_name=generated_file.file_name,
                severity="error",
                code="MISSING_INCLUDE",
                message=(
                    "Le modèle ne contient aucun include."
                ),
            )
        )

    explore_names = extract_object_names(
        content,
        "explore",
    )

    for duplicate_name in find_duplicates(
        explore_names
    ):
        issues.append(
            LookMLValidationIssue(
                file_name=generated_file.file_name,
                severity="error",
                code="DUPLICATE_EXPLORE",
                message=(
                    "L'Explore est déclaré plusieurs fois."
                ),
                object_name=duplicate_name,
            )
        )

    for explore_name in explore_names:
        if explore_name not in available_view_names:
            issues.append(
                LookMLValidationIssue(
                    file_name=(
                        generated_file.file_name
                    ),
                    severity="error",
                    code="UNKNOWN_EXPLORE_VIEW",
                    message=(
                        "L'Explore référence une vue "
                        "qui n'existe pas."
                    ),
                    object_name=explore_name,
                )
            )

    join_names = extract_object_names(
        content,
        "join",
    )

    for join_name in join_names:
        if join_name not in available_view_names:
            issues.append(
                LookMLValidationIssue(
                    file_name=(
                        generated_file.file_name
                    ),
                    severity="error",
                    code="UNKNOWN_JOIN_VIEW",
                    message=(
                        "La jointure référence une vue "
                        "qui n'existe pas."
                    ),
                    object_name=join_name,
                )
            )

    references = extract_field_references(
        content
    )

    for reference in references:
        if "." not in reference:
            continue

        referenced_view = reference.split(
            ".",
            maxsplit=1,
        )[0]

        if referenced_view not in available_view_names:
            issues.append(
                LookMLValidationIssue(
                    file_name=(
                        generated_file.file_name
                    ),
                    severity="error",
                    code="UNKNOWN_VIEW_REFERENCE",
                    message=(
                        "Une expression référence "
                        "une vue inconnue."
                    ),
                    object_name=referenced_view,
                )
            )

    return issues

def validate_lookml_file(
    generated_file: GeneratedLookMLFile,
    available_view_names: set[str],
) -> LookMLFileValidationResult:
    """
    Valide un artefact LookML individuel.
    """

    issues: list[LookMLValidationIssue] = []

    issues.extend(
        validate_balanced_braces(
            generated_file
        )
    )

    if generated_file.file_type == "view":
        issues.extend(
            validate_view_file(
                generated_file
            )
        )

        issues.extend(
            validate_local_field_references(
                generated_file
            )
        )

    elif generated_file.file_type == "model":
        issues.extend(
            validate_model_file(
                generated_file,
                available_view_names,
            )
        )

    error_count = sum(
        issue.severity == "error"
        for issue in issues
    )

    return LookMLFileValidationResult(
        file_name=generated_file.file_name,
        file_type=generated_file.file_type,
        valid=error_count == 0,
        issue_count=len(issues),
        issues=issues,
    )

def validate_lookml_artifacts(
    generation_result: LookMLGenerationResult,
) -> LookMLValidationReport:
    """
    Valide tous les artefacts LookML générés.
    """

    if generation_result.generation_status == "blocked":
        raise ValueError(
            "Une génération bloquée ne contient "
            "aucun LookML validable."
        )

    if not generation_result.files:
        raise ValueError(
            "Aucun artefact LookML n'est disponible."
        )

    view_files = [
        generated_file
        for generated_file in generation_result.files
        if generated_file.file_type == "view"
    ]

    model_files = [
        generated_file
        for generated_file in generation_result.files
        if generated_file.file_type == "model"
    ]

    available_view_names = {
        generated_file.source_name
        for generated_file in view_files
    }

    global_issues: list[
        LookMLValidationIssue
    ] = []

    if len(model_files) == 0:
        global_issues.append(
            LookMLValidationIssue(
                file_name="<generation>",
                severity="error",
                code="MISSING_MODEL_FILE",
                message=(
                    "Aucun fichier modèle n'a été généré."
                ),
            )
        )

    elif len(model_files) > 1:
        global_issues.append(
            LookMLValidationIssue(
                file_name="<generation>",
                severity="error",
                code="MULTIPLE_MODEL_FILES",
                message=(
                    "Plusieurs fichiers modèle ont "
                    "été générés."
                ),
            )
        )

    file_names = [
        generated_file.file_name
        for generated_file
        in generation_result.files
    ]

    for duplicate_name in find_duplicates(
        file_names
    ):
        global_issues.append(
            LookMLValidationIssue(
                file_name=duplicate_name,
                severity="error",
                code="DUPLICATE_FILE_NAME",
                message=(
                    "Plusieurs artefacts possèdent "
                    "le même nom de fichier."
                ),
            )
        )

    file_results = [
        validate_lookml_file(
            generated_file=generated_file,
            available_view_names=(
                available_view_names
            ),
        )
        for generated_file
        in generation_result.files
    ]

    all_issues = list(global_issues)

    for file_result in file_results:
        all_issues.extend(
            file_result.issues
        )

    error_count = sum(
        issue.severity == "error"
        for issue in all_issues
    )

    warning_count = sum(
        issue.severity == "warning"
        for issue in all_issues
    )

    return LookMLValidationReport(
        valid=error_count == 0,
        validated_file_count=len(
            generation_result.files
        ),
        error_count=error_count,
        warning_count=warning_count,
        file_results=file_results,
        issues=all_issues,
    )

