from example_analysis import *

import dstpy as dst
import logging
import os
import yaml
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataFrameAnalyzer:
    def __init__(self, config_file: str):
        """
        Initializes the DataFrameAnalyzer with configurations from a YAML file.

        :param config_file: Path to the YAML configuration file.
        """
        self.config = self._load_config(config_file)
        self.input_file = self.config.get('input_file', os.environ.get('ALL_HYBRID'))  # Default to environment variable
        self.tree_name = self.config.get('tree_name', 'taTree')
        self.df = self._load_dataframe()
        logger.info(f"DataFrame for tree {self.tree_name} loaded successfully.")

    @staticmethod
    def _load_config(config_file: str) -> Dict:
        """Load the YAML configuration file."""
        with open(config_file, 'r') as file:
            return yaml.safe_load(file)

    def _load_dataframe(self) -> dst.ROOT.RDataFrame:
        """Load the ROOT TTree into a RDataFrame."""
        return dst.ROOT.RDataFrame(self.tree_name, self.input_file)

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
        name = col['name']
        expression = col['expression']
        logger.info(f"Defining new column: {name} with expression: {expression}")
        self.df = self.df.Define(name, expression)
        return self

    def create_histogram(self, histogram_info: Dict) -> dst.ROOT.TH1F:
        """
        Create a histogram for a given column in the dataframe.
        :param histogram_info: Dictionary containing histogram parameters.
        """
        hist = histogram_info
        logger.info(f"Creating histogram for column: {hist['column']}")
        histogram = self.df.Histo1D((hist['name'], hist['title'], hist['bins'], hist['min'], hist['max']),
                                    hist['column'])
        histogram.SetXTitle(hist['x_title'])
        histogram.SetYTitle(hist['y_title'])
        return histogram.GetPtr()

    @staticmethod
    def save_histogram(histogram: dst.ROOT.TH1F, output_file: str) -> None:
        """
        Save an individual histogram to a ROOT file.

        :param histogram: The histogram to be saved.
        :param output_file: The name of the output ROOT file.
        """
        logger.info(f"Saving histogram to {output_file}")
        with dst.ROOT.TFile(output_file, "RECREATE") as root_file:
            histogram.Write()  # Write the histogram to the ROOT file
        logger.info(f"Histogram saved successfully to {output_file}")

    def save_histograms(self, histograms: List[dst.ROOT.TH1F]) -> None:
        """
        Save each histogram to a separate ROOT file in the specified directory.

        :param histograms: List of histograms to be saved.
        :param output_dir: Directory where individual ROOT files will be saved.
        """
        output_dir = self.config.get('output_dir', './')
        logger.info(f"Saving histograms to individual files in directory: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)
        for hist in histograms:
            # Create a unique file name for each histogram based on its name
            output_file = f"{output_dir}/{hist.GetName()}.root"
            self.save_histogram(hist, output_file)

    def run_analysis(self) -> List[dst.ROOT.TH1F]:
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

        # Apply selections
        for selection in selections:
            self.apply_selection(selection)

        # Create histograms
        histograms = []
        for hist in hist_params:
            histograms.append(self.create_histogram(hist))

        logger.info("Analysis complete.")
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
    analysis_config = "/home/zane/software/new_analysis/txHybridDF/config/txhybrid_config.yaml"
    example_analysis(analysis_config)
