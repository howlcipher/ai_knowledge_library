"""
Standardized System Logger Module.
"""

import logging


class SystemLogger:
    """
    Class to create and manage standardized loggers.
    """

    DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    @classmethod
    def setup_logger(
        cls, name: str, level: int = logging.DEBUG, console_level: int = logging.INFO
    ) -> logging.Logger:
        """
        Sets up and returns a configured logger instance.
        """
        logger = logging.getLogger(name)
        logger.setLevel(level)

        if not logger.handlers:
            ch = logging.StreamHandler()
            ch.setLevel(console_level)

            formatter = logging.Formatter(cls.DEFAULT_FORMAT)
            ch.setFormatter(formatter)

            logger.addHandler(ch)

        return logger


def setup_logger(name: str):
    """
    Legacy wrapper for setup_logger to ensure exactly the same functionality
    for scripts that import this function directly.
    """
    return SystemLogger.setup_logger(name)


def main():
    """Main entry point for testing the logger."""
    log = setup_logger("test")
    log.info("Standardized logging system initialized.")


if __name__ == "__main__":
    main()
