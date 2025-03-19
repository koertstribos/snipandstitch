# This file is part of the 'snipandstitch' package.
#this file contains private and internal definitions for the SnipStitch class
#see Trial.py for public methods

import numpy as np
from scipy import stats
# setting values
INTERPOLATION_WIDTH = 100 #ms

EXTEND_EVENTS = 2 #ms
MEDIAN_WIDTH = 4 #samples

class SnipStitch():
    def __init__(self, trial, event):
        self._event = event
        self._trial = trial

        setupInfo = trial._setupInfo

        self.doInterpolateSlope = True
        self._dCorr = 0

        global INTERPOLATION_WIDTH, EXTEND_EVENTS, MEDIAN_WIDTH
        interpolationSamples = setupInfo.Indeces(INTERPOLATION_WIDTH)
        medianSamples = MEDIAN_WIDTH
        extendEvents = setupInfo.Indeces(EXTEND_EVENTS)

        self._startIndex = event.start - extendEvents
        self._endIndex = event.end + extendEvents

        #get dTot
        valuesBeforeEvent = [trial.RawPupsize(i) for i in range(self._startIndex - medianSamples, self._startIndex)]
        valuesAfterEvent = [trial.RawPupsize(i) for i in range(self._endIndex, self._endIndex + medianSamples)]
        self._dTot = np.median(valuesAfterEvent) - np.median(valuesBeforeEvent)

        #get dPup
        #get raw puptrace window
        puptrace = [trial.RawPupsize(i) for i in range(self._startIndex - interpolationSamples, self._startIndex)]
        #get slope in pupsize/sample
        slope, _, _, p, _ = stats.linregress(range(len(puptrace)), puptrace)
        #TODO: maybe implement this failsafe
        if p > 0.05 and False:
            self._dPup = 0
        else:
            self._dPup = slope * len(puptrace)

        self.SetInterpolation()

    def SetInterpolation(self):
        valueBefore = self._trial.CorrectedPupsize(index=self._startIndex)
        valueAfter = self._trial.CorrectedPupsize(index=self._endIndex)

        dValue = valueAfter - valueBefore

        self._interpolationLambda = lambda x: valueBefore + (dValue * (x - self._startIndex) / (self._endIndex - self._startIndex))

    def Correct(self, index, value):
        if index <= self._startIndex:
            return value
        elif index >= self._endIndex:
            return value - self.corrValue
        else:
            return self._interpolationLambda(index)

    @property
    def corrValue(self):

        dPup = [0, self._dPup][self.doInterpolateSlope]
        dCorr = self._dCorr

        return self._dTot - dPup - dCorr

    def SetCorrectionSettings(self, doInterpolateSlope = None, participantCorrectionValue = None):
        if doInterpolateSlope == None:
            doInterpolateSlope = self.doInterpolateSlope
        if participantCorrectionValue == None:
            participantCorrectionValue = self._dCorr

        self.doInterpolateSlope = doInterpolateSlope
        self._dCorr = participantCorrectionValue

        self.SetInterpolation()

    def __repr__(self):
        return f"SnipStitch. Adding {self.corrValue} ({self._dTot}+{self._dPup}+{self._dCorr}). "
    