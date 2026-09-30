from typing import Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


SemanticType = Literal[
    "integer",
    "float",
    "boolean",
    "date",
    "string",
]

ConfidenceLevel = Literal[
    "low",
    "medium",
    "high",
]

QualityLevel = Literal[
    "excellent",
    "good",
    "warning",
    "critical",
]

class ColumnMetadata(BaseModel):
    """
    Représente les métadonnées techniques et sémantiques
    d'une colonne provenant d'un fichier tabulaire.
    """

    model_config = ConfigDict(extra="forbid")

    name: str = Field(
        min_length=1,
        description="Nom de la colonne.",
    )

    pandas_type: str = Field(
        min_length=1,
        description="Type technique détecté par Pandas.",
    )

    semantic_type: SemanticType = Field(
        description="Type simplifié utilisé par la couche sémantique.",
    )

    nullable: bool = Field(
        description="Indique si la colonne contient au moins une valeur nulle.",
    )

    null_count: int = Field(
        ge=0,
        description="Nombre de valeurs nulles dans la colonne.",
    )

    unique_count: int = Field(
        ge=0,
        description="Nombre de valeurs distinctes non nulles.",
    )

    sample_values: list[Any] = Field(
        default_factory=list,
        max_length=3,
        description="Exemples de valeurs provenant de la colonne.",
    )


class PrimaryKeyCandidate(BaseModel):
    """
    Représente l'évaluation technique d'une colonne
    pouvant servir de clé primaire.
    """

    model_config = ConfigDict(extra="forbid")

    column_name: str = Field(
        min_length=1,
        description="Nom de la colonne candidate.",
    )

    score: int = Field(
        ge=0,
        le=100,
        description=(
            "Score heuristique compris entre 0 et 100. "
            "Ce score ne constitue pas une confirmation métier."
        ),
    )

    confidence: ConfidenceLevel = Field(
        description=(
            "Niveau de confiance technique associé au score."
        ),
    )

    reasons: list[str] = Field(
        default_factory=list,
        description=(
            "Raisons techniques ayant augmenté le score."
        ),
    )

    warnings: list[str] = Field(
        default_factory=list,
        description=(
            "Limites et risques associés à la colonne."
        ),
    )

    recommended: bool = Field(
        default=False,
        description=(
            "Indique si cette colonne est la candidate "
            "technique recommandée."
        ),
    )


class DataQualityReport(BaseModel):
    """
    Représente le résultat de l'analyse technique
    de qualité d'un fichier tabulaire.
    """

    model_config = ConfigDict(extra="forbid")

    quality_score: int = Field(
        ge=0,
        le=100,
        description=(
            "Score technique de qualité compris entre 0 et 100."
        ),
    )

    quality_level: QualityLevel = Field(
        description=(
            "Niveau de qualité associé au score technique."
        ),
    )

    total_null_values: int = Field(
        ge=0,
        description=(
            "Nombre total de valeurs nulles dans le fichier."
        ),
    )

    duplicate_row_count: int = Field(
        ge=0,
        description=(
            "Nombre de lignes entièrement dupliquées."
        ),
    )

    duplicate_row_ratio: float = Field(
        ge=0,
        le=1,
        description=(
            "Proportion de lignes entièrement dupliquées."
        ),
    )

    constant_columns: list[str] = Field(
        default_factory=list,
        description=(
            "Colonnes contenant une seule valeur distincte."
        ),
    )

    high_null_columns: list[str] = Field(
        default_factory=list,
        description=(
            "Colonnes dont le taux de valeurs nulles "
            "est supérieur ou égal à 30 pour cent."
        ),
    )

    warnings: list[str] = Field(
        default_factory=list,
        description=(
            "Problèmes techniques détectés pendant l'analyse."
        ),
    )

    recommendations: list[str] = Field(
        default_factory=list,
        description=(
            "Actions recommandées pour améliorer les données."
        ),
    )


class TableMetadata(BaseModel):
    """
    Représente les métadonnées complètes d'une table
    extraite depuis un fichier CSV.
    """

    model_config = ConfigDict(extra="forbid")

    file_name: str = Field(
        min_length=1,
        description="Nom du fichier source.",
    )

    table_name: str = Field(
        min_length=1,
        description="Nom logique de la table.",
    )

    file_path: str = Field(
        min_length=1,
        description="Chemin absolu du fichier analysé.",
    )

    row_count: int = Field(
        ge=0,
        description="Nombre total de lignes.",
    )

    column_count: int = Field(
        ge=1,
        description="Nombre total de colonnes.",
    )

    primary_key_candidates: list[str] = Field(
        default_factory=list,
        description="Colonnes pouvant représenter une clé primaire.",
    )

    primary_key_analysis: list[PrimaryKeyCandidate] = Field(
        default_factory=list,
        description=(
           "Évaluation détaillée des clés primaires candidates."
        ),
    )

    quality_report: DataQualityReport = Field(
        description=(
            "Rapport technique de qualité des données."
        ),
    )
    
    columns: list[ColumnMetadata] = Field(
        min_length=1,
        description="Métadonnées détaillées des colonnes.",
    )
    
    @model_validator(mode="after")
    def validate_table_consistency(self) -> "TableMetadata":
        """
        Vérifie la cohérence globale des métadonnées.
        """

        if self.column_count != len(self.columns):
            raise ValueError(
                "column_count doit être égal au nombre "
                "d'éléments présents dans columns."
            )

        column_names = {
            column.name
            for column in self.columns
        }

        unknown_candidates = [
            candidate
            for candidate in self.primary_key_candidates
            if candidate not in column_names
        ]

        if unknown_candidates:
            raise ValueError(
                "Certaines clés candidates ne correspondent "
                "à aucune colonne : "
                + ", ".join(unknown_candidates)
            )

        return self


