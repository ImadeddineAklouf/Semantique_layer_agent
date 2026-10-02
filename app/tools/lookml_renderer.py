from app.schemas import (
    GeneratedLookMLFile,
    LookMLGenerationResult,
    SemanticDimension,
    SemanticJoin,
    SemanticMeasure,
    SemanticModelSpecification,
    SemanticViewSpecification,
)

def indent_text(
    text: str,
    spaces: int = 2,
) -> str:
    """
    Ajoute une indentation à chaque ligne non vide.
    """

    indentation = " " * spaces

    return "\n".join(
        (
            indentation + line
            if line
            else ""
        )
        for line in text.splitlines()
    )

def escape_lookml_string(
    value: str,
) -> str:
    """
    Protège une chaîne utilisée entre guillemets LookML.
    """

    return (
        value
        .replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\r", " ")
        .replace("\n", " ")
    )

def render_quoted_parameter(
    parameter_name: str,
    value: str,
) -> str:
    """
    Génère un paramètre LookML contenant une chaîne.
    """

    escaped_value = escape_lookml_string(value)

    return (
        f'{parameter_name}: "{escaped_value}"'
    )

def render_warning_comments(
    warnings: list[str],
) -> str:
    """
    Transforme des avertissements en commentaires LookML.
    """

    if not warnings:
        return ""

    comment_lines = [
        "# WARNING: "
        + warning.replace("\n", " ").strip()
        for warning in warnings
    ]

    return "\n".join(comment_lines)

def render_dimension(
    dimension: SemanticDimension,
) -> str:
    """
    Génère le bloc LookML d'une dimension.
    """

    lines: list[str] = []

    warning_comments = render_warning_comments(
        dimension.warnings
    )

    if warning_comments:
        lines.append(warning_comments)

    lines.append(
        f"dimension: {dimension.name} {{"
    )

    lines.append(
        indent_text(
            render_quoted_parameter(
                "label",
                dimension.label,
            )
        )
    )

    if dimension.description:
        lines.append(
            indent_text(
                render_quoted_parameter(
                    "description",
                    dimension.description,
                )
            )
        )

    lines.append(
        indent_text(
            f"type: {dimension.field_type}"
        )
    )

    if dimension.primary_key:
        lines.append(
            indent_text(
                "primary_key: yes"
            )
        )

    if dimension.hidden:
        lines.append(
            indent_text(
                "hidden: yes"
            )
        )

    if dimension.sensitive:
        lines.append(
            indent_text(
                "# Sensitive field: access controls "
                "should be reviewed."
            )
        )

    if dimension.field_type == "date":
        lines.append(
            indent_text(
                "datatype: date"
            )
        )

    elif dimension.field_type == "date_time":
        lines.append(
            indent_text(
                "datatype: datetime"
            )
        )

    lines.append(
        indent_text(
            f"sql: {dimension.sql_expression} ;;"
        )
    )

    lines.append("}")

    return "\n".join(lines)

def render_measure(
    measure: SemanticMeasure,
) -> str:
    """
    Génère le bloc LookML d'une mesure.
    """

    lines: list[str] = []

    warning_comments = render_warning_comments(
        measure.warnings
    )

    if warning_comments:
        lines.append(warning_comments)

    lines.append(
        f"measure: {measure.name} {{"
    )

    lines.append(
        indent_text(
            render_quoted_parameter(
                "label",
                measure.label,
            )
        )
    )

    if measure.description:
        lines.append(
            indent_text(
                render_quoted_parameter(
                    "description",
                    measure.description,
                )
            )
        )

    lines.append(
        indent_text(
            f"type: {measure.measure_type}"
        )
    )

    if measure.sql_expression:
        lines.append(
            indent_text(
                f"sql: {measure.sql_expression} ;;"
            )
        )

    if measure.value_format:
        lines.append(
            indent_text(
                render_quoted_parameter(
                    "value_format",
                    measure.value_format,
                )
            )
        )

    lines.append("}")

    return "\n".join(lines)

def render_view(
    view: SemanticViewSpecification,
    default_schema: str,
) -> GeneratedLookMLFile:
    """
    Génère un fichier .view.lkml en mémoire.
    """

    lines: list[str] = []

    lines.append(
        f"# Generated from {view.source_file}"
    )

    lines.append(
        f"# Validation status: "
        f"{view.validation_status}"
    )

    view_warnings = render_warning_comments(
        view.warnings
    )

    if view_warnings:
        lines.append(view_warnings)

    lines.append("")

    lines.append(
        f"view: {view.view_name} {{"
    )

    lines.append(
        indent_text(
            f"sql_table_name: "
            f"{default_schema}."
            f"{view.source_table_name} ;;"
        )
    )

    lines.append("")

    for index, dimension in enumerate(
        view.dimensions
    ):
        rendered_dimension = render_dimension(
            dimension
        )

        lines.append(
            indent_text(
                rendered_dimension
            )
        )

        if (
            index < len(view.dimensions) - 1
            or view.measures
        ):
            lines.append("")

    for index, measure in enumerate(
        view.measures
    ):
        rendered_measure = render_measure(
            measure
        )

        lines.append(
            indent_text(
                rendered_measure
            )
        )

        if index < len(view.measures) - 1:
            lines.append("")

    lines.append("}")

    content = "\n".join(lines).rstrip() + "\n"

    warnings = list(view.warnings)

    for dimension in view.dimensions:
        warnings.extend(dimension.warnings)

    for measure in view.measures:
        warnings.extend(measure.warnings)

    return GeneratedLookMLFile(
        file_name=(
            f"{view.view_name}.view.lkml"
        ),
        file_type="view",
        content=content,
        source_name=view.view_name,
        warnings=list(
            dict.fromkeys(warnings)
        ),
    )

def render_join(
    join: SemanticJoin,
) -> str:
    """
    Génère un bloc join LookML.

    Ce bloc doit être placé dans un Explore.
    """

    lines: list[str] = []

    warning_comments = render_warning_comments(
        join.warnings
    )

    if warning_comments:
        lines.append(warning_comments)

    lines.append(
        f"join: {join.name} {{"
    )

    lines.append(
        indent_text(
            "type: left_outer"
        )
    )

    lines.append(
        indent_text(
            f"relationship: {join.relationship}"
        )
    )

    lines.append(
        indent_text(
            f"sql_on: {join.sql_on} ;;"
        )
    )

    lines.append("}")

    return "\n".join(lines)

def render_explore(
    view: SemanticViewSpecification,
) -> str:
    """
    Génère l'Explore correspondant à une vue.
    """

    lines: list[str] = []

    lines.append(
        f"explore: {view.view_name} {{"
    )

    for index, join in enumerate(view.joins):
        if index == 0:
            lines.append("")

        lines.append(
            indent_text(
                render_join(join)
            )
        )

        if index < len(view.joins) - 1:
            lines.append("")

    lines.append("}")

    return "\n".join(lines)

def render_model(
    model: SemanticModelSpecification,
) -> GeneratedLookMLFile:
    """
    Génère le fichier .model.lkml en mémoire.
    """

    if not model.connection_name:
        raise ValueError(
            "La connexion Looker est obligatoire "
            "pour générer le fichier modèle."
        )

    lines: list[str] = []

    lines.append(
        "# Generated by Semantic Layer Builder"
    )

    lines.append(
        f"# Project: {model.project_name}"
    )

    lines.append("")

    lines.append(
        render_quoted_parameter(
            "connection",
            model.connection_name,
        )
    )

    lines.append(
        'include: "/*.view.lkml"'
    )

    lines.append("")

    for index, view in enumerate(model.views):
        lines.append(
            render_explore(view)
        )

        if index < len(model.views) - 1:
            lines.append("")

    content = "\n".join(lines).rstrip() + "\n"

    warnings = list(model.warnings)

    for view in model.views:
        warnings.extend(view.warnings)

    return GeneratedLookMLFile(
        file_name=(
            f"{model.model_name}.model.lkml"
        ),
        file_type="model",
        content=content,
        source_name=model.model_name,
        warnings=list(
            dict.fromkeys(warnings)
        ),
    )

def render_lookml_artifacts(
    model: SemanticModelSpecification,
) -> LookMLGenerationResult:
    """
    Transforme un modèle sémantique en artefacts LookML.

    Les artefacts sont générés en mémoire.
    Aucun fichier n'est écrit sur le disque.
    """

    if not model.generation_ready:
        return LookMLGenerationResult(
            model_name=model.model_name,
            generation_status="blocked",
            files=[],
            output_directory=None,
            written_files=[],
            missing_information=(
                model.missing_information
            ),
            warnings=model.warnings,
        )

    if not model.default_schema:
        return LookMLGenerationResult(
            model_name=model.model_name,
            generation_status="blocked",
            files=[],
            output_directory=None,
            written_files=[],
            missing_information=[
                "Nom du schéma ou dataset physique."
            ],
            warnings=model.warnings,
        )

    if not model.connection_name:
        return LookMLGenerationResult(
            model_name=model.model_name,
            generation_status="blocked",
            files=[],
            output_directory=None,
            written_files=[],
            missing_information=[
                "Nom de la connexion Looker."
            ],
            warnings=model.warnings,
        )

    generated_files: list[
        GeneratedLookMLFile
    ] = []

    for view in model.views:
        generated_files.append(
            render_view(
                view=view,
                default_schema=model.default_schema,
            )
        )

    generated_files.append(
        render_model(model)
    )

    all_warnings: list[str] = list(
        model.warnings
    )

    for generated_file in generated_files:
        all_warnings.extend(
            generated_file.warnings
        )

    unique_warnings = list(
        dict.fromkeys(all_warnings)
    )

    if unique_warnings:
        generation_status = (
            "generated_with_warnings"
        )

    else:
        generation_status = "generated"

    return LookMLGenerationResult(
        model_name=model.model_name,
        generation_status=generation_status,
        files=generated_files,
        output_directory=None,
        written_files=[],
        missing_information=[],
        warnings=unique_warnings,
    )

