from typing import Any

from app.schemas import CardinalityType
from app.tools.relationship_checker import (
    analyze_relationship,
)


def analyze_table_relationship(
    source_file_path: str,
    source_column: str,
    target_file_path: str,
    target_column: str,
    documented_cardinality: CardinalityType,
) -> dict[str, Any]:
    """
    Analyse une relation entre deux fichiers CSV.

    Utilise cet outil lorsqu'un utilisateur souhaite vérifier
    une relation, une clé étrangère ou une cardinalité entre
    deux tables représentées par des fichiers CSV.

    La table source est généralement la table qui contient
    la clé étrangère.

    La table cible est généralement la table qui contient
    la clé primaire ou la clé de référence.

    L'analyse vérifie notamment :
    - l'existence des colonnes de jointure ;
    - la compatibilité de leurs types ;
    - les valeurs de clé étrangère nulles ;
    - les valeurs de clé étrangère orphelines ;
    - le taux de correspondance ;
    - la cardinalité réellement observée ;
    - la cohérence avec la cardinalité documentée.

    Args:
        source_file_path:
            Chemin du fichier CSV contenant généralement
            la clé étrangère.

        source_column:
            Nom de la colonne de jointure dans la table source.

        target_file_path:
            Chemin du fichier CSV contenant généralement
            la clé de référence.

        target_column:
            Nom de la colonne de jointure dans la table cible.

        documented_cardinality:
            Cardinalité déclarée dans la documentation.
            Valeurs autorisées :
            one-to-one, one-to-many, many-to-one,
            many-to-many ou unknown.

    Returns:
        Un dictionnaire contenant :
        - status ;
        - relationship_report en cas de succès ;
        - error_type et message en cas d'erreur.
    """

    try:
        report = analyze_relationship(
            source_file_path=source_file_path,
            source_column=source_column,
            target_file_path=target_file_path,
            target_column=target_column,
            documented_cardinality=(
                documented_cardinality
            ),
        )

        return {
            "status": "success",
            "relationship_report": report.model_dump(
                mode="json"
            ),
        }

    except FileNotFoundError as error:
        return {
            "status": "error",
            "error_type": "file_not_found",
            "message": str(error),
        }

    except ValueError as error:
        return {
            "status": "error",
            "error_type": "invalid_input",
            "message": str(error),
        }

    except Exception as error:
        return {
            "status": "error",
            "error_type": "unexpected_error",
            "message": str(error),
        }