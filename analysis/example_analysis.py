# user_functions.py

import numpy as np
from typing import Optional, List, Union, Any, Dict
import logging
import awkward as ak
import dstpy as dst
from utils import logger


class UserFunctions:
    """
    User-defined functions to be used in the analysis.
    """

    def __init__(self):
        pass

    def say_hello(self):
        """
        Function to print hello.
        """
        logger.info("Hello!")

    # @dst.ROOT.Numba.Declare(['float', 'float'], 'float')
    def get_core_xxyy(self, hit_sds: np.ndarray, pulse_area: np.ndarray) -> List[
            Union[Dict[str, Union[str, Any]], Dict[str, Union[str, Any]]]]:
        try:
            logger.info("Calculating mean SD signals...")

            # Convert the numpy arrays to awkward arrays
            pulse_area = ak.from_iter(pulse_area)
            hit_sds = ak.from_iter(hit_sds)

            # Calculate the mean of the pulse area for each hit
            mean_pulses = ak.mean(pulse_area, axis=2)
            # Get the index of the hit with the maximum average signal between both layers
            max_vem_indices = ak.argmax(mean_pulses, axis=1)

            logger.info("Locating SD at shower core...")
            # Get the local indices of the hits for each event
            local_indices = ak.local_index(hit_sds, axis=1)

            logger.info("Success. Returning CLF positions of core SDs.")
            core_sds = ak.flatten(hit_sds[local_indices == max_vem_indices])
            sd_core_x = core_sds[:, 0]
            sd_core_y = core_sds[:, 1]
            logger.debug(f"SDCoreX: {sd_core_x}")
            logger.debug(f"SDCoreY: {sd_core_y}")
            return [{"name": "SDCoreX", "expression": ak.to_numpy(sd_core_x), "init": True},
                    {"name": "SDCoreY", "expression": ak.to_numpy(sd_core_y), "init": True}]

        except Exception as e:
            logger.error(f"Error in Get Core XXYY: {str(e)}")
            return []


if __name__ == "__main__":
    raise ImportError("This module should not be run directly. Import it as a module.")
