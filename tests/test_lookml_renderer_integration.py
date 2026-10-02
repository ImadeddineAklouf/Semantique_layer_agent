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
    Construit le modèle sémantique réel à partir
    des fichiers CLIENTS et ORDERS.

    Returns:
        Le modèle sémantique validé par Pydantic.
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

    assert result["status"] == "success"

    assert "semantic_model" in result

    semantic_model = (
        SemanticModelSpecification.model_validate(
            result["semantic_model"]
        )
    )

    assert semantic_model.generation_ready is True

    return semantic_model


def build_real_generation_result(
) -> LookMLGenerationResult:
    """
    Construit le modèle réel, puis génère
    les artefacts LookML en mémoire.

    Aucun fichier n'est écrit sur le disque.
    """

    semantic_model = build_real_semantic_model()

    generation_result = render_lookml_artifacts(
        semantic_model
    )

    return generation_result


def get_generated_file(
    generation_result: LookMLGenerationResult,
    file_name: str,
):
    """
    Retourne un artefact LookML à partir
    de son nom de fichier.

    Raises:
        AssertionError:
            si le fichier n'existe pas.
    """

    matching_files = [
        generated_file
        for generated_file
        in generation_result.files
        if generated_file.file_name == file_name
    ]

    assert len(matching_files) == 1, (
        f"Le fichier {file_name} devait être généré "
        "exactement une fois."
    )

    return matching_files[0]


def get_generated_content(
    generation_result: LookMLGenerationResult,
    file_name: str,
) -> str:
    """
    Retourne le contenu d'un artefact LookML.
    """

    generated_file = get_generated_file(
        generation_result=generation_result,
        file_name=file_name,
    )

    return generated_file.content


def test_real_semantic_model_is_ready() -> None:
    """
    Vérifie que le modèle réel est prêt
    lorsque la connexion et le schéma sont fournis.
    """

    semantic_model = build_real_semantic_model()

    assert semantic_model.model_name == "sales"

    assert (
        semantic_model.project_name
        == "semantic_layer_builder"
    )

    assert (
        semantic_model.connection_name
        == "bigquery_connection"
    )

    assert (
        semantic_model.default_schema
        == "analytics"
    )

    assert semantic_model.generation_ready is True
    assert semantic_model.missing_information == []


def test_real_generation_creates_three_files() -> None:
    """
    Vérifie la génération des deux vues
    et du fichier modèle.
    """

    result = build_real_generation_result()

    file_names = [
        generated_file.file_name
        for generated_file in result.files
    ]

    assert file_names == [
        "clients.view.lkml",
        "orders.view.lkml",
        "sales.model.lkml",
    ]


def test_real_generation_has_expected_status() -> None:
    """
    Vérifie le statut global de génération.

    Le résultat contient des avertissements légitimes :
    données sensibles et mesures automatiques.
    """

    result = build_real_generation_result()

    assert result.generation_status == (
        "generated_with_warnings"
    )

    assert result.missing_information == []

    assert result.output_directory is None

    assert result.written_files == []

    assert len(result.warnings) > 0


def test_real_generated_files_have_expected_types(
) -> None:
    """
    Vérifie les types des artefacts générés.
    """

    result = build_real_generation_result()

    clients_file = get_generated_file(
        result,
        "clients.view.lkml",
    )

    orders_file = get_generated_file(
        result,
        "orders.view.lkml",
    )

    model_file = get_generated_file(
        result,
        "sales.model.lkml",
    )

    assert clients_file.file_type == "view"
    assert clients_file.source_name == "clients"

    assert orders_file.file_type == "view"
    assert orders_file.source_name == "orders"

    assert model_file.file_type == "model"
    assert model_file.source_name == "sales"


def test_real_clients_view_has_expected_table() -> None:
    """
    Vérifie la déclaration de la table CLIENTS.
    """

    result = build_real_generation_result()

    content = get_generated_content(
        result,
        "clients.view.lkml",
    )

    assert "view: clients {" in content

    assert (
        "sql_table_name: analytics.CLIENTS ;;"
        in content
    )


def test_real_clients_view_has_expected_dimensions(
) -> None:
    """
    Vérifie les cinq dimensions de CLIENTS.
    """

    result = build_real_generation_result()

    content = get_generated_content(
        result,
        "clients.view.lkml",
    )

    expected_dimensions = [
        "client_id",
        "client_name",
        "country",
        "creation_date",
        "is_active",
    ]

    for dimension_name in expected_dimensions:
        assert (
            f"dimension: {dimension_name} {{"
            in content
        )


def test_real_clients_view_has_primary_key() -> None:
    """
    Vérifie que CLIENT_ID est généré
    comme clé primaire LookML.

    Le test vérifie directement les propriétés attendues
    dans le fichier généré sans rechercher la première
    accolade fermante, car ${TABLE} en contient déjà une.
    """

    result = build_real_generation_result()

    content = get_generated_content(
        result,
        "clients.view.lkml",
    )

    assert "dimension: client_id {" in content

    assert (
        "primary_key: yes"
        in content
    )

    assert (
        "sql: ${TABLE}.CLIENT_ID ;;"
        in content
    )

def test_real_clients_view_marks_sensitive_field(
) -> None:
    """
    Vérifie que CLIENT_NAME conserve
    un avertissement de sensibilité.
    """

    result = build_real_generation_result()

    generated_file = get_generated_file(
        result,
        "clients.view.lkml",
    )

    content = generated_file.content

    assert "dimension: client_name {" in content

    assert (
        "# Sensitive field:"
        in content
    )

    assert len(generated_file.warnings) > 0


def test_real_clients_view_has_count_measure() -> None:
    """
    Vérifie la mesure count de CLIENTS.
    """

    result = build_real_generation_result()

    content = get_generated_content(
        result,
        "clients.view.lkml",
    )

    assert "measure: count {" in content
    assert "type: count" in content


def test_real_orders_view_has_expected_table() -> None:
    """
    Vérifie la déclaration de la table ORDERS.
    """

    result = build_real_generation_result()

    content = get_generated_content(
        result,
        "orders.view.lkml",
    )

    assert "view: orders {" in content

    assert (
        "sql_table_name: analytics.ORDERS ;;"
        in content
    )


def test_real_orders_view_has_expected_dimensions(
) -> None:
    """
    Vérifie les cinq dimensions d'ORDERS.
    """

    result = build_real_generation_result()

    content = get_generated_content(
        result,
        "orders.view.lkml",
    )

    expected_dimensions = [
        "order_id",
        "client_id",
        "order_date",
        "amount",
        "status",
    ]

    for dimension_name in expected_dimensions:
        assert (
            f"dimension: {dimension_name} {{"
            in content
        )


def test_real_orders_view_has_primary_key() -> None:
    """
    Vérifie que ORDER_ID devient
    la clé primaire de la vue ORDERS.
    """

    result = build_real_generation_result()

    content = get_generated_content(
        result,
        "orders.view.lkml",
    )

    assert "dimension: order_id {" in content

    assert (
        "primary_key: yes"
        in content
    )

    assert (
        "sql: ${TABLE}.ORDER_ID ;;"
        in content
    )


def test_real_orders_view_has_expected_measures(
) -> None:
    """
    Vérifie les mesures de la vue ORDERS.
    """

    result = build_real_generation_result()

    content = get_generated_content(
        result,
        "orders.view.lkml",
    )

    expected_measures = [
        "count",
        "total_amount",
        "average_amount",
        "minimum_amount",
        "maximum_amount",
    ]

    for measure_name in expected_measures:
        assert (
            f"measure: {measure_name} {{"
            in content
        )


def test_real_orders_amount_measures_have_expected_types(
) -> None:
    """
    Vérifie les agrégations générées
    à partir de la colonne AMOUNT.
    """

    result = build_real_generation_result()

    content = get_generated_content(
        result,
        "orders.view.lkml",
    )

    assert "measure: total_amount {" in content
    assert "type: sum" in content

    assert (
        "measure: average_amount {"
        in content
    )

    assert "type: average" in content

    assert (
        "measure: minimum_amount {"
        in content
    )

    assert "type: min" in content

    assert (
        "measure: maximum_amount {"
        in content
    )

    assert "type: max" in content

    assert content.count(
        "sql: ${amount} ;;"
    ) == 4


def test_real_orders_view_does_not_aggregate_ids(
) -> None:
    """
    Vérifie qu'aucune mesure n'est générée
    à partir des identifiants.
    """

    result = build_real_generation_result()

    content = get_generated_content(
        result,
        "orders.view.lkml",
    )

    forbidden_measure_names = [
        "total_order_id",
        "average_order_id",
        "minimum_order_id",
        "maximum_order_id",
        "total_client_id",
        "average_client_id",
        "minimum_client_id",
        "maximum_client_id",
    ]

    for measure_name in forbidden_measure_names:
        assert measure_name not in content


def test_real_model_has_expected_connection() -> None:
    """
    Vérifie la connexion et l'inclusion
    des fichiers de vue.
    """

    result = build_real_generation_result()

    content = get_generated_content(
        result,
        "sales.model.lkml",
    )

    assert (
        'connection: "bigquery_connection"'
        in content
    )

    assert (
        'include: "/*.view.lkml"'
        in content
    )


def test_real_model_has_expected_explores() -> None:
    """
    Vérifie les Explores CLIENTS et ORDERS.
    """

    result = build_real_generation_result()

    content = get_generated_content(
        result,
        "sales.model.lkml",
    )

    assert "explore: clients {" in content
    assert "explore: orders {" in content


def test_real_model_has_clients_join_in_orders(
) -> None:
    """
    Vérifie la jointure ORDERS vers CLIENTS.
    """

    result = build_real_generation_result()

    content = get_generated_content(
        result,
        "sales.model.lkml",
    )

    assert "join: clients {" in content

    assert (
        "type: left_outer"
        in content
    )

    assert (
        "relationship: many_to_one"
        in content
    )

    assert (
        "sql_on: ${orders.client_id} "
        "= ${clients.client_id} ;;"
        in content
    )


def test_real_generation_does_not_write_files() -> None:
    """
    Vérifie que le renderer reste sans effet
    de bord sur le système de fichiers.
    """

    result = build_real_generation_result()
 
    assert result.output_directory is None
    assert result.written_files == []

def test_real_clients_view_has_only_one_primary_key(
) -> None:
    """
    Vérifie que la vue CLIENTS contient
    exactement une clé primaire.
    """

    result = build_real_generation_result()

    content = get_generated_content(
        result,
        "clients.view.lkml",
    )

    assert content.count(
        "primary_key: yes"
    ) == 1


def test_real_orders_view_has_only_one_primary_key(
) -> None:
    """
    Vérifie que la vue ORDERS contient
    exactement une clé primaire.
    """

    result = build_real_generation_result()

    content = get_generated_content(
        result,
        "orders.view.lkml",
    )

    assert content.count(
        "primary_key: yes"
    ) == 1