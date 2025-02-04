import numpy as np
import argparse
from pathlib import Path


def parse_user_args():
    """Parse the command-line arguments."""
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
    """Load the data from the ROOT file using RDataFrame."""
    import dstpy
    rdf = dstpy.ROOT.RDataFrame(tree_name, file_path)
    if column_names:
        return rdf.AsNumpy(column_names)
    elif omit_columns:
        all_columns = list(rdf.GetColumnNames())
        selected_columns = [col for col in all_columns if col not in omit_columns]
        return rdf.AsNumpy(selected_columns)
    return rdf.AsNumpy()


def convert_objects_to_np(data):
    """Convert ROOT objects to NumPy-compatible types."""
    for key, value in data.items():
        if value.dtype.kind == 'O':  # Object or non-standard types
            # Convert ROOT objects like std::vector to NumPy arrays
            data[key] = np.array([np.array(list(v), dtype=np.float64) if hasattr(v, "__iter__") else v for v in value])


def main():
    args = parse_user_args()
    data = load_data(args.file_path, args.column_names, args.omit_columns, args.tree_name)
    if not args.as_obj:
        convert_objects_to_np(data)
    # Save data to .npz
    output_file = Path(args.output_dir) / f"{Path(args.file_path).stem}.npz"
    np.savez(output_file, **data)
    print(f"Data saved to {output_file}")


if __name__ == "__main__":
    main()
