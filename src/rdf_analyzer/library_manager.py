from typing import Dict, Any

import dstpy as dst

from src.rdf_analyzer.utils import logger


class LibraryFunctionHandler:
    def __init__(self, user_class_instance: Any):
        self.user_class_instance = user_class_instance

    def apply_library_function(self, user_function: Dict, df: dst.ROOT.RDataFrame) -> Dict[str, Any]:
        """
        Apply a user-defined function to the DataFrame to create a new column.
        """
        new_column = user_function['new_column']
        func_call = user_function['callable']
        func_args = user_function.get('args', [])
        func_arg_list = [arg['value'] for arg in func_args]

        if not func_call:
            logger.info(f"No function call found for {new_column}. Trying default methods...")
            if len(func_arg_list) == 1:
                try:
                    new_column_info = {'name': new_column, 'expression': f"{func_arg_list[0]}"}
                except Exception as e:
                    logger.warning(f"Error while defining new column {new_column}: {str(e)}")
                    new_column_info = None
            elif len(func_arg_list) == 2:
                try:
                    new_column_info = {'name': new_column, 'expression': f"{func_arg_list[0]}[{func_arg_list[1]}]"}
                except Exception as e:
                    logger.warning(f"Error while defining new column {new_column}: {str(e)}")
                    new_column_info = None
            else:
                logger.warning(f"No matching function call. Too many parameters. Column {new_column} not filled.")
                new_column_info = None


        elif hasattr(self.user_class_instance, func_call):
            func = getattr(self.user_class_instance, func_call)
            dst.ROOT.gInterpreter.Declare(func(*func_arg_list))
            new_column_info = {'name': new_column, 'expression': f"{func_call}({', '.join(func_arg_list)})"}

        else:
            logger.warning(f"User function {func_call} not found. Column {new_column} not filled.")
            new_column_info = None

        return new_column_info
