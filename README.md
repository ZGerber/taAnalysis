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
git clone https://github.com/yourusername/yourproject.git
cd yourproject
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
python analysis/dataFrameAnalysis.py /path/to/config.yaml
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
    init: True

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
    options: ~
```

### New Columns

The `new_columns` section in the YAML configuration file allows users to define new columns in the dataframe. Each entry in this section specifies a new column to be created, including its name, the expression used to calculate its values, and whether it should be initialized.

#### Example

```yaml
new_columns:
  - name: "NewColumn1"
    expression: "column1 + column2"
    init: True
  - name: "NewColumn2"
    expression: "column3 * 2"
    init: False
```

#### Fields

- **name**: The name of the new column to be created.
- **expression**: The expression used to calculate the values of the new column. This can be a mathematical operation or a function applied to existing columns.
- **init**: A boolean value indicating whether the column should be initialized. If `True`, the column will be created during the analysis process. Otherwise it will be created via user-defined functions.

By defining new columns in this section, users can extend the dataframe with additional calculated data, which can then be used in further analysis or visualizations.
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
