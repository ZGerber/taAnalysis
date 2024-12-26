import os
from typing import Dict, List

import dstpy as dst

from src.rdf_analyzer.utils import logger


class HistogramManager:
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir

    @staticmethod
    def create_histogram(hist: Dict, df: dst.ROOT.RDataFrame) -> dst.ROOT.TH1F:
        """
        Create a histogram or profile plot for a given column in the dataframe, depending on the 'style' specified.

        This method decides whether to create a simple histogram or a profile plot based on the 'style' key in the
        provided histogram dictionary.

        :param hist: A dictionary containing the histogram or profile plot configuration. Expected keys:
            - 'style': The type of plot to create, either 'histogram' or 'profile_plot'.
            - 'name', 'title', 'bins', 'min', 'max', 'column', etc., depending on the style.
        :param df: The RDataFrame from which the histogram will be created.
        :return: The created histogram (TH1F object), or None if creation fails or no matching style is found.
        """
        if hist['style'] == 'histogram':
            logger.info(f"Creating histogram for {hist['column']}")
            return HistogramManager._create_histogram(hist, df)
        elif hist['style'] == 'profile_plot':
            logger.info(f"Creating profile plot for {hist['x_column']} vs. {hist['y_column']}")
            return HistogramManager._create_profile_plot(hist, df)
        return None

    @staticmethod
    def _create_histogram(hist: Dict, df: dst.ROOT.RDataFrame) -> dst.ROOT.TH1F:
        """
        Create a simple 1D histogram for a specified column in the dataframe.

        This method uses the 'Histo1D' function to create a histogram based on the provided settings in the
        'hist' dictionary. It also sets additional drawing parameters after histogram creation.

        :param hist: A dictionary containing histogram configuration. Expected keys:
            - 'name', 'title', 'bins', 'min', 'max', 'column' (the data column for the histogram).
        :param df: The RDataFrame containing the column to be used for the histogram.
        :return: The created TH1F histogram, or None if an error occurs during creation.
        """
        try:
            histogram = df.Histo1D(
                (hist['name'], hist['title'], hist['bins'], hist['min'], hist['max']),
                hist['column']
            )
        except Exception as e:
            logger.warning(f"No column found for histogram. {str(e)}. No histogram created.")
            return None
        HistogramManager._set_histogram_parameters(hist, histogram)
        return histogram.GetPtr()

    @staticmethod
    def _create_profile_plot(hist: Dict, df: dst.ROOT.RDataFrame) -> dst.ROOT.TH1F:
        """
        Create a profile plot for the given x and y columns in the dataframe.

        This method uses the 'Profile1D' function to create a profile plot. It also handles cases where custom
        bin edges are provided for the x-axis.

        :param hist: A dictionary containing profile plot configuration. Expected keys:
            - 'name', 'title', 'x_bins', 'x_min', 'x_max', 'options', 'x_column', 'y_column', & optionally 'x_bin_edges'
        :param df: The RDataFrame containing the data for the profile plot.
        :return: The created TH1F profile plot, or None if an error occurs.
        """
        x_bin_edges = hist.get('x_bin_edges', [])
        if x_bin_edges:
            x_bin_edges_vec = HistogramManager._convert_to_std_vector(x_bin_edges)
            histo = df.Profile1D(
                (hist['name'], hist['title'], len(x_bin_edges) - 1, x_bin_edges_vec.data(),
                 hist['options']), hist['x_column'], hist['y_column'])
        else:
            histo = df.Profile1D(
                (hist['name'], hist['title'], hist['x_bins'], hist['x_min'], hist['x_max'], hist['options']),
                hist['x_column'], hist['y_column'])
        HistogramManager._set_histogram_parameters(hist, histo)
        return histo.GetPtr()

    @staticmethod
    def _convert_to_std_vector(x_bin_edges: List[float]) -> dst.ROOT.std.vector('double'):
        """
        Convert a list of x-bin edges to a ROOT std::vector of doubles.

        This helper function is used to convert a list of float values representing bin edges into a ROOT std::vector.

        :param x_bin_edges: A list of x-bin edges (floats) to be converted.
        :return: A ROOT std::vector containing the x-bin edges.
        """
        x_bin_edges.sort()
        x_bins = dst.ROOT.std.vector('double')()
        for edge in x_bin_edges:
            x_bins.push_back(float(edge))
        return x_bins

    @staticmethod
    def _set_histogram_parameters(hist: Dict, histogram: dst.ROOT.TH1F) -> None:
        """
        Set the drawing parameters for the created histogram.

        This method sets the X and Y axis titles and optionally disables the statistics box based on the
        configuration dictionary.

        :param hist: A dictionary containing settings for the histogram. Expected keys:
            - 'x_title': The title for the X-axis.
            - 'y_title': The title for the Y-axis.
            - 'show_stats': Boolean indicating whether to display the statistics box.
        :param histogram: The TH1F histogram whose parameters will be set.
        :return: None
        """
        histogram.SetXTitle(hist['x_title'])
        histogram.SetYTitle(hist['y_title'])
        if not hist['show_stats']:
            histogram.SetStats(0)

    @staticmethod
    def save_histogram(histogram: dst.ROOT.TH1F, output_file: str) -> None:
        """
        Save the given histogram to a ROOT file.

        This method saves the histogram as a `.root` file, which can be opened with ROOT or other compatible tools.

        :param histogram: The TH1F histogram to be saved.
        :param output_file: The path to the output ROOT file where the histogram will be saved.
        :return: None
        """
        with dst.ROOT.TFile(output_file, "RECREATE"):
            histogram.Write()
        logger.info(f"Saved histogram to {output_file}")

    def save_histograms(self, histograms: List[dst.ROOT.TH1F]) -> None:
        """
        Save each histogram to a separate ROOT file in the specified directory.

        :param histograms: List of histograms to be saved.
        """
        logger.info(f"Saving histograms...")
        os.makedirs(self.output_dir, exist_ok=True)
        for hist in histograms:
            if not hist:
                continue
            output_file = f"{self.output_dir}/{hist.GetName()}.root"
            self.save_histogram(hist, output_file)

    @staticmethod
    def plot_histograms(histograms: List[dst.ROOT.TH1F]) -> None:
        """
        Plot histograms on a ROOT canvas.

        :param histograms: List of histograms to be plotted.
        """
        logger.info("Plotting histograms...")
        canvas = dst.ROOT.TCanvas("canvas", "Analysis Results", 800, 600)
        for hist in histograms:
            if hist:
                hist.Draw()
                canvas.Update()
                input("Press Enter to continue...")