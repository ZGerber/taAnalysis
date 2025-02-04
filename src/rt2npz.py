import argparse
import uproot
import awkward as ak
from pathlib import Path


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert ROOT file to Parquet with column selection.")
    parser.add_argument("file_path", type=str, help="Path to the ROOT file")
    parser.add_argument("column_names", type=str, nargs="*",
                        help="Columns to convert (default: all)")
    parser.add_argument("--tree_name", type=str, default="taTree",
                        help="TTree name (default: 'taTree')")
    parser.add_argument("-o", "--output_dir", type=str, default=".",
                        help="Output directory (default: current)")
    parser.add_argument("-x", "--omit_columns", type=str, nargs="*",
                        help="Columns to exclude (overrides column_names)")
    return parser.parse_args()


def get_columns(tree, args):
    """Resolve column selection logic."""
    all_columns = tree.keys()

    if args.omit_columns:
        return [col for col in all_columns if col not in args.omit_columns]
    if args.column_names:
        return [col for col in args.column_names if col in all_columns]
    return all_columns


def save_parquet(data, input_path, output_dir):
    """Save converted data to Parquet format."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    stem = Path(input_path).stem
    output_path = output_dir / f"{stem}.parquet"

    ak.to_parquet(data, output_path)
    print(f"Saved converted data to: {output_path}")


def main():
    args = parse_args()

    # Load ROOT data
    with uproot.open(args.file_path) as file:
        tree = file[args.tree_name]
        columns = get_columns(tree, args)

        if not columns:
            raise ValueError("No valid columns selected for conversion")

        data = tree.arrays(columns)

    # Convert and save
    save_parquet(data, args.file_path, args.output_dir)


if __name__ == "__main__":
    main()
