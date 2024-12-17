import colorlog
import logging
import argparse

def setup_logger():
    """
    Set up the logger with color formatting.

    :return: Configured logger instance.
    """
    # Create a logger
    logger = logging.getLogger(__name__)

    # Set the logging level (e.g., DEBUG, INFO)
    logger.setLevel(logging.DEBUG)

    # Create a handler for printing log messages to the console
    handler = logging.StreamHandler()

    # Create a formatter with colors
    formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(levelname)-8s%(reset)s %(white)s%(message)s',
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }
    )

    # Set the formatter for the handler
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)

    return logger

logger = setup_logger()

def parse_arguments():
    """
    Parse command-line arguments for the script.

    :return: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Run the DataFrame analysis with a specified YAML configuration file.")
    parser.add_argument("config_file", type=str, help="Path to the YAML configuration file.")
    parser.add_argument("-r", "--report", action="store_true", help="Print the efficiency report after applying cuts.")
    return parser.parse_args()
