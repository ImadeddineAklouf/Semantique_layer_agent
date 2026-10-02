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
    build_numeric_measures,
    build_semantic_model,
    build_semantic_view,
    create_field_label,
    map_join_relationship,
    map_semantic_field_type,
    normalize_semantic_name,
)


def build_test_view(
    csv_path: str,
    documentation_path: str,
    relationship_reports=None,
):
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


def test_normalize_semantic_name() -> None:
    assert normalize_semantic_name(
        "CLIENT_ID"
    ) == "client_id"

    assert normalize_semantic_name(
        "Customer Name"
    ) == "customer_name"

    assert normalize_semantic_name(
        "ORDER--STATUS"
    ) == "order_status"


def test_create_field_label() -> None:
    assert create_field_label(
        "CLIENT_ID"
    ) == "Client ID"

    assert create_field_label(
        "CREATION_DATE"
    ) == "Creation Date"


def test_map_semantic_field_type() -> None:
    assert map_semantic_field_type(
        "integer"
    ) == "number"

    assert map_semantic_field_type(
        "boolean"
    ) == "yesno"

    assert map_semantic_field_type(
        "date"
    ) == "date"

    assert map_semantic_field_type(
        "unsupported"
    ) == "unknown"


def test_map_join_relationship() -> None:
    assert map_join_relationship(
        "many-to-one"
    ) == "many_to_one"

    assert map_join_relationship(
        "one-to-many"
    ) == "one_to_many"

    assert map_join_relationship(
        "unsupported"
    ) == "unknown"


def test_build_clients_view() -> None:
    view = build_test_view(
        csv_path="data/inputs/clients.csv",
        documentation_path=(
            "data/documentation/"
            "clients_documentation.md"
        ),
    )

    assert view.view_name == "clients"
    assert view.source_table_name == "CLIENTS"
    assert view.primary_key == "CLIENT_ID"

    dimension_names = [
        dimension.name
        for dimension in view.dimensions
    ]

    assert dimension_names == [
        "client_id",
        "client_name",
        "country",
        "creation_date",
        "is_active",
    ]

    assert [
        measure.name
        for measure in view.measures
    ] == ["count"]

    assert view.sensitive_fields == [
        "CLIENT_NAME"
    ]


def test_clients_primary_key_dimension() -> None:
    view = build_test_view(
        csv_path="data/inputs/clients.csv",
        documentation_path=(
            "data/documentation/"
            "clients_documentation.md"
        ),
    )

    primary_dimensions = [
        dimension
        for dimension in view.dimensions
        if dimension.primary_key
    ]

    assert len(primary_dimensions) == 1

    assert (
        primary_dimensions[0].source_column
        == "CLIENT_ID"
    )


def test_build_orders_numeric_measures() -> None:
    metadata = read_csv_metadata(
        "data/inputs/orders.csv"
    )

    measures = build_numeric_measures(
        metadata
    )

    measure_names = [
        measure.name
        for measure in measures
    ]

    assert measure_names == [
        "total_amount",
        "average_amount",
        "minimum_amount",
        "maximum_amount",
    ]

    assert "total_order_id" not in measure_names
    assert "total_client_id" not in measure_names


def test_build_orders_view_with_join() -> None:
    relationship = analyze_relationship(
        source_file_path="data/inputs/orders.csv",
        source_column="CLIENT_ID",
        target_file_path="data/inputs/clients.csv",
        target_column="CLIENT_ID",
        documented_cardinality="many-to-one",
    )

    view = build_test_view(
        csv_path="data/inputs/orders.csv",
        documentation_path=(
            "data/documentation/"
            "orders_documentation.md"
        ),
        relationship_reports=[
            relationship,
        ],
    )

    assert view.view_name == "orders"
    assert view.primary_key == "ORDER_ID"
    assert len(view.joins) == 1

    join = view.joins[0]

    assert join.name == "clients"
    assert join.relationship == "many_to_one"

    assert join.sql_on == (
        "${orders.client_id} = "
        "${clients.client_id}"
    )

    assert join.foreign_key_match_ratio == 1.0
    assert join.orphan_value_count == 0


def test_invalid_relationship_requires_review() -> None:
    relationship = analyze_relationship(
        source_file_path=(
            "data/inputs/orders_with_orphans.csv"
        ),
        source_column="CLIENT_ID",
        target_file_path=(
            "data/inputs/clients.csv"
        ),
        target_column="CLIENT_ID",
        documented_cardinality="many-to-one",
    )

    view = build_test_view(
        csv_path=(
            "data/inputs/orders_with_orphans.csv"
        ),
        documentation_path=(
            "data/documentation/"
            "orders_documentation.md"
        ),
        relationship_reports=[
            relationship,
        ],
    )

    assert view.validation_status == (
        "requires_review"
    )

    assert view.joins[0].validation_status == (
        "requires_review"
    )

    assert view.joins[0].orphan_value_count == 1


def test_build_semantic_model_not_ready_without_connection(
) -> None:
    clients_view = build_test_view(
        csv_path="data/inputs/clients.csv",
        documentation_path=(
            "data/documentation/"
            "clients_documentation.md"
        ),
    )

    model = build_semantic_model(
        model_name="sales",
        project_name="semantic_layer_builder",
        connection_name=None,
        default_schema=None,
        views=[clients_view],
    )

    assert model.generation_ready is False

    assert (
        "Nom de la connexion Looker."
        in model.missing_information
    )

    assert (
        "Nom du schéma ou dataset physique."
        in model.missing_information
    )


def test_build_semantic_model_ready_with_configuration(
) -> None:
    clients_view = build_test_view(
        csv_path="data/inputs/clients.csv",
        documentation_path=(
            "data/documentation/"
            "clients_documentation.md"
        ),
    )

    model = build_semantic_model(
        model_name="sales",
        project_name="semantic_layer_builder",
        connection_name="bigquery_connection",
        default_schema="analytics",
        views=[clients_view],
    )

    if clients_view.validation_status == (
        "requires_review"
    ):
        assert model.generation_ready is False
    else:
        assert model.generation_ready is True

def test_orders_view_inherits_measure_warnings() -> None:
    relationship = analyze_relationship(
        source_file_path="data/inputs/orders.csv",
        source_column="CLIENT_ID",
        target_file_path="data/inputs/clients.csv",
        target_column="CLIENT_ID",
        documented_cardinality="many-to-one",
    )

    view = build_test_view(
        csv_path="data/inputs/orders.csv",
        documentation_path=(
            "data/documentation/"
            "orders_documentation.md"
        ),
        relationship_reports=[
            relationship,
        ],
    )

    measure_statuses = {
        measure.validation_status
        for measure in view.measures
    }

    assert "warning" in measure_statuses
    assert view.validation_status == "warning"