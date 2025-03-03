# This file is part of the 'snipandstitch' package.
#this file contains private and internal definitions for the Trial class
#see Trial.py for public methods

from . import _SnipStitch
import inspect

#one trial
class _T():
    def __init__(self, trace, events):
        self._trace = trace
        self._events = events

        #check if events are in the trace
        end = self._events[-1].end
        if end > len(self._trace):
            raise ValueError(f"Events should be provided relative to each trial, but the last event ends at index {end} while the trace has length {len(self._trace)}")

    def Correct(self, index, value):
        if not hasattr(self, '_SnipStitches'):
            raise ValueError("SnipStitches not set")
        
        for ss in self._SnipStitches:
            value = ss.Correct(index, value)
        return value

    def __getitem__(self, index):
        if 0 <= index < len(self._trace):
            return self._trace[index]
        else:
            #check if caller is already _part, which would cause an infinite loop
            stack = inspect.stack()
            callerFrame = stack[1]
            callerObj = callerFrame.frame.f_locals.get('self')

            if callerObj == self.part:
                raise Exception(f"index {index} out of range and self-referential call detected")
            
            return self.part[index+self.part.RelativeStart(self)]
        
    @property
    def residualCorrection(self):
        if not hasattr(self, '_SnipStitches'):
            raise ValueError("SnipStitches not set when accessing residual error of a trial")
        return sum([ss.corrValue for ss in self._SnipStitches])
    
    @property
    def eventCount(self):
        return len(self._events)
    
    @property
    def gazeDeviation(self):
        startPoint = self.Pos(0)
        endPoint = self.Pos(len(self)-1)

        return self.part._setupInfo.Distance(startPoint, endPoint)
    
    @property
    def part(self):
        if hasattr(self, '_part'):
            return self._part
        else:
            raise ValueError("Participant not set")

    def __len__(self):
        return len(self._trace)
    
    def __repr__(self):
        return f"Trial"
    
    def _MakeSnipStitches(self):
        self._SnipStitches = []
        for event in self._events:
            self._SnipStitches.append(_SnipStitch.SnipStitch(self, event))

    def _SetSnipStitchSettings(self, doInterpolateSlope, participantCorrectionValue):
        for ss in self._SnipStitches:
            ss.SetCorrectionSettings(doInterpolateSlope, participantCorrectionValue)

    def _LinkParticipant(self, participant):
        self._part = participant

    def _Pupsize(self, index):
        return self.part.Pupsize(index+self.part.RelativeStart(self))
    
    def _Pos(self, index):
        return self.part.Pos(index+self.part.RelativeStart(self))
    
    def _CorrectedPupsize(self, index):
        return self.part._CorrectedPupsize(index+self.part.RelativeStart(self))
    