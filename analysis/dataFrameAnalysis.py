from example_analysis import UserFunctions

import dstpy as dst
import logging
import os
import yaml
import numpy as np
from typing import List, Dict, Tuple, Any
from config.utils import logger, parse_arguments


class DataFrameAnalyzer:
    def __init__(self, config_file: str, args: Any):
        """
        Initializes the DataFrameAnalyzer with configurations from a YAML file.

        :param config_file: Path to the YAML configuration file.
        :param args: Parsed command-line arguments.
        """
        self.config = self._load_config(config_file)
        self.input_file = self.config.get('input_file', os.environ.get('ALL_HYBRID'))  # Default to environment variable
        self.tree_name = self.config.get('tree_name', 'taTree')
        self.detector = self.config.get('detector', 'None')
        self.df = self._load_dataframe()
        self.args = args
        logger.info(f"DataFrame for tree {self.tree_name} loaded successfully.")

    @staticmethod
    def _load_config(config_file: str) -> Dict:
        """
        Load the YAML configuration file.

        :param config_file: Path to the YAML configuration file.
        :return: Dictionary containing the configuration parameters.
        """
        with open(config_file, 'r') as file:
            return yaml.safe_load(file)

    @property
    def _profile_fit_index(self) -> int:
        """
        Get the index of the profile fit parameter.

        :return: Index of the profile fit parameter.
        """
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

    def apply_selection(self, selection: str, cutnum: int) -> 'DataFrameAnalyzer':
        """
        Apply event selection to the RDataFrame using ROOT's filter.

        :param selection: The filtering condition as a string.
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
        col = column_info

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
        :return: Created histogram.
        """
        hist = histogram_info

        if hist['style'] == 'histogram':
            logger.info(f"Creating histogram for column: {hist.get('column', 'N/A')}")
            # Create histogram using parameters from the YAML file
            histogram = self.df.Histo1D(
                (hist['name'], hist['title'], hist['bins'], hist['min'], hist['max']),
                hist['column'])
            histogram.SetXTitle(hist['x_title'])
            histogram.SetYTitle(hist['y_title'])
            if not hist['show_stats']:
                histogram.SetStats(0)
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
        selections  = self.config.get('cuts', [])
        new_columns = self.config.get('new_columns', [])
        hist_params = self.config.get('hist_params', [])

        # Define new columns
        for col in new_columns:
            self.define_new_column(col)

        # Prepare the user function arguments
        user_functions = self.config.get('user_functions', [])
        for user_function in user_functions:
            func_name  = user_function['name']
            new_column = user_function['new_column']
            func_call  = user_function['callable']
            func_args  = user_function.get('args', [])
            func_arg_list = [arg['value'] for arg in func_args]

            user_func_instance = UserFunctions(logger)

            # Dynamically call the function from UserFunctions class
            if hasattr(user_func_instance, func_call):
                func = getattr(user_func_instance, func_call)
                logger.info(f"Running user function {func_name} with arguments: {func_arg_list}")

                new_column_info = {'name': new_column,
                                   'expression': f"Numba::{func_call}({', '.join(func_arg_list)})"}

                self.define_new_column(new_column_info)
                logger.debug(f"Defined new column: {new_column} with data: {self.df.AsNumpy([new_column])[new_column]}")

        # Apply selections. Number them in case the user wants to generate a report.
        for i, selection in enumerate(selections, start=1):
            self.apply_selection(selection, i)

        # Create histograms
        histogram_list = []
        for hist in hist_params:
            histogram_list.append(self.create_histogram(hist))

        logger.info("ANALYSIS COMPLETE!")

        # Print the efficiency report after applying cuts
        if self.args.report:
            logger.info("Printing efficiency report...")
            self.df.Report().Print()
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


def main():
    args = parse_arguments()

    # Initialize the DataFrameAnalyzer with the configuration file
    analyzer = DataFrameAnalyzer(args.config_file, args)

    # Run the analysis and get the list of histograms
    my_histograms = analyzer.run_analysis()

    # Save the histograms to ROOT files
    # analyzer.save_histograms(my_histograms)

    # Plot the histograms on a ROOT canvas
    # plot_histograms(my_histograms)


if __name__ == "__main__":
    main()
