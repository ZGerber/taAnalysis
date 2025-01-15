import numpy as np
import argparse
import dstpy
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
    return parser.parse_args()


def load_data(file_path, column_names, tree_name="taTree"):
    """Load the data from the ROOT file using RDataFrame"""
    rdf = dstpy.ROOT.RDataFrame(tree_name, file_path)
    if column_names:
        return rdf.AsNumpy(column_names)
    return rdf.AsNumpy()


def main():
    args = parse_user_args()
    data = load_data(args.file_path, args.column_names)
    np.savez(f"{Path(args.file_path).stem}.npz", **data)


if __name__ == "__main__":
    main()
