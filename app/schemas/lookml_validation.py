from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


LookMLValidationSeverity = Literal[
    "error",
    "warning",
    "info",
]


class LookMLValidationIssue(BaseModel):
    """
    Représente un problème détecté
    dans un artefact LookML.
    """

    model_config = ConfigDict(extra="forbid")

    file_name: str = Field(
        min_length=1,
        description=(
            "Nom du fichier concerné."
        ),
    )

    severity: LookMLValidationSeverity = Field(
        description=(
            "Sévérité du problème."
        ),
    )

    code: str = Field(
        min_length=1,
        description=(
            "Code stable du problème."
        ),
    )

    message: str = Field(
        min_length=1,
        description=(
            "Description du problème."
        ),
    )

    object_name: str | None = Field(
        default=None,
        description=(
            "Objet LookML concerné."
        ),
    )


class LookMLFileValidationResult(BaseModel):
    """
    Résultat de validation d'un fichier LookML.
    """

    model_config = ConfigDict(extra="forbid")

    file_name: str = Field(
        min_length=1,
    )

    file_type: Literal[
        "view",
        "model",
    ]

    valid: bool

    issue_count: int = Field(
        ge=0,
    )

    issues: list[
        LookMLValidationIssue
    ] = Field(
        default_factory=list,
    )


class LookMLValidationReport(BaseModel):
    """
    Rapport global de validation locale LookML.
    """

    model_config = ConfigDict(extra="forbid")

    valid: bool

    validated_file_count: int = Field(
        ge=0,
    )

    error_count: int = Field(
        ge=0,
    )

    warning_count: int = Field(
        ge=0,
    )

    file_results: list[
        LookMLFileValidationResult
    ] = Field(
        default_factory=list,
    )

    issues: list[
        LookMLValidationIssue
    ] = Field(
        default_factory=list,
    )