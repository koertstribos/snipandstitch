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
    def __init__(self, trialTrace, trialEvents, setupInfo):
        super().__init__(trialTrace, trialEvents, setupInfo)

    def CorrectedPupsize(self, index):
        if index < 0 or index >= len(self):
            raise Exception(f"index {index} out of range")
        return super()._CorrectedPupsize(index)

    def RawPupsize(self, index):
        if index < 0 or index >= len(self):
            raise Exception(f"index {index} out of range")
        return super()._RawPupsize(index)
    
    def Pos(self, index):
        if index < 0 or index >= len(self):
            raise Exception(f"index {index} out of range")
        return super()._Pos(index)
    
