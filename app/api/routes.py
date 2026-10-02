from typing import Any
from pathlib import Path

from fastapi import (
    APIRouter,
    HTTPException,
    status,
)
from app.config import settings
from app.api.schemas import (
    ConsistencyAnalysisRequest,
    DocumentationAnalysisRequest,
    HealthResponse,
    LookMLGenerationRequest,
    LookMLProjectRequest,
    MetadataAnalysisRequest,
    RelationshipAnalysisRequest,
    SemanticModelBuildRequest,
)
from app.tools.consistency_tools import (
    compare_csv_with_documentation,
)
from app.tools.documentation_tools import (
    analyze_documentation_file,
)
from app.tools.lookml_generation_tools import (
    generate_lookml_project,
)
from app.tools.metadata_tools import (
    analyze_csv_file,
)
from app.tools.relationship_tools import (
    analyze_table_relationship,
)
from app.tools.semantic_model_tools import (
    build_semantic_model_from_sources,
)


router = APIRouter()

ALLOWED_OUTPUT_ROOT = str(
    settings.output_directory
)

def raise_for_tool_failure(
    result: dict[str, Any],
) -> None:
    """
    Transforme les erreurs retournées par les Tools
    déterministes en réponses HTTP structurées.
    """

    if result.get("status") == "success":
        return

    error_type = result.get("error_type")

    if error_type == "file_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result,
        )

    if error_type in {
        "invalid_input",
        "invalid_format",
        "empty_file",
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result,
        )

    raise HTTPException(
        status_code=(
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
        detail=result,
    )


def raise_for_pipeline_failure(
    result: dict[str, Any],
) -> None:
    """
    Transforme les échecs du pipeline LookML
    en erreurs HTTP structurées.
    """

    pipeline_status = result.get("status")

    if pipeline_status == "success":
        return

    if pipeline_status in {
        "blocked",
        "validation_failed",
    }:
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=result,
        )

    error_type = result.get("error_type")

    if error_type == "file_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result,
        )

    if error_type == "file_exists":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=result,
        )

    if error_type == "invalid_input":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result,
        )

    raise HTTPException(
        status_code=(
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
        detail=result,
    )


@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
)

def health_check() -> HealthResponse:
    """
    Vérifie que l'API est disponible.
    """

    return HealthResponse(
        status="healthy",
        service=settings.application_name,
        version=settings.application_version,
    )

@router.post(
    "/api/v1/metadata/analyze",
    tags=["Analysis"],
)
def analyze_metadata(
    request: MetadataAnalysisRequest,
) -> dict[str, Any]:
    """
    Analyse les métadonnées techniques
    d'un fichier CSV.
    """

    result = analyze_csv_file(
        request.file_path
    )

    raise_for_tool_failure(result)

    return result


@router.post(
    "/api/v1/documentation/analyze",
    tags=["Analysis"],
)
def analyze_documentation(
    request: DocumentationAnalysisRequest,
) -> dict[str, Any]:
    """
    Analyse une documentation métier
    Markdown ou TXT.
    """

    result = analyze_documentation_file(
        request.file_path
    )

    raise_for_tool_failure(result)

    return result


@router.post(
    "/api/v1/consistency/analyze",
    tags=["Analysis"],
)
def analyze_consistency(
    request: ConsistencyAnalysisRequest,
) -> dict[str, Any]:
    """
    Compare un fichier CSV avec
    sa documentation métier.
    """

    result = compare_csv_with_documentation(
        request.csv_file_path,
        request.documentation_file_path,
    )

    raise_for_tool_failure(result)

    return result


@router.post(
    "/api/v1/relationships/analyze",
    tags=["Analysis"],
)
def analyze_relationship(
    request: RelationshipAnalysisRequest,
) -> dict[str, Any]:
    """
    Analyse une relation entre deux tables.
    """

    result = analyze_table_relationship(
        source_file_path=(
            request.source_file_path
        ),
        source_column=request.source_column,
        target_file_path=(
            request.target_file_path
        ),
        target_column=request.target_column,
        documented_cardinality=(
            request.documented_cardinality
        ),
    )

    raise_for_tool_failure(result)

    return result


@router.post(
    "/api/v1/semantic-model/build",
    tags=["Semantic Model"],
)
def build_semantic_model(
    request: SemanticModelBuildRequest,
) -> dict[str, Any]:
    """
    Construit une spécification sémantique
    sans produire de fichiers LookML.
    """

    result = build_semantic_model_from_sources(
        model_name=request.model_name,
        project_name=request.project_name,
        clients_csv_path=(
            request.clients_csv_path
        ),
        clients_documentation_path=(
            request.clients_documentation_path
        ),
        orders_csv_path=(
            request.orders_csv_path
        ),
        orders_documentation_path=(
            request.orders_documentation_path
        ),
        relationship_source_column=(
            request.relationship_source_column
        ),
        relationship_target_column=(
            request.relationship_target_column
        ),
        documented_cardinality=(
            request.documented_cardinality
        ),
        connection_name=request.connection_name,
        default_schema=request.default_schema,
    )

    raise_for_tool_failure(result)

    return result


@router.post(
    "/api/v1/lookml/preview",
    tags=["LookML"],
)
def preview_lookml_project(
    request: LookMLProjectRequest,
) -> dict[str, Any]:
    """
    Génère et valide les artefacts LookML
    sans écrire de fichiers.
    """

    result = generate_lookml_project(
        model_name=request.model_name,
        project_name=request.project_name,
        clients_csv_path=(
            request.clients_csv_path
        ),
        clients_documentation_path=(
            request.clients_documentation_path
        ),
        orders_csv_path=(
            request.orders_csv_path
        ),
        orders_documentation_path=(
            request.orders_documentation_path
        ),
        relationship_source_column=(
            request.relationship_source_column
        ),
        relationship_target_column=(
            request.relationship_target_column
        ),
        documented_cardinality=(
            request.documented_cardinality
        ),
        connection_name=request.connection_name,
        default_schema=request.default_schema,
        write_files=False,
        overwrite=False,
    )

    raise_for_pipeline_failure(result)

    return result

@router.post(
    "/api/v1/lookml/generate",
    tags=["LookML"],
)
def generate_lookml_files(
    request: LookMLGenerationRequest,
) -> dict[str, Any]:
    """
    Génère, valide et écrit les fichiers LookML.
    """

    requested_output = Path(
        request.output_directory
    )

    if requested_output.is_absolute():
        resolved_output_directory = str(
            requested_output.resolve()
        )

    else:
        resolved_output_directory = str(
            (
                settings.project_root
                / requested_output
            ).resolve()
        )

    result = generate_lookml_project(
        model_name=request.model_name,
        project_name=request.project_name,
        clients_csv_path=(
            request.clients_csv_path
        ),
        clients_documentation_path=(
            request.clients_documentation_path
        ),
        orders_csv_path=(
            request.orders_csv_path
        ),
        orders_documentation_path=(
            request.orders_documentation_path
        ),
        relationship_source_column=(
            request.relationship_source_column
        ),
        relationship_target_column=(
            request.relationship_target_column
        ),
        documented_cardinality=(
            request.documented_cardinality
        ),
        connection_name=(
            request.connection_name
        ),
        default_schema=(
            request.default_schema
        ),
        output_directory=(
            resolved_output_directory
        ),
        allowed_root_directory=(
            ALLOWED_OUTPUT_ROOT
        ),
        write_files=True,
        overwrite=request.overwrite,
    )

    raise_for_pipeline_failure(result)

    return result