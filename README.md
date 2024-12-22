# taAnalysis

This project is in development.

The goal is to provide a simple, easy-to-use interface for Telescope Array (TA) data analysis.

Users can create tailored analyses with little to no prior knowledge of TA data structures, analysis tools, or even programming languages.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Requirements](#requirements)
- [Usage](#usage)
- [Configuration](#configuration)
- [User-Defined Functions](#user-defined-functions)
- [Authors](#authors)

## Introduction

This project aims to simplify the process of analyzing data from the Telescope Array (TA) experiment. It provides a user-friendly interface that allows users to perform complex data analyses with minimal effort.

## Features

- Easy-to-use interface for TA data analysis
- Configurable through YAML files
- Supports custom user functions
- Generates histograms and profile plots
- Applies event selection criteria
- Saves results to ROOT files

## Installation

To install the project, clone the repository and install the required dependencies:

```bash
git clone https://github.com/ZGerber/taAnalysis.git
cd taAnalysis
```

See [Requirements](#requirements) for dependencies.

## Requirements

It is assumed that your data is in the form of a ROOT file.

- Python 3.8+
- ROOT
- dstpy
- PyYAML
- colorlog 

## Usage

To run the analysis, execute the main script with the path to the configuration file:

```bash
python analysis/dataFrameAnalyzer.py /path/to/config.yaml
```

### Detailed Usage Example

Here is a detailed example of how to use the analysis tool:

1. **Prepare the Configuration File**: Create a YAML configuration file with the necessary parameters. For example:

```yaml
input_file: "/path/to/your/input_file.root"
tree_name: "yourTreeName"
output_dir: "/path/to/output_directory"

detector: "yourDetector"
detectors:
  - name: "yourDetector"
    site_id: 1
    profile: 1

new_columns:
  - name: "NewColumn"
    expression: "some_expression"

cuts:
  - "NewColumn > 100"

hist_params:
  - name: "histNewColumn"
    title: "New Column Histogram"
    style: "histogram"
    column: "NewColumn"
    bins: 50
    min: 0
    max: 200
    x_title: "New Column"
    y_title: "Frequency"
    show_stats: True
    options: ~
```

2. **Run the Analysis**: Execute the main script with the path to your configuration file:

```bash
python analysis/dataFrameAnalyzer.py /path/to/your/config.yaml
```

3. **View the Results**: The results, including histograms and any other output, will be saved in the specified output directory.

### Command-Line Options

The script supports the following command-line options:

- `config_file`: Path to the YAML configuration file.
- `-h` or `--help`: Display the help message.
- `-r` or `--report`: Print the efficiency report after applying cuts.

To display the help message, run:

```bash
python analysis/dataFrameAnalyzer.py -h
```

## Configuration

The analysis is configured through a YAML file. Below is an example configuration:

```yaml
input_file: ${ALL_HYBRID}
tree_name: "taTree"
output_dir: "/home/zane/software/new_analysis/txHybridDF/results"

detector: "mdtax4"
detectors:
  - name: "mdtax4"
    site_id: 7
    profile: 6
  - name: "brtax4"
    site_id: 8
    profile: 7

new_columns:
  - name: "Xmax"
    expression: "prfc.xm[{profile_fit_index}]"

cuts:
  - "Xmax > Xlow"
  - "Xmax < Xhigh"
  - "LogEnergy >= 18.5"

hist_params:
  - name: "hXmax"
    title: "X_{max}"
    style: "histogram"
    column: "Xmax"
    bins: 20
    min: 300
    max: 1400
    x_title: "X_{max} [g/cm^{2}]"
    y_title: "Events"
    show_stats: True
    options: ~
```

### Configuration Options

The configuration file allows users to specify various parameters for the analysis. Below are detailed explanations of the configuration options:

- **input_file**: Path to the input ROOT file containing the data.
- **tree_name**: Name of the ROOT TTree to be analyzed.
- **output_dir**: Directory to save the output results.
- **detector**: Name of the detector to be used in the analysis.
- **detectors**: List of detectors with their respective site IDs and profile fit indices.
- **new_columns**: List of new columns to define in the dataframe.
- **cuts**: List of event selection criteria.
- **hist_params**: List of histogram parameters.

### New Columns

The `new_columns` section in the YAML configuration file allows users to define new columns in the dataframe. Each entry in this section specifies a new column to be created, including its name and the expression used to calculate its values.

#### Example

```yaml
new_columns:
  - name: "NewColumn1"
    expression: "column1 + column2"
  - name: "NewColumn2"
    expression: "column3 * 2"
```

#### Fields

- **name**: The name of the new column to be created.
- **expression**: The expression used to calculate the values of the new column. This can be a mathematical operation or a function applied to existing columns.

By defining new columns in this section, users can extend the dataframe with additional calculated data, which can then be used in further analysis or visualizations.

### Event Selection Criteria

The `cuts` section in the YAML configuration file allows users to specify event selection criteria. Each entry in this section is a condition that must be met for an event to be included in the analysis.

#### Example

```yaml
cuts:
  - "NewColumn1 > 100"
  - "NewColumn2 < 50"
```

### Histogram Parameters

The `hist_params` section in the YAML configuration file allows users to specify parameters for creating histograms. Each entry in this section defines a histogram to be created, including its name, title, style, column to be plotted, number of bins, range, axis titles, additional options, and whether to show the statistics box.

#### Example

```yaml
hist_params:
  - name: "histNewColumn1"
    title: "New Column 1 Histogram"
    style: "histogram"
    column: "NewColumn1"
    bins: 50
    min: 0
    max: 200
    x_title: "New Column 1"
    y_title: "Frequency"
    show_stats: True
    options: ~
```

#### Fields

- **name**: The name of the histogram.
- **title**: The title of the histogram.
- **style**: The style of the plot (e.g., "histogram" or "profile_plot").
- **column**: The column to be plotted.
- **bins**: The number of bins in the histogram.
- **min**: The minimum value of the histogram.
- **max**: The maximum value of the histogram.
- **x_title**: The title of the x-axis.
- **y_title**: The title of the y-axis.
- **show_stats**: A boolean value indicating whether to show the statistics box on the plot.
- **options**: Additional options for the histogram.

## User-Defined Functions

Users can create their own functions using the `UserFunctions` class. These functions are used to perform complex calculations on dataframe columns and return data that will be used to fill new columns.

### Creating a User Function

1. **Define the Function**: Add your function to the `UserFunctions` class in the `example_analysis.py` file. The function should take the necessary columns as input and return a dictionary with new column names and their corresponding data.

```python
class UserFunctions:
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def say_hello(self):
        self.logger.info("Hello!")

    def my_custom_function(self, column1: np.ndarray, column2: np.ndarray) -> Dict[str, np.ndarray]:
        self.logger.info("Running custom function...")
        # Perform calculations
        result = column1 + column2
        return {"NewColumn": result}
```

### Update the Configuration

Add the function to the `user_functions` section in the YAML configuration file. Specify the function name, callable, and the columns it requires.

```yaml
user_functions:
  - name: "My Custom Function"
    callable: "my_custom_function"
    args:
      - name: "column1"
        value: "ExistingColumn1"
      - name: "column2"
        value: "ExistingColumn2"
```

### Run the Analysis

The `DataFrameAnalyzer` will automatically call the user-defined function during the analysis process, and the new columns will be added to the dataframe.

By following these steps, users can extend the functionality of the analysis by adding custom calculations tailored to their specific needs.

## Authors

- [Zane Gerber](https://www.github.com/ZGerber)
