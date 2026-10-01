from typing import Any

from app.tools.document_reader import read_document
from app.tools.business_document_parser import parse_business_document



def analyze_documentation_file(
    file_path: str,
) -> dict[str, Any]:
    """
    Analyse un document métier Markdown ou TXT.

    Utilise cet outil lorsqu'un utilisateur demande
    d'analyser le contenu ou la structure d'un document
    métier au format Markdown ou texte.

    L'analyse retourne notamment :
    - le nom du document ;
    - son format ;
    - son titre principal ;
    - le nombre de caractères et de mots ;
    - les sections détectées ;
    - le contenu complet du document.

    Args:
        file_path: Chemin local vers le document à analyser.

    Returns:
        Un dictionnaire contenant :
        - status : résultat de l'exécution ;
        - document : contenu structuré en cas de succès ;
        - error_type et message en cas d'erreur.
    """

    try:
        document = read_document(file_path)
        business_analysis = parse_business_document(
            document
        )
        return {
            "status": "success",
            "document": document.model_dump(
                mode="json"
            ),
            "business_analysis": business_analysis.model_dump(
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
            "error_type": "invalid_document",
            "message": str(error),
        }

    except Exception as error:
        return {
            "status": "error",
            "error_type": "unexpected_error",
            "message": str(error),
        }