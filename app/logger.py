import logging
import logging.config

logger = logging.getLogger('nightlight')

VALID_LOG_LEVELS = [
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL"
]

file_json = '''{
    "timestamp": "%(asctime)s",
    "level": "%(levelname)s",
    "file": "%(filename)s",
    "function": "%(funcName)s",
    "message": "%(message)s",
}'''

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(levelname)s - %(message)s",
            "datefmt": "%d-%m-%Y %H:%M:%S"
        },
        "file": {
            "format": "%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s",
            "datefmt": "%d-%m-%Y %H:%M:%S"
        },
        "file_json": {
            "format": file_json,
            "datefmt": "%d-%m-%Y %H:%M:%S"
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "default"
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "nightlight.log",
            "formatter": "file",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 3
        },
        "file_json": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "nightlight.log",
            "formatter": "file_json",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 3
        },
    },
    "loggers": {
        "nightlight": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}


def create_logger(log_to_file: bool, file_log_format: str,
                  log_level: str) -> logging.Logger:
    """Creates a logger with an optional file handler."""
    global logger

    if log_level not in VALID_LOG_LEVELS:
        logger.CRITICAL(
            f"The configured log level {log_level} is not valid! The logger will use 'info' now")
        log_level = "INFO"

    if log_to_file:
        file_handler = "file_json" if file_log_format == "json" else "file"
        LOGGING_CONFIG["loggers"]["nightlight"]["handlers"].append(
            file_handler)

    # Apply the logging configuration
    logging.config.dictConfig(LOGGING_CONFIG)

    # Set up logger for the app
    logger = logging.getLogger('nightlight')
    return logger
