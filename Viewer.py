# This file is part of the 'snipandstitch' package.
#this file contains the class Viewer
#the Viewer class can be used to visually inspect Snip and Stitch performance
from . import _Viewer

# Viewer class
# This class is used to view the corrected pupil size trace of a trial
#   initialisation
# viewer = Viewer(trials)
# trials: list of Trial objects
# 
# instantly pops up an interactive viewer object
class Viewer(_Viewer._V):
    def __init__(self, trials):
        super().__init__(trials)