import ast
import os
from pathlib import Path as P
from pathlib import PurePath as PP
from peakutils import baseline

import matplotlib.pyplot as plt
import numpy as np

def subtract(data):
    """subtract. removes baseline from lineshape, assuming data has been phased

    :param data: signal
    """
    
    return data - baseline(data)
