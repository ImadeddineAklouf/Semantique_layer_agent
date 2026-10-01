from typing import Any

from app.tools.business_document_parser import (
    parse_business_document,
)
from app.tools.consistency_checker import (
    compare_metadata_with_documentation,
)
from app.tools.csv_reader import read_csv_metadata
from app.tools.document_reader import read_document


def compare_csv_with_documentation(
    csv_file_path: str,
    documentation_file_path: str,
) -> dict[str, Any]:
    """
    Compare les métadonnées techniques d'un fichier CSV
    avec les informations déclarées dans un document métier.

    Utilise cet outil lorsqu'un utilisateur souhaite vérifier
    la cohérence entre un fichier CSV et sa documentation.

    La comparaison analyse notamment :
    - le nom de la table ;
    - les colonnes présentes dans les deux sources ;
    - les colonnes absentes ou non documentées ;
    - les types techniques et métier ;
    - la nullabilité ;
    - l'unicité ;
    - la clé primaire ;
    - certaines règles métier techniquement vérifiables ;
    - les avertissements et recommandations.

    Args:
        csv_file_path:
            Chemin local vers le fichier CSV à analyser.

        documentation_file_path:
            Chemin local vers le document métier Markdown
            ou TXT à comparer avec le CSV.

    Returns:
        Un dictionnaire contenant :
        - status ;
        - csv_metadata ;
        - documentation_analysis ;
        - consistency_report ;
        - error_type et message en cas d'erreur.
    """

    try:
        metadata = read_csv_metadata(
            csv_file_path
        )

        document = read_document(
            documentation_file_path
        )

        documentation_analysis = (
            parse_business_document(
                document
            )
        )

        consistency_report = (
            compare_metadata_with_documentation(
                metadata=metadata,
                documentation=documentation_analysis,
            )
        )

        return {
            "status": "success",
            "csv_metadata": metadata.model_dump(
                mode="json"
            ),
            "documentation_analysis": (
                documentation_analysis.model_dump(
                    mode="json"
                )
            ),
            "consistency_report": (
                consistency_report.model_dump(
                    mode="json"
                )
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
