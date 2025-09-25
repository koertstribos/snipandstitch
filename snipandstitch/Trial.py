# This file is part of the 'snipandstitch' package.
#this file contains the class Trial
#a Trial object contains information regarding one trial

from . import _Trial

#Trial class
#this class contains information of one trial

#   initialisation
#trial = Trial(trialTrace, trialEvents)
#trialTrace: list of samples, each sample is a dict or list that contains x, y, and pupsize
#trialEvents: list of Event objects (see Event.py)
class Trial(_Trial._T):
    def __init__(self, trialTrace, trialEvents, samplingRate = None):
        super().__init__(trialTrace, trialEvents, samplingRate)

    #CorrectedPupsize
    #returns a pupil size measurement at a given index after applying snipandstitch correcton
    #in:
    #index: int, index of sample relative to trial
    #out:
    #float, corrected pupil size from that index
    def CorrectedPupsize(self, index):

        return super()._CorrectedPupsize(index)

    #RawPupsize
    #returns a pupil size measurement at a given index without applying snipandstitch correction
    #in:
    #index: int, index of sample relative to trial
    #out:
    #float, corrected pupil size from that index
    def RawPupsize(self, index):

        return super()._RawPupsize(index)

    #Pos
    #returns position of gaze at a given index
    #in:
    #index: int, index of sample relative to trial
    #out:
    #(x,y) tuple. Type is defined by user in Trial() initialisation
    def Pos(self, index):
        if index < 0 or index >= len(self):
            raise Exception(f"index {index} out of range")
        return super()._Pos(index)

    #SetInterpolateSlope
    #Turn the intra-saccadic slope interpolation on or off
    #in:
    #doInterpolate, Bool. Whether to interpolate
    #out:
    #None
    def SetInterpolateSlope(self, doInterpolate):
        super()._SetSnipStitchSettings(doInterpolateSlope = doInterpolate)

    #SetLinearCorrection
    #in Functions.py, see a function for setting the linear correction value
    
