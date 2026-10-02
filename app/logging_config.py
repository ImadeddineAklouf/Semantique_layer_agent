import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.config import settings


LOGGER_NAME = "semantic_layer_builder"


def get_log_level(
    level_name: str,
) -> int:
    """
    Convertit un niveau textuel en niveau logging.

    Une valeur inconnue utilise INFO.
    """

    return getattr(
        logging,
        level_name.upper(),
        logging.INFO,
    )


def create_console_handler(
    log_level: int,
    formatter: logging.Formatter,
) -> logging.StreamHandler:
    """
    Crée le handler destiné au terminal.
    """

    handler = logging.StreamHandler()

    handler.setLevel(log_level)
    handler.setFormatter(formatter)

    return handler


def create_file_handler(
    log_file_path: Path,
    log_level: int,
    formatter: logging.Formatter,
) -> RotatingFileHandler:
    """
    Crée un fichier de logs rotatif.

    Le fichier actif est limité à 5 Mo.
    Cinq sauvegardes sont conservées.
    """

    handler = RotatingFileHandler(
        filename=log_file_path,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )

    handler.setLevel(log_level)
    handler.setFormatter(formatter)

    return handler


def configure_logging(
    force: bool = False,
) -> logging.Logger:
    """
    Configure le logger principal.

    La fonction peut être appelée plusieurs fois
    sans dupliquer les handlers.

    Args:
        force:
            Supprime puis recrée les handlers
            lorsque la valeur est True.

    Returns:
        Le logger principal configuré.
    """

    logger = logging.getLogger(
        LOGGER_NAME
    )

    if logger.handlers and not force:
        return logger

    if force:
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)

    settings.log_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    log_file_path = (
        settings.log_directory
        / settings.log_file_name
    )

    log_level = get_log_level(
        settings.log_level
    )

    formatter = logging.Formatter(
        fmt=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logger.setLevel(log_level)
    logger.propagate = False

    logger.addHandler(
        create_console_handler(
            log_level=log_level,
            formatter=formatter,
        )
    )

    logger.addHandler(
        create_file_handler(
            log_file_path=log_file_path,
            log_level=log_level,
            formatter=formatter,
        )
    )

    return logger


def get_logger(
    component_name: str | None = None,
) -> logging.Logger:
    """
    Retourne le logger principal ou un logger enfant.

    Exemples :
        get_logger()
        get_logger("api")
        get_logger("lookml_generation")
    """

    configure_logging()

    if not component_name:
        return logging.getLogger(
            LOGGER_NAME
        )

    return logging.getLogger(
        f"{LOGGER_NAME}.{component_name}"
    )