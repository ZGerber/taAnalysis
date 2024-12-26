from rdf_analyzer.data_frame_analyzer import DataFrameAnalyzer
from rdf_analyzer.histogram_manager import HistogramManager
from rdf_analyzer.utils import logger, parse_arguments


def main():
    args = parse_arguments()

    client = None
    if args.parallel:
        logger.warning("Parallel processing with Dask is not supported in this version. Running in serial mode.")
        # from rdf_analyzer import setup_dask_client
        # client = setup_dask_client()

    analyzer = DataFrameAnalyzer(args, client)

    # Run the my_analysis and get the list of histograms
    my_histograms = analyzer.run_analysis()

    histogram_manager = HistogramManager(analyzer.df_handler.output_dir)
    # Save histograms, if needed
    if not args.no_save:
        histogram_manager.save_histograms(my_histograms)

    # Plot the histograms on a ROOT canvas
    if args.draw:
        histogram_manager.plot_histograms(my_histograms)


if __name__ == "__main__":
    main()
