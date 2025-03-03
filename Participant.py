# This file is part of the 'snipandstitch' package.
#this file contains the class Participant
#the Participant class contains all trials of a participant

from . import _Participant

#Participant 
#this class contains all trials of a participant
#   initialisation:
#participant = Participant(trials, setupInfo, pupsizeIndex, xIndex, yIndex)
#trials: list of Trial objects
#setupInfo: SetupInfo object
#pupsizeIndex: index or key that pupilsize is saved under in each sample
#xIndex: index or key that x position is saved under in each sample
#yIndex: index or key that y position is saved under in each sample
class Participant(_Participant._P):
    def __init__(self, trials, setupInfo, pupsizeIndex=2, xIndex=0, yIndex=1):
        super().__init__(trials, setupInfo, pupsizeIndex, xIndex, yIndex)

    # # # # #
    #public methods
    
    #SetCorrection
    #sets the correction settings
    #arguments:
    #   estimateSlope: bool, if True, pupil size during saccade is interpolated
    #   participantCorrection: bool, if True, participant specific correction is applied
    def SetCorrection(self, estimateSlope, participantCorrection):
        super._SetCorrectionSettings(estimateSlope, participantCorrection)

    #CorrectedPupsize
    #returns the corrected value at that index
    #arguments:
    #   index: the index of the value to correct
    #returns:
    #   corrected value
    def CorrectedPupsize(self, index):
        return super()._CorrectedPupsize(index)