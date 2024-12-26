from typing import List, Dict, Any

import dstpy as dst
import numpy as np

from rdf_analyzer.utils import logger


class DataFrameManager:
    def __init__(self, tree_name: str, input_file: str, output_dir: str, client: Any = None, parallel: bool = False):
        """
        Initializes the DataFrameHandler with the given ROOT TTree and input file.

        :param tree_name: Name of the ROOT TTree to be loaded into a DataFrame.
        :param input_file: Path to the ROOT file containing the TTree.
        :param output_dir: Path to the directory where output files will be saved.
        :param client: Dask client for parallel processing (optional).
        :param parallel: Whether to enable parallel processing (default is False).
        """
        self.tree_name = tree_name
        self.input_file = input_file
        self.output_dir = output_dir
        self.client = client
        self.parallel = parallel
        self.df = self._load_dataframe()

    def _load_dataframe(self) -> dst.ROOT.RDataFrame:
        """
        Loads the ROOT TTree into a RDataFrame.

        If parallel processing is enabled, the DataFrame will be loaded with Dask support; otherwise,
        it will be loaded in a single-threaded mode.

        :return: The RDataFrame loaded from the specified TTree and input file.
        """
        if self.parallel:
            return dst.ROOT.RDataFrame(self.tree_name, self.input_file)
        return dst.ROOT.RDataFrame(self.tree_name, self.input_file)

    def column_to_numpy(self, columns: List[str]) -> Dict[str, np.ndarray]:
        """
        Prepares the data (columns) from the DataFrame as NumPy arrays.

        This method extracts the specified columns from the DataFrame and returns them as a dictionary
        with column names as keys and their respective data as NumPy arrays.

        :param columns: List of column names to extract from the DataFrame.
        :return: A dictionary where keys are column names and values are the corresponding NumPy arrays.
        """
        return {column: self._extract_column(column) for column in columns}

    def _extract_column(self, column: str) -> np.ndarray:
        """
        Extracts column data from the DataFrame and handles any errors during extraction.

        If an error occurs while extracting a column, an empty NumPy array is returned and the error is logged.

        :param column: The name of the column to extract from the DataFrame.
        :return: A NumPy array containing the column's data, or an empty array if an error occurs.
        """
        try:
            return self.df.AsNumpy([column])[column]
        except Exception as e:
            logger.error(f"Error while extracting column {column}: {str(e)}")
            return np.array([])

    def define_new_column(self, column_info: Dict) -> 'DataFrameManager':
        """
        Define a new column in the RDataFrame.

        :param column_info: Dictionary containing column name and expression.
        :return: Self for chaining.
        """
        expression = column_info['expression'] \
            if isinstance(column_info['expression'], str) \
            else column_info['expression']
        self.df = self.df.Define(column_info['name'], expression)
        logger.info(f"Defined new column {column_info['name']} with expression: {expression}")
        # self.df.Display([f"{column_info['name']}"]).Print()
        return self

    def apply_selection(self, selection: str, cut_num: int) -> 'DataFrameManager':
        """
        Applies event selection to the RDataFrame using ROOT's filter.

        The specified selection condition is applied to the DataFrame, and the rows are filtered based on
        the condition. A cut number is also assigned to label the selection in the filtering process.

        :param selection: The filtering condition as a string expression.
        :param cut_num: The cut number used to label the selection.
        :return: The DataFrameHandler instance, enabling method chaining.
        """
        logger.info(f"Applying selection: {selection}")
        self.df = self.df.Filter(selection, f"Cut_{cut_num}")
        return self
