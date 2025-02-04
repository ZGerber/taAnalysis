# txHybrid_composition.py


class TAx4HybridComposition:
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
    def findMaxIndex(input_vector: str) -> str:
        """
        Generate C++ code to find the index of the maximum value in a ROOT RVec.

        :param input_vector: Name of the input vector.
        :return: C++ code as a string.
        """
        return f"""
                int findMaxIndex(const ROOT::RVec<double>& {input_vector}) {{
                    if ({input_vector}.empty()) {{
                        return -1;
                    }}

                    auto maxIt = std::max_element({input_vector}.begin(), {input_vector}.end());
                    return std::distance({input_vector}.begin(), maxIt);  
                }}
        """

    @staticmethod
    def calculateMeanOfVectors(innerVec: str) -> str:
        """
        Generate C++ code to calculate the mean of each vector in a vector of vectors.

        :param innerVec: Name of the input vector of vectors.
        :return: C++ code as a string.
        """
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

    @staticmethod
    def coreProximity(HybridCoreX: str, HybridCoreY: str, HotSD_CLF_X: str, HotSD_CLF_Y: str) -> str:
        """
        Generate a complete C++ function that calculates the distance between two points using
        the TMath::Sqrt and TMath::Power functions.

        :param HybridCoreX: Name of the variable holding the X coordinate of HybridCore.
        :param HybridCoreY: Name of the variable holding the Y coordinate of HybridCore.
        :param HotSD_CLF_X: Name of the variable holding the X coordinate of HotSD_CLF.
        :param HotSD_CLF_Y: Name of the variable holding the Y coordinate of HotSD_CLF.
        :return: C++ code for the function as a string.
        """
        return f"""
                double coreProximity(double {HybridCoreX}, double {HybridCoreY}, 
                                         double {HotSD_CLF_X}, double {HotSD_CLF_Y}) {{
                    return TMath::Sqrt(
                        TMath::Power({HybridCoreX} - {HotSD_CLF_X}, 2) + 
                        TMath::Power({HybridCoreY} - {HotSD_CLF_Y}, 2)
                    ) / 1000.;
                }}
                """

    @staticmethod
    def getFD_CLF(det_name: str) -> str:
        """
        Generate a complete C++ function that calls the get_fd_xyz_clf method of TLUTI_DETECTORS
        and fills the fd_xyz_clf array based on the det_name string.

        :param det_name: The string representing the detector name (det).
        :return: C++ code for the function as a string.
        """
        return f"""
                void getFD_CLF(const std::string &{det_name}) {{
                    double fd_xyz_clf[3];
                    return TLUTI_DETECTORS::get_fd_xyz_clf({det_name}, fd_xyz_clf);
                }}
                """

    @staticmethod
    def addConstant_to_RVec(input_vector: str, constant: str) -> str:
        return f"""
                void addConstant_to_RVec(double {input_vector}, const double {constant}) {{
                    return {input_vector} + {constant};
                }}
                """
