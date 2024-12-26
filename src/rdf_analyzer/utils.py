import argparse
import logging

import colorlog


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
    detectors = ["mdtax4fd", "mdtax4sd", "brtax4fd", "brtax4sd", "mdfd", "talefd", "tasd", "brm", "lr"]
    parser = argparse.ArgumentParser(description="Run the DataFrame analysis with a specified YAML configuration file.")
    parser.add_argument("config_file",
                        type=str,
                        help="Path to the YAML configuration file.")
    # parser.add_argument("detector", type=str, choices=detectors, help="Choose detector.")
    parser.add_argument("-r", "--report",
                        action="store_true",
                        help="Print the efficiency report after applying cuts.")
    parser.add_argument("-n", "--no_save",
                        action="store_true",
                        help="Plots will not be saved. (Plots are saved by default.)")
    parser.add_argument("-d", "--draw",
                        action="store_true",
                        help="Display plots after completing analysis.")
    parser.add_argument("-p", "--parallel",
                        action="store_true",
                        help="Use parallel processing with Dask [not yet implemented].")
    return parser.parse_args()


def setup_dask_client(n_workers: int = 4, threads_per_worker: int = 1, memory_limit: str = '2GB',
                      local_directory: str = '/tmp'):
    """
    Set up a Dask client and cluster for parallel processing.

    :param n_workers: Number of Dask workers.
    :param threads_per_worker: Number of threads per Dask worker.
    :param memory_limit: Memory limit per worker.
    :param local_directory: Directory for local Dask worker files.
    :return: Dask Client object.
    """
    logger.info("Using parallel processing with Dask")
    from dask.distributed import Client, LocalCluster

    # Set up the Dask LocalCluster
    cluster = LocalCluster(
        n_workers=n_workers,
        threads_per_worker=threads_per_worker,
        memory_limit=memory_limit,
        local_directory=local_directory
    )
    client = Client(cluster)
    logger.info(f"Dask client configured: {client}")

    return client

