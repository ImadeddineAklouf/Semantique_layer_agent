from pathlib import Path
from typing import Any

from app.schemas import (
    ColumnMetadata,
    ConfidenceLevel,
    DataQualityReport,
    PrimaryKeyCandidate,
    QualityLevel,
    SemanticType,
    TableMetadata,
)

import pandas as pd


def convert_value_to_json_compatible(value: Any) -> Any:
    """
    Convertit une valeur Pandas ou NumPy en valeur compatible avec JSON.

    Exemples :
    - int64 devient int
    - float64 devient float
    - NaN devient None
    - Timestamp devient une chaîne ISO
    """

    if pd.isna(value):
        return None

    if isinstance(value, pd.Timestamp):
        return value.isoformat()

    if hasattr(value, "item"):
        return value.item()

    return value


def detect_semantic_type(series: pd.Series) -> SemanticType:
    """
    Détermine un type métier simplifié pour une colonne.

    Les types possibles sont :
    - integer
    - float
    - boolean
    - date
    - string
    """

    if pd.api.types.is_bool_dtype(series):
        return "boolean"

    if pd.api.types.is_integer_dtype(series):
        return "integer"

    if pd.api.types.is_float_dtype(series):
        return "float"

    non_null_values = series.dropna()

    if non_null_values.empty:
        return "string"

    if pd.api.types.is_datetime64_any_dtype(series):
        return "date"

    if series.dtype == "object" or pd.api.types.is_string_dtype(series):
        converted_dates = pd.to_datetime(
            non_null_values,
            errors="coerce",
            format="mixed",
        )

        date_ratio = converted_dates.notna().mean()

        if date_ratio >= 0.80:
            return "date"

    return "string"


def detect_primary_key_candidates(dataframe: pd.DataFrame) -> list[str]:
    """
    Recherche les colonnes pouvant représenter une cl

    Une colonne est considérée comme candidate si :
    - elle ne contient aucune valeur nulle ;
    - toutes ses valeurs sont uniques.
    """

    candidates = []

    for column_name in dataframe.columns:
        column = dataframe[column_name]

        has_no_null_values = column.notna().all()
        contains_unique_values = column.is_unique

        if has_no_null_values and contains_unique_values:
            candidates.append(str(column_name))

    return candidates


def get_confidence_level(score: int) -> ConfidenceLevel:
    """
    Transforme un score technique en niveau de confiance.

    Ce niveau reste une estimation heuristique.
    """

    if score >= 75:
        return "high"

    if score >= 50:
        return "medium"

    return "low"


def analyze_primary_key_candidates(dataframe: pd.DataFrame,) -> list[PrimaryKeyCandidate]:
    """
    Évalue les colonnes uniques et non nulles à partir
    de règles heuristiques explicables.

    Le résultat ne constitue pas une confirmation métier.
    """

    candidate_names = detect_primary_key_candidates(
        dataframe
    )

    analyses: list[PrimaryKeyCandidate] = []

    for column_name in candidate_names:
        column = dataframe[column_name]
        normalized_name = str(column_name).upper()

        score = 50

        reasons = [
            "La colonne ne contient aucune valeur nulle.",
            "Toutes les valeurs observées sont uniques.",
        ]

        warnings: list[str] = []

        if (
            normalized_name == "ID"
            or normalized_name.endswith("_ID")
        ):
            score += 30

            reasons.append(
                "Le nom de la colonne correspond à un "
                "identifiant ou se termine par _ID."
            )

        elif "ID" in normalized_name:
            score += 15

            reasons.append(
                "Le nom de la colonne contient le terme ID."
            )

        if pd.api.types.is_integer_dtype(column):
            score += 10

            reasons.append(
                "La colonne possède un type entier."
            )

        if "NAME" in normalized_name:
            score -= 20

            warnings.append(
                "Un nom n'est généralement pas un identifiant "
                "stable ou garanti comme unique."
            )

        if (
            "DATE" in normalized_name
            or "TIME" in normalized_name
        ):
            score -= 20

            warnings.append(
                "Une date ou un horodatage peut être partagé "
                "par plusieurs enregistrements."
            )

        if "DESCRIPTION" in normalized_name:
            score -= 25

            warnings.append(
                "Une description ne constitue généralement "
                "pas une clé primaire fiable."
            )

        if len(dataframe) < 20:
            score -= 10

            warnings.append(
                "Le fichier contient moins de 20 lignes. "
                "L'unicité peut être liée à la petite taille "
                "de l'échantillon."
            )

        score = max(
            0,
            min(score, 100),
        )

        analyses.append(
            PrimaryKeyCandidate(
                column_name=str(column_name),
                score=score,
                confidence=get_confidence_level(score),
                reasons=reasons,
                warnings=warnings,
                recommended=False,
            )
        )

    analyses.sort(
        key=lambda candidate: candidate.score,
        reverse=True,
    )

    if analyses:
        highest_score = analyses[0].score

        highest_candidates = [
            candidate
            for candidate in analyses
            if candidate.score == highest_score
        ]

        if len(highest_candidates) == 1:
            analyses[0].recommended = True

    return analyses


def get_quality_level(
    score: int,
) -> QualityLevel:
    """
    Convertit un score de qualité en niveau lisible.
    """

    if score >= 90:
        return "excellent"

    if score >= 75:
        return "good"

    if score >= 50:
        return "warning"

    return "critical"


def analyze_data_quality(
    dataframe: pd.DataFrame,
) -> DataQualityReport:
    """
    Analyse plusieurs indicateurs techniques de qualité.

    Le rapport vérifie :
    - les valeurs nulles ;
    - les lignes dupliquées ;
    - les colonnes constantes ;
    - les colonnes fortement affectées par les valeurs nulles.

    Le score produit est une heuristique technique.
    """

    row_count = len(dataframe)

    total_null_values = int(
        dataframe.isna().sum().sum()
    )

    duplicate_row_count = int(
        dataframe.duplicated().sum()
    )

    if row_count > 0:
        duplicate_row_ratio = (
            duplicate_row_count / row_count
        )
    else:
        duplicate_row_ratio = 0.0

    constant_columns: list[str] = []
    high_null_columns: list[str] = []
    warnings: list[str] = []
    recommendations: list[str] = []

    score = 100

    for column_name in dataframe.columns:
        column = dataframe[column_name]

        unique_count = int(
            column.nunique(dropna=True)
        )

        null_count = int(
            column.isna().sum()
        )

        null_ratio = (
            null_count / row_count
            if row_count > 0
            else 0.0
        )

        if unique_count <= 1:
            constant_columns.append(
                str(column_name)
            )

        if null_ratio >= 0.30:
            high_null_columns.append(
                str(column_name)
            )

    if total_null_values > 0:
        score -= 10

        warnings.append(
            f"Le fichier contient "
            f"{total_null_values} valeur(s) nulle(s)."
        )

        recommendations.append(
            "Vérifier si les valeurs nulles sont autorisées "
            "par les règles métier."
        )

    if high_null_columns:
        score -= 20

        warnings.append(
            "Certaines colonnes contiennent au moins "
            "30 pour cent de valeurs nulles : "
            + ", ".join(high_null_columns)
            + "."
        )

        recommendations.append(
            "Étudier la suppression, l'imputation ou la "
            "correction des colonnes fortement incomplètes."
        )

    if duplicate_row_count > 0:
        score -= 20

        warnings.append(
            f"Le fichier contient "
            f"{duplicate_row_count} ligne(s) dupliquée(s)."
        )

        recommendations.append(
            "Analyser les doublons et déterminer s'ils doivent "
            "être supprimés ou consolidés."
        )

    if constant_columns:
        score -= 10

        warnings.append(
            "Certaines colonnes ne contiennent qu'une seule "
            "valeur distincte : "
            + ", ".join(constant_columns)
            + "."
        )

        recommendations.append(
            "Vérifier l'utilité métier des colonnes constantes."
        )

    if row_count < 20:
        score -= 5

        warnings.append(
            "Le fichier contient moins de 20 lignes. "
            "Les conclusions statistiques sont limitées."
        )

        recommendations.append(
            "Effectuer également l'analyse sur un volume "
            "de données plus représentatif."
        )

    score = max(
        0,
        min(score, 100),
    )

    return DataQualityReport(
        quality_score=score,
        quality_level=get_quality_level(score),
        total_null_values=total_null_values,
        duplicate_row_count=duplicate_row_count,
        duplicate_row_ratio=round(
            duplicate_row_ratio,
            4,
        ),
        constant_columns=constant_columns,
        high_null_columns=high_null_columns,
        warnings=warnings,
        recommendations=recommendations,
    )


def read_csv_metadata(file_path: str) -> TableMetadata:
    """
    Lit un fichier CSV et retourne ses principales métadonnées.

    Args:
        file_path: chemin vers le fichier CSV.

    Returns:
        Un dictionnaire contenant les métadonnées de la table.

    Raises:
        FileNotFoundError: si le fichier n'existe pas.
        ValueError: si le fichier n'est pas un CSV ou s'il est vide.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Le fichier n'existe pas : {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Le chemin ne correspond pas à un fichier : {path}"
        )

    if path.suffix.lower() != ".csv":
        raise ValueError(
            f"Le format '{path.suffix}' n'est pas accepté. "
            "Un fichier CSV est attendu."
        )

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

    if dataframe.empty:
        raise ValueError(
            f"Le fichier CSV ne contient aucune ligne : {path}"
        )

    columns_metadata = []

    for column_name in dataframe.columns:
        column = dataframe[column_name]

        sample_values = [
            convert_value_to_json_compatible(value) for value in column.dropna().head(3).tolist()
        ]

        column_metadata = ColumnMetadata(
            name=str(column_name),
            pandas_type=str(column.dtype),
            semantic_type=detect_semantic_type(column),
            nullable=bool(column.isna().any()),
            null_count=int(column.isna().sum()),
            unique_count=int(column.nunique(dropna=True)),
            sample_values=sample_values,
        )

        columns_metadata.append(column_metadata)

    return TableMetadata(
        file_name=path.name,
        table_name=path.stem.upper(),
        file_path=str(path.resolve()),
        row_count=int(len(dataframe)),
        column_count=int(len(dataframe.columns)),
        primary_key_candidates=detect_primary_key_candidates(dataframe),
        primary_key_analysis=analyze_primary_key_candidates(dataframe),
        quality_report = analyze_data_quality(dataframe),
        columns=columns_metadata,
    )