# taAnalysis

## Introduction

`taAnalysis` is a simple, easy-to-use interface for Telescope Array (TA) data analysis. The program allows users to provide a YAML configuration file that guides the analysis process. The program reads data from a ROOT tree, creates an RDataFrame, fills columns, applies cuts, produces plots, and saves them. 

Users can perform more complex operations by using the C++ functions defined in the `library/` folder. The library is prepopulated with functions for common analysis tasks, but users can add more functions by writing them in the `custom_functions` module. The functions in the library are written in Python, but they return entire C++ functions as a string.

## Installation

To install `taAnalysis`, follow these steps:

1. Clone the repository:
    ```sh
    git clone https://github.com/ZGerber/taAnalysis.git
    cd taAnalysis
    ```

2. Install the required dependencies:
    ```sh
    pip install .
    ```

3. Ensure you have ROOT installed. You can download and install ROOT from [here](https://root.cern/install/).
4. For Telescope Array analysis, dstpy will also be required. You can get this from the dst2k-ta-pro software package.

## Usage

To run the program, use the following command:
```sh
python src/runMyAnalysis.py <path_to_yaml_config_file>
```

### Command-line Arguments

- `config_file`: Path to the YAML configuration file.
- `-r, --report`: Print the efficiency report after applying cuts.
- `-n, --no_save`: Do not save plots (plots are saved by default).
- `-d, --draw`: Display plots after completing analysis.
- `-p, --parallel`: Use parallel processing with Dask (not yet implemented).

## Configuration

The program is guided by YAML configuration files. Below is a description of the structure and fields of the YAML configuration files.

### Example Configuration File

```yaml
input_file: "/full/path/to/input_file"
tree_name: "tree_name"
output_dir: "/full/path/to/output_directory"
library_file: "/full/path/to/library_file"

# Do not change. This is the default value.
detector: null

# New columns to define
new_columns:
  - name: "EXAMPLE_COLUMN"
    expression: "example.dst.variable[{example_index}]"

  - name: "ANOTHER_EXAMPLE_COLUMN"
    expression: "another_example.dst.variable[{another_index}][0]"

# Event Selection Criteria
cuts:
  - "EXAMPLE_COLUMN > 500"
  - "ANOTHER_EXAMPLE_COLUMN < TMath::Pi()"
  - "YET_ANOTHER_EXAMPLE > 4/3"

# Histogram parameters
hist_params:
  # Create a histogram:
  - name: "histogramExample"
    title: "Example Histogram"
    style: "histogram"
    column: "EXAMPLE_COLUMN"
    bins: # Number of bins
    min: # min value
    max: # max value
    x_title: "X label with [units]"
    y_title: "Y label with [units]"
    show_stats: True
    options: ~

  # Create a profile plot:
  - name: "profileExample"
    title: "Profile Plot Title"
    style: "profile_plot"
    x_column: "EXAMPLE_COLUMN"
    y_column: "ANOTHER_EXAMPLE_COLUMN"
    x_bins: # Number of bins for x-axis
    y_bins: # Number of bins for y-axis
    x_min: # min x value
    x_max: # max x value
    x_bin_edges: # List of bin edges for x-axis. Overrides x_bins, x_min, and x_max.
      - 18.5
      - 18.75
      - 19.0
      - 19.25
      - 19.8
      - 20.3
    y_min:   # min y value
    y_max:   # max y value
    x_title: "X label with [units]"
    y_title: "Y label with [units]"
    show_stats: True
    options: ""

# For methods defined in the UserFunctions class:
user_functions:
  - name: "Example Function"
    callable: "name_of_method"
    args:
      - value: "EXAMPLE_COLUMN"
      - value: "ANOTHER_EXAMPLE_COLUMN"
```


## Details about `src/library/`

The `library/` directory contains various utility functions for generating C++ code related to ROOT RVec operations. 

ROOT currently supports vectorized operations on fundamental data types and RVec's thereof. However, data will often be deeply nested. 
Since RVec is only capable of 'hiding' the first layer, the remaining layers will be non-compatible data types such as `std::<vector<>>`.

To solve this, the user must loop over entries manually. Fortunately, most of these tasks can be accomplished with boilerplate code, reducing
or eliminating the user's need to know C++. Some of these predefined functions have been placed in `library/` and organized by the type of anlaysis
being conducted (TA-specific). More will be added as development continues.

An example is below: 

### `calculateMeanOfVectors`

Generates C++ code to calculate the mean of each vector in a vector of vectors.

```python
@staticmethod
def calculateMeanOfVectors(innerVec: str) -> str:
    return f"""
            std::vector<double> calculateMeanOfVectors(const ROOT::RVec<std::vector<double>> &{innerVec}) {{
                std::vector<double> mean;

                for (const auto &v : {innerVec}) {{
                    double mean_sum = 0;
                    unsigned int mean_count = v.size();

                    for (const auto &e : v) {{
                        mean_sum += e;
                    }}

                    if (mean_count > 0) {{
                        mean.push_back(mean_sum / mean_count);
                    }} else {{
                        mean.push_back(0);
                    }}
                }}

                return mean;
            }}
            """
```


## Author

Zane Gerber
