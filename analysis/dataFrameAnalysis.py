from example_analysis import UserFunctions

import colorlog
import dstpy as dst
import logging
import os
import yaml
import numpy as np
from typing import List, Dict, Tuple, Any


def setup_logger():
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


class DataFrameAnalyzer:
    def __init__(self, config_file: str):
        """
        Initializes the DataFrameAnalyzer with configurations from a YAML file.

        :param config_file: Path to the YAML configuration file.
        """
        self.config = self._load_config(config_file)
        self.input_file = self.config.get('input_file', os.environ.get('ALL_HYBRID'))  # Default to environment variable
        self.tree_name = self.config.get('tree_name', 'taTree')
        self.detector = self.config.get('detector', 'None')
        self.df = self._load_dataframe()
        logger.info(f"DataFrame for tree {self.tree_name} loaded successfully.")

    @staticmethod
    def _load_config(config_file: str) -> Dict:
        """Load the YAML configuration file."""
        with open(config_file, 'r') as file:
            return yaml.safe_load(file)

    @property
    def _profile_fit_index(self) -> int:
        """Get the index of the profile fit parameter."""
        try:
            det = self.detector
            detectors = self.config.get('detectors', {})
            for d in detectors:
                if d['name'] == self.detector:
                    return d.get('profile', 0)
        except Exception as e:
            logger.error(f"Error while getting profile fit index: {str(e)}")
            return 0


    def _replace_profile_fit_index_in_expression(self, expression: str) -> str:
        """Replace the placeholder in the expression with the actual profile_fit_index."""
        return expression.format(profile_fit_index=self._profile_fit_index)

    def _load_dataframe(self) -> dst.ROOT.RDataFrame:
        """Load the ROOT TTree into a RDataFrame."""
        return dst.ROOT.RDataFrame(self.tree_name, self.input_file)

    def prepare_data(self, columns: List[str]) -> Dict[str, np.ndarray]:
        """
        Prepare the data (columns) from the dataframe as numpy arrays.

        :param columns: List of column names to extract from the dataframe.
        :return: Dictionary of column names mapped to numpy arrays.
        """
        data = {}
        for column in columns:
            try:
                data[column] = self.df.AsNumpy([column])[column]
            except Exception as e:
                logger.error(f"Error while extracting column {column}: {str(e)}")
        return data

    def apply_selection(self, selection: str) -> 'DataFrameAnalyzer':
        """
        Apply event selection to the RDataFrame using ROOT's filter.

        :param selection: The filtering condition as a string.
        :return: Self for chaining.
        """
        logger.info(f"Applying selection: {selection}")
        self.df = self.df.Filter(selection)
        return self

    def define_new_column(self, column_info: Dict) -> 'DataFrameAnalyzer':
        """
        Define a new column in the RDataFrame.

        :param column_info: Dictionary containing column name and expression.
        :return: Self for chaining.
        """
        col = column_info
        if not col['init']:
            logger.info(f"Skipping column: {col.get('name', 'N/A')}. No initialization requested.")
            return self
        name = col['name']
        if isinstance(col['expression'], str):
            expression = self._replace_profile_fit_index_in_expression(col['expression'])
            self.df = self.df.Define(name, expression)
        else:
            expression = col['expression']
            self.df = self.df.Define(name, expression)

        logger.info(f"Defining new column: {name} with expression: {expression}")
        return self

    def create_histogram(self, histogram_info: Dict) -> dst.ROOT.TH1F:
        """
        Create a histogram for a given column in the dataframe.
        :param histogram_info: Dictionary containing histogram parameters.
        """
        hist = histogram_info

        if hist['style'] == 'histogram':
            logger.info(f"Creating histogram for column: {hist.get('column', 'N/A')}")
            # Create histogram using parameters from the YAML file
            histogram = self.df.Histo1D(
                (hist['name'], hist['title'], hist['bins'], hist['min'], hist['max']),
                hist['column']
            )
            histogram.SetXTitle(hist['x_title'])
            histogram.SetYTitle(hist['y_title'])
            if not hist['show_stats']:
                histogram.SetStats(0)
            if hist['y_range_user']:
                histogram.GetYaxis().SetRangeUser(hist['y_range_user'][0], hist['y_range_user'][1])
            return histogram.GetPtr()

        elif hist['style'] == 'profile_plot':
            logger.info(f"Creating profile plot for columns: {hist.get('y_column')} and {hist.get('x_column')}")

            # Plot can be defined by number of bins over some domain, or by custom bin edges:
            x_bin_edges = hist.get('x_bin_edges', [])
            if x_bin_edges:
                # Convert the bin edges to ROOT std::vector<double>
                x_bins = dst.ROOT.std.vector('double')()
                for edge in x_bin_edges:
                    x_bins.push_back(float(edge))

                # Create profile plot with bin edges
                histogram = self.df.Profile1D(
                    (hist['name'], hist['title'], len(x_bins) - 1, x_bins.data(), hist['options']),
                    hist['x_column'], hist['y_column']
                )
            else:
                # Create profile plot with 'x_bins', 'x_min', 'x_max' if no bin edges are provided
                histogram = self.df.Profile1D(
                    (hist['name'], hist['title'], hist['x_bins'], hist['x_min'], hist['x_max'], hist['options']),
                    hist['x_column'], hist['y_column']
                )

            histogram.SetXTitle(hist['x_title'])
            histogram.SetYTitle(hist['y_title'])
            if not hist['show_stats']:
                histogram.SetStats(0)
            # if hist['x_range_user']:
            #     logger.debug(f"Setting x-axis range: {hist['x_range_user']}")
            #     histogram.GetXaxis().SetRangeUser(int(hist['x_range_user'][0]), int(hist['x_range_user'][1]))
            # if hist['y_range_user']:
            #     logger.debug(f"Setting y-axis range: {hist['y_range_user']}")
            #     histogram.GetYaxis().SetRangeUser(int(hist['y_range_user'][0]), int(hist['y_range_user'][1]))
            return histogram.GetPtr()

    @staticmethod
    def save_histogram(histogram: dst.ROOT.TH1F, output_file: str) -> None:
        """
        Save an individual histogram to a ROOT file.

        :param histogram: The histogram to be saved.
        :param output_file: The name of the output ROOT file.
        """
        with dst.ROOT.TFile(output_file, "RECREATE") as root_file:
            histogram.Write()  # Write the histogram to the ROOT file
        logger.info(f"Saved histogram to {output_file}")

    def save_histograms(self, histograms: List[dst.ROOT.TH1F]) -> None:
        """
        Save each histogram to a separate ROOT file in the specified directory.

        :param histograms: List of histograms to be saved.
        :param output_dir: Directory where individual ROOT files will be saved.
        """
        output_dir = self.config.get('output_dir', './')
        logger.info(f"Saving histograms...")
        os.makedirs(output_dir, exist_ok=True)
        for hist in histograms:
            # Create a unique file name for each histogram based on its name
            output_file = f"{output_dir}/{hist.GetName()}.root"
            self.save_histogram(hist, output_file)

    def run_analysis(self) -> List[Any]:
        """
        Run the full analysis: apply selections, define new columns, and create histograms.

        :return: List of histograms generated from the analysis.
        """
        # Extract configuration details
        selections = self.config.get('cuts', [])
        new_columns = self.config.get('new_columns', [])
        hist_params = self.config.get('hist_params', [])

        # Define new columns
        for col in new_columns:
            self.define_new_column(col)

        # Prepare the user function arguments
        user_functions = self.config.get('user_functions', [])
        for user_function in user_functions:
            func_name = user_function['name']
            func_call = user_function['callable']
            func_args = user_function.get('args', [])

            # Prepare the data (columns) for user functions
            logger.info(f"Preparing data for user function: {func_name}")
            if func_args:
                column_data = self.prepare_data([arg['value'] for arg in func_args])
            else:
                column_data = {}

            user_func_instance = UserFunctions(logger)

            # Dynamically call the function from UserFunctions class
            if hasattr(user_func_instance, func_call):
                func = getattr(user_func_instance, func_call)
                logger.info(f"Running user function: {func_name} with arguments: {[arg['value'] for arg in func_args]}")

                # logger.debug(f"{[arg for arg in column_data if arg in column_data]}")
                # Pass the arguments as numpy arrays
                results = func(*[column_data[arg['value']] for arg in func_args if arg['value'] in column_data])

                logger.debug(f"{func_name} results: {results}")

                # for result in results:
                #     self.define_new_column(result)

        # Apply selections
        for selection in selections:
            self.apply_selection(selection)

        # Create histograms
        histogram_list = []
        for hist in hist_params:
            histogram_list.append(self.create_histogram(hist))

        logger.info("ANALYSIS COMPLETE!")
        return histogram_list


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
    logger = setup_logger()

    analysis_config = "/home/zane/software/new_analysis/txHybridDF/config/txhybrid_config.yaml"

    analyzer = DataFrameAnalyzer(analysis_config)

    my_histograms = analyzer.run_analysis()

    analyzer.save_histograms(my_histograms)

    # plot_histograms(my_histograms)
