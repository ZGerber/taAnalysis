import argparse
import awkward as ak
import numpy as np
import pyarrow.parquet as pq
import re


def parse_args():
    parser = argparse.ArgumentParser(
        description="Process physics data in Parquet format with multiple transformation options"
    )
    parser.add_argument("input_file", help="Input Parquet file")
    parser.add_argument("-o", "--output", default="processed_data.parquet",
                        help="Output file name (default: processed_data.parquet)")
    parser.add_argument("--filter", type=str,
                        help="Filter expression (e.g., 'Energy > 50 & NHits > 3')")
    parser.add_argument("--add-features", nargs="+",
                        help="New features to add from jagged columns (e.g., 'MIP0:mean,max')")
    parser.add_argument("--truncate", nargs="+", type=lambda x: x.split(":"),
                        help="Truncate/pad jagged columns (e.g., 'MIP0:100' for max 100 elements)")
    parser.add_argument("--scale", nargs="+", type=lambda x: x.split(":"),
                        help="Scale numeric columns (e.g., 'Energy:zscore' or 'Xmax:minmax')")
    parser.add_argument("--rename", nargs="+", type=lambda x: x.split(":"),
                        help="Rename columns (e.g., 'Energy_mc:true_energy')")
    parser.add_argument("--format", choices=["parquet", "npz", "hdf5"], default="parquet",
                        help="Output format (default: parquet)")
    return parser.parse_args()


def process_data(data, args):
    """Apply all requested transformations to the data"""

    # 1. Filter events
    if args.filter:
        mask = eval(args.filter, {"ak": ak}, data)
        data = data[mask]

    # 2. Process jagged arrays
    if args.truncate:
        for col_spec in args.truncate:
            col, max_len = col_spec
            padded = ak.pad_none(data[col], int(max_len), clip=True)
            data[col] = ak.fill_none(padded, 0)

    # 3. Add derived features
    if args.add_features:
        for feature_spec in args.add_features:
            col, ops = feature_spec.split(":")
            jagged = data[col]
            for op in ops.split(","):
                if op == "mean":
                    data[f"{col}_mean"] = ak.mean(jagged, axis=1)
                elif op == "max":
                    data[f"{col}_max"] = ak.max(jagged, axis=1)
                elif op == "sum":
                    data[f"{col}_sum"] = ak.sum(jagged, axis=1)
                elif op == "count":
                    data[f"{col}_count"] = ak.num(jagged, axis=1)

    # 4. Scale numeric columns
    if args.scale:
        for col, method in args.scale:
            values = ak.to_numpy(data[col])
            if method == "zscore":
                mean, std = np.mean(values), np.std(values)
                data[col] = (values - mean) / std
            elif method == "minmax":
                _min, _max = np.min(values), np.max(values)
                data[col] = (values - _min) / (_max - _min)

    # 5. Rename columns
    if args.rename:
        for old_name, new_name in args.rename:
            data[new_name] = data[old_name]
            del data[old_name]

    return data


def save_data(data, args):
    """Save processed data in requested format"""
    if args.format == "parquet":
        ak.to_parquet(data, args.output)
    elif args.format == "npz":
        np.savez(args.output, **{k: ak.to_numpy(v) for k, v in data.items()})
    elif args.format == "hdf5":
        ak.to_hdf5(data, args.output)
    print(f"Saved processed data to {args.output}")


def main():
    args = parse_args()

    # Load data with memory mapping for large files
    data = ak.from_parquet(args.input_file)

    # Process data
    processed_data = process_data(data, args)

    # Save results
    save_data(processed_data, args)


if __name__ == "__main__":
    main()
