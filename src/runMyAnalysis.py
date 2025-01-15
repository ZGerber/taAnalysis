from src.rdf_analyzer.data_frame_analyzer import DataFrameAnalyzer
from src.rdf_analyzer.utils import logger, parse_arguments


def main():
    args = parse_arguments()

    client = None
    if args.parallel:
        logger.warning("Parallel processing with Dask is not supported in this version. Running in serial mode.")
        # from rdf_analyzer import setup_dask_client
        # client = setup_dask_client()

    my_analysis = DataFrameAnalyzer(args, client)

    # Run the my_analysis and get the list of histograms
    my_histograms = my_analysis.run_analysis()

    # Save histograms, unless the user specifies not to
    if not args.no_save:
        my_analysis.histogram_manager.save_histograms(my_histograms)

    # Plot the histograms on a ROOT canvas
    if args.draw:
        my_analysis.histogram_manager.plot_histograms(my_histograms)

    # Print the efficiency report
    if args.report:
        my_analysis.df_manager.df.Report().Print()

    # Save the DataFrame of good events
    my_analysis.df_manager.save_df(my_analysis.df_manager.output_dir)


if __name__ == "__main__":
    main()
