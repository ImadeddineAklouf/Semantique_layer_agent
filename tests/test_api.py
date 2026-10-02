from pathlib import Path

from fastapi.testclient import TestClient

from app.api.main import app
from types import SimpleNamespace

import app.api.routes as api_routes

client = TestClient(app)


PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]


def create_valid_payload() -> dict:
    """
    Crée une requête API valide utilisant
    les fichiers réels du projet.
    """

    return {
        "model_name": "sales",
        "project_name": (
            "semantic_layer_builder"
        ),
        "clients_csv_path": str(
            PROJECT_ROOT
            / "data"
            / "inputs"
            / "clients.csv"
        ),
        "clients_documentation_path": str(
            PROJECT_ROOT
            / "data"
            / "documentation"
            / "clients_documentation.md"
        ),
        "orders_csv_path": str(
            PROJECT_ROOT
            / "data"
            / "inputs"
            / "orders.csv"
        ),
        "orders_documentation_path": str(
            PROJECT_ROOT
            / "data"
            / "documentation"
            / "orders_documentation.md"
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
        "connection_name": (
            "bigquery_connection"
        ),
        "default_schema": "analytics",
    }


def test_health_endpoint_returns_success() -> None:
    """
    Vérifie l'état de santé de l'API.
    """

    response = client.get("/health")

    assert response.status_code == 200

    assert response.json() == {
        "status": "healthy",
        "service": (
            "semantic-layer-builder"
        ),
        "version": "0.1.0",
    }


def test_openapi_contains_expected_routes() -> None:
    """
    Vérifie que les routes sont bien présentes
    dans la documentation OpenAPI.
    """

    response = client.get("/openapi.json")

    assert response.status_code == 200

    paths = response.json()["paths"]

    assert "/health" in paths

    assert (
        "/api/v1/lookml/preview"
        in paths
    )

    assert (
        "/api/v1/lookml/generate"
        in paths
    )

    assert "get" in paths["/health"]

    assert (
        "post"
        in paths[
            "/api/v1/lookml/preview"
        ]
    )

    assert (
        "post"
        in paths[
            "/api/v1/lookml/generate"
        ]
    )


def test_preview_endpoint_returns_success() -> None:
    """
    Vérifie la génération et la validation
    LookML sans écriture de fichiers.
    """

    response = client.post(
        "/api/v1/lookml/preview",
        json=create_valid_payload(),
    )

    assert response.status_code == 200

    result = response.json()

    assert result["status"] == "success"

    assert (
        result["pipeline_stage"]
        == "lookml_validation"
    )

    assert (
        result["validation_report"]["valid"]
        is True
    )

    assert (
        result["validation_report"]["error_count"]
        == 0
    )

    assert result["written_files"] == []


def test_preview_returns_three_artifacts() -> None:
    """
    Vérifie les trois artefacts produits
    par la prévisualisation.
    """

    response = client.post(
        "/api/v1/lookml/preview",
        json=create_valid_payload(),
    )

    assert response.status_code == 200

    result = response.json()

    file_names = [
        generated_file["file_name"]
        for generated_file
        in result["generation_result"]["files"]
    ]

    assert file_names == [
        "clients.view.lkml",
        "orders.view.lkml",
        "sales.model.lkml",
    ]


def test_preview_returns_ready_semantic_model() -> None:
    """
    Vérifie le modèle sémantique retourné
    par l'endpoint de prévisualisation.
    """

    response = client.post(
        "/api/v1/lookml/preview",
        json=create_valid_payload(),
    )

    assert response.status_code == 200

    semantic_model = response.json()[
        "semantic_model"
    ]

    assert (
        semantic_model["generation_ready"]
        is True
    )

    assert (
        semantic_model["connection_name"]
        == "bigquery_connection"
    )

    assert (
        semantic_model["default_schema"]
        == "analytics"
    )

    assert (
        semantic_model["missing_information"]
        == []
    )

    view_names = [
        view["view_name"]
        for view in semantic_model["views"]
    ]

    assert view_names == [
        "clients",
        "orders",
    ]


def test_preview_returns_valid_relationship() -> None:
    """
    Vérifie la relation ORDERS vers CLIENTS.
    """

    response = client.post(
        "/api/v1/lookml/preview",
        json=create_valid_payload(),
    )

    assert response.status_code == 200

    relationship = response.json()[
        "relationship_report"
    ]

    assert (
        relationship["overall_status"]
        == "valid"
    )

    assert (
        relationship["relationship_score"]
        == 100
    )

    assert (
        relationship["referential_integrity"]
        ["orphan_value_count"]
        == 0
    )

    assert (
        relationship["referential_integrity"]
        ["match_ratio"]
        == 1.0
    )

    assert (
        relationship["cardinality_analysis"]
        ["detected_cardinality"]
        == "many-to-one"
    )


def test_preview_rejects_missing_source() -> None:
    """
    Vérifie qu'un fichier source absent
    produit une réponse HTTP 404.
    """

    payload = create_valid_payload()

    payload["clients_csv_path"] = str(
        PROJECT_ROOT
        / "data"
        / "inputs"
        / "missing.csv"
    )

    response = client.post(
        "/api/v1/lookml/preview",
        json=payload,
    )

    assert response.status_code == 404

    detail = response.json()["detail"]

    assert detail["status"] == "error"

    assert (
        detail["error_type"]
        == "file_not_found"
    )


def test_preview_rejects_invalid_cardinality() -> None:
    """
    Vérifie la validation Pydantic
    de la cardinalité.
    """

    payload = create_valid_payload()

    payload["documented_cardinality"] = (
        "one-to-several"
    )

    response = client.post(
        "/api/v1/lookml/preview",
        json=payload,
    )

    assert response.status_code == 422


def test_preview_rejects_missing_required_field() -> None:
    """
    Vérifie qu'un paramètre obligatoire absent
    produit une réponse HTTP 422.
    """

    payload = create_valid_payload()

    del payload["connection_name"]

    response = client.post(
        "/api/v1/lookml/preview",
        json=payload,
    )

    assert response.status_code == 422


def test_preview_rejects_unknown_field() -> None:
    """
    Vérifie que les champs inconnus
    sont refusés.
    """

    payload = create_valid_payload()

    payload["unexpected_field"] = (
        "not allowed"
    )

    response = client.post(
        "/api/v1/lookml/preview",
        json=payload,
    )

    assert response.status_code == 422


def test_generate_endpoint_writes_three_files(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """
    Vérifie l'écriture réelle des trois fichiers
    dans un environnement temporaire sécurisé.
    """

    monkeypatch.chdir(tmp_path)

    payload = create_valid_payload()

    payload["output_directory"] = (
        "data/outputs/lookml"
    )

    payload["overwrite"] = False

    response = client.post(
        "/api/v1/lookml/generate",
        json=payload,
    )

    assert response.status_code == 200

    result = response.json()

    assert result["status"] == "success"

    assert (
        result["pipeline_stage"]
        == "completed"
    )

    assert (
        result["validation_report"]["valid"]
        is True
    )

    assert len(result["written_files"]) == 3

    expected_file_names = {
        "clients.view.lkml",
        "orders.view.lkml",
        "sales.model.lkml",
    }

    written_file_names = {
        Path(file_path).name
        for file_path
        in result["written_files"]
    }

    assert (
        written_file_names
        == expected_file_names
    )

def test_generate_endpoint_writes_three_files(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """
    Vérifie l'écriture réelle des trois fichiers
    dans un environnement temporaire sécurisé.

    Le test remplace localement la racine du projet
    et la racine autorisée des sorties afin de ne pas
    écrire dans le vrai dossier data/outputs.
    """

    temporary_output_root = (
        tmp_path / "data" / "outputs"
    )

    temporary_settings = SimpleNamespace(
        project_root=tmp_path,
        output_directory=temporary_output_root,
    )

    monkeypatch.setattr(
        api_routes,
        "settings",
        temporary_settings,
    )

    monkeypatch.setattr(
        api_routes,
        "ALLOWED_OUTPUT_ROOT",
        str(temporary_output_root),
    )

    payload = create_valid_payload()

    payload["output_directory"] = (
        "data/outputs/lookml"
    )

    payload["overwrite"] = False

    response = client.post(
        "/api/v1/lookml/generate",
        json=payload,
    )

    assert response.status_code == 200

    result = response.json()

    assert result["status"] == "success"

    assert (
        result["pipeline_stage"]
        == "completed"
    )

    assert (
        result["validation_report"]["valid"]
        is True
    )

    assert len(result["written_files"]) == 3

    expected_file_names = {
        "clients.view.lkml",
        "orders.view.lkml",
        "sales.model.lkml",
    }

    written_paths = {
        Path(file_path)
        for file_path in result["written_files"]
    }

    written_file_names = {
        path.name
        for path in written_paths
    }

    assert (
        written_file_names
        == expected_file_names
    )

    for file_path in written_paths:
        assert file_path.exists()
        assert file_path.is_file()

        file_path.resolve().relative_to(
            temporary_output_root.resolve()
        )

def test_root_endpoint_returns_service_information(
) -> None:
    response = client.get("/")

    assert response.status_code == 200

    result = response.json()

    assert (
        result["service"]
        == "semantic-layer-builder"
    )

    assert result["version"] == "0.1.0"

    assert result["environment"] == (
        "development"
    )

    assert result["documentation"] == "/docs"
    assert result["health"] == "/health"

def test_health_response_contains_request_id() -> None:
    """
    Vérifie que chaque réponse possède
    un identifiant de requête.
    """

    response = client.get("/health")

    assert response.status_code == 200

    assert "X-Request-ID" in response.headers

    request_id = response.headers[
        "X-Request-ID"
    ]

    assert request_id
    assert len(request_id) == 32


def test_request_ids_are_unique() -> None:
    """
    Vérifie que deux requêtes différentes
    reçoivent des identifiants différents.
    """

    first_response = client.get("/health")
    second_response = client.get("/health")

    first_request_id = first_response.headers[
        "X-Request-ID"
    ]

    second_request_id = second_response.headers[
        "X-Request-ID"
    ]

    assert first_request_id != second_request_id