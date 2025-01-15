
from typing import Any, List
import importlib.util
import sys
import os

import dstpy as dst

from src.rdf_analyzer.config_manager import ConfigManager
from src.rdf_analyzer.data_frame_manager import DataFrameManager
from src.rdf_analyzer.histogram_manager import HistogramManager
from src.rdf_analyzer.library_manager import LibraryFunctionHandler

from src.rdf_analyzer.utils import logger


class DataFrameAnalyzer:
    def __init__(self, args: Any, client: Any = None):
        self.args = args
        self.client = client

        # Initialize ConfigManager
        self.config_manager = ConfigManager(self.args)

        # Get the analysis + detector configuration
        self.config = self.config_manager.config

        # Initialize other components
        self.df_manager = DataFrameManager(self.config['tree_name'],
                                           self.config['input_file'],
                                           self.config['output_dir'],
                                           self.client,
                                           self.args.parallel)

        self.user_function_handler = LibraryFunctionHandler(self._load_analysis_library())
        self.histogram_manager = HistogramManager(self.df_manager.output_dir)

    def _load_analysis_library(self) -> Any:
        """
        Dynamically load and instantiate the class from the library_file.

        The analysis file is set in the YAML configuration. These files contain a library of predefined functions
        that can be used to define new columns, apply cuts, and perform other operations on the DataFrame.

        Any extra functions should be defined in custom_functions.py and specified in the YAML configuration.

        :return: Instance of the class found in the file.
        """
        # Extract the module name from the file path
        module_name = os.path.basename(self.config['library_file']).replace(".py", "")

        # Load the module dynamically using importlib
        spec = importlib.util.spec_from_file_location(str(module_name), self.config['library_file'])
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # Find the first class defined in the module (assuming only one class)
        classes = [cls for cls in module.__dict__.values() if isinstance(cls, type)]
        if len(classes) != 1:
            logger.critical(f"Expected a single class in {self.config['library_file']}, but found {len(classes)}.")
            sys.exit(1)

        # Instantiate the class and return it
        return classes[0]()

    def run_analysis(self) -> List[dst.ROOT.TH1F]:
        histograms = []

        # Define new columns:
        logger.info("Defining new columns...")
        for col in self.config.get('new_columns', []):
            self.df_manager.define_new_column(col)

        # Apply user functions to define custom columns:
        for user_function in self.config.get('user_functions', []):
            new_column_dict = self.user_function_handler.apply_library_function(user_function, self.df_manager.df)
            self.df_manager.define_new_column(new_column_dict)

        # Apply cuts:
        logger.info("Applying cuts...")
        for selection in self.config.get('cuts', []):
            self.df_manager.apply_selection(selection)

        # Create histograms:
        logger.info("Creating histograms...")
        for hist in self.config.get('hist_params', []):
            histograms.append(self.histogram_manager.create_histogram(hist, self.df_manager.df))

        return histograms
