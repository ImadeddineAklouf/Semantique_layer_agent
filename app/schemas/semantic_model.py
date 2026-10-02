from typing import Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


SemanticFieldType = Literal[
    "string",
    "number",
    "yesno",
    "date",
    "date_time",
    "unknown",
]


SemanticMeasureType = Literal[
    "count",
    "count_distinct",
    "sum",
    "average",
    "min",
    "max",
]


SemanticJoinRelationship = Literal[
    "one_to_one",
    "one_to_many",
    "many_to_one",
    "many_to_many",
    "unknown",
]


ValidationStatus = Literal[
    "validated",
    "warning",
    "requires_review",
]

class SemanticDimension(BaseModel):
    """
    Représente une dimension destinée à la couche sémantique.
    """

    model_config = ConfigDict(extra="forbid")

    name: str = Field(
        min_length=1,
        description=(
            "Nom technique normalisé de la dimension."
        ),
    )

    source_column: str = Field(
        min_length=1,
        description=(
            "Nom de la colonne physique source."
        ),
    )

    label: str = Field(
        min_length=1,
        description=(
            "Libellé lisible de la dimension."
        ),
    )

    description: str | None = Field(
        default=None,
        description=(
            "Description métier de la dimension."
        ),
    )

    field_type: SemanticFieldType = Field(
        description=(
            "Type sémantique destiné au futur LookML."
        ),
    )

    sql_expression: str = Field(
        min_length=1,
        description=(
            "Expression SQL de la dimension."
        ),
    )

    primary_key: bool = Field(
        default=False,
        description=(
            "Indique si la dimension représente "
            "la clé primaire métier validée."
        ),
    )

    hidden: bool = Field(
        default=False,
        description=(
            "Indique si la dimension doit être masquée."
        ),
    )

    sensitive: bool = Field(
        default=False,
        description=(
            "Indique si la dimension contient "
            "une donnée sensible."
        ),
    )

    required: bool | None = Field(
        default=None,
        description=(
            "Indique si la donnée est obligatoire "
            "selon la documentation."
        ),
    )

    unique: bool | None = Field(
        default=None,
        description=(
            "Indique si la donnée est documentée "
            "comme unique."
        ),
    )

    allowed_values: list[str] = Field(
        default_factory=list,
        description=(
            "Valeurs autorisées documentées."
        ),
    )

    validation_status: ValidationStatus = Field(
        default="validated",
        description=(
            "Niveau de validation de la dimension."
        ),
    )

    warnings: list[str] = Field(
        default_factory=list,
        description=(
            "Avertissements associés à la dimension."
        ),
    )


class SemanticMeasure(BaseModel):
    """
    Représente une mesure destinée à la couche sémantique.
    """

    model_config = ConfigDict(extra="forbid")

    name: str = Field(
        min_length=1,
        description="Nom technique de la mesure.",
    )

    label: str = Field(
        min_length=1,
        description="Libellé lisible de la mesure.",
    )

    description: str | None = Field(
        default=None,
        description="Description métier de la mesure.",
    )

    measure_type: SemanticMeasureType = Field(
        description="Type d'agrégation de la mesure.",
    )

    source_column: str | None = Field(
        default=None,
        description=(
            "Colonne source utilisée par la mesure."
        ),
    )

    sql_expression: str | None = Field(
        default=None,
        description=(
            "Expression SQL de la mesure."
        ),
    )

    value_format: str | None = Field(
        default=None,
        description=(
            "Format d'affichage futur de la mesure."
        ),
    )

    validation_status: ValidationStatus = Field(
        default="validated",
        description=(
            "Niveau de validation de la mesure."
        ),
    )

    warnings: list[str] = Field(
        default_factory=list,
        description=(
            "Avertissements associés à la mesure."
        ),
    )


class SemanticJoin(BaseModel):
    """
    Représente une jointure validée entre deux vues.
    """

    model_config = ConfigDict(extra="forbid")

    name: str = Field(
        min_length=1,
        description=(
            "Nom de la vue ou table cible."
        ),
    )

    source_table: str = Field(
        min_length=1,
        description="Nom de la table source.",
    )

    source_column: str = Field(
        min_length=1,
        description="Colonne source de la jointure.",
    )

    target_table: str = Field(
        min_length=1,
        description="Nom de la table cible.",
    )

    target_column: str = Field(
        min_length=1,
        description="Colonne cible de la jointure.",
    )

    relationship: SemanticJoinRelationship = Field(
        description=(
            "Cardinalité utilisée dans la couche sémantique."
        ),
    )

    sql_on: str = Field(
        min_length=1,
        description=(
            "Condition SQL de la jointure."
        ),
    )

    foreign_key_match_ratio: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description=(
            "Taux de correspondance observé "
            "pour la clé étrangère."
        ),
    )

    orphan_value_count: int | None = Field(
        default=None,
        ge=0,
        description=(
            "Nombre de valeurs orphelines détectées."
        ),
    )

    validation_status: ValidationStatus = Field(
        default="validated",
        description=(
            "Niveau de validation de la jointure."
        ),
    )

    warnings: list[str] = Field(
        default_factory=list,
        description=(
            "Avertissements associés à la jointure."
        ),
    )


class SemanticViewSpecification(BaseModel):
    """
    Représente la spécification complète d'une vue sémantique.
    """

    model_config = ConfigDict(extra="forbid")

    view_name: str = Field(
        min_length=1,
        description=(
            "Nom normalisé de la future vue LookML."
        ),
    )

    source_table_name: str = Field(
        min_length=1,
        description=(
            "Nom de la table physique source."
        ),
    )

    source_file: str = Field(
        min_length=1,
        description=(
            "Fichier utilisé pour construire la spécification."
        ),
    )

    label: str = Field(
        min_length=1,
        description=(
            "Libellé métier de la vue."
        ),
    )

    description: str | None = Field(
        default=None,
        description=(
            "Description générale de la vue."
        ),
    )

    primary_key: str | None = Field(
        default=None,
        description=(
            "Nom de la colonne retenue comme clé primaire."
        ),
    )

    dimensions: list[SemanticDimension] = Field(
        min_length=1,
        description=(
            "Dimensions de la vue sémantique."
        ),
    )

    measures: list[SemanticMeasure] = Field(
        default_factory=list,
        description=(
            "Mesures de la vue sémantique."
        ),
    )

    joins: list[SemanticJoin] = Field(
        default_factory=list,
        description=(
            "Jointures validées depuis cette vue."
        ),
    )

    sensitive_fields: list[str] = Field(
        default_factory=list,
        description=(
            "Liste des champs sensibles."
        ),
    )

    documented_rules: list[str] = Field(
        default_factory=list,
        description=(
            "Règles métier associées à la vue."
        ),
    )

    validation_status: ValidationStatus = Field(
        description=(
            "Statut global de validation de la vue."
        ),
    )

    warnings: list[str] = Field(
        default_factory=list,
        description=(
            "Avertissements globaux de la vue."
        ),
    )

    recommendations: list[str] = Field(
        default_factory=list,
        description=(
            "Recommandations avant génération."
        ),
    )

    @model_validator(mode="after")
    def validate_view_consistency(
        self,
    ) -> "SemanticViewSpecification":
        """
        Vérifie la cohérence interne de la vue.
        """

        dimension_names = {
            dimension.name
            for dimension in self.dimensions
        }

        source_columns = {
            dimension.source_column
            for dimension in self.dimensions
        }

        if len(dimension_names) != len(self.dimensions):
            raise ValueError(
                "Les noms des dimensions doivent être uniques."
            )

        if self.primary_key is not None:
            if self.primary_key not in source_columns:
                raise ValueError(
                    "La clé primaire doit correspondre "
                    "à une colonne source des dimensions."
                )

            primary_key_dimensions = [
                dimension
                for dimension in self.dimensions
                if (
                    dimension.source_column
                    == self.primary_key
                    and dimension.primary_key
                )
            ]

            if len(primary_key_dimensions) != 1:
                raise ValueError(
                    "Une seule dimension doit être marquée "
                    "comme clé primaire."
                )

        unknown_sensitive_fields = [
            field_name
            for field_name in self.sensitive_fields
            if field_name not in source_columns
        ]

        if unknown_sensitive_fields:
            raise ValueError(
                "Certains champs sensibles ne correspondent "
                "à aucune dimension : "
                + ", ".join(unknown_sensitive_fields)
            )

        return self


class SemanticModelSpecification(BaseModel):
    """
    Représente la spécification sémantique globale
    préparant la génération LookML.
    """

    model_config = ConfigDict(extra="forbid")

    model_name: str = Field(
        min_length=1,
        description=(
            "Nom du modèle sémantique."
        ),
    )

    project_name: str = Field(
        min_length=1,
        description=(
            "Nom du projet LookML cible."
        ),
    )

    connection_name: str | None = Field(
        default=None,
        description=(
            "Nom de la future connexion Looker."
        ),
    )

    default_schema: str | None = Field(
        default=None,
        description=(
            "Schéma ou dataset physique par défaut."
        ),
    )

    views: list[SemanticViewSpecification] = Field(
        min_length=1,
        description=(
            "Vues composant le modèle sémantique."
        ),
    )

    generation_ready: bool = Field(
        description=(
            "Indique si la spécification est suffisamment "
            "complète pour lancer la génération."
        ),
    )

    missing_information: list[str] = Field(
        default_factory=list,
        description=(
            "Informations encore nécessaires "
            "avant génération finale."
        ),
    )

    warnings: list[str] = Field(
        default_factory=list,
        description=(
            "Avertissements globaux du modèle."
        ),
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Métadonnées complémentaires du modèle."
        ),
    )

    @model_validator(mode="after")
    def validate_model_consistency(
        self,
    ) -> "SemanticModelSpecification":
        """
        Vérifie la cohérence globale du modèle.
        """

        view_names = {
            view.view_name
            for view in self.views
        }

        if len(view_names) != len(self.views):
            raise ValueError(
                "Les noms des vues doivent être uniques."
            )

        if self.generation_ready:
            if self.missing_information:
                raise ValueError(
                    "Un modèle prêt à être généré ne doit "
                    "pas contenir d'informations manquantes."
                )

            invalid_views = [
                view.view_name
                for view in self.views
                if (
                    view.validation_status
                    == "requires_review"
                )
            ]

            if invalid_views:
                raise ValueError(
                    "Les vues suivantes nécessitent encore "
                    "une validation : "
                    + ", ".join(invalid_views)
                )

        return self


