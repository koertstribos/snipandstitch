"""private and internal definitions for the SnipStitch class, part of the 'snipandstitch' package.
a snipstitch instance defines one saccade correction"""
import numpy as np
from scipy import stats
# setting values
INTERPOLATION_WIDTH = 100.0 #ms
EXTEND_EVENTS = 1 #sample
MEDIAN_WIDTH = 4 #samples

import matplotlib.pyplot as plt

#SnipStitch class
#this class contains variables and formulas for one snipandstitch correction (one corrected saccade)

#    Initialisation
#ss = SnipStitch(trial, event)
#trial: a Trial object
#event: an Event object
class SnipStitch():
    def __init__(self, trial, event):
        """Initialize SnipStitch object.
        
        Args:
            trial: a Trial object
            event: an Event object
        """
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

    def SetInterpolation(self):
        """Set pupil values between saccade on- and offset using linear interpolation."""
        #get dVal
        correctedValueBefore = self._trial.CorrectedPupsize(index=self._startIndex)
        dValue = self._trial.RawPupsize(self._endIndex) - self._trial.RawPupsize(self._startIndex) - self.corrValue

        #set lambda that takes time in trial
        #          relative time in saccade -> pupPre              + (corrected pupil size change over saccade) * (relative time in saccade)
        self._interpolationLambda = lambda x: correctedValueBefore + (dValue * (x - self._startIndex) / (self._endIndex - self._startIndex))

    def Interpolate_dPup(self, trial):
        """Set doInterpolateSlope to False in this object. (overwritten by SnipStitchSRate objects)"""
        self.doInterpolateSlope = False

    def Correct(self, index, value):
        """Return corrected pupil size value.
        
        Args:
            index: Index where pupil size is corrected
            value: Value before correction
        
        Returns:
            float: Pupil value after correction
        """
        
        #if index before correction, return uncorrected value
        if index <= self._startIndex:
            return value
        
        #if index after saccade end, correct value by subtracting dCorr
        elif index >= self._endIndex:
            return value - self.corrValue
        
        #if index between saccade onset and saccade end, correct value by returning value at saccade start
        else:
            return self._trial.CorrectedPupsize(index=self._startIndex)

    @property
    def corrValue(self):
        """Return the core value that is subtracted from pupil size values after saccade offset."""
        dCorr = self._dCorr

        return self._dTot - dCorr

    def SetCorrectionSettings(self, doInterpolateSlope = None, participantCorrectionValue = None):
        """Set settings for correction.
        
        Args:
            doInterpolateSlope: Bool or None. If not None, determines whether intra-saccadic dPup is estimated
            participantCorrectionValue: float, per-saccade buildup value. 0 or None for no buildup correction
        """
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

    def __repr__(self):
        """Return text explanation of the snipandstitch. Logs corrValue property and its counterparts."""
        return f"SnipStitch. Adding {self.corrValue} ({self._dTot}+{self._dCorr}). "
    

class SnipStitchSRate(SnipStitch):
    def __init__(self, trial, event):
        """
        __init__
        Args:
        trial: Trial Object
        event: Event Object
        """
        super().__init__(trial, event)

    def Interpolate_dPup(self, trial):
        """Calculate dPup from interpolation of pre-saccadic slope."""
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

        #set pupil-change estimate by multiplying slope (a.u./sample) with saccade duration (samples)
        self._dPup = slope * (self._endIndex - self._startIndex)


    @property
    def corrValue(self):
        """Return the core value that is subtracted from pupil size values after saccade offset."""

        dPup = self._dPup if self.doInterpolateSlope else 0
        dCorr = self._dCorr

        return self._dTot - dPup - dCorr

    def Correct(self, index, value):
        """Return corrected pupil size value.
        
        Args:
            index: Index where pupil size is corrected
            value: Value before correction
        
        Returns:
            float: Pupil value after correction
        """

        #if index before correction, return uncorrected value
        if index <= self._startIndex:
            return value
        
        #if index after saccade, subtract correction value
        elif index >= self._endIndex:
            return value - self.corrValue
        
        #if index during saccade, return interpolated value between start and end
        else:
            return self._interpolationLambda(index)


    def __repr__(self):
        """Return text explanation of the snipandstitch. Logs corrValue property and its counterparts."""
        return f"SnipStitch. Adding {self.corrValue} ({self._dTot}+{self._dPup}+{self._dCorr}). "
