from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


CardinalityInput = Literal[
    "one-to-one",
    "one-to-many",
    "many-to-one",
    "many-to-many",
    "unknown",
]


class MetadataAnalysisRequest(BaseModel):
    """
    Requête d'analyse des métadonnées
    techniques d'un fichier CSV.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    file_path: str = Field(
        min_length=1,
        description=(
            "Chemin du fichier CSV à analyser."
        ),
        examples=[
            "data/inputs/clients.csv",
        ],
    )


class DocumentationAnalysisRequest(BaseModel):
    """
    Requête d'analyse d'une documentation
    métier Markdown ou TXT.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    file_path: str = Field(
        min_length=1,
        description=(
            "Chemin de la documentation métier "
            "à analyser."
        ),
        examples=[
            "data/documentation/"
            "clients_documentation.md",
        ],
    )


class ConsistencyAnalysisRequest(BaseModel):
    """
    Requête de comparaison entre un fichier CSV
    et sa documentation métier.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    csv_file_path: str = Field(
        min_length=1,
        description=(
            "Chemin du fichier CSV à comparer."
        ),
        examples=[
            "data/inputs/clients.csv",
        ],
    )

    documentation_file_path: str = Field(
        min_length=1,
        description=(
            "Chemin de la documentation métier "
            "associée au fichier CSV."
        ),
        examples=[
            "data/documentation/"
            "clients_documentation.md",
        ],
    )


class RelationshipAnalysisRequest(BaseModel):
    """
    Requête d'analyse d'une relation
    entre deux fichiers CSV.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    source_file_path: str = Field(
        min_length=1,
        description=(
            "Chemin du fichier CSV source contenant "
            "généralement la clé étrangère."
        ),
        examples=[
            "data/inputs/orders.csv",
        ],
    )

    source_column: str = Field(
        min_length=1,
        description=(
            "Nom de la colonne source de la relation."
        ),
        examples=[
            "CLIENT_ID",
        ],
    )

    target_file_path: str = Field(
        min_length=1,
        description=(
            "Chemin du fichier CSV cible contenant "
            "généralement la clé de référence."
        ),
        examples=[
            "data/inputs/clients.csv",
        ],
    )

    target_column: str = Field(
        min_length=1,
        description=(
            "Nom de la colonne cible de la relation."
        ),
        examples=[
            "CLIENT_ID",
        ],
    )

    documented_cardinality: CardinalityInput = Field(
        description=(
            "Cardinalité documentée de la source "
            "vers la cible."
        ),
        examples=[
            "many-to-one",
        ],
    )


class LookMLProjectRequest(BaseModel):
    """
    Requête de prévisualisation d'un projet LookML.

    Tous les paramètres nécessaires à la génération
    LookML doivent être fournis.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    model_name: str = Field(
        min_length=1,
        description=(
            "Nom du modèle LookML."
        ),
        examples=[
            "sales",
        ],
    )

    project_name: str = Field(
        min_length=1,
        description=(
            "Nom du projet LookML."
        ),
        examples=[
            "semantic_layer_builder",
        ],
    )

    clients_csv_path: str = Field(
        min_length=1,
        description=(
            "Chemin du fichier CSV CLIENTS."
        ),
        examples=[
            "data/inputs/clients.csv",
        ],
    )

    clients_documentation_path: str = Field(
        min_length=1,
        description=(
            "Chemin de la documentation métier CLIENTS."
        ),
        examples=[
            "data/documentation/"
            "clients_documentation.md",
        ],
    )

    orders_csv_path: str = Field(
        min_length=1,
        description=(
            "Chemin du fichier CSV ORDERS."
        ),
        examples=[
            "data/inputs/orders.csv",
        ],
    )

    orders_documentation_path: str = Field(
        min_length=1,
        description=(
            "Chemin de la documentation métier ORDERS."
        ),
        examples=[
            "data/documentation/"
            "orders_documentation.md",
        ],
    )

    relationship_source_column: str = Field(
        min_length=1,
        description=(
            "Colonne source de la relation, située "
            "généralement dans ORDERS."
        ),
        examples=[
            "CLIENT_ID",
        ],
    )

    relationship_target_column: str = Field(
        min_length=1,
        description=(
            "Colonne cible de la relation, située "
            "généralement dans CLIENTS."
        ),
        examples=[
            "CLIENT_ID",
        ],
    )

    documented_cardinality: CardinalityInput = Field(
        description=(
            "Cardinalité documentée de la source "
            "vers la cible."
        ),
        examples=[
            "many-to-one",
        ],
    )

    connection_name: str = Field(
        min_length=1,
        description=(
            "Nom de la connexion Looker."
        ),
        examples=[
            "bigquery_connection",
        ],
    )

    default_schema: str = Field(
        min_length=1,
        description=(
            "Nom du schéma ou dataset physique."
        ),
        examples=[
            "analytics",
        ],
    )


class SemanticModelBuildRequest(BaseModel):
    """
    Requête de construction d'un modèle sémantique
    sans génération de fichiers LookML.

    La connexion Looker et le schéma physique sont
    facultatifs afin de permettre la création
    d'un brouillon de modèle sémantique.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    model_name: str = Field(
        min_length=1,
        description=(
            "Nom du modèle sémantique."
        ),
        examples=[
            "sales",
        ],
    )

    project_name: str = Field(
        min_length=1,
        description=(
            "Nom du projet LookML cible."
        ),
        examples=[
            "semantic_layer_builder",
        ],
    )

    clients_csv_path: str = Field(
        min_length=1,
        description=(
            "Chemin du fichier CSV CLIENTS."
        ),
        examples=[
            "data/inputs/clients.csv",
        ],
    )

    clients_documentation_path: str = Field(
        min_length=1,
        description=(
            "Chemin de la documentation métier CLIENTS."
        ),
        examples=[
            "data/documentation/"
            "clients_documentation.md",
        ],
    )

    orders_csv_path: str = Field(
        min_length=1,
        description=(
            "Chemin du fichier CSV ORDERS."
        ),
        examples=[
            "data/inputs/orders.csv",
        ],
    )

    orders_documentation_path: str = Field(
        min_length=1,
        description=(
            "Chemin de la documentation métier ORDERS."
        ),
        examples=[
            "data/documentation/"
            "orders_documentation.md",
        ],
    )

    relationship_source_column: str = Field(
        min_length=1,
        description=(
            "Colonne source de la relation."
        ),
        examples=[
            "CLIENT_ID",
        ],
    )

    relationship_target_column: str = Field(
        min_length=1,
        description=(
            "Colonne cible de la relation."
        ),
        examples=[
            "CLIENT_ID",
        ],
    )

    documented_cardinality: CardinalityInput = Field(
        description=(
            "Cardinalité documentée de la source "
            "vers la cible."
        ),
        examples=[
            "many-to-one",
        ],
    )

    connection_name: str | None = Field(
        default=None,
        description=(
            "Nom facultatif de la connexion Looker."
        ),
        examples=[
            "bigquery_connection",
        ],
    )

    default_schema: str | None = Field(
        default=None,
        description=(
            "Nom facultatif du schéma ou dataset physique."
        ),
        examples=[
            "analytics",
        ],
    )


class LookMLGenerationRequest(
    LookMLProjectRequest
):
    """
    Requête de génération et d'écriture
    des fichiers LookML.

    Cette requête étend LookMLProjectRequest
    avec les paramètres liés à l'écriture.
    """

    output_directory: str = Field(
        default="data/outputs/lookml",
        min_length=1,
        description=(
            "Répertoire de sortie des fichiers LookML. "
            "Le répertoire doit rester dans la racine "
            "autorisée par le serveur."
        ),
        examples=[
            "data/outputs/lookml",
        ],
    )

    overwrite: bool = Field(
        default=False,
        description=(
            "Autorise explicitement l'écrasement "
            "des fichiers LookML existants."
        ),
    )


class HealthResponse(BaseModel):
    """
    Réponse de l'endpoint de santé de l'API.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    status: Literal["healthy"] = Field(
        description=(
            "État de santé du service."
        ),
    )

    service: str = Field(
        min_length=1,
        description=(
            "Nom du service."
        ),
    )

    version: str = Field(
        min_length=1,
        description=(
            "Version actuelle de l'API."
        ),
    )