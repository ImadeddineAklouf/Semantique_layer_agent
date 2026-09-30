from typing import Any

from app.tools.csv_reader import read_csv_metadata


def analyze_csv_file(file_path: str) -> dict[str, Any]:
    """
    Analyse un fichier CSV et retourne ses métadonnées structurées.

    Cette fonction vérifie le fichier, détecte les colonnes, les types
    techniques et sémantiques, les valeurs nulles, les valeurs uniques
    et les colonnes pouvant représenter une clé primaire.

    Args:
        file_path: Chemin vers le fichier CSV à analyser.

    Returns:
        Un dictionnaire contenant :
        - status : résultat de l'exécution ;
        - metadata : métadonnées structurées du fichier en cas de succès ;
        - error_type et message en cas d'erreur.
    """

    try:
        metadata = read_csv_metadata(file_path)

        return {
            "status": "success",
            "metadata": metadata.model_dump(mode="json"),
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
            "error_type": "invalid_csv",
            "message": str(error),
        }

    except Exception as error:
        return {
            "status": "error",
            "error_type": "unexpected_error",
            "message": str(error),
        }