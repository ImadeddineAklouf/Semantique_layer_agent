from app.tools import (
    build_semantic_model_from_sources,
)


def build_valid_model_result(
    connection_name=None,
    default_schema=None,
):
    return build_semantic_model_from_sources(
        model_name="sales",
        project_name="semantic_layer_builder",
        clients_csv_path="data/inputs/clients.csv",
        clients_documentation_path=(
            "data/documentation/"
            "clients_documentation.md"
        ),
        orders_csv_path="data/inputs/orders.csv",
        orders_documentation_path=(
            "data/documentation/"
            "orders_documentation.md"
        ),
        relationship_source_column="CLIENT_ID",
        relationship_target_column="CLIENT_ID",
        documented_cardinality="many-to-one",
        connection_name=connection_name,
        default_schema=default_schema,
    )


def test_semantic_model_tool_returns_success() -> None:
    result = build_valid_model_result()

    assert result["status"] == "success"
    assert "semantic_model" in result
    assert "relationship_report" in result
    assert "consistency_reports" in result


def test_semantic_model_contains_expected_views() -> None:
    result = build_valid_model_result()

    model = result["semantic_model"]

    view_names = [
        view["view_name"]
        for view in model["views"]
    ]

    assert view_names == [
        "clients",
        "orders",
    ]


def test_clients_view_has_expected_fields() -> None:
    result = build_valid_model_result()

    clients_view = next(
        view
        for view in result["semantic_model"]["views"]
        if view["view_name"] == "clients"
    )

    assert clients_view["primary_key"] == "CLIENT_ID"

    dimension_names = [
        dimension["name"]
        for dimension in clients_view["dimensions"]
    ]

    assert dimension_names == [
        "client_id",
        "client_name",
        "country",
        "creation_date",
        "is_active",
    ]

    assert clients_view["sensitive_fields"] == [
        "CLIENT_NAME"
    ]


def test_orders_view_has_expected_measures() -> None:
    result = build_valid_model_result()

    orders_view = next(
        view
        for view in result["semantic_model"]["views"]
        if view["view_name"] == "orders"
    )

    measure_names = [
        measure["name"]
        for measure in orders_view["measures"]
    ]

    assert measure_names == [
        "count",
        "total_amount",
        "average_amount",
        "minimum_amount",
        "maximum_amount",
    ]


def test_orders_view_has_clients_join() -> None:
    result = build_valid_model_result()

    orders_view = next(
        view
        for view in result["semantic_model"]["views"]
        if view["view_name"] == "orders"
    )

    assert len(orders_view["joins"]) == 1

    join = orders_view["joins"][0]

    assert join["name"] == "clients"
    assert join["relationship"] == "many_to_one"

    assert join["sql_on"] == (
        "${orders.client_id} = "
        "${clients.client_id}"
    )

    assert join["foreign_key_match_ratio"] == 1.0
    assert join["orphan_value_count"] == 0


def test_model_is_not_ready_without_looker_config() -> None:
    result = build_valid_model_result()

    model = result["semantic_model"]

    assert model["generation_ready"] is False

    assert (
        "Nom de la connexion Looker."
        in model["missing_information"]
    )

    assert (
        "Nom du schéma ou dataset physique."
        in model["missing_information"]
    )


def test_model_configuration_is_preserved() -> None:
    result = build_valid_model_result(
        connection_name="bigquery_connection",
        default_schema="analytics",
    )

    model = result["semantic_model"]

    assert (
        model["connection_name"]
        == "bigquery_connection"
    )

    assert model["default_schema"] == "analytics"


def test_invalid_relationship_requires_review() -> None:
    result = build_semantic_model_from_sources(
        model_name="sales",
        project_name="semantic_layer_builder",
        clients_csv_path="data/inputs/clients.csv",
        clients_documentation_path=(
            "data/documentation/"
            "clients_documentation.md"
        ),
        orders_csv_path=(
            "data/inputs/orders_with_orphans.csv"
        ),
        orders_documentation_path=(
            "data/documentation/"
            "orders_documentation.md"
        ),
        relationship_source_column="CLIENT_ID",
        relationship_target_column="CLIENT_ID",
        documented_cardinality="many-to-one",
    )