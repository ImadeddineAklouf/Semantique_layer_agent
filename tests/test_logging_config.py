import logging

from app.logging_config import (
    LOGGER_NAME,
    configure_logging,
    get_log_level,
    get_logger,
)


def test_get_log_level_returns_expected_levels(
) -> None:
    assert get_log_level("DEBUG") == logging.DEBUG
    assert get_log_level("INFO") == logging.INFO

    assert (
        get_log_level("WARNING")
        == logging.WARNING
    )

    assert get_log_level("ERROR") == logging.ERROR


def test_unknown_log_level_defaults_to_info(
) -> None:
    assert (
        get_log_level("UNKNOWN")
        == logging.INFO
    )


def test_configure_logging_returns_logger(
) -> None:
    logger = configure_logging(
        force=True
    )

    assert isinstance(
        logger,
        logging.Logger,
    )

    assert logger.name == LOGGER_NAME
    assert logger.propagate is False

    assert len(logger.handlers) == 2


def test_get_logger_returns_child_logger(
) -> None:
    logger = get_logger("api")

    assert logger.name == (
        f"{LOGGER_NAME}.api"
    )


def test_repeated_configuration_does_not_duplicate_handlers(
) -> None:
    first_logger = configure_logging(
        force=True
    )

    handler_count = len(
        first_logger.handlers
    )

    second_logger = configure_logging(
        force=False
    )

    assert second_logger is first_logger

    assert len(
        second_logger.handlers
    ) == handler_count