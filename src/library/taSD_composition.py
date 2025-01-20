# taSD_composition.py


class TASDCompositionFunctions:
    """
    A class that contains various utility functions for generating C++ code
    related to ROOT RVec operations.
    """

    @staticmethod
    def extractLayers(input_vector: str, layer: str) -> str:
        """
        Generate C++ code to extract the fadc0 part from a 3D ROOT::RVec<std::vector<std::vector<int>>>
        (i.e., fadc[N][0][128]).

        :param FADC: Name of the input vector (assumed to be fadc).
        :return: C++ code as a string.
        """
        layer = int(layer)
        function_name = f"extractLayers_{input_vector}_{layer}"
        return f"""
                #ifndef {function_name}_H
                #define {function_name}_H
                
                ROOT::RVec<int> {function_name}(const ROOT::RVec<std::vector<std::vector<int>>>& {input_vector}, int layer) {{
                    ROOT::RVec<int> output_vector;

                    for (size_t i = 0; i < {input_vector}.size(); ++i) {{
                        for (size_t j = 0; j < 128; ++j) {{
                            output_vector.push_back({input_vector}[i][{layer}][j]);
                        }}
                    }}
                    return output_vector;
                }}
                
                #endif
        """

    # @staticmethod
    # def extractFADC1(FADC: str) -> str:
    #     """
    #     Generate C++ code to extract the fadc1 part from a 3D ROOT::RVec<std::vector<std::vector<int>>>
    #     (i.e., fadc[N][1][128]).
    #
    #     :param FADC: Name of the input vector (assumed to be fadc).
    #     :return: C++ code as a string.
    #     """
    #     return f"""
    #             ROOT::RVec<int> extractFADC1(const ROOT::RVec<std::vector<std::vector<int>>>& {FADC}) {{
    #                 ROOT::RVec<int> fadc1;
    #
    #                 for (size_t i = 0; i < {FADC}.size(); ++i) {{
    #                     for (size_t j = 0; j < 128; ++j) {{
    #                         fadc1.push_back({FADC}[i][1][j]);
    #                     }}
    #                 }}
    #                 return fadc1;
    #             }}
    #     """
