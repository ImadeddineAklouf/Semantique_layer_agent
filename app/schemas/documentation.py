from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


DocumentFormat = Literal[
    "markdown",
    "text",
]

EvidenceType = Literal[
    "explicit",
    "inferred",
    "missing",
    "ambiguous",
]

RelationshipType = Literal[
    "one-to-one",
    "one-to-many",
    "many-to-one",
    "many-to-many",
    "unknown",
]

class DocumentSection(BaseModel):
    """
    Représente une section extraite d'un document.
    """

    model_config = ConfigDict(extra="forbid")

    title: str = Field(
        min_length=1,
        description="Titre de la section.",
    )

    level: int = Field(
        ge=1,
        le=6,
        description=(
            "Niveau hiérarchique du titre Markdown."
        ),
    )

    content: str = Field(
        description=(
            "Contenu textuel associé à la section."
        ),
    )


class DocumentMetadata(BaseModel):
    """
    Représente les informations générales
    d'un document analysé.
    """

    model_config = ConfigDict(extra="forbid")

    file_name: str = Field(
        min_length=1,
        description="Nom du fichier source.",
    )

    file_path: str = Field(
        min_length=1,
        description="Chemin absolu du document.",
    )

    document_format: DocumentFormat = Field(
        description="Format technique du document.",
    )

    title: str | None = Field(
        default=None,
        description=(
            "Titre principal détecté dans le document."
        ),
    )

    character_count: int = Field(
        ge=0,
        description=(
            "Nombre total de caractères dans le document."
        ),
    )

    word_count: int = Field(
        ge=0,
        description=(
            "Nombre approximatif de mots."
        ),
    )

    section_count: int = Field(
        ge=0,
        description=(
            "Nombre de sections détectées."
        ),
    )

    sections: list[DocumentSection] = Field(
        default_factory=list,
        description=(
            "Sections structurées extraites du document."
        ),
    )

    raw_content: str = Field(
        description=(
            "Contenu textuel complet du document."
        ),
    )


class DocumentedColumn(BaseModel):
    """
    Représente une colonne décrite dans la documentation métier.
    """

    model_config = ConfigDict(extra="forbid")

    name: str = Field(
        min_length=1,
        description="Nom de la colonne documentée.",
    )

    description: str | None = Field(
        default=None,
        description="Description métier de la colonne.",
    )

    business_type: str | None = Field(
        default=None,
        description="Type métier déclaré dans le document.",
    )

    expected_format: str | None = Field(
        default=None,
        description="Format attendu déclaré dans le document.",
    )

    required: bool | None = Field(
        default=None,
        description=(
            "Indique si la colonne est documentée "
            "comme obligatoire."
        ),
    )

    unique: bool | None = Field(
        default=None,
        description=(
            "Indique si la colonne est documentée "
            "comme unique."
        ),
    )

    sensitive: bool | None = Field(
        default=None,
        description=(
            "Indique si la colonne est documentée "
            "comme sensible."
        ),
    )

    allowed_values: list[str] = Field(
        default_factory=list,
        description="Valeurs autorisées documentées.",
    )

    evidence_type: EvidenceType = Field(
        default="explicit",
        description=(
            "Nature de la preuve documentaire."
        ),
    )


class BusinessRule(BaseModel):
    """
    Représente une règle métier déclarée dans le document.
    """

    model_config = ConfigDict(extra="forbid")

    rule_id: str = Field(
        min_length=1,
        description="Identifiant interne de la règle.",
    )

    description: str = Field(
        min_length=1,
        description="Texte complet de la règle métier.",
    )

    related_columns: list[str] = Field(
        default_factory=list,
        description=(
            "Colonnes explicitement mentionnées dans la règle."
        ),
    )

    evidence_type: EvidenceType = Field(
        default="explicit",
        description="Nature de la preuve documentaire.",
    )


class DocumentedRelationship(BaseModel):
    """
    Représente une relation entre deux tables
    explicitement décrite dans la documentation.
    """

    model_config = ConfigDict(extra="forbid")

    source_table: str = Field(
        min_length=1,
        description="Nom de la table source.",
    )

    source_column: str = Field(
        min_length=1,
        description="Colonne de jointure de la table source.",
    )

    target_table: str = Field(
        min_length=1,
        description="Nom de la table cible.",
    )

    target_column: str = Field(
        min_length=1,
        description="Colonne de jointure de la table cible.",
    )

    relationship_type: RelationshipType = Field(
        default="unknown",
        description="Type de relation documenté.",
    )

    cardinality_description: str | None = Field(
        default=None,
        description=(
            "Description textuelle de la cardinalité."
        ),
    )

    evidence_type: EvidenceType = Field(
        default="explicit",
        description="Nature de la preuve documentaire.",
    )


class SensitiveDataItem(BaseModel):
    """
    Représente une donnée identifiée comme sensible
    dans le document métier.
    """

    model_config = ConfigDict(extra="forbid")

    column_name: str = Field(
        min_length=1,
        description="Nom de la colonne sensible.",
    )

    risk_description: str | None = Field(
        default=None,
        description="Description du risque documenté.",
    )

    precautions: list[str] = Field(
        default_factory=list,
        description=(
            "Précautions explicitement indiquées."
        ),
    )

    evidence_type: EvidenceType = Field(
        default="explicit",
        description="Nature de la preuve documentaire.",
    )


class BusinessDocumentationAnalysis(BaseModel):
    """
    Représente l'analyse métier structurée
    extraite d'un document.
    """

    model_config = ConfigDict(extra="forbid")

    source_file: str = Field(
        min_length=1,
        description="Nom du document source.",
    )

    document_title: str | None = Field(
        default=None,
        description="Titre principal du document.",
    )

    table_name: str | None = Field(
        default=None,
        description="Nom de la table documentée.",
    )

    table_description: str | None = Field(
        default=None,
        description="Description métier générale de la table.",
    )

    documented_primary_key: str | None = Field(
        default=None,
        description=(
            "Clé primaire explicitement déclarée."
        ),
    )

    update_frequency: str | None = Field(
        default=None,
        description=(
            "Fréquence de mise à jour déclarée."
        ),
    )

    columns: list[DocumentedColumn] = Field(
        default_factory=list,
        description="Colonnes décrites dans le document.",
    )

    business_rules: list[BusinessRule] = Field(
        default_factory=list,
        description="Règles métier explicitement déclarées.",
    )

    relationships: list[DocumentedRelationship] = Field(
        default_factory=list,
        description="Relations documentées.",
    )

    sensitive_data: list[SensitiveDataItem] = Field(
        default_factory=list,
        description="Données sensibles documentées.",
    )

    missing_information: list[str] = Field(
        default_factory=list,
        description=(
            "Informations explicitement déclarées comme manquantes."
        ),
    )

    warnings: list[str] = Field(
        default_factory=list,
        description=(
            "Ambiguïtés et limites détectées pendant l'extraction."
        ),
    )