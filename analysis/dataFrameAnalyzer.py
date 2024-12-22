from library import *
import dstpy as dst
import os
import sys
import yaml
import numpy as np
from typing import List, Dict, Any
from utils import logger, ConfigError
import importlib.util


class DataFrameAnalyzer:
    def __init__(self, config_file: str, args: Any, client: Any = None):
        """
        Initializes the DataFrameAnalyzer with configurations from a YAML file.

        :param config_file: Path to the YAML configuration file.
        :param args: Parsed command-line arguments.
        :param client: Dask client for parallel processing (optional).
        """
        self.args = args
        self.client = client
        self.config = self._load_config(config_file)

        # Load attributes from the config
        self.input_file = self.config.get('input_file')
        self.analysis_file = self.config.get('analysis_file')
        self.tree_name = self.config.get('tree_name')
        self.detector = self.config.get('detector')

        # Validate the configuration
        self._validate_config()

        # Initialize the ROOT DataFrame
        self.df = self._load_dataframe()
        logger.info(f"DataFrame for tree {self.tree_name} loaded successfully.")

        # Load and instantiate the class from the analysis_file (Python file)
        self.user_class_instance = self._load_analysis_class()

    @staticmethod
    def _load_config(config_file: str) -> Dict:
        """
        Load the YAML configuration file.

        :param config_file: Path to the YAML configuration file.
        :return: Dictionary containing the configuration parameters.
        """
        with open(config_file, 'r') as file:
            return yaml.safe_load(file)

    def _validate_config(self):
        """
        Validate the required configuration parameters. Raises an error if any are missing.

        :raises ConfigError: If a required configuration parameter is missing.
        """
        # Required attributes that must not be None
        required_config = {
            'input_file': self.input_file,
            'analysis_file': self.analysis_file,
            'tree_name': self.tree_name,
            'detector': self.detector
        }

        for param, value in required_config.items():
            if value is None:
                raise ConfigError(f"Configuration error: '{param}' cannot be None.")

    def _load_analysis_class(self) -> Any:
        """
        Dynamically load and instantiate the class from the analysis_file.

        :param analysis_file: Path to the Python file containing the class.
        :return: Instance of the class found in the file.
        """
        # Extract the module name from the file path
        module_name = os.path.basename(self.analysis_file).replace(".py", "")

        # Load the module dynamically using importlib
        spec = importlib.util.spec_from_file_location(module_name, self.analysis_file)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # Find the first class defined in the module (assuming only one class)
        classes = [cls for cls in module.__dict__.values() if isinstance(cls, type)]
        if len(classes) != 1:
            logger.error(f"Expected a single class in {self.analysis_file}, but found {len(classes)} classes.")
            sys.exit(1)

        # Instantiate the class and return it
        return classes[0]()

    @property
    def _profile_fit_index(self) -> int:
        """
        Get the index of the profile fit parameter.

        :return: Index of the profile fit parameter.
        :raises: Exception if the profile index cannot be determined.
        """
        try:
            detectors = self.config.get('detectors', {})
            for d in detectors:
                if d['name'] == self.detector:
                    return d.get('profile', 0)
        except Exception as e:
            logger.error(f"Error while getting profile fit index: {str(e)}")
        return 0

    def _replace_profile_fit_index_in_expression(self, expression: str) -> str:
        """
        Replace the placeholder in the expression with the actual profile_fit_index.

        :param expression: Expression containing the placeholder.
        :return: Expression with the placeholder replaced by the actual profile_fit_index.
        """
        return expression.format(profile_fit_index=self._profile_fit_index)

    def _load_dataframe(self) -> dst.ROOT.RDataFrame:
        """
        Load the ROOT TTree into a RDataFrame.

        :return: RDataFrame containing the data from the ROOT TTree.
        """
        if self.args.parallel:
            # dataFrame = dst.ROOT.RDF.Experimental.Distributed.Dask.RDataFrame
            # return dataFrame(self.tree_name, self.input_file, daskclient=self.client)
            return dst.ROOT.RDataFrame(self.tree_name, self.input_file)
        else:
            return dst.ROOT.RDataFrame(self.tree_name, self.input_file)

    def prepare_data(self, columns: List[str]) -> Dict[str, np.ndarray]:
        """
        Prepare the data (columns) from the dataframe as numpy arrays.

        :param columns: List of column names to extract from the dataframe.
        :return: Dictionary of column names mapped to numpy arrays.
        """
        return {column: self._extract_column(column) for column in columns}

    def _extract_column(self, column: str) -> np.ndarray:
        """
        Extract column data from the DataFrame and handle errors.

        :param column: The column name to extract.
        :return: Numpy array of the column data, or an empty array if an error occurs.
        """
        try:
            return self.df.AsNumpy([column])[column]
        except Exception as e:
            logger.error(f"Error while extracting column {column}: {str(e)}")
            return np.array([])

    def apply_selection(self, selection: str, cutnum: int) -> 'DataFrameAnalyzer':
        """
        Apply event selection to the RDataFrame using ROOT's filter.

        :param selection: The filtering condition as a string.
        :param cutnum: Cut number used to label the selection.
        :return: Self for chaining.
        """
        logger.info(f"Applying selection: {selection}")
        self.df = self.df.Filter(selection, f"Cut_{cutnum}")
        return self

    def define_new_column(self, column_info: Dict) -> 'DataFrameAnalyzer':
        """
        Define a new column in the RDataFrame.

        :param column_info: Dictionary containing column name and expression.
        :return: Self for chaining.
        """
        expression = self._replace_profile_fit_index_in_expression(column_info['expression']) if isinstance(
            column_info['expression'], str) else column_info['expression']
        self.df = self.df.Define(column_info['name'], expression)
        logger.info(f"Defining new column: {column_info['name']} with expression: {expression}")
        return self

    def create_histogram(self, histogram_info: Dict) -> dst.ROOT.TH1F:
        """
        Create a histogram for a given column in the dataframe.

        :param histogram_info: Dictionary containing histogram parameters.
        :return: Created histogram.
        """
        if histogram_info['style'] == 'histogram':
            return self._create_histogram(histogram_info)
        elif histogram_info['style'] == 'profile_plot':
            return self._create_profile_plot(histogram_info)
        return None

    def _create_histogram(self, hist: Dict) -> dst.ROOT.TH1F:
        """
        Create a simple histogram.

        :param hist: Dictionary containing histogram parameters.
        :return: Created histogram.
        """
        logger.info(f"Creating histogram for column: {hist.get('column', 'N/A')}")
        histogram = self.df.Histo1D(
            (hist['name'], hist['title'], hist['bins'], hist['min'], hist['max']),
            hist['column']
        )
        self._set_histogram_parameters(hist, histogram)
        return histogram.GetPtr()

    def _create_profile_plot(self, hist: Dict) -> dst.ROOT.TH1F:
        """
        Create a profile plot.

        :param hist: Dictionary containing profile plot parameters.
        :return: Created profile plot.
        """
        logger.info(f"Creating profile plot for columns: {hist.get('y_column')} and {hist.get('x_column')}")

        x_bin_edges = hist.get('x_bin_edges', [])

        if x_bin_edges:
            x_bin_edges_vec = self._convert_to_std_vector(x_bin_edges)
            histo = self.df.Profile1D(
                (hist['name'], hist['title'], len(x_bin_edges) - 1, x_bin_edges_vec.data(),
                 hist['options']), hist['x_column'], hist['y_column'])
        else:
            histo = self.df.Profile1D(
                (hist['name'], hist['title'], hist['x_bins'], hist['x_min'], hist['x_max'], hist['options']),
                hist['x_column'], hist['y_column'])
        self._set_histogram_parameters(hist, histo)
        return histo.GetPtr()

    @staticmethod
    def _convert_to_std_vector(x_bin_edges: List[float]) -> dst.ROOT.std.vector('double'):
        """
        Convert x_bin_edges to a ROOT std::vector<double>.

        :param x_bin_edges: List of x bin edges.
        :return: ROOT std::vector of type double containing the bin edges.
        """
        x_bin_edges.sort()
        x_bins = dst.ROOT.std.vector('double')()
        for edge in x_bin_edges:
            x_bins.push_back(float(edge))
        return x_bins

    @staticmethod
    def _set_histogram_parameters(hist: Dict, histogram: dst.ROOT.TH1F) -> None:
        """
        Set the parameters for drawing histograms.

        :param hist: Dictionary containing axis title information.
        :param histogram: Histogram to set titles on.
        """
        histogram.SetXTitle(hist['x_title'])
        histogram.SetYTitle(hist['y_title'])
        if not hist['show_stats']:
            histogram.SetStats(0)

    @staticmethod
    def save_histogram(histogram: dst.ROOT.TH1F, output_file: str) -> None:
        """
        Save an individual histogram to a ROOT file.

        :param histogram: The histogram to be saved.
        :param output_file: The name of the output ROOT file.
        """
        with dst.ROOT.TFile(output_file, "RECREATE"):
            histogram.Write()
        logger.info(f"Saved histogram to {output_file}")

    def save_histograms(self, histograms: List[dst.ROOT.TH1F]) -> None:
        """
        Save each histogram to a separate ROOT file in the specified directory.

        :param histograms: List of histograms to be saved.
        """
        output_dir = self.config.get('output_dir', './')
        logger.info(f"Saving histograms...")
        os.makedirs(output_dir, exist_ok=True)
        for hist in histograms:
            output_file = f"{output_dir}/{hist.GetName()}.root"
            self.save_histogram(hist, output_file)

    def _apply_user_function(self, user_function: Dict) -> None:
        """
        Apply a user-defined function to the DataFrame to create a new column.

        :param user_function: Dictionary containing user function information.
        """
        language = user_function['language']
        new_column = user_function['new_column']
        func_call = user_function['callable']
        func_args = user_function.get('args', [])
        func_arg_list = [arg['value'] for arg in func_args]
        func_arg_csv = ', '.join(func_arg_list)

        self.user_class_instance = self._load_analysis_class()

        if not func_call and language in ['ROOT', 'RDF', 'direct', 'None', None]:
            new_column_info = {'name': new_column, 'expression': f"{func_arg_list[0]}[{func_arg_list[1]}]"}

        elif hasattr(self.user_class_instance, func_call):
            func = getattr(self.user_class_instance, func_call)
            logger.info(f"Running user function {func_call} with arguments: {func_arg_list}")

            if language in ['C++', 'cpp', 'c++', 'cxx']:
                dst.ROOT.gInterpreter.Declare(func(*func_arg_list))
                new_column_info = {'name': new_column, 'expression': f"{func_call}({func_arg_csv})"}

            elif language in ['python', 'Python', 'py']:
                new_column_info = {'name': new_column, 'expression': f"Numba::{func_call}({func_arg_csv})"}

            else:
                logger.warning(f"Unsupported language: {language}. Column {new_column} not filled.")
                new_column_info = None
        else:
            logger.warning(f"User function {func_call} not found. Column {new_column} not filled.")
            new_column_info = None

        if new_column_info:
            self.define_new_column(new_column_info)

    def run_analysis(self) -> List[Any]:
        """
        Run the full analysis: apply selections, define new columns, and create histograms.

        :return: List of histograms generated from the analysis.
        """
        histograms = []

        # Define new columns
        for col in self.config.get('new_columns', []):
            self.define_new_column(col)

        # Apply user functions
        for user_function in self.config.get('user_functions', []):
            self._apply_user_function(user_function)

        # Apply cuts
        for i, selection in enumerate(self.config.get('cuts', []), start=1):
            self.apply_selection(selection, i)

        # Create histograms
        for hist in self.config.get('hist_params', []):
            histograms.append(self.create_histogram(hist))

        logger.info("ANALYSIS COMPLETE!")

        if self.args.report:
            logger.info("Printing efficiency report...")
            self.df.Report().Print()

        return histograms


def plot_histograms(histograms: List[dst.ROOT.TH1F]) -> None:
    """
    Plot histograms on a ROOT canvas.

    :param histograms: List of histograms to be plotted.
    """
    canvas = dst.ROOT.TCanvas("canvas", "Analysis Results", 800, 600)
    for hist in histograms:
        hist.Draw()
        canvas.Update()
        input("Press Enter to continue...")


if __name__ == "__main__":
    logger.error("This module should not be run directly. Import it as a module.")
    sys.exit(1)
