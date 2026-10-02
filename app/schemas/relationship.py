from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


RelationshipStatus = Literal[
    "valid",
    "warning",
    "invalid",
    "not_verifiable",
]


CardinalityType = Literal[
    "one-to-one",
    "one-to-many",
    "many-to-one",
    "many-to-many",
    "unknown",
]

class RelationshipColumnValidation(BaseModel):
    """
    Représente la validation des colonnes
    impliquées dans une relation.
    """

    model_config = ConfigDict(extra="forbid")

    source_column_exists: bool = Field(
        description=(
            "Indique si la colonne source existe."
        ),
    )

    target_column_exists: bool = Field(
        description=(
            "Indique si la colonne cible existe."
        ),
    )

    source_column_type: str | None = Field(
        default=None,
        description=(
            "Type sémantique de la colonne source."
        ),
    )

    target_column_type: str | None = Field(
        default=None,
        description=(
            "Type sémantique de la colonne cible."
        ),
    )

    types_compatible: bool | None = Field(
        default=None,
        description=(
            "Indique si les types des deux colonnes "
            "sont compatibles."
        ),
    )

    status: RelationshipStatus = Field(
        description=(
            "Statut de validation des colonnes."
        ),
    )

    issues: list[str] = Field(
        default_factory=list,
        description=(
            "Problèmes relatifs aux colonnes."
        ),
    )


class ReferentialIntegrityResult(BaseModel):
    """
    Représente la vérification de l'intégrité référentielle.
    """

    model_config = ConfigDict(extra="forbid")

    total_foreign_key_values: int = Field(
        ge=0,
        description=(
            "Nombre total de valeurs de clé étrangère "
            "non nulles."
        ),
    )

    matched_foreign_key_values: int = Field(
        ge=0,
        description=(
            "Nombre de valeurs correspondant "
            "à une clé de la table cible."
        ),
    )

    orphan_value_count: int = Field(
        ge=0,
        description=(
            "Nombre de valeurs étrangères sans correspondance."
        ),
    )

    orphan_values: list[str] = Field(
        default_factory=list,
        max_length=20,
        description=(
            "Exemples de valeurs orphelines."
        ),
    )

    null_foreign_key_count: int = Field(
        ge=0,
        description=(
            "Nombre de clés étrangères nulles."
        ),
    )

    match_ratio: float = Field(
        ge=0,
        le=1,
        description=(
            "Proportion de clés étrangères "
            "ayant une correspondance."
        ),
    )

    status: RelationshipStatus = Field(
        description=(
            "Statut de l'intégrité référentielle."
        ),
    )


class CardinalityAnalysis(BaseModel):
    """
    Représente l'analyse technique de cardinalité.
    """

    model_config = ConfigDict(extra="forbid")

    documented_cardinality: CardinalityType = Field(
        description=(
            "Cardinalité déclarée dans la documentation."
        ),
    )

    detected_cardinality: CardinalityType = Field(
        description=(
            "Cardinalité détectée dans les données."
        ),
    )

    source_values_unique: bool = Field(
        description=(
            "Indique si les valeurs source sont uniques."
        ),
    )

    target_values_unique: bool = Field(
        description=(
            "Indique si les valeurs cible sont uniques."
        ),
    )

    status: RelationshipStatus = Field(
        description=(
            "Statut de cohérence de la cardinalité."
        ),
    )

    explanation: str = Field(
        min_length=1,
        description=(
            "Explication de la cardinalité détectée."
        ),
    )


class RelationshipAnalysisReport(BaseModel):
    """
    Rapport global d'analyse d'une relation
    entre deux tables.
    """

    model_config = ConfigDict(extra="forbid")

    source_file: str = Field(
        min_length=1,
        description="Fichier CSV source.",
    )

    target_file: str = Field(
        min_length=1,
        description="Fichier CSV cible.",
    )

    source_table: str = Field(
        min_length=1,
        description="Table source.",
    )

    source_column: str = Field(
        min_length=1,
        description="Colonne source de la relation.",
    )

    target_table: str = Field(
        min_length=1,
        description="Table cible.",
    )

    target_column: str = Field(
        min_length=1,
        description="Colonne cible de la relation.",
    )

    column_validation: RelationshipColumnValidation = Field(
        description=(
            "Validation des colonnes de jointure."
        ),
    )

    referential_integrity: ReferentialIntegrityResult = Field(
        description=(
            "Résultat d'intégrité référentielle."
        ),
    )

    cardinality_analysis: CardinalityAnalysis = Field(
        description=(
            "Analyse de la cardinalité."
        ),
    )

    overall_status: RelationshipStatus = Field(
        description=(
            "Statut global de la relation."
        ),
    )

    relationship_score: int = Field(
        ge=0,
        le=100,
        description=(
            "Score heuristique de validité de la relation."
        ),
    )

    warnings: list[str] = Field(
        default_factory=list,
        description=(
            "Avertissements détectés."
        ),
    )

    recommendations: list[str] = Field(
        default_factory=list,
        description=(
            "Actions recommandées."
        ),
    )


