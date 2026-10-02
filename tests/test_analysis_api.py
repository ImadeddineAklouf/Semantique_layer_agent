from pathlib import Path

from fastapi.testclient import TestClient

from app.api.main import app


client = TestClient(app)


PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]

CLIENTS_CSV = str(
    PROJECT_ROOT
    / "data"
    / "inputs"
    / "clients.csv"
)

CLIENTS_DOCUMENTATION = str(
    PROJECT_ROOT
    / "data"
    / "documentation"
    / "clients_documentation.md"
)

ORDERS_CSV = str(
    PROJECT_ROOT
    / "data"
    / "inputs"
    / "orders.csv"
)

ORDERS_DOCUMENTATION = str(
    PROJECT_ROOT
    / "data"
    / "documentation"
    / "orders_documentation.md"
)


def create_semantic_model_payload() -> dict:
    """
    Crée une requête valide de construction
    du modèle sémantique.
    """

    return {
        "model_name": "sales",
        "project_name": (
            "semantic_layer_builder"
        ),
        "clients_csv_path": CLIENTS_CSV,
        "clients_documentation_path": (
            CLIENTS_DOCUMENTATION
        ),
        "orders_csv_path": ORDERS_CSV,
        "orders_documentation_path": (
            ORDERS_DOCUMENTATION
        ),
        "relationship_source_column": (
            "CLIENT_ID"
        ),
        "relationship_target_column": (
            "CLIENT_ID"
        ),
        "documented_cardinality": (
            "many-to-one"
        ),
    }


def test_metadata_endpoint_returns_success() -> None:
    response = client.post(
        "/api/v1/metadata/analyze",
        json={
            "file_path": CLIENTS_CSV,
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["status"] == "success"

    metadata = result["metadata"]

    assert metadata["table_name"] == "CLIENTS"
    assert metadata["row_count"] == 4

    assert [
        column["name"]
        for column in metadata["columns"]
    ] == [
        "CLIENT_ID",
        "CLIENT_NAME",
        "COUNTRY",
        "CREATION_DATE",
        "IS_ACTIVE",
    ]


def test_metadata_endpoint_returns_404() -> None:
    response = client.post(
        "/api/v1/metadata/analyze",
        json={
            "file_path": str(
                PROJECT_ROOT
                / "data"
                / "inputs"
                / "missing.csv"
            ),
        },
    )

    assert response.status_code == 404

    detail = response.json()["detail"]

    assert (
        detail["error_type"]
        == "file_not_found"
    )


def test_documentation_endpoint_returns_success(
) -> None:
    response = client.post(
        "/api/v1/documentation/analyze",
        json={
            "file_path": (
                CLIENTS_DOCUMENTATION
            ),
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["status"] == "success"

    analysis = result["business_analysis"]

    assert analysis["table_name"] == "CLIENTS"

    assert (
        analysis["documented_primary_key"]
        == "CLIENT_ID"
    )

    assert len(analysis["columns"]) == 5

    assert (
        len(analysis["business_rules"])
        == 8
    )


def test_consistency_endpoint_returns_success(
) -> None:
    response = client.post(
        "/api/v1/consistency/analyze",
        json={
            "csv_file_path": CLIENTS_CSV,
            "documentation_file_path": (
                CLIENTS_DOCUMENTATION
            ),
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["status"] == "success"

    report = result["consistency_report"]

    assert (
        report["technical_table_name"]
        == "CLIENTS"
    )

    assert (
        report["documented_table_name"]
        == "CLIENTS"
    )

    assert (
        report["table_name_status"]
        == "consistent"
    )

    assert (
        report["primary_key_result"]["status"]
        == "consistent"
    )


def test_relationship_endpoint_returns_success(
) -> None:
    response = client.post(
        "/api/v1/relationships/analyze",
        json={
            "source_file_path": ORDERS_CSV,
            "source_column": "CLIENT_ID",
            "target_file_path": CLIENTS_CSV,
            "target_column": "CLIENT_ID",
            "documented_cardinality": (
                "many-to-one"
            ),
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["status"] == "success"

    report = result["relationship_report"]

    assert report["overall_status"] == "valid"

    assert (
        report["relationship_score"]
        == 100
    )

    assert (
        report["referential_integrity"]
        ["orphan_value_count"]
        == 0
    )

    assert (
        report["cardinality_analysis"]
        ["detected_cardinality"]
        == "many-to-one"
    )


def test_relationship_endpoint_reports_invalid_column(
) -> None:
    response = client.post(
        "/api/v1/relationships/analyze",
        json={
            "source_file_path": ORDERS_CSV,
            "source_column": "UNKNOWN_ID",
            "target_file_path": CLIENTS_CSV,
            "target_column": "CLIENT_ID",
            "documented_cardinality": (
                "many-to-one"
            ),
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["status"] == "success"

    report = result["relationship_report"]

    assert report["overall_status"] == "invalid"

    assert (
        report["column_validation"]
        ["source_column_exists"]
        is False
    )


def test_semantic_model_endpoint_builds_draft(
) -> None:
    payload = create_semantic_model_payload()

    response = client.post(
        "/api/v1/semantic-model/build",
        json=payload,
    )

    assert response.status_code == 200

    result = response.json()

    assert result["status"] == "success"

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


def test_semantic_model_endpoint_builds_ready_model(
) -> None:
    payload = create_semantic_model_payload()

    payload["connection_name"] = (
        "bigquery_connection"
    )

    payload["default_schema"] = "analytics"

    response = client.post(
        "/api/v1/semantic-model/build",
        json=payload,
    )

    assert response.status_code == 200

    result = response.json()

    assert result["status"] == "success"

    model = result["semantic_model"]

    assert model["generation_ready"] is True
    assert model["missing_information"] == []

    assert [
        view["view_name"]
        for view in model["views"]
    ] == [
        "clients",
        "orders",
    ]


def test_metadata_endpoint_rejects_unknown_field(
) -> None:
    response = client.post(
        "/api/v1/metadata/analyze",
        json={
            "file_path": CLIENTS_CSV,
            "unexpected_field": (
                "not allowed"
            ),
        },
    )

    assert response.status_code == 422


def test_relationship_endpoint_rejects_bad_cardinality(
) -> None:
    response = client.post(
        "/api/v1/relationships/analyze",
        json={
            "source_file_path": ORDERS_CSV,
            "source_column": "CLIENT_ID",
            "target_file_path": CLIENTS_CSV,
            "target_column": "CLIENT_ID",
            "documented_cardinality": (
                "several-to-one"
            ),
        },
    )

    assert response.status_code == 422