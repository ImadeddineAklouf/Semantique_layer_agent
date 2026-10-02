from pathlib import Path
from uuid import uuid4

from app.schemas import (
    GeneratedLookMLFile,
    LookMLGenerationResult,
)

ALLOWED_LOOKML_SUFFIXES = (
    ".view.lkml",
    ".model.lkml",
)

def validate_lookml_file_name(
    file_name: str,
) -> str:
    """
    Vérifie qu'un nom de fichier LookML est sûr.

    Le nom ne doit contenir ni chemin absolu,
    ni sous-répertoire, ni traversée de répertoire.

    Args:
        file_name:
            Nom du fichier à vérifier.

    Returns:
        Le nom validé.

    Raises:
        ValueError:
            si le nom est dangereux ou invalide.
    """

    if not file_name.strip():
        raise ValueError(
            "Le nom du fichier LookML ne peut pas être vide."
        )

    path = Path(file_name)

    if path.is_absolute():
        raise ValueError(
            "Un nom de fichier LookML ne peut pas "
            "être un chemin absolu."
        )

    if path.name != file_name:
        raise ValueError(
            "Le nom du fichier LookML ne doit contenir "
            "aucun sous-répertoire."
        )

    if file_name in {".", ".."}:
        raise ValueError(
            "Le nom du fichier LookML est invalide."
        )

    if not file_name.endswith(
        ALLOWED_LOOKML_SUFFIXES
    ):
        raise ValueError(
            "Extension LookML non autorisée. "
            "Les extensions acceptées sont "
            "'.view.lkml' et '.model.lkml'."
        )

    return file_name

def validate_lookml_file_type(
    generated_file: GeneratedLookMLFile,
) -> None:
    """
    Vérifie la cohérence entre le type déclaré
    et l'extension du fichier.
    """

    if (
        generated_file.file_type == "view"
        and not generated_file.file_name.endswith(
            ".view.lkml"
        )
    ):
        raise ValueError(
            "Un artefact de type 'view' doit utiliser "
            "l'extension '.view.lkml'."
        )

    if (
        generated_file.file_type == "model"
        and not generated_file.file_name.endswith(
            ".model.lkml"
        )
    ):
        raise ValueError(
            "Un artefact de type 'model' doit utiliser "
            "l'extension '.model.lkml'."
        )

def resolve_output_directory(
    output_directory: str,
    allowed_root_directory: str,
) -> Path:
    """
    Résout et valide le répertoire de sortie.

    Le répertoire final doit se trouver dans
    allowed_root_directory.

    Args:
        output_directory:
            Répertoire demandé pour les fichiers LookML.

        allowed_root_directory:
            Répertoire racine autorisé.

    Returns:
        Le chemin absolu validé.

    Raises:
        ValueError:
            si le répertoire sort de la racine autorisée.
    """

    allowed_root = Path(
        allowed_root_directory
    ).resolve()

    requested_directory = Path(
        output_directory
    )

    if requested_directory.is_absolute():
        resolved_directory = (
            requested_directory.resolve()
        )

    else:
        resolved_directory = (
            Path.cwd()
            / requested_directory
        ).resolve()

    try:
        resolved_directory.relative_to(
            allowed_root
        )

    except ValueError as error:
        raise ValueError(
            "Le répertoire de sortie doit rester "
            f"dans le répertoire autorisé : {allowed_root}"
        ) from error

    return resolved_directory

def validate_unique_file_names(
    generated_files: list[GeneratedLookMLFile],
) -> None:
    """
    Vérifie que deux artefacts ne possèdent pas
    le même nom de fichier.
    """

    file_names = [
        generated_file.file_name
        for generated_file in generated_files
    ]

    duplicate_names = sorted(
        {
            file_name
            for file_name in file_names
            if file_names.count(file_name) > 1
        }
    )

    if duplicate_names:
        raise ValueError(
            "Plusieurs artefacts possèdent le même "
            "nom de fichier : "
            + ", ".join(duplicate_names)
        )

def write_text_atomically(
    target_path: Path,
    content: str,
    overwrite: bool,
) -> None:
    """
    Écrit un fichier UTF-8 via un fichier temporaire.

    Le fichier temporaire est remplacé atomiquement
    lorsque l'écriture est terminée.
    """

    if target_path.exists() and not overwrite:
        raise FileExistsError(
            "Le fichier existe déjà et l'écrasement "
            f"n'est pas autorisé : {target_path}"
        )

    temporary_path = target_path.with_name(
        f".{target_path.name}."
        f"{uuid4().hex}.tmp"
    )

    try:
        temporary_path.write_text(
            content,
            encoding="utf-8",
            newline="\n",
        )

        if (
            target_path.exists()
            and overwrite
        ):
            target_path.unlink()

        temporary_path.replace(target_path)

    finally:
        if temporary_path.exists():
            temporary_path.unlink()

def write_lookml_artifacts(
    generation_result: LookMLGenerationResult,
    output_directory: str = (
        "data/outputs/lookml"
    ),
    allowed_root_directory: str = (
        "data/outputs"
    ),
    overwrite: bool = False,
) -> LookMLGenerationResult:
    """
    Écrit les artefacts LookML sur le disque.

    Args:
        generation_result:
            Résultat produit par render_lookml_artifacts().

        output_directory:
            Répertoire dans lequel les fichiers seront écrits.

        allowed_root_directory:
            Racine autorisée pour les sorties.

        overwrite:
            Autorise l'écrasement des fichiers existants
            lorsque la valeur est True.

    Returns:
        Une nouvelle instance LookMLGenerationResult
        contenant les chemins écrits.

    Raises:
        ValueError:
            si la génération est bloquée, si les fichiers
            sont invalides ou si le chemin est dangereux.

        FileExistsError:
            si un fichier existe déjà et overwrite=False.
    """

    if generation_result.generation_status == "blocked":
        raise ValueError(
            "Les fichiers LookML ne peuvent pas être écrits "
            "car la génération est bloquée."
        )

    if not generation_result.files:
        raise ValueError(
            "Aucun artefact LookML n'est disponible "
            "pour l'écriture."
        )

    validate_unique_file_names(
        generation_result.files
    )

    resolved_output_directory = (
        resolve_output_directory(
            output_directory=output_directory,
            allowed_root_directory=(
                allowed_root_directory
            ),
        )
    )

    target_paths: list[Path] = []

    for generated_file in generation_result.files:
        validated_file_name = (
            validate_lookml_file_name(
                generated_file.file_name
            )
        )

        validate_lookml_file_type(
            generated_file
        )

        target_path = (
            resolved_output_directory
            / validated_file_name
        ).resolve()

        try:
            target_path.relative_to(
                resolved_output_directory
            )

        except ValueError as error:
            raise ValueError(
                "Le fichier de sortie tente de quitter "
                "le répertoire autorisé."
            ) from error

        target_paths.append(
            target_path
        )

    existing_files = [
        target_path
        for target_path in target_paths
        if target_path.exists()
    ]

    if existing_files and not overwrite:
        existing_file_names = ", ".join(
            str(path)
            for path in existing_files
        )

        raise FileExistsError(
            "Les fichiers suivants existent déjà : "
            f"{existing_file_names}. "
            "Utilisez overwrite=True pour les remplacer."
        )

    resolved_output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    written_files: list[str] = []

    for generated_file, target_path in zip(
        generation_result.files,
        target_paths,
        strict=True,
    ):
        write_text_atomically(
            target_path=target_path,
            content=generated_file.content,
            overwrite=overwrite,
        )

        written_files.append(
            str(target_path)
        )

    return generation_result.model_copy(
        update={
            "output_directory": str(
                resolved_output_directory
            ),
            "written_files": written_files,
        }
    )

