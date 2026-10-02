from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


LookMLFileType = Literal[
    "view",
    "model",
]


class GeneratedLookMLFile(BaseModel):
    """
    Représente un fichier LookML généré en mémoire.
    """

    model_config = ConfigDict(extra="forbid")

    file_name: str = Field(
        min_length=1,
        description="Nom du fichier LookML.",
    )

    file_type: LookMLFileType = Field(
        description="Type du fichier LookML.",
    )

    content: str = Field(
        min_length=1,
        description="Contenu LookML généré.",
    )

    source_name: str = Field(
        min_length=1,
        description=(
            "Nom de la vue ou du modèle source."
        ),
    )

    warnings: list[str] = Field(
        default_factory=list,
        description=(
            "Avertissements associés au fichier."
        ),
    )


class LookMLGenerationResult(BaseModel):
    """
    Représente le résultat complet
    d'une génération LookML.
    """

    model_config = ConfigDict(extra="forbid")

    model_name: str = Field(
        min_length=1,
        description="Nom du modèle généré.",
    )

    generation_status: Literal[
        "generated",
        "blocked",
        "generated_with_warnings",
    ] = Field(
        description="Statut global de génération.",
    )

    files: list[GeneratedLookMLFile] = Field(
        default_factory=list,
        description="Fichiers LookML générés.",
    )

    output_directory: str | None = Field(
        default=None,
        description=(
            "Répertoire de sortie des fichiers."
        ),
    )

    written_files: list[str] = Field(
        default_factory=list,
        description=(
            "Chemins des fichiers réellement écrits."
        ),
    )

    missing_information: list[str] = Field(
        default_factory=list,
        description=(
            "Informations empêchant la génération."
        ),
    )

    warnings: list[str] = Field(
        default_factory=list,
        description=(
            "Avertissements globaux."
        ),
    )