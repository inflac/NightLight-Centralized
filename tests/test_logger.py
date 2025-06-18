import logging
from unittest.mock import patch

from app.logger import LOGGING_CONFIG, create_logger


@patch("app.logger.logger")
def test_create_logger_invalid_log_level(mock_logger):
    logger = create_logger(log_to_file=False, file_log_format="", log_level="NOTALEVEL")
    assert logger.getEffectiveLevel() == logging.INFO
    mock_logger.critical.assert_any_call("The configured log level 'NOTALEVEL' is not valid! The logger will use 'info' now")


def test_file_handler_not_duplicated():
    LOGGING_CONFIG["loggers"]["nightlight"]["handlers"] = ["file"]

    create_logger(log_to_file=True, file_log_format="", log_level="INFO")
    handlers = LOGGING_CONFIG["loggers"]["nightlight"]["handlers"]
    assert handlers.count("file") == 1
