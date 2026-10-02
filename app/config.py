import os
from pathlib import Path

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class ApplicationSettings(BaseModel):
    """
    Configuration centralisée du
    Semantic Layer Builder.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    application_name: str = Field(
        min_length=1,
    )

    application_version: str = Field(
        min_length=1,
    )

    environment: str = Field(
        min_length=1,
    )

    agent_model: str = Field(
        min_length=1,
    )

    project_root: Path

    data_directory: Path

    input_directory: Path

    documentation_directory: Path

    output_directory: Path

    lookml_output_directory: Path

    log_level: str = Field(
        min_length=1,
    )

    log_directory: Path

    log_file_name: str = Field(
        min_length=1,
    )


def get_project_root() -> Path:
    """
    Retourne la racine absolue du projet.
    """

    return Path(
        __file__
    ).resolve().parents[1]


def load_settings() -> ApplicationSettings:
    """
    Charge la configuration depuis
    les variables d'environnement.

    Des valeurs locales sûres sont utilisées
    lorsque les variables sont absentes.
    """

    project_root = get_project_root()

    data_directory = (
        project_root / "data"
    )

    output_directory = (
        data_directory / "outputs"
    )

    log_directory = (
        project_root / "logs"
    )

    return ApplicationSettings(
        application_name=os.getenv(
            "APP_NAME",
            "semantic-layer-builder",
        ),
        application_version=os.getenv(
            "APP_VERSION",
            "0.1.0",
        ),
        environment=os.getenv(
            "APP_ENV",
            "development",
        ),
        agent_model=os.getenv(
            "AGENT_MODEL",
            "gemini-flash-latest",
        ),
        project_root=project_root,
        data_directory=data_directory,
        input_directory=(
            data_directory / "inputs"
        ),
        documentation_directory=(
            data_directory / "documentation"
        ),
        output_directory=output_directory,
        lookml_output_directory=(
            output_directory / "lookml"
        ),
        log_level=os.getenv(
            "LOG_LEVEL",
            "INFO",
        ).upper(),
        log_directory=log_directory,
        log_file_name=os.getenv(
            "LOG_FILE_NAME",
            "semantic_layer_builder.log",
        ),
    )


settings = load_settings()