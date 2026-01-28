"""This file is part of the 'snipandstitch' package.

This module contains protected and private definitions for the Viewer class.
See Viewer.py for usage of public methods.
"""

import tkinter as tk
from . import _Trial

class _V():
    """Internal Viewer class for interactive trial visualization.
    args: trials, list of Trial objects
    For initialization details, see Viewer.py.
    """
    def __init__(self, trials):
        """Initialize the Viewer with a list of trials.
        
        Args:
            trials: list of Trial objects to view
        """

        #pack to list if only one Trial is provided
        if isinstance(trials, _Trial._T):
            trials = [trials]

        #check if items in list are Trial objects
        try:
            for t in trials:
                if not isinstance (t, _Trial._T):
                    raise Exception(f"Viewer can only be initialised using a list of Trial objects, but received a list of {type(t)}")
        except:
            raise Exception(f"Viewer can only be initialised using a list of Trial objects, but received {trials}")

        self._ts = trials
        self.root = tk.Tk()
        self.root.title("Viewer")
        
        self.viewingResolution = 1
        self._currentlyViewing = 0

        #add buttons for trial selection
        self.previousButton = tk.Button(self.root, text="Previous", command=lambda: self.ChangeTrial(-1))
        self.previousButton.pack(side=tk.LEFT)

        self.nextButton = tk.Button(self.root, text="Next", command=lambda: self.ChangeTrial(1))
        self.nextButton.pack(side=tk.LEFT)

        #add button for viewing directly
        self.viewButton = tk.Button(self.root, text="View", command=self.ViewTrial)
        self.viewButton.pack(side=tk.LEFT)

        self.trialInfoButton = tk.Button(self.root, text="Trial info", command=self.PrintTrialInfo)

        self.root.mainloop()

    def ChangeTrial(self, change):
        """Increment or decrement viewed trial, and view it.
        
        Args:
            change: int, representing the increment amount (+1 or -1)
        """
        self._currentlyViewing += change
        self._currentlyViewing %= len(self._ts)
        self.ViewTrial()

    def PrintTrialInfo(self):
        """Print info of the trial that is currently being viewed."""
        print(self._ts[self._currentlyViewing]._SnipStitches.__repr__())

    #TODO(?): here, it could be unclear or illogical that the settings in a trial are changed for good. This could cause unwanted behaviour.
    def ViewTrial(self):
        """View the trial that is currently selected.
        
        Note: The settings in a trial are changed permanently. This could cause unwanted behaviour.
        """
        trial = self._ts[self._currentlyViewing]
        trial._View(self)
