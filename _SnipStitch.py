# This file is part of the 'snipandstitch' package.
#this file contains private and internal definitions for the SnipStitch class
#see Trial.py for public methods

import numpy as np
from scipy import stats
# setting values
INTERPOLATION_WIDTH = 100 #ms
EXTEND_EVENTS = 2 #ms
MEDIAN_WIDTH = 4 #samples

#SnipStitch class
#this class contains variables and formulas for one snipandstitch correction (one corrected saccade)

#    Initialisation
#ss = SnipStitch(trial, event)
#trial: a Trial object
#event: an Event object
class SnipStitch():
    #__init__
    def __init__(self, trial, event):
        self._event = event
        self._trial = trial
        setupInfo = trial._setupInfo
        self.doInterpolateSlope = True
        self._dCorr = 0

        #get values defined above, and convert to indeces when required
        global INTERPOLATION_WIDTH, EXTEND_EVENTS, MEDIAN_WIDTH
        interpolationSamples = setupInfo.Indeces(INTERPOLATION_WIDTH)
        medianSamples = MEDIAN_WIDTH
        extendEvents = setupInfo.Indeces(EXTEND_EVENTS)

        #get start and end index
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
        #we could here only use the slope if p is below 0.05, but currently we assume that the slope is always a better estimate than 0
        self._dPup = slope * len(puptrace)

        #call SetInterpolation()
        self.SetInterpolation()

    #SetInterpolation
    #sets pupil values between saccade on- and offset using linear interpolation (digitally)
    def SetInterpolation(self):
        valueBefore = self._trial.CorrectedPupsize(index=self._startIndex)
        valueAfter = self._trial.CorrectedPupsize(index=self._endIndex)

        dValue = valueAfter - valueBefore

        self._interpolationLambda = lambda x: valueBefore + (dValue * (x - self._startIndex) / (self._endIndex - self._startIndex))

    #Correct
    #returns corrected pupil size value 
    #args:
    #index:    Index where pupil size is corrected
    #value:    Value before correction
    #returns:
    #float    Pupil value after correction
    def Correct(self, index, value):
        if index <= self._startIndex:
            return value
        elif index >= self._endIndex:
            return value - self.corrValue
        else:
            return self._interpolationLambda(index)

    #corrValue, the 'core value' that is subtracted from pupil size values after saccade offset
    @property
    def corrValue(self):

        dPup = [0, self._dPup][self.doInterpolateSlope]
        dCorr = self._dCorr

        return self._dTot - dPup - dCorr

    #SetCorrectionSettings
    #sets settings for correction. Whether intra-saccadic dPup is estimated, and the amount of buildup correction
    #args:
    #doInterpolateSlope: Bool or None. If not None, determines whether intra-saccadic dPup is estimated
    #participantCorrectionValue:    float, per-saccade buildup value. 0 or None for no buildup correction
    def SetCorrectionSettings(self, doInterpolateSlope = None, participantCorrectionValue = None):
        if doInterpolateSlope == None:
            doInterpolateSlope = self.doInterpolateSlope
        if participantCorrectionValue == None:
            participantCorrectionValue = self._dCorr

        self.doInterpolateSlope = doInterpolateSlope
        self._dCorr = participantCorrectionValue

        self.SetInterpolation()

    #text explanation of the snipandstitch. Logs corrValue property and its counterparts.
    def __repr__(self):
        return f"SnipStitch. Adding {self.corrValue} ({self._dTot}+{self._dPup}+{self._dCorr}). "
    
