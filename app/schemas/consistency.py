from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ConsistencyStatus = Literal[
    "consistent",
    "warning",
    "inconsistent",
    "not_verifiable",
]


ConsistencyLevel = Literal[
    "excellent",
    "good",
    "warning",
    "critical",
]

class ColumnConsistencyResult(BaseModel):
    """
    Représente la comparaison entre une colonne technique
    et sa définition dans la documentation métier.
    """

    model_config = ConfigDict(extra="forbid")

    column_name: str = Field(
        min_length=1,
        description="Nom de la colonne comparée.",
    )

    exists_in_data: bool = Field(
        description=(
            "Indique si la colonne existe dans le CSV."
        ),
    )

    exists_in_documentation: bool = Field(
        description=(
            "Indique si la colonne est décrite "
            "dans la documentation."
        ),
    )

    technical_type: str | None = Field(
        default=None,
        description=(
            "Type sémantique détecté dans les données."
        ),
    )

    documented_type: str | None = Field(
        default=None,
        description=(
            "Type métier déclaré dans la documentation."
        ),
    )

    type_status: ConsistencyStatus = Field(
        default="not_verifiable",
        description=(
            "Résultat de la comparaison des types."
        ),
    )

    technical_nullable: bool | None = Field(
        default=None,
        description=(
            "Présence observée de valeurs nulles."
        ),
    )

    documented_required: bool | None = Field(
        default=None,
        description=(
            "Caractère obligatoire déclaré "
            "dans la documentation."
        ),
    )

    nullability_status: ConsistencyStatus = Field(
        default="not_verifiable",
        description=(
            "Résultat de la comparaison de nullabilité."
        ),
    )

    technical_unique: bool | None = Field(
        default=None,
        description=(
            "Indique si les valeurs observées sont uniques."
        ),
    )

    documented_unique: bool | None = Field(
        default=None,
        description=(
            "Unicité déclarée dans la documentation."
        ),
    )

    uniqueness_status: ConsistencyStatus = Field(
        default="not_verifiable",
        description=(
            "Résultat de la comparaison de l'unicité."
        ),
    )

    overall_status: ConsistencyStatus = Field(
        description=(
            "Statut global de cohérence de la colonne."
        ),
    )

    issues: list[str] = Field(
        default_factory=list,
        description=(
            "Incohérences et risques détectés."
        ),
    )

    recommendations: list[str] = Field(
        default_factory=list,
        description=(
            "Actions recommandées pour la colonne."
        ),
    )


class PrimaryKeyConsistencyResult(BaseModel):
    """
    Représente la comparaison entre la clé primaire
    documentée et les candidats techniques.
    """

    model_config = ConfigDict(extra="forbid")

    documented_primary_key: str | None = Field(
        default=None,
        description=(
            "Clé primaire déclarée dans la documentation."
        ),
    )

    technical_candidates: list[str] = Field(
        default_factory=list,
        description=(
            "Clés primaires candidates détectées "
            "techniquement."
        ),
    )

    recommended_technical_candidate: str | None = Field(
        default=None,
        description=(
            "Candidate technique recommandée."
        ),
    )

    status: ConsistencyStatus = Field(
        description=(
            "Statut de cohérence de la clé primaire."
        ),
    )

    issues: list[str] = Field(
        default_factory=list,
        description=(
            "Incohérences relatives à la clé primaire."
        ),
    )

    recommendations: list[str] = Field(
        default_factory=list,
        description=(
            "Actions recommandées."
        ),
    )


class BusinessRuleValidationResult(BaseModel):
    """
    Représente le résultat de validation technique
    d'une règle métier documentée.
    """

    model_config = ConfigDict(extra="forbid")

    rule_id: str = Field(
        min_length=1,
        description="Identifiant de la règle métier.",
    )

    description: str = Field(
        min_length=1,
        description="Texte de la règle métier.",
    )

    related_columns: list[str] = Field(
        default_factory=list,
        description=(
            "Colonnes associées à la règle."
        ),
    )

    status: ConsistencyStatus = Field(
        description=(
            "Statut de validation de la règle."
        ),
    )

    evidence: list[str] = Field(
        default_factory=list,
        description=(
            "Éléments techniques utilisés pour la validation."
        ),
    )

    issues: list[str] = Field(
        default_factory=list,
        description=(
            "Problèmes détectés pendant la validation."
        ),
    )


class ConsistencyReport(BaseModel):
    """
    Rapport global de comparaison entre les métadonnées
    techniques et la documentation métier.
    """

    model_config = ConfigDict(extra="forbid")

    data_source_file: str = Field(
        min_length=1,
        description="Nom du fichier CSV analysé.",
    )

    documentation_source_file: str = Field(
        min_length=1,
        description="Nom du document métier analysé.",
    )

    technical_table_name: str = Field(
        min_length=1,
        description=(
            "Nom de table calculé depuis le CSV."
        ),
    )

    documented_table_name: str | None = Field(
        default=None,
        description=(
            "Nom de table extrait de la documentation."
        ),
    )

    table_name_status: ConsistencyStatus = Field(
        description=(
            "Cohérence entre les noms de table."
        ),
    )

    consistency_score: int = Field(
        ge=0,
        le=100,
        description=(
            "Score heuristique global de cohérence."
        ),
    )

    consistency_level: ConsistencyLevel = Field(
        description=(
            "Niveau global associé au score."
        ),
    )

    column_results: list[ColumnConsistencyResult] = Field(
        default_factory=list,
        description=(
            "Résultats détaillés pour les colonnes."
        ),
    )

    primary_key_result: PrimaryKeyConsistencyResult = Field(
        description=(
            "Résultat de cohérence de la clé primaire."
        ),
    )

    business_rule_results: list[
        BusinessRuleValidationResult
    ] = Field(
        default_factory=list,
        description=(
            "Résultats de validation des règles métier."
        ),
    )

    undocumented_columns: list[str] = Field(
        default_factory=list,
        description=(
            "Colonnes techniques absentes "
            "de la documentation."
        ),
    )

    missing_data_columns: list[str] = Field(
        default_factory=list,
        description=(
            "Colonnes documentées mais absentes du CSV."
        ),
    )

    documented_relationships: int = Field(
        ge=0,
        description=(
            "Nombre de relations déclarées "
            "dans la documentation."
        ),
    )

    warnings: list[str] = Field(
        default_factory=list,
        description=(
            "Avertissements globaux."
        ),
    )

    recommendations: list[str] = Field(
        default_factory=list,
        description=(
            "Recommandations globales."
        ),
    )


