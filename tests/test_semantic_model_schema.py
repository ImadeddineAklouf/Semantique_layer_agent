import pytest
from pydantic import ValidationError

from app.schemas import (
    SemanticDimension,
    SemanticJoin,
    SemanticMeasure,
    SemanticModelSpecification,
    SemanticViewSpecification,
)


def create_client_id_dimension() -> SemanticDimension:
    return SemanticDimension(
        name="client_id",
        source_column="CLIENT_ID",
        label="Client ID",
        description=(
            "Identifiant technique unique du client."
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
        description="Nom complet du client.",
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
            "Champ contenant une donnée personnelle."
        ],
    )


def create_count_measure() -> SemanticMeasure:
    return SemanticMeasure(
        name="count",
        label="Count",
        description="Nombre total de clients.",
        measure_type="count",
        source_column=None,
        sql_expression=None,
        value_format=None,
        validation_status="validated",
        warnings=[],
    )


def create_orders_join() -> SemanticJoin:
    return SemanticJoin(
        name="orders",
        source_table="CLIENTS",
        source_column="CLIENT_ID",
        target_table="ORDERS",
        target_column="CLIENT_ID",
        relationship="one_to_many",
        sql_on=(
            "${clients.CLIENT_ID} = "
            "${orders.CLIENT_ID}"
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
        description=(
            "Vue sémantique des clients."
        ),
        primary_key="CLIENT_ID",
        dimensions=[
            create_client_id_dimension(),
            create_client_name_dimension(),
        ],
        measures=[
            create_count_measure(),
        ],
        joins=[
            create_orders_join(),
        ],
        sensitive_fields=[
            "CLIENT_NAME",
        ],
        documented_rules=[
            "CLIENT_ID doit être renseigné.",
        ],
        validation_status="warning",
        warnings=[
            "CLIENT_NAME est une donnée sensible."
        ],
        recommendations=[
            "Appliquer un contrôle d'accès."
        ],
    )


def test_semantic_dimension_accepts_valid_data() -> None:
    dimension = create_client_id_dimension()

    assert dimension.name == "client_id"
    assert dimension.source_column == "CLIENT_ID"
    assert dimension.primary_key is True
    assert dimension.field_type == "number"


def test_semantic_dimension_rejects_invalid_type() -> None:
    invalid_data = (
        create_client_id_dimension().model_dump()
    )

    invalid_data["field_type"] = "integer"

    with pytest.raises(ValidationError):
        SemanticDimension.model_validate(
            invalid_data
        )


def test_semantic_measure_accepts_count() -> None:
    measure = create_count_measure()

    assert measure.measure_type == "count"
    assert measure.source_column is None


def test_semantic_join_accepts_valid_data() -> None:
    join = create_orders_join()

    assert join.relationship == "one_to_many"
    assert join.foreign_key_match_ratio == 1.0
    assert join.orphan_value_count == 0


def test_semantic_join_rejects_invalid_ratio() -> None:
    invalid_data = create_orders_join().model_dump()

    invalid_data["foreign_key_match_ratio"] = 1.5

    with pytest.raises(ValidationError):
        SemanticJoin.model_validate(invalid_data)


def test_semantic_view_accepts_valid_data() -> None:
    view = create_clients_view()

    assert view.view_name == "clients"
    assert view.primary_key == "CLIENT_ID"
    assert len(view.dimensions) == 2
    assert len(view.measures) == 1
    assert len(view.joins) == 1


def test_semantic_view_rejects_unknown_primary_key() -> None:
    invalid_data = create_clients_view().model_dump()

    invalid_data["primary_key"] = "UNKNOWN_ID"

    with pytest.raises(
        ValidationError,
        match="clé primaire",
    ):
        SemanticViewSpecification.model_validate(
            invalid_data
        )


def test_semantic_view_rejects_duplicate_dimensions() -> None:
    invalid_view = {
        "view_name": "clients",
        "source_table_name": "CLIENTS",
        "source_file": "clients.csv",
        "label": "Clients",
        "description": None,
        "primary_key": "CLIENT_ID",
        "dimensions": [
            create_client_id_dimension(),
            create_client_id_dimension(),
        ],
        "measures": [],
        "joins": [],
        "sensitive_fields": [],
        "documented_rules": [],
        "validation_status": "requires_review",
        "warnings": [],
        "recommendations": [],
    }

    with pytest.raises(
        ValidationError,
        match="dimensions",
    ):
        SemanticViewSpecification.model_validate(
            invalid_view
        )


def test_semantic_view_rejects_unknown_sensitive_field() -> None:
    invalid_data = create_clients_view().model_dump()

    invalid_data["sensitive_fields"] = [
        "UNKNOWN_FIELD",
    ]

    with pytest.raises(
        ValidationError,
        match="champs sensibles",
    ):
        SemanticViewSpecification.model_validate(
            invalid_data
        )


def test_semantic_model_accepts_valid_data() -> None:
    model = SemanticModelSpecification(
        model_name="sales",
        project_name="semantic_layer_builder",
        connection_name=None,
        default_schema=None,
        views=[
            create_clients_view(),
        ],
        generation_ready=False,
        missing_information=[
            "Nom de la connexion Looker.",
            "Nom du schéma physique.",
        ],
        warnings=[],
        metadata={
            "version": "0.1.0",
        },
    )

    assert model.model_name == "sales"
    assert len(model.views) == 1
    assert model.generation_ready is False


def test_ready_model_rejects_missing_information() -> None:
    with pytest.raises(
        ValidationError,
        match="informations manquantes",
    ):
        SemanticModelSpecification(
            model_name="sales",
            project_name="semantic_layer_builder",
            connection_name="bigquery_connection",
            default_schema="analytics",
            views=[
                create_clients_view(),
            ],
            generation_ready=True,
            missing_information=[
                "Information encore absente.",
            ],
            warnings=[],
            metadata={},
        )


def test_ready_model_rejects_view_requiring_review() -> None:
    view_data = create_clients_view().model_dump()

    view_data["validation_status"] = (
        "requires_review"
    )

    view = SemanticViewSpecification.model_validate(
        view_data
    )

    with pytest.raises(
        ValidationError,
        match="nécessitent encore",
    ):
        SemanticModelSpecification(
            model_name="sales",
            project_name="semantic_layer_builder",
            connection_name="connection",
            default_schema="analytics",
            views=[view],
            generation_ready=True,
            missing_information=[],
            warnings=[],
            metadata={},
        )


def test_semantic_model_rejects_duplicate_view_names() -> None:
    view = create_clients_view()

    with pytest.raises(
        ValidationError,
        match="vues",
    ):
        SemanticModelSpecification(
            model_name="sales",
            project_name="semantic_layer_builder",
            connection_name=None,
            default_schema=None,
            views=[view, view],
            generation_ready=False,
            missing_information=[],
            warnings=[],
            metadata={},
        )


def test_semantic_schema_rejects_extra_field() -> None:
    invalid_data = (
        create_client_id_dimension().model_dump()
    )

    invalid_data["unknown_field"] = "not allowed"

    with pytest.raises(ValidationError):
        SemanticDimension.model_validate(
            invalid_data
        )