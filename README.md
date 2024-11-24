
# taAnalysis

This project is in development.

The goal is to provide a simple, easy-to-use interface for Telescope Array (TA) data analysis. 

Users can create tailored analyses with little to no prior knowledge of TA data structures, analysis tools, or even programming languages.

The program:
* Makes use of the ROOT analysis toolbox. The ROOT tree is converted to a data frame and manipulated in a modern way.
* Is controlled by a YAML configuration file. Users can design their analysis in a readable, plain-text format. 
* Is completely customizable and extensible via user-defined functions.

### Usage

A new analysis can be created by constructing a YAML file. This file provides instructions to the program and tells it how to interact with the dataframe, how to create histograms, which user functions to call, etc. 

A template and example are provided in config/.

The YAML file should be provided to the dataFrameAnalysis.py program. Run this from the command line:

```bash
python dataFrameAnalysis.py
```

The program will automatically perform the analysis based on the input file. It will create the desired plots and save them. They can also be drawn, if the user chooses. 

## Authors

- [Zane Gerber](https://www.github.com/ZGerber)

