from typing import Dict, Any
import sys

import yaml

from src.rdf_analyzer.utils import logger


class ConfigManager:
    def __init__(self, args: Any):
        self.args              = args
        self.config            = self._load_config(self.args.config_file)
        self.detector_config   = self._load_config(self.config.get('detector_config'))

        self.set_detector_config()

        self.detector_id       = self._detector_id()
        self.profile_fit_index = self._profile_fit_index()

        self._replace_placeholders_in_yaml()
        self._validate_config()

    @staticmethod
    def _load_config(config_file: str) -> Dict[str, Any]:
        """
        Loads a YAML configuration file and returns its contents as a dictionary.

        :param config_file: Path to the YAML configuration file.
        :return: A dictionary representing the configuration from the YAML file.
        """
        with open(config_file, 'r') as file:
            try:
                return yaml.safe_load(file)
            except yaml.YAMLError as e:
                logger.critical(f"Error while loading the configuration file: {str(e)}")
                sys.exit(1)

    def _validate_config(self):
        """
        Validates the configuration dictionary by checking for required parameters.

        This method ensures that essential parameters like 'input_file', 'library_file',
        'tree_name', and 'detector' are present and not None.

        :param config: The configuration dictionary to validate.
        :raises ConfigError: If any required configuration parameter is missing or None.
        """
        required_config = {
            'input_file': self.config.get('input_file'),
            'library_file': self.config.get('library_file'),
            'tree_name': self.config.get('tree_name'),
            'detector_id': self.detector_id
        }
        for param, value in required_config.items():
            if value is None:
                raise ConfigError(f"{param}")

        logger.info("Configuration validated successfully! Beginning analysis...")

    def _replace_placeholders_in_yaml(self) -> None:
        """
        Replaces placeholders such as 'profile_fit_index' and 'detector_id_placeholder' in the YAML config
        directly with their actual values.

        This method assumes that the configuration is a dictionary that can contain strings, lists, and dictionaries.
        """

        # Define the replacements map (placeholders to actual values)
        replacements = {
            "profile_fit_index": str(self.profile_fit_index),
            "detector_id_placeholder": self.detector_id,
            "fd_clf_x": str(self.config.get('detector').get('clf_x')),
            "fd_clf_y": str(self.config.get('detector').get('clf_y'))
        }

        # Function to perform the replacement in a string
        def replace_string(value: str) -> str:
            for placeholder, replacement in replacements.items():
                if placeholder in value:
                    value = value.replace(placeholder, replacement)
            return value

        # Iterate over the entire configuration dictionary (this will also handle lists and nested dictionaries)
        def replace_in_dict(d: dict) -> None:
            for key, value in d.items():
                if isinstance(value, str):
                    # Replace placeholders in strings
                    d[key] = replace_string(value)
                elif isinstance(value, dict):
                    # Recursively replace in nested dictionaries
                    replace_in_dict(value)
                elif isinstance(value, list):
                    # Replace in list elements (if any are strings)
                    for i, item in enumerate(value):
                        if isinstance(item, str):
                            value[i] = replace_string(item)
                        elif isinstance(item, dict):
                            replace_in_dict(item)

        # Start replacing in the main config
        replace_in_dict(self.config)

    def _profile_fit_index(self) -> int:
        """
        Get the index of the profile fit parameter.

        :return: Index of the profile fit parameter.
        :raises: Exception if the profile index cannot be determined.
        """
        try:
            return self.config.get('profile_fit_index', 4)
        except Exception as e:
            logger.error(f"Error while getting profile fit index: {str(e)}")
        return 0

    def _detector_id(self) -> Dict[str, Any]:
        """
        Get the detector ID from the configuration.

        :return: Detector ID from the configuration.
        :raises: Exception if the detector ID cannot be determined.
        """
        try:
            return self.config['detector']['detector_id']
        except Exception as e:
            logger.error(f"Error while getting detector ID: {str(e)}")
        return self.config

    def set_detector_config(self) -> Dict[str, Any]:
        """
        Set the info from the detector config in the analysis configuration.

        :return: The updated analysis configuration dictionary with detector information.
        """
        try:
            self.config['detector'] = self.detector_config
            return self.config
        except Exception as e:
            logger.error(f"Error while getting detector configuration: {str(e)}")
        return self.config


class ConfigError(Exception):
    """Exception raised when a required configuration is missing."""

    def __init__(self, missing_parameter):
        self.missing_parameter = missing_parameter
        self._log_error()

    def _log_error(self):
        """
        Log the error when a missing configuration parameter is encountered.
        """
        logger.critical(f"Configuration error: '{self.missing_parameter}' cannot be None.")
        sys.exit(1)

    def __str__(self):
        """
        String representation of the error. When the exception is printed,
        this will be shown.
        """
        return f"Configuration error: '{self.missing_parameter}' cannot be None."