# This file is part of the 'snipandstitch' package.
#this file contains protected and private definitions for the Viewer class
#see Viewer.py for usage of public methods

import tkinter as tk

class _V():
    def __init__(self, trials):
        self._ts = trials
        self.setupInfo = trials._setupInfo

        self.root = tk.Tk()
        self.root.title("Viewer")

        self.extraViewingWidth = 0
        self.viewingResolution = 1

        self.correctingParticipantOffset = True
        self.interpolatingPupilSizeChange = True

        self._currentlyViewing = 0

        #add buttons for trial selection
        self.previousButton = tk.Button(self.root, text="Previous", command=lambda: self.ChangeTrial(-1))
        self.previousButton.pack(side=tk.LEFT)

        self.nextButton = tk.Button(self.root, text="Next", command=lambda: self.ChangeTrial(1))
        self.nextButton.pack(side=tk.LEFT)

        #add buttons for toggling correction settings
        self.togglePartCorrectButton = tk.Button(self.root, text="Toggle participant correction", command=lambda: self.Toggle('p'))
        self.togglePartCorrectButton.pack(side=tk.LEFT)

        self.toggleInterpolationButton = tk.Button(self.root, text="Toggle interpolation", command=lambda: self.Toggle('i'))
        self.toggleInterpolationButton.pack(side=tk.LEFT)

        #add button for viewing directly
        self.viewButton = tk.Button(self.root, text="View", command=self.ViewTrial)
        self.viewButton.pack(side=tk.LEFT)

        self.trialInfoButton = tk.Button(self.root, text="Trial info", command=self.PrintTrialInfo)


        self.root.mainloop()

    def ChangeTrial(self, change):
        self._currentlyViewing += change
        self._currentlyViewing %= self._ts.trialCount
        self.ViewTrial()

    def Toggle(self, value):
        if value == 'p':
            self.correctingParticipantOffset = not self.correctingParticipantOffset
            print(f"Participant correction is now {self.correctingParticipantOffset}")
        elif value == 'i':
            self.interpolatingPupilSizeChange = not self.interpolatingPupilSizeChange
            print(f"Interpolation is now {self.interpolatingPupilSizeChange}")
        else:
            raise ValueError(f"Value {value} not supported")
        
        self.ViewTrial()

    def PrintTrialInfo(self):
        print(self._ts[self._currentlyViewing]._SnipStitches.__repr__())

    def ViewTrial(self):
        self._ts._SetCorrectionSettings(self.interpolatingPupilSizeChange, self.correctingParticipantOffset)

        self._ts.View(self._currentlyViewing, self)
        


