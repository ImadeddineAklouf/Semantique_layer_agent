from app.schemas import (
    LookMLGenerationResult,
    SemanticModelSpecification,
)
from app.tools import (
    build_semantic_model_from_sources,
    render_lookml_artifacts,
)


def build_real_semantic_model(
) -> SemanticModelSpecification:
    """
    Construit le véritable modèle sémantique sales
    à partir des sources CLIENTS et ORDERS.
    """

    result = build_semantic_model_from_sources(
        model_name="sales",
        project_name="semantic_layer_builder",
        clients_csv_path=(
            "data/inputs/clients.csv"
        ),
        clients_documentation_path=(
            "data/documentation/"
            "clients_documentation.md"
        ),
        orders_csv_path=(
            "data/inputs/orders.csv"
        ),
        orders_documentation_path=(
            "data/documentation/"
            "orders_documentation.md"
        ),
        relationship_source_column="CLIENT_ID",
        relationship_target_column="CLIENT_ID",
        documented_cardinality="many-to-one",
        connection_name="bigquery_connection",
        default_schema="analytics",
    )

    if result["status"] != "success":
        raise RuntimeError(
            "La construction du modèle sémantique "
            f"a échoué : {result}"
        )

    return SemanticModelSpecification.model_validate(
        result["semantic_model"]
    )


def render_real_lookml(
) -> LookMLGenerationResult:
    """
    Construit le modèle puis génère les artefacts
    LookML en mémoire.
    """

    semantic_model = build_real_semantic_model()

    return render_lookml_artifacts(
        semantic_model
    )


def main() -> None:
    semantic_model = build_real_semantic_model()

    print("=" * 80)
    print("MODÈLE SÉMANTIQUE")
    print("=" * 80)

    print(
        "Nom :",
        semantic_model.model_name,
    )

    print(
        "Projet :",
        semantic_model.project_name,
    )

    print(
        "Connexion :",
        semantic_model.connection_name,
    )

    print(
        "Schéma :",
        semantic_model.default_schema,
    )

    print(
        "Prêt :",
        semantic_model.generation_ready,
    )

    print(
        "Vues :",
        [
            view.view_name
            for view in semantic_model.views
        ],
    )

    generation_result = render_lookml_artifacts(
        semantic_model
    )

    print()
    print("=" * 80)
    print("RÉSULTAT DE GÉNÉRATION")
    print("=" * 80)

    print(
        "Statut :",
        generation_result.generation_status,
    )

    print(
        "Nombre de fichiers :",
        len(generation_result.files),
    )

    print(
        "Fichiers :",
        [
            generated_file.file_name
            for generated_file
            in generation_result.files
        ],
    )

    print(
        "Fichiers écrits :",
        generation_result.written_files,
    )

    print(
        "Informations manquantes :",
        generation_result.missing_information,
    )

    print(
        "Nombre d'avertissements :",
        len(generation_result.warnings),
    )

    for generated_file in generation_result.files:
        print()
        print("=" * 80)
        print(generated_file.file_name)
        print("=" * 80)
        print(generated_file.content)


if __name__ == "__main__":
    main()