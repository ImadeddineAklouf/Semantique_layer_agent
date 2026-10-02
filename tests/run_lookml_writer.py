from app.schemas import (
    SemanticModelSpecification,
)
from app.tools import (
    build_semantic_model_from_sources,
    render_lookml_artifacts,
    write_lookml_artifacts,
)


def main() -> None:
    semantic_result = (
        build_semantic_model_from_sources(
            model_name="sales",
            project_name=(
                "semantic_layer_builder"
            ),
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
            relationship_source_column=(
                "CLIENT_ID"
            ),
            relationship_target_column=(
                "CLIENT_ID"
            ),
            documented_cardinality=(
                "many-to-one"
            ),
            connection_name=(
                "bigquery_connection"
            ),
            default_schema="analytics",
        )
    )

    if semantic_result["status"] != "success":
        raise RuntimeError(
            semantic_result
        )

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

    written_result = write_lookml_artifacts(
        generation_result=(
            generation_result
        ),
        output_directory=(
            "data/outputs/lookml"
        ),
        allowed_root_directory=(
            "data/outputs"
        ),
        overwrite=True,
    )

    print(
        "Statut :",
        written_result.generation_status,
    )

    print(
        "Répertoire :",
        written_result.output_directory,
    )

    print("Fichiers écrits :")

    for file_path in (
        written_result.written_files
    ):
        print("-", file_path)


if __name__ == "__main__":
    main()
    