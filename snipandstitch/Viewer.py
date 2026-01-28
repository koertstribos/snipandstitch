"""This file is part of the 'snipandstitch' package.

This module contains the Viewer class which can be used to visually inspect Snip and Stitch performance.
"""
from . import _Viewer


class Viewer(_Viewer._V):
    """Viewer class for viewing the corrected pupil size trace of a trial.
    
    Instantly pops up an interactive viewer object showing trial data.
    
    Args:
        trials: list of Trial objects to visualize
    """
    def __init__(self, trials):
        super().__init__(trials)
