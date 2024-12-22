from analysis.dataFrameAnalyzer import DataFrameAnalyzer, plot_histograms
from utils import logger, parse_arguments


def main():
    args = parse_arguments()

    client = None
    if args.parallel:
        logger.warning("Parallel processing with Dask is not supported in this version. Running in serial mode.")
        # from utils import setup_dask_client
        # client = setup_dask_client()

    analyzer = DataFrameAnalyzer(args.config_file, args, client)

    # Run the analysis and get the list of histograms
    my_histograms = analyzer.run_analysis()

    # Save histograms, if needed
    analyzer.save_histograms(my_histograms)

    # Plot the histograms on a ROOT canvas
    plot_histograms(my_histograms)


if __name__ == "__main__":
    main()
