import numpy as np
import argparse
from pathlib import Path


def parse_user_args():
    """Parse the command-line arguments"""
    parser = argparse.ArgumentParser(description="Convert ROOT file to NumPy arrays. Only selected columns are converted.")
    parser.add_argument("file_path",
                        type=str,
                        help="Path to the ROOT file")
    parser.add_argument("column_names",
                        type=str,
                        nargs="*",
                        help="Names of the columns to create, separated by spaces. Default is all columns.")
    parser.add_argument("--tree_name",
                        type=str,
                        default="taTree",
                        help="Name of the TTree in the ROOT file. Default is 'taTree'.")
    parser.add_argument("-o", "--output_dir",
                        type=str,
                        default=".",
                        help="Directory for output file(s). Default is ./")
    parser.add_argument("-x", "--omit_columns",
                        type=str,
                        nargs="*",
                        help="Names of the columns to omit, separated by spaces. Overrides --column_names.")
    parser.add_argument("--as_obj",
                        action="store_true",
                        help="Save the objects as they are instead of converting them to NumPy arrays.")
    return parser.parse_args()


def load_data(file_path, column_names, omit_columns=None, tree_name="taTree"):
    """Load the data from the ROOT file using RDataFrame"""
    import dstpy
    rdf = dstpy.ROOT.RDataFrame(tree_name, file_path)
    if column_names:
        return rdf.AsNumpy(column_names)
    elif omit_columns:
        return rdf.AsNumpy([str(col) for col in rdf.GetColumnNames() if col not in omit_columns])
    return rdf.AsNumpy()


def convert_objects_to_np(data):
    for key, value in data.items():
        if data[key].dtype.kind == 'O':
            for i, v in enumerate(value):
                data[key][i] = np.array(list(v))


def main():
    args = parse_user_args()
    data = load_data(args.file_path, args.column_names, args.omit_columns, args.tree_name)
    if not args.as_obj:
        convert_objects_to_np(data)
    np.savez(f"{Path(args.file_path).stem}.npz", **data)


if __name__ == "__main__":
    main()
