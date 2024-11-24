# user_functions.py

import numpy as np
from typing import Optional, List, Union, Any
import logging
import awkward as ak


class UserFunctions:
    """
    User-defined functions to be used in the analysis.
    """
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def print_hello(self):
        """
        Function to print hello.
        """
        self.logger.info("Hello!")

    def get_hit_sd_index(self, pulse_area: np.ndarray) -> List[Optional[int]]:
        """
        Function to calculate the index of the hit with the maximum average signal.

        :param nhits: Numpy array of hit data (column from the dataframe)
        :param pulse_area: Numpy array of pulse area data (column from the dataframe)
        :return: Index of the hit with the maximum average signal
        """
        try:
            self.logger.info("Calculating mean SD signals...")

            # Convert the numpy arrays to awkward arrays
            pulse_area = ak.from_iter(pulse_area)

            # Calculate the mean of the pulse area for each hit
            mean_pulses = ak.mean(pulse_area, axis=2)

            # Get the index of the hit with the maximum average signal between both layers
            max_vem_indices = ak.argmax(mean_pulses, axis=1)

            self.logger.info("Successfully calculated mean SD signals. Returning indices of largest signals...")
            return max_vem_indices

        except Exception as e:
            self.logger.error(f"Error in Get Hit SD Index: {str(e)}")
            return []

