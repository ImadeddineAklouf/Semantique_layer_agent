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


def build_view(
    csv_path: str,
    documentation_path: str,
    relationship_reports=None,
):
    """
    Construit une vue sémantique complète.
    """

    metadata = read_csv_metadata(csv_path)

    documentation = parse_business_document(
        read_document(documentation_path)
    )

    consistency = (
        compare_metadata_with_documentation(
            metadata=metadata,
            documentation=documentation,
        )
    )

    return build_semantic_view(
        metadata=metadata,
        documentation=documentation,
        consistency_report=consistency,
        relationship_reports=(
            relationship_reports or []
        ),
    )


def main() -> None:
    relationship = analyze_relationship(
        source_file_path="data/inputs/orders.csv",
        source_column="CLIENT_ID",
        target_file_path="data/inputs/clients.csv",
        target_column="CLIENT_ID",
        documented_cardinality="many-to-one",
    )

    clients_view = build_view(
        csv_path="data/inputs/clients.csv",
        documentation_path=(
            "data/documentation/"
            "clients_documentation.md"
        ),
    )

    orders_view = build_view(
        csv_path="data/inputs/orders.csv",
        documentation_path=(
            "data/documentation/"
            "orders_documentation.md"
        ),
        relationship_reports=[relationship],
    )

    model = build_semantic_model(
        model_name="sales",
        project_name="semantic_layer_builder",
        connection_name=None,
        default_schema=None,
        views=[
            clients_view,
            orders_view,
        ],
    )

    print("Modèle :", model.model_name)
    print("Projet :", model.project_name)
    print("Prêt :", model.generation_ready)
    print(
        "Informations manquantes :",
        model.missing_information,
    )

    for view in model.views:
        print()
        print("Vue :", view.view_name)
        print("Table :", view.source_table_name)
        print("Clé primaire :", view.primary_key)
        print(
            "Dimensions :",
            [
                dimension.name
                for dimension in view.dimensions
            ],
        )
        print(
            "Mesures :",
            [
                measure.name
                for measure in view.measures
            ],
        )
        print(
            "Jointures :",
            [
                join.name
                for join in view.joins
            ],
        )
        print(
            "Champs sensibles :",
            view.sensitive_fields,
        )
        print(
            "Statut :",
            view.validation_status,
        )


if __name__ == "__main__":
    main()