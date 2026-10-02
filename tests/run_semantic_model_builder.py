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


def main() -> None:
    """
    Construit un modèle sémantique contenant
    les vues CLIENTS et ORDERS.
    """

    clients_metadata = read_csv_metadata(
        "data/inputs/clients.csv"
    )

    clients_document = read_document(
        "data/documentation/"
        "clients_documentation.md"
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
        "data/inputs/orders.csv"
    )

    orders_document = read_document(
        "data/documentation/"
        "orders_documentation.md"
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

    orders_to_clients_relationship = (
        analyze_relationship(
            source_file_path=(
                "data/inputs/orders.csv"
            ),
            source_column="CLIENT_ID",
            target_file_path=(
                "data/inputs/clients.csv"
            ),
            target_column="CLIENT_ID",
            documented_cardinality="many-to-one",
        )
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
            orders_to_clients_relationship,
        ],
    )

    semantic_model = build_semantic_model(
        model_name="sales",
        project_name="semantic_layer_builder",
        connection_name=None,
        default_schema=None,
        views=[
            clients_view,
            orders_view,
        ],
    )

    print(
        semantic_model.model_dump_json(
            indent=2
        )
    )


if __name__ == "__main__":
    main()