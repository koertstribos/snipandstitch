# This file is part of the 'snipandstitch' package.
#this file contains private and internal definitions for the SnipStitch class
#a snipstitch instance defines one saccade correction
#see Trial.py for public methods

import numpy as np
from scipy import stats
# setting values
INTERPOLATION_WIDTH = 100 #ms
EXTEND_EVENTS = 1 #sample
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
        self._dCorr = 0

        #copy global variables if required
        global INTERPOLATION_WIDTH, EXTEND_EVENTS, MEDIAN_WIDTH

        medianSamples = MEDIAN_WIDTH
        extendEvents = EXTEND_EVENTS

        #get start and end index
        self._startIndex = event.start - extendEvents
        self._endIndex = event.end + extendEvents

        #get dTot
        valuesBeforeEvent = [trial.RawPupsize(i) for i in range(self._startIndex - medianSamples, self._startIndex)]
        valuesAfterEvent = [trial.RawPupsize(i) for i in range(self._endIndex, self._endIndex + medianSamples)]
        self._dTot = np.median(valuesAfterEvent) - np.median(valuesBeforeEvent)

        #set dPup interpolation (if the method exists)
        self.Interpolate_dPup(trial)

        #set interpolation
        self.SetInterpolation()

    #SetInterpolation
    #sets pupil values between saccade on- and offset using linear interpolation (digitally)
    def SetInterpolation(self):
        #get dVal
        correctedValueBefore = self._trial.CorrectedPupsize(index=self._startIndex)
        dValue = self._trial.RawPupsize(self._endIndex) - self._trial.RawPupsize(self._startIndex) - self.corrValue

        #set lambda that takes time in trial
        #          relative time in saccade -> pupPre              + (corrected pupil size change over saccade) * (relative time in saccade)
        self._interpolationLambda = lambda x: correctedValueBefore + (dValue * (x - self._startIndex) / (self._endIndex - self._startIndex))

    #Interpolate_dPup
    #in this object, only set doInterpolateSlope to False
    def Interpolate_dPup(self, trial):
        self.doInterpolateSlope = False

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
        dCorr = self._dCorr

        return self._dTot - dCorr

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

        #if the user requested doInterpolateSlope, raise exception, as no sampling rate is known
        #yet, here we still check whether sRate is given, so that we don't need to overwrite this function in subclass
        if doInterpolateSlope and self._trial._samplingRate is None:
            raise ValueError("Cannot set doInterpolateSlope to True, as no sampling rate is known. Set samplingRate in Trial Object initialisation.")

        self.doInterpolateSlope = doInterpolateSlope
        self._dCorr = participantCorrectionValue

        self.SetInterpolation()

    #text explanation of the snipandstitch. Logs corrValue property and its counterparts.
    def __repr__(self):
        return f"SnipStitch. Adding {self.corrValue} ({self._dTot}+{self._dCorr}). "
    

class SnipStitchSRate(SnipStitch):
    def __init__(self, trial, event):
        super().__init__(trial, event)

    def Interpolate_dPup(self, trial):
        self.doInterpolateSlope = True
        interpolationSamples = int(trial._samplingRate * INTERPOLATION_WIDTH / 1000) #convert ms to samples
        #check if interpolationSamples is at least 1
        if interpolationSamples is not None and interpolationSamples < 1:
            interpolationSamples = 1
            print(f"Warning: INTERPOLATION_WIDTH ({INTERPOLATION_WIDTH}ms) is too small for sample rate {trial._samplingRate}Hz. Using 1 sample instead.")

        #get dPup
        #get raw puptrace window
        puptrace = [trial.RawPupsize(i) for i in range(self._startIndex - interpolationSamples, self._startIndex)]
        #get slope in pupsize/sample
        slope, _, _, p, _ = stats.linregress(range(len(puptrace)), puptrace)
        #we could here only use the slope if p is below 0.05, but currently we assume that the slope is always a better estimate than 0
        self._dPup = slope * len(puptrace)

    #corrValue, the 'core value' that is subtracted from pupil size values after saccade offset
    @property
    def corrValue(self):

        dPup = self._dPup if self.doInterpolateSlope else 0
        dCorr = self._dCorr

        return self._dTot - dPup - dCorr
    
    #text explanation of the snipandstitch. Logs corrValue property and its counterparts.
    def __repr__(self):
        return f"SnipStitch. Adding {self.corrValue} ({self._dTot}+{self._dPup}+{self._dCorr}). "
