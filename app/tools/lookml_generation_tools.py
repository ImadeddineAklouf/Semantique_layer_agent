from typing import Any

from app.schemas import (
    CardinalityType,
    SemanticModelSpecification,
)
from app.tools.lookml_renderer import (
    render_lookml_artifacts,
)
from app.tools.lookml_validator import (
    validate_lookml_artifacts,
)
from app.tools.lookml_writer import (
    write_lookml_artifacts,
)
from app.tools.semantic_model_tools import (
    build_semantic_model_from_sources,
)

def generate_lookml_project(
    model_name: str,
    project_name: str,
    clients_csv_path: str,
    clients_documentation_path: str,
    orders_csv_path: str,
    orders_documentation_path: str,
    relationship_source_column: str,
    relationship_target_column: str,
    documented_cardinality: CardinalityType,
    connection_name: str,
    default_schema: str,
    output_directory: str = "data/outputs/lookml",
    allowed_root_directory: str = "data/outputs",
    write_files: bool = True,
    overwrite: bool = False,
) -> dict[str, Any]:
    """
    Construit, génère, valide et écrit un projet LookML.

    Cette fonction représente la façade finale du pipeline
    de génération LookML.

    Étapes exécutées :

    1. Analyse des fichiers CSV.
    2. Analyse des documentations métier.
    3. Comparaison technique et documentaire.
    4. Analyse de la relation ORDERS vers CLIENTS.
    5. Construction du modèle sémantique.
    6. Génération des artefacts LookML en mémoire.
    7. Validation locale des artefacts LookML.
    8. Écriture facultative des fichiers sur le disque.

    Args:
        model_name:
            Nom du modèle LookML à générer.

        project_name:
            Nom du projet sémantique cible.

        clients_csv_path:
            Chemin du fichier CSV CLIENTS.

        clients_documentation_path:
            Chemin de la documentation CLIENTS.

        orders_csv_path:
            Chemin du fichier CSV ORDERS.

        orders_documentation_path:
            Chemin de la documentation ORDERS.

        relationship_source_column:
            Colonne source de la relation dans ORDERS.

        relationship_target_column:
            Colonne cible de la relation dans CLIENTS.

        documented_cardinality:
            Cardinalité documentée de la source vers la cible.

        connection_name:
            Nom de la connexion Looker.

        default_schema:
            Nom du schéma ou dataset physique.

        output_directory:
            Répertoire de sortie des fichiers LookML.

        allowed_root_directory:
            Racine dans laquelle les écritures sont autorisées.

        write_files:
            Indique si les artefacts validés doivent être
            écrits sur le disque.

        overwrite:
            Autorise l'écrasement des fichiers existants.

    Returns:
        Un dictionnaire contenant :

        - status ;
        - pipeline_stage ;
        - semantic_model ;
        - generation_result ;
        - validation_report ;
        - written_files ;
        - error_type et message en cas d'erreur.
    """

    try:
        semantic_result = (
            build_semantic_model_from_sources(
                model_name=model_name,
                project_name=project_name,
                clients_csv_path=clients_csv_path,
                clients_documentation_path=(
                    clients_documentation_path
                ),
                orders_csv_path=orders_csv_path,
                orders_documentation_path=(
                    orders_documentation_path
                ),
                relationship_source_column=(
                    relationship_source_column
                ),
                relationship_target_column=(
                    relationship_target_column
                ),
                documented_cardinality=(
                    documented_cardinality
                ),
                connection_name=connection_name,
                default_schema=default_schema,
            )
        )

        if semantic_result["status"] != "success":
            return {
                "status": "error",
                "pipeline_stage": (
                    "semantic_model_building"
                ),
                "error_type": semantic_result.get(
                    "error_type",
                    "semantic_model_error",
                ),
                "message": semantic_result.get(
                    "message",
                    "La construction du modèle "
                    "sémantique a échoué.",
                ),
            }

        semantic_model = (
            SemanticModelSpecification.model_validate(
                semantic_result["semantic_model"]
            )
        )

        generation_result = (
            render_lookml_artifacts(
                semantic_model
            )
        )

        if (
            generation_result.generation_status
            == "blocked"
        ):
            return {
                "status": "blocked",
                "pipeline_stage": (
                    "lookml_rendering"
                ),
                "semantic_model": (
                    semantic_model.model_dump(
                        mode="json"
                    )
                ),
                "generation_result": (
                    generation_result.model_dump(
                        mode="json"
                    )
                ),
                "validation_report": None,
                "written_files": [],
                "message": (
                    "La génération LookML est bloquée "
                    "car le modèle sémantique n'est pas "
                    "suffisamment complet."
                ),
            }

        validation_report = (
            validate_lookml_artifacts(
                generation_result
            )
        )

        if not validation_report.valid:
            return {
                "status": "validation_failed",
                "pipeline_stage": (
                    "lookml_validation"
                ),
                "semantic_model": (
                    semantic_model.model_dump(
                        mode="json"
                    )
                ),
                "generation_result": (
                    generation_result.model_dump(
                        mode="json"
                    )
                ),
                "validation_report": (
                    validation_report.model_dump(
                        mode="json"
                    )
                ),
                "written_files": [],
                "message": (
                    "Les artefacts LookML ont été "
                    "générés, mais la validation locale "
                    "a détecté des erreurs."
                ),
            }

        if not write_files:
            return {
                "status": "success",
                "pipeline_stage": (
                    "lookml_validation"
                ),
                "semantic_model": (
                    semantic_model.model_dump(
                        mode="json"
                    )
                ),
                "generation_result": (
                    generation_result.model_dump(
                        mode="json"
                    )
                ),
                "validation_report": (
                    validation_report.model_dump(
                        mode="json"
                    )
                ),
                "relationship_report": (
                    semantic_result.get(
                        "relationship_report"
                    )
                ),
                "consistency_reports": (
                    semantic_result.get(
                        "consistency_reports"
                    )
                ),
                "written_files": [],
                "message": (
                    "Les artefacts LookML ont été "
                    "générés et validés en mémoire. "
                    "Aucun fichier n'a été écrit."
                ),
            }

        written_result = write_lookml_artifacts(
            generation_result=generation_result,
            output_directory=output_directory,
            allowed_root_directory=(
                allowed_root_directory
            ),
            overwrite=overwrite,
        )

        return {
            "status": "success",
            "pipeline_stage": "completed",
            "semantic_model": (
                semantic_model.model_dump(
                    mode="json"
                )
            ),
            "generation_result": (
                written_result.model_dump(
                    mode="json"
                )
            ),
            "validation_report": (
                validation_report.model_dump(
                    mode="json"
                )
            ),
            "relationship_report": (
                semantic_result.get(
                    "relationship_report"
                )
            ),
            "consistency_reports": (
                semantic_result.get(
                    "consistency_reports"
                )
            ),
            "written_files": (
                written_result.written_files
            ),
            "message": (
                "Le projet LookML a été construit, "
                "validé et écrit avec succès."
            ),
        }

    except FileExistsError as error:
        return {
            "status": "error",
            "pipeline_stage": "lookml_writing",
            "error_type": "file_exists",
            "message": str(error),
        }

    except FileNotFoundError as error:
        return {
            "status": "error",
            "pipeline_stage": "source_loading",
            "error_type": "file_not_found",
            "message": str(error),
        }

    except ValueError as error:
        return {
            "status": "error",
            "pipeline_stage": "pipeline_validation",
            "error_type": "invalid_input",
            "message": str(error),
        }

    except Exception as error:
        return {
            "status": "error",
            "pipeline_stage": "unexpected",
            "error_type": "unexpected_error",
            "message": str(error),
        }