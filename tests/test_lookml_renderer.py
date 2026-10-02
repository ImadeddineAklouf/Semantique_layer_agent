from app.schemas import (
    SemanticDimension,
    SemanticJoin,
    SemanticMeasure,
    SemanticModelSpecification,
    SemanticViewSpecification,
)
from app.tools.lookml_renderer import (
    escape_lookml_string,
    render_dimension,
    render_explore,
    render_join,
    render_lookml_artifacts,
    render_measure,
    render_model,
    render_view,
)


def create_client_id_dimension() -> SemanticDimension:
    return SemanticDimension(
        name="client_id",
        source_column="CLIENT_ID",
        label="Client ID",
        description=(
            "Identifiant unique du client."
        ),
        field_type="number",
        sql_expression="${TABLE}.CLIENT_ID",
        primary_key=True,
        hidden=False,
        sensitive=False,
        required=True,
        unique=True,
        allowed_values=[],
        validation_status="validated",
        warnings=[],
    )


def create_client_name_dimension() -> SemanticDimension:
    return SemanticDimension(
        name="client_name",
        source_column="CLIENT_NAME",
        label="Client Name",
        description="Nom du client.",
        field_type="string",
        sql_expression="${TABLE}.CLIENT_NAME",
        primary_key=False,
        hidden=False,
        sensitive=True,
        required=True,
        unique=False,
        allowed_values=[],
        validation_status="warning",
        warnings=[
            "Champ sensible."
        ],
    )


def create_count_measure() -> SemanticMeasure:
    return SemanticMeasure(
        name="count",
        label="Count",
        description="Nombre total d'enregistrements.",
        measure_type="count",
        source_column=None,
        sql_expression=None,
        value_format=None,
        validation_status="validated",
        warnings=[],
    )


def create_total_amount_measure() -> SemanticMeasure:
    return SemanticMeasure(
        name="total_amount",
        label="Total Amount",
        description=(
            "Somme des montants des commandes."
        ),
        measure_type="sum",
        source_column="AMOUNT",
        sql_expression="${amount}",
        value_format=None,
        validation_status="warning",
        warnings=[
            "Mesure à valider par le métier."
        ],
    )


def create_clients_join() -> SemanticJoin:
    return SemanticJoin(
        name="clients",
        source_table="ORDERS",
        source_column="CLIENT_ID",
        target_table="CLIENTS",
        target_column="CLIENT_ID",
        relationship="many_to_one",
        sql_on=(
            "${orders.client_id} = "
            "${clients.client_id}"
        ),
        foreign_key_match_ratio=1.0,
        orphan_value_count=0,
        validation_status="validated",
        warnings=[],
    )


def create_clients_view() -> SemanticViewSpecification:
    return SemanticViewSpecification(
        view_name="clients",
        source_table_name="CLIENTS",
        source_file="clients.csv",
        label="Clients",
        description="Vue des clients.",
        primary_key="CLIENT_ID",
        dimensions=[
            create_client_id_dimension(),
            create_client_name_dimension(),
        ],
        measures=[
            create_count_measure(),
        ],
        joins=[],
        sensitive_fields=[
            "CLIENT_NAME",
        ],
        documented_rules=[],
        validation_status="warning",
        warnings=[
            "CLIENT_NAME est sensible."
        ],
        recommendations=[],
    )


def create_orders_view() -> SemanticViewSpecification:
    return SemanticViewSpecification(
        view_name="orders",
        source_table_name="ORDERS",
        source_file="orders.csv",
        label="Orders",
        description="Vue des commandes.",
        primary_key="ORDER_ID",
        dimensions=[
            SemanticDimension(
                name="order_id",
                source_column="ORDER_ID",
                label="Order ID",
                description=(
                    "Identifiant de commande."
                ),
                field_type="number",
                sql_expression="${TABLE}.ORDER_ID",
                primary_key=True,
                hidden=False,
                sensitive=False,
                required=True,
                unique=True,
                allowed_values=[],
                validation_status="validated",
                warnings=[],
            ),
            SemanticDimension(
                name="amount",
                source_column="AMOUNT",
                label="Amount",
                description="Montant de commande.",
                field_type="number",
                sql_expression="${TABLE}.AMOUNT",
                primary_key=False,
                hidden=False,
                sensitive=False,
                required=True,
                unique=False,
                allowed_values=[],
                validation_status="validated",
                warnings=[],
            ),
        ],
        measures=[
            create_count_measure(),
            create_total_amount_measure(),
        ],
        joins=[
            create_clients_join(),
        ],
        sensitive_fields=[],
        documented_rules=[],
        validation_status="warning",
        warnings=[],
        recommendations=[],
    )


def create_model(
    generation_ready: bool = True,
) -> SemanticModelSpecification:
    return SemanticModelSpecification(
        model_name="sales",
        project_name="semantic_layer_builder",
        connection_name=(
            "bigquery_connection"
            if generation_ready
            else None
        ),
        default_schema=(
            "analytics"
            if generation_ready
            else None
        ),
        views=[
            create_clients_view(),
            create_orders_view(),
        ],
        generation_ready=generation_ready,
        missing_information=(
            []
            if generation_ready
            else [
                "Nom de la connexion Looker.",
                "Nom du schéma ou dataset physique.",
            ]
        ),
        warnings=[
            "Certaines vues comportent "
            "des avertissements."
        ],
        metadata={},
    )


def test_escape_lookml_string() -> None:
    assert escape_lookml_string(
        'Nom "sensible"'
    ) == 'Nom \\"sensible\\"'


def test_render_dimension() -> None:
    content = render_dimension(
        create_client_id_dimension()
    )

    assert "dimension: client_id {" in content
    assert 'label: "Client ID"' in content
    assert "type: number" in content
    assert "primary_key: yes" in content

    assert (
        "sql: ${TABLE}.CLIENT_ID ;;"
        in content
    )


def test_render_sensitive_dimension_adds_comment(
) -> None:
    content = render_dimension(
        create_client_name_dimension()
    )

    assert (
        "# WARNING: Champ sensible."
        in content
    )

    assert "# Sensitive field:" in content


def test_render_count_measure_without_sql() -> None:
    content = render_measure(
        create_count_measure()
    )

    assert "measure: count {" in content
    assert "type: count" in content
    assert "sql:" not in content


def test_render_sum_measure_with_sql() -> None:
    content = render_measure(
        create_total_amount_measure()
    )

    assert "measure: total_amount {" in content
    assert "type: sum" in content
    assert "sql: ${amount} ;;" in content


def test_render_view() -> None:
    generated_file = render_view(
        view=create_clients_view(),
        default_schema="analytics",
    )

    assert (
        generated_file.file_name
        == "clients.view.lkml"
    )

    assert (
        "view: clients {"
        in generated_file.content
    )

    assert (
        "sql_table_name: "
        "analytics.CLIENTS ;;"
        in generated_file.content
    )

    assert (
        "dimension: client_id {"
        in generated_file.content
    )

    assert (
        "measure: count {"
        in generated_file.content
    )


def test_render_join() -> None:
    content = render_join(
        create_clients_join()
    )

    assert "join: clients {" in content
    assert "type: left_outer" in content

    assert (
        "relationship: many_to_one"
        in content
    )

    assert (
        "sql_on: ${orders.client_id} "
        "= ${clients.client_id} ;;"
        in content
    )


def test_render_orders_explore_contains_join(
) -> None:
    content = render_explore(
        create_orders_view()
    )

    assert "explore: orders {" in content
    assert "join: clients {" in content


def test_render_model() -> None:
    generated_file = render_model(
        create_model()
    )

    assert (
        generated_file.file_name
        == "sales.model.lkml"
    )

    assert (
        'connection: "bigquery_connection"'
        in generated_file.content
    )

    assert (
        'include: "/*.view.lkml"'
        in generated_file.content
    )

    assert (
        "explore: clients {"
        in generated_file.content
    )

    assert (
        "explore: orders {"
        in generated_file.content
    )


def test_render_all_artifacts() -> None:
    result = render_lookml_artifacts(
        create_model()
    )

    assert result.generation_status == (
        "generated_with_warnings"
    )

    file_names = [
        generated_file.file_name
        for generated_file in result.files
    ]

    assert file_names == [
        "clients.view.lkml",
        "orders.view.lkml",
        "sales.model.lkml",
    ]

    assert result.written_files == []


def test_render_is_blocked_when_model_not_ready(
) -> None:
    result = render_lookml_artifacts(
        create_model(
            generation_ready=False
        )
    )

    assert result.generation_status == "blocked"
    assert result.files == []

    assert (
        "Nom de la connexion Looker."
        in result.missing_information
    )