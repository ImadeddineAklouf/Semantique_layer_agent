from typing import Any

from app.schemas import CardinalityType
from app.tools.business_document_parser import (
    parse_business_document,
)
from app.tools.consistency_checker import (
    compare_metadata_with_documentation,
)
from app.tools.csv_reader import read_csv_metadata
from app.tools.document_reader import read_document
from app.tools.relationship_checker import (
    analyze_relationship,
)
from app.tools.semantic_model_builder import (
    build_semantic_model,
    build_semantic_view,
)


def build_semantic_model_from_sources(
    model_name: str,
    project_name: str,
    clients_csv_path: str,
    clients_documentation_path: str,
    orders_csv_path: str,
    orders_documentation_path: str,
    relationship_source_column: str,
    relationship_target_column: str,
    documented_cardinality: CardinalityType,
    connection_name: str | None = None,
    default_schema: str | None = None,
) -> dict[str, Any]:
    """
    Construit une spécification de modèle sémantique
    à partir des tables CLIENTS et ORDERS.

    Ce Tool analyse les deux fichiers CSV, analyse leurs
    documentations métier, vérifie leur cohérence, valide
    leur relation, puis construit un modèle sémantique
    intermédiaire.

    Le Tool ne génère pas encore de LookML.

    Args:
        model_name:
            Nom du modèle sémantique à construire.

        project_name:
            Nom du projet LookML cible.

        clients_csv_path:
            Chemin du fichier CSV représentant CLIENTS.

        clients_documentation_path:
            Chemin de la documentation métier de CLIENTS.

        orders_csv_path:
            Chemin du fichier CSV représentant ORDERS.

        orders_documentation_path:
            Chemin de la documentation métier de ORDERS.

        relationship_source_column:
            Colonne source de la relation dans ORDERS.

        relationship_target_column:
            Colonne cible de la relation dans CLIENTS.

        documented_cardinality:
            Cardinalité documentée de la source vers la cible.

        connection_name:
            Nom facultatif de la connexion Looker.

        default_schema:
            Nom facultatif du schéma ou dataset physique.

    Returns:
        Un dictionnaire contenant :
        - status ;
        - semantic_model en cas de succès ;
        - relationship_report ;
        - consistency_reports ;
        - error_type et message en cas d'erreur.
    """

    try:
        clients_metadata = read_csv_metadata(
            clients_csv_path
        )

        clients_document = read_document(
            clients_documentation_path
        )

        clients_documentation = (
            parse_business_document(
                clients_document
            )
        )

        clients_consistency = (
            compare_metadata_with_documentation(
                metadata=clients_metadata,
                documentation=clients_documentation,
            )
        )

        orders_metadata = read_csv_metadata(
            orders_csv_path
        )

        orders_document = read_document(
            orders_documentation_path
        )

        orders_documentation = (
            parse_business_document(
                orders_document
            )
        )

        orders_consistency = (
            compare_metadata_with_documentation(
                metadata=orders_metadata,
                documentation=orders_documentation,
            )
        )

        relationship_report = analyze_relationship(
            source_file_path=orders_csv_path,
            source_column=relationship_source_column,
            target_file_path=clients_csv_path,
            target_column=relationship_target_column,
            documented_cardinality=(
                documented_cardinality
            ),
        )

        clients_view = build_semantic_view(
            metadata=clients_metadata,
            documentation=clients_documentation,
            consistency_report=clients_consistency,
            relationship_reports=[],
        )

        orders_view = build_semantic_view(
            metadata=orders_metadata,
            documentation=orders_documentation,
            consistency_report=orders_consistency,
            relationship_reports=[
                relationship_report,
            ],
        )

        semantic_model = build_semantic_model(
            model_name=model_name,
            project_name=project_name,
            connection_name=connection_name,
            default_schema=default_schema,
            views=[
                clients_view,
                orders_view,
            ],
        )

        return {
            "status": "success",
            "semantic_model": (
                semantic_model.model_dump(
                    mode="json"
                )
            ),
            "relationship_report": (
                relationship_report.model_dump(
                    mode="json"
                )
            ),
            "consistency_reports": {
                "clients": (
                    clients_consistency.model_dump(
                        mode="json"
                    )
                ),
                "orders": (
                    orders_consistency.model_dump(
                        mode="json"
                    )
                ),
            },
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