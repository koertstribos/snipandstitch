# This file is part of the 'snipandstitch' package.
#this file contains protected and private definitions for the Viewer class
#see Viewer.py for usage of public methods

import tkinter as tk

#_V class
#for initialisation, see Viewer.py

class _V():
    def __init__(self, trials):
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

    #ChangeTrial
    #increment or decrement viewed trial, and view it
    #args:
    #    change: int, representing the increment amount (+1, or -1)
    #out:
    #    None
    def ChangeTrial(self, change):
        self._currentlyViewing += change
        self._currentlyViewing %= len(self._ts)
        self.ViewTrial()

    #PrintTrialInfo
    #prints info of the trial that is currently being viewed
    def PrintTrialInfo(self):
        print(self._ts[self._currentlyViewing]._SnipStitches.__repr__())

    #ViewTrial
    #view the trial that is currently selected
    #TODO(?): here, it could be unclear or illogical that the settings in a trial are changed for good. This could cause unwanted behaviour.
    def ViewTrial(self):
        trial = self._ts[self._currentlyViewing]
        trial._View(self)