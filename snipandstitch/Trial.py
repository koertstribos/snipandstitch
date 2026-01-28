"""This file is part of the 'snipandstitch' package.

This module contains the Trial class which holds information regarding one trial.
"""

from . import _Trial


class Trial(_Trial._T):
    """Trial class contains information of one trial.
    
    Args:
        trialTrace: list of samples, each sample is a dict or list that contains x, y, and pupil size
        trialEvents: list of Event objects (see Event.py)
        samplingRate: sampling rate in Hz (optional)
    """
    def __init__(self, trialTrace, trialEvents, samplingRate = None):
        super().__init__(trialTrace, trialEvents, samplingRate)

    def CorrectedPupsize(self, index):
        """Return a pupil size measurement at a given index after applying snipandstitch correction.
        
        Args:
            index: int, index of sample relative to trial
        
        Returns:
            float: corrected pupil size from that index
        """
        return super()._CorrectedPupsize(index)

    def RawPupsize(self, index):
        """Return a pupil size measurement at a given index without applying snipandstitch correction.
        
        Args:
            index: int, index of sample relative to trial
        
        Returns:
            float: raw pupil size from that index
        """
        return super()._RawPupsize(index)

    def Pos(self, index):
        """Return position of gaze at a given index.
        
        Args:
            index: int, index of sample relative to trial
        
        Returns:
            tuple: (x, y) gaze coordinates. Type is defined by user in Trial() initialization.
        """
        if index < 0 or index >= len(self):
            raise Exception(f"index {index} out of range")
        return super()._Pos(index)

    def SetInterpolateSlope(self, doInterpolate):
        """Turn the intra-saccadic slope interpolation on or off.
        
        Args:
            doInterpolate: Bool. Whether to interpolate.
        """
        super()._SetSnipStitchSettings(doInterpolateSlope = doInterpolate)
    
