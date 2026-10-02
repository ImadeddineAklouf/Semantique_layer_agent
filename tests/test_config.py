from pathlib import Path

from app.config import (
    ApplicationSettings,
    get_project_root,
    load_settings,
    settings,
)


def test_project_root_exists() -> None:
    project_root = get_project_root()

    assert project_root.exists()
    assert project_root.is_dir()

    assert (
        project_root
        / "app"
    ).exists()


def test_settings_have_expected_defaults() -> None:
    assert (
        settings.application_name
        == "semantic-layer-builder"
    )

    assert settings.application_version == "0.1.0"
    assert settings.environment == "development"

    assert settings.agent_model == (
        "gemini-flash-latest"
    )

    assert settings.log_level == "INFO"


def test_settings_paths_are_absolute() -> None:
    paths = [
        settings.project_root,
        settings.data_directory,
        settings.input_directory,
        settings.documentation_directory,
        settings.output_directory,
        settings.lookml_output_directory,
        settings.log_directory
    ]

    for path in paths:
        assert isinstance(path, Path)
        assert path.is_absolute()


def test_settings_paths_are_inside_project() -> None:
    paths = [
        settings.data_directory,
        settings.input_directory,
        settings.documentation_directory,
        settings.output_directory,
        settings.lookml_output_directory,
    ]

    for path in paths:
        path.relative_to(
            settings.project_root
        )


def test_load_settings_returns_model() -> None:
    loaded_settings = load_settings()

    assert isinstance(
        loaded_settings,
        ApplicationSettings,
    )


def test_settings_are_immutable() -> None:
    try:
        settings.application_name = "changed"

    except Exception:
        pass

    assert (
        settings.application_name
        == "semantic-layer-builder"
    )

def test_logging_settings_have_expected_defaults(
) -> None:
    assert settings.log_level == "INFO"

    assert (
        settings.log_file_name
        == "semantic_layer_builder.log"
    )

    assert (
        settings.log_directory
        == settings.project_root / "logs"
    )