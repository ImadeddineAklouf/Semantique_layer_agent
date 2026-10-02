from pathlib import Path

import pandas as pd

from app.schemas import (
    CardinalityAnalysis,
    CardinalityType,
    ReferentialIntegrityResult,
    RelationshipAnalysisReport,
    RelationshipColumnValidation,
    RelationshipStatus,
)
from app.tools.csv_reader import read_csv_metadata


def load_relationship_dataframe(
    file_path: str,
) -> pd.DataFrame:
    """
    Charge un fichier CSV utilisé dans une relation.

    La fonction read_csv_metadata() est appelée en premier
    afin de réutiliser les contrôles déjà présents dans le projet.

    Args:
        file_path:
            Chemin vers le fichier CSV.

    Returns:
        Le DataFrame chargé avec Pandas.

    Raises:
        FileNotFoundError:
            si le fichier n'existe pas.

        ValueError:
            si le fichier est invalide ou vide.
    """

    read_csv_metadata(file_path)

    path = Path(file_path)

    try:
        dataframe = pd.read_csv(path)

    except pd.errors.EmptyDataError as error:
        raise ValueError(
            f"Le fichier CSV est vide : {path}"
        ) from error

    except pd.errors.ParserError as error:
        raise ValueError(
            f"Le fichier CSV ne peut pas être analysé : {path}"
        ) from error

    return dataframe

def get_column_metadata(
    file_path: str,
    column_name: str,
):
    """
    Retourne les métadonnées d'une colonne.

    Args:
        file_path:
            Chemin vers le fichier CSV.

        column_name:
            Nom de la colonne recherchée.

    Returns:
        L'objet ColumnMetadata correspondant,
        ou None si la colonne n'existe pas.
    """

    metadata = read_csv_metadata(file_path)

    for column in metadata.columns:
        if column.name == column_name:
            return column

    return None

def validate_relationship_columns(
    source_file_path: str,
    source_column: str,
    target_file_path: str,
    target_column: str,
) -> RelationshipColumnValidation:
    """
    Vérifie l'existence et la compatibilité des colonnes
    participant à la relation.
    """

    source_metadata = read_csv_metadata(
        source_file_path
    )

    target_metadata = read_csv_metadata(
        target_file_path
    )

    source_column_metadata = next(
        (
            column
            for column in source_metadata.columns
            if column.name == source_column
        ),
        None,
    )

    target_column_metadata = next(
        (
            column
            for column in target_metadata.columns
            if column.name == target_column
        ),
        None,
    )

    source_exists = (
        source_column_metadata is not None
    )

    target_exists = (
        target_column_metadata is not None
    )

    issues: list[str] = []

    if not source_exists:
        issues.append(
            f"La colonne source '{source_column}' "
            "n'existe pas."
        )

    if not target_exists:
        issues.append(
            f"La colonne cible '{target_column}' "
            "n'existe pas."
        )

    if not source_exists or not target_exists:
        return RelationshipColumnValidation(
            source_column_exists=source_exists,
            target_column_exists=target_exists,
            source_column_type=(
                source_column_metadata.semantic_type
                if source_column_metadata
                else None
            ),
            target_column_type=(
                target_column_metadata.semantic_type
                if target_column_metadata
                else None
            ),
            types_compatible=None,
            status="invalid",
            issues=issues,
        )

    source_type = (
        source_column_metadata.semantic_type
    )

    target_type = (
        target_column_metadata.semantic_type
    )

    types_compatible = (
        source_type == target_type
    )

    if types_compatible:
        status: RelationshipStatus = "valid"

    else:
        status = "invalid"

        issues.append(
            "Les types des colonnes de jointure "
            "ne sont pas compatibles : "
            f"source='{source_type}', "
            f"cible='{target_type}'."
        )

    return RelationshipColumnValidation(
        source_column_exists=True,
        target_column_exists=True,
        source_column_type=source_type,
        target_column_type=target_type,
        types_compatible=types_compatible,
        status=status,
        issues=issues,
    )

def analyze_referential_integrity(
    source_dataframe: pd.DataFrame,
    source_column: str,
    target_dataframe: pd.DataFrame,
    target_column: str,
) -> ReferentialIntegrityResult:
    """
    Vérifie que les valeurs de clé étrangère de la source
    existent dans la colonne cible.

    Dans notre exemple :
    ORDERS.CLIENT_ID doit exister dans CLIENTS.CLIENT_ID.
    """

    source_series = source_dataframe[
        source_column
    ]

    target_series = target_dataframe[
        target_column
    ]

    null_foreign_key_count = int(
        source_series.isna().sum()
    )

    non_null_source_values = (
        source_series.dropna()
    )

    target_values = set(
        target_series.dropna().tolist()
    )

    unmatched_mask = (
        ~non_null_source_values.isin(
            target_values
        )
    )

    orphan_series = non_null_source_values[
        unmatched_mask
    ]

    orphan_values_raw = (
        orphan_series
        .drop_duplicates()
        .head(20)
        .tolist()
    )

    orphan_values = [
        str(value)
        for value in orphan_values_raw
    ]

    total_foreign_key_values = int(
        len(non_null_source_values)
    )

    orphan_value_count = int(
        unmatched_mask.sum()
    )

    matched_foreign_key_values = (
        total_foreign_key_values
        - orphan_value_count
    )

    if total_foreign_key_values > 0:
        match_ratio = (
            matched_foreign_key_values
            / total_foreign_key_values
        )
    else:
        match_ratio = 0.0

    if (
        orphan_value_count == 0
        and null_foreign_key_count == 0
    ):
        status: RelationshipStatus = "valid"

    elif orphan_value_count > 0:
        status = "invalid"

    else:
        status = "warning"

    return ReferentialIntegrityResult(
        total_foreign_key_values=(
            total_foreign_key_values
        ),
        matched_foreign_key_values=(
            matched_foreign_key_values
        ),
        orphan_value_count=orphan_value_count,
        orphan_values=orphan_values,
        null_foreign_key_count=(
            null_foreign_key_count
        ),
        match_ratio=round(
            match_ratio,
            4,
        ),
        status=status,
    )

def detect_relationship_cardinality(
    source_dataframe: pd.DataFrame,
    source_column: str,
    target_dataframe: pd.DataFrame,
    target_column: str,
) -> tuple[CardinalityType, bool, bool]:
    """
    Détecte la cardinalité à partir de l'unicité
    des colonnes de jointure.

    Returns:
        Un tuple contenant :
        - la cardinalité détectée ;
        - l'unicité de la colonne source ;
        - l'unicité de la colonne cible.
    """

    source_values = (
        source_dataframe[source_column]
        .dropna()
    )

    target_values = (
        target_dataframe[target_column]
        .dropna()
    )

    source_values_unique = (
        source_values.is_unique
    )

    target_values_unique = (
        target_values.is_unique
    )

    if (
        source_values_unique
        and target_values_unique
    ):
        detected_cardinality: CardinalityType = (
            "one-to-one"
        )

    elif (
        not source_values_unique
        and target_values_unique
    ):
        detected_cardinality = "many-to-one"

    elif (
        source_values_unique
        and not target_values_unique
    ):
        detected_cardinality = "one-to-many"

    else:
        detected_cardinality = "many-to-many"

    return (
        detected_cardinality,
        source_values_unique,
        target_values_unique,
    )

def analyze_cardinality(
    source_dataframe: pd.DataFrame,
    source_column: str,
    target_dataframe: pd.DataFrame,
    target_column: str,
    documented_cardinality: CardinalityType,
) -> CardinalityAnalysis:
    """
    Compare la cardinalité documentée
    avec la cardinalité détectée.
    """

    (
        detected_cardinality,
        source_values_unique,
        target_values_unique,
    ) = detect_relationship_cardinality(
        source_dataframe=source_dataframe,
        source_column=source_column,
        target_dataframe=target_dataframe,
        target_column=target_column,
    )

    if documented_cardinality == "unknown":
        status: RelationshipStatus = (
            "not_verifiable"
        )

        explanation = (
            "La cardinalité technique détectée est "
            f"'{detected_cardinality}', mais aucune "
            "cardinalité précise n'est documentée."
        )

    elif (
        documented_cardinality
        == detected_cardinality
    ):
        status = "valid"

        explanation = (
            "La cardinalité détectée dans les données "
            f"('{detected_cardinality}') correspond "
            "à la cardinalité documentée."
        )

    else:
        status = "invalid"

        explanation = (
            "La cardinalité détectée dans les données "
            f"('{detected_cardinality}') ne correspond "
            "pas à la cardinalité documentée "
            f"('{documented_cardinality}')."
        )

    return CardinalityAnalysis(
        documented_cardinality=(
            documented_cardinality
        ),
        detected_cardinality=(
            detected_cardinality
        ),
        source_values_unique=(
            source_values_unique
        ),
        target_values_unique=(
            target_values_unique
        ),
        status=status,
        explanation=explanation,
    )

def determine_relationship_status(
    column_status: RelationshipStatus,
    integrity_status: RelationshipStatus,
    cardinality_status: RelationshipStatus,
) -> RelationshipStatus:
    """
    Détermine le statut global de la relation.
    """

    statuses = {
        column_status,
        integrity_status,
        cardinality_status,
    }

    if "invalid" in statuses:
        return "invalid"

    if "warning" in statuses:
        return "warning"

    if "not_verifiable" in statuses:
        return "not_verifiable"

    return "valid"

def calculate_relationship_score(
    column_status: RelationshipStatus,
    integrity_status: RelationshipStatus,
    cardinality_status: RelationshipStatus,
) -> int:
    """
    Calcule un score heuristique de relation.
    """

    score = 100

    if column_status == "invalid":
        score -= 40

    elif column_status == "warning":
        score -= 15

    elif column_status == "not_verifiable":
        score -= 10

    if integrity_status == "invalid":
        score -= 40

    elif integrity_status == "warning":
        score -= 20

    elif integrity_status == "not_verifiable":
        score -= 10

    if cardinality_status == "invalid":
        score -= 20

    elif cardinality_status == "warning":
        score -= 10

    elif cardinality_status == "not_verifiable":
        score -= 5

    return max(
        0,
        min(score, 100),
    )

def analyze_relationship(
    source_file_path: str,
    source_column: str,
    target_file_path: str,
    target_column: str,
    documented_cardinality: CardinalityType,
) -> RelationshipAnalysisReport:
    """
    Analyse une relation entre deux fichiers CSV.

    Args:
        source_file_path:
            Fichier contenant la clé étrangère.

        source_column:
            Colonne de clé étrangère.

        target_file_path:
            Fichier contenant la clé de référence.

        target_column:
            Colonne de référence cible.

        documented_cardinality:
            Cardinalité déclarée dans la documentation.

    Returns:
        Un rapport Pydantic RelationshipAnalysisReport.
    """

    source_metadata = read_csv_metadata(
        source_file_path
    )

    target_metadata = read_csv_metadata(
        target_file_path
    )

    source_dataframe = (
        load_relationship_dataframe(
            source_file_path
        )
    )

    target_dataframe = (
        load_relationship_dataframe(
            target_file_path
        )
    )

    column_validation = (
        validate_relationship_columns(
            source_file_path=source_file_path,
            source_column=source_column,
            target_file_path=target_file_path,
            target_column=target_column,
        )
    )

    warnings: list[str] = []
    recommendations: list[str] = []

    if (
        not column_validation.source_column_exists
        or not column_validation.target_column_exists
    ):
        empty_integrity = ReferentialIntegrityResult(
            total_foreign_key_values=0,
            matched_foreign_key_values=0,
            orphan_value_count=0,
            orphan_values=[],
            null_foreign_key_count=0,
            match_ratio=0.0,
            status="not_verifiable",
        )

        empty_cardinality = CardinalityAnalysis(
            documented_cardinality=(
                documented_cardinality
            ),
            detected_cardinality="unknown",
            source_values_unique=False,
            target_values_unique=False,
            status="not_verifiable",
            explanation=(
                "La cardinalité ne peut pas être analysée "
                "car une colonne de jointure est absente."
            ),
        )

        recommendations.append(
            "Corriger le nom ou la présence des colonnes "
            "de jointure avant de réanalyser la relation."
        )

        return RelationshipAnalysisReport(
            source_file=source_metadata.file_name,
            target_file=target_metadata.file_name,
            source_table=source_metadata.table_name,
            source_column=source_column,
            target_table=target_metadata.table_name,
            target_column=target_column,
            column_validation=column_validation,
            referential_integrity=empty_integrity,
            cardinality_analysis=empty_cardinality,
            overall_status="invalid",
            relationship_score=20,
            warnings=warnings,
            recommendations=recommendations,
        )

    referential_integrity = (
        analyze_referential_integrity(
            source_dataframe=source_dataframe,
            source_column=source_column,
            target_dataframe=target_dataframe,
            target_column=target_column,
        )
    )

    cardinality_analysis = analyze_cardinality(
        source_dataframe=source_dataframe,
        source_column=source_column,
        target_dataframe=target_dataframe,
        target_column=target_column,
        documented_cardinality=(
            documented_cardinality
        ),
    )

    overall_status = determine_relationship_status(
        column_status=column_validation.status,
        integrity_status=(
            referential_integrity.status
        ),
        cardinality_status=(
            cardinality_analysis.status
        ),
    )

    relationship_score = (
        calculate_relationship_score(
            column_status=column_validation.status,
            integrity_status=(
                referential_integrity.status
            ),
            cardinality_status=(
                cardinality_analysis.status
            ),
        )
    )

    if (
        referential_integrity.orphan_value_count
        > 0
    ):
        warnings.append(
            "La relation contient des clés étrangères "
            "sans correspondance dans la table cible."
        )

        recommendations.append(
            "Corriger ou supprimer les enregistrements "
            "orphelins."
        )

    if (
        referential_integrity
        .null_foreign_key_count
        > 0
    ):
        warnings.append(
            "Certaines clés étrangères sont nulles."
        )

        recommendations.append(
            "Vérifier si la relation est facultative "
            "ou corriger les valeurs nulles."
        )

    if cardinality_analysis.status == "invalid":
        warnings.append(
            "La cardinalité détectée diffère "
            "de la cardinalité documentée."
        )

        recommendations.append(
            "Vérifier la documentation ou les doublons "
            "dans les colonnes de jointure."
        )

    if column_validation.status == "invalid":
        recommendations.append(
            "Aligner les types des colonnes "
            "de jointure."
        )

    return RelationshipAnalysisReport(
        source_file=source_metadata.file_name,
        target_file=target_metadata.file_name,
        source_table=source_metadata.table_name,
        source_column=source_column,
        target_table=target_metadata.table_name,
        target_column=target_column,
        column_validation=column_validation,
        referential_integrity=referential_integrity,
        cardinality_analysis=cardinality_analysis,
        overall_status=overall_status,
        relationship_score=relationship_score,
        warnings=warnings,
        recommendations=recommendations,
    )

