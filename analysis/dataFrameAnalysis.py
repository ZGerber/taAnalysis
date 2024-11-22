import dstpy as dst
import logging
from typing import List, Dict
import config
from example_analysis import *
import os

# Setting up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataFrameAnalyzer:
    def __init__(self, input_file: str, tree_name: str):
        """
        Initializes the DataFrameAnalyzer with the given ROOT file and tree.

        :param input_file: Path to the ROOT file.
        :param tree_name: Name of the ROOT tree.
        """
        self.input_file = input_file
        self.tree_name = tree_name
        self.df = self._load_dataframe()
        logger.info(f"DataFrame for tree {self.tree_name} loaded successfully.")

    def _load_dataframe(self) -> dst.ROOT.RDataFrame:
        """Load the ROOT TTree into a RDataFrame."""
        # file = ROOT.TFile(self.input_file)
        # tree = file.Get(self.tree_name)
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

    def define_new_column(self, name: str, expression: str) -> 'DataFrameAnalyzer':
        """
        Define a new column in the RDataFrame, selecting the appropriate index based on the detector.

        :param name: The name of the new column.
        :param expression: The expression to calculate the new column values.
        :return: Self for chaining.
        """
        # Detector ID logic based on the "stpln.eyeid" leaf
        # Assuming that only one element of the vector is non-zero
        # self.df = self.df.Define("detector_id",
        #                          "stpln.eyeid[0] > 0 ? 0 : (stpln.eyeid[1] > 0 ? 1 : (stpln.eyeid[2] > 0 ? 2 : ("
        #                          "stpln.eyeid[3] > 0 ? 3 : (stpln.eyeid[4] > 0 ? 4 : (stpln.eyeid[5] > 0 ? 5 : ("
        #                          "stpln.eyeid[6] > 0 ? 6 : 7)))))))")
        #
        # new_name = f"detector_{name}"
        new_name = name
        logger.info(f"Defining new column: {new_name} with expression: {expression}")

        self.df = self.df.Define(new_name, expression)
        self.df.Describe()
        # self.df = self.df.Define("test_column", "1")
        return self

    def create_histogram(self, column_name: str, bins: int, min_val: float, max_val: float) -> dst.ROOT.TH1F:
        """
        Create a histogram for a given column in the dataframe.

        :param column_name: The column name to use for histogram binning.
        :param bins: Number of histogram bins.
        :param min_val: Minimum value of the histogram range.
        :param max_val: Maximum value of the histogram range.
        :return: A ROOT histogram object.
        """
        logger.info(f"Creating histogram for column: {column_name}")
        histogram = self.df.Histo1D((column_name, column_name, bins, min_val, max_val), column_name)
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

    def save_histograms(self, histograms: List[dst.ROOT.TH1F], output_dir: str) -> None:
        """
        Save each histogram to a separate ROOT file in the specified directory.

        :param histograms: List of histograms to be saved.
        :param output_dir: Directory where individual ROOT files will be saved.
        """
        logger.info(f"Saving histograms to individual files in directory: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)
        for hist in histograms:
            # Create a unique file name for each histogram based on its name
            output_file = f"{output_dir}/{hist.GetName()}.root"
            self.save_histogram(hist, output_file)

    def run_analysis(self, selections: List[str], new_columns: List[Dict], hist_params: List[Dict]) -> List[dst.ROOT.TH1F]:
        """
        Run the full analysis: apply selections, define new columns, and create histograms.

        :param selections: List of selection strings.
        :param new_columns: List of dictionaries containing column names and expressions.
        :param hist_params: List of histogram parameter dictionaries.
        """
        # Define new columns (dynamically determined based on the detector)
        for col in new_columns:
            self.define_new_column(col['name'], col['expression'])

        # Apply selections
        for selection in selections:
            self.apply_selection(selection)

        # Create histograms
        histograms = []
        for hist in hist_params:
            histograms.append(self.create_histogram(hist['column'], hist['bins'], hist['min'], hist['max']))

        # Store histograms or plot them here
        logger.info("Analysis complete.")
        return histograms


# Function to show histograms in a canvas (if needed)
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
    input_file = config.INPUT_FILE  # Path to the ROOT file
    tree_name = config.TREE_NAME
    output_dir = config.OUTPUT_DIR
    example_analysis(input_file, tree_name, output_dir)



