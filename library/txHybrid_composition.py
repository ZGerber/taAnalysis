# txHybrid_composition.py


class TAx4HybridCompositionFunctions:
    """
    A class that contains various utility functions for generating C++ code
    related to ROOT RVec operations.
    """

    @staticmethod
    def findMaxInRVec(input_vector: str) -> str:
        """
        Generate C++ code to find the maximum value in a ROOT RVec.

        :param input_vector: Name of the input vector.
        :return: C++ code as a string.
        """
        return f"""
                double findMaxInRVec(const ROOT::RVec<double>& {input_vector}) {{
                    if ({input_vector}.empty()) {{
                        return std::numeric_limits<double>::lowest();
                    }}
                    double maxVal = {input_vector}[0];
                    for (const auto& v : {input_vector}) {{
                        if (v > maxVal) {{
                            maxVal = v;
                        }}
                    }}
                    return maxVal;
                }}
        """

    @staticmethod
    def findHotSDIndex(input_vector: str) -> str:
        """
        Generate C++ code to find the index of the maximum value in a ROOT RVec.

        :param input_vector: Name of the input vector.
        :return: C++ code as a string.
        """
        return f"""
                int findHotSDIndex(const ROOT::RVec<double>& {input_vector}) {{
                    if ({input_vector}.empty()) {{
                        return -1;
                    }}

                    auto maxIt = std::max_element({input_vector}.begin(), {input_vector}.end());
                    return std::distance({input_vector}.begin(), maxIt);  
                }}
        """

    @staticmethod
    def meanVectorVector(innerVec: str) -> str:
        """
        Generate C++ code to calculate the mean of each vector in a vector of vectors.

        :param innerVec: Name of the input vector of vectors.
        :return: C++ code as a string.
        """
        return f"""
                std::vector<double> meanVectorVector(const ROOT::RVec<std::vector<double>> &{innerVec}) {{
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
