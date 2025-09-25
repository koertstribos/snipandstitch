# This file is part of the 'snipandstitch' package.
#this file contains private and internal definitions for the Trial class
#see Trial.py for public methods

from . import _SnipStitch
import matplotlib.pyplot as plt
from math import dist

#one trial
#contains information of one trial

#    initialisation
#    See subclass Trial (Trial.py)
class _T():
    #__init__
    def __init__(self, trace, events, samplingRate):
        self._trace = trace
        self._events = events
        self._samplingRate = samplingRate

        #check if events are in the trace
        end = self._events[-1].end
        if end > len(self._trace):
            raise ValueError(f"Events should be provided relative to each trial, but the last event ends at index {end} while the trace has length {len(self._trace)}")

        #call _MakeSnipStitches
        self._MakeSnipStitches()

    #_Correct
    #returns corrected pupil size value at specified index
    #args:
    #index:    int, representing index relative to trial
    #value:    float, value before correction
    #returns:
    #float; value after correction
    def _Correct(self, index, value):
        if not hasattr(self, '_SnipStitches'):
            raise ValueError("SnipStitches not set")
        
        for ss in self._SnipStitches:
            value = ss.Correct(index, value)
        return value

    #__getitem__ 
    #return a pupil size value at a given inex
    #corrects the pupil size value if corrections are set. If not, returns raw pupsize
    #in:
    #    index: int, representing index relative to trial
    def __getitem__(self, index):
        if isinstance(index, slice):
            return [self[i] for i in range(index.start, index.stop, index.step)]
        
        elif not isinstance(index, int):
            raise Exception(f"index {index} not supported. Should be int or slice")
        
        val = self._RawPupsize(index)

        if hasattr(self, '_SnipStitches'):
            return self._Correct(index, val)
        
        print(f"Warning: no SnipStitches set for trial, returning raw value")
        return val

    #residualCorrection 
    #sum of values that each snipandstitch uses to correct pupil size
    #this value should be near 0 for properly working methods, assuming that gaze starts and ends at roughly the same position
    @property
    def residualCorrection(self):
        if not hasattr(self, '_SnipStitches'):
            raise ValueError("SnipStitches not set when accessing residual error of a trial")
        return sum([ss.corrValue for ss in self._SnipStitches])

    #eventCount
    #count of events
    @property
    def eventCount(self):
        return len(self._events)

    #__len__
    #count of samples
    def __len__(self):
        return len(self._trace)

    #__repr__
    #just returns 'Trial'
    def __repr__(self):
        return f"Trial"

    #_MakeSnipStitches
    #initialises SnipStitch objects belonging to this trial
    #args:
    #
    #returns:
    #    None
    def _MakeSnipStitches(self):
        self._SnipStitches = []

        if self._samplingRate is None:
            for event in self._events:
                self._SnipStitches.append(_SnipStitch.SnipStitch(self, event))
        else:
            for event in self._events:
                self._SnipStitches.append(_SnipStitch.SnipStitchSRate(self, event))

    #_SetSnipStitchSettings
    #sets the settings of each snipstitch belonging to this trial
    #args:
    #    doInterpolateSlope: whether to interpolate slope (bool). If None, setting is left unchanged
    #    participantCorrectionValue:    value to correct linear error accumulation. A float to set that value If None, setting is left unchanged.
    # returns:
    #    None
    #see Functions.py for usage
    def _SetSnipStitchSettings(self, doInterpolateSlope = None, participantCorrectionValue = None):
        for ss in self._SnipStitches:
            ss.SetCorrectionSettings(doInterpolateSlope, participantCorrectionValue)

    #_ClampIndex
    #clamps an index, ensuring that no out-of-bounds indeces are used
    #args:
    #    Index:    Int, representing index relative to trial
    #out:
    #    Int, Index clamped between 0 and len(self)-1
    def _ClampIndex(self, index):
        return max(0, min(len(self)-1, index))

    #_RawPupsize
    #gets uncorrected pupil size at index
    #args:
    #    index:    Int, representing index relative to trial
    #out:
    #    float, raw pupil size at index
    def _RawPupsize(self, index):
        return self._trace[self._ClampIndex(index)][2]

    #_Pos
    #gets position arguments at index
    #args:
    #    index:    Int, representing index relative to trial
    #out:
    #    tuple (x,y), gaze coordinates at index. Type depends on user definition.
    def _Pos(self, index):
        return self._trace[self._ClampIndex(index)][:2]

    #_CorrectedPupsize
    #gets corrected pupil size at index
    #args:
    #    index:    Int, representing index relative to trial
    #out:
    #    float, corrected pupil size from that index
    def _CorrectedPupsize(self, index):
        return self[self._ClampIndex(index)]

    #_View
    #makes a Viewer object show this trial
    #args:
    #    viewer:    Viewer object
    #out:
    #    None
    def _View(self, viewer):
        startIndex = 0
        endIndex = len(self)
        
        fig, axs = plt.subplots(2)

        res = {'t': [], 'raw': [], 'corr':[], 'dist':[]}

        for i in range(startIndex, endIndex, viewer.viewingResolution):
            res['t'].append(i-startIndex)
            res['raw'].append(self.RawPupsize(i))
            res['dist'].append(dist(self.Pos(i),self.Pos(startIndex)))
            res['corr'].append(self.CorrectedPupsize(i))

        axs[0].plot(res['t'], res['raw'], c= [0,    0,  0])
        axs[0].plot(res['t'], res['corr'], c=[190/255, 131/255,   181/255])
        axs[1].plot(res['t'], res['dist'], c=[0,    0,  0])

        #plot events
        #before plotting events, get ylims because using axhline will change them
        ylims = axs[0].get_ylim()
        for event in self._events:
            [event.Draw(ax, ylims = ylims, resolution = viewer.viewingResolution)
             for ax in axs]

        #plot centre radius as horizontal dashed line
        axs[1].axhline(y=0, color=[0, 0, 0], linestyle='--')

        axs[0].set_title(f"")

        axs[0].set(xlabel='t (a.u.)', ylabel='pupil size')

        axs[1].get_xaxis().set_visible(False)
        axs[1].set(ylabel = 'gaze deviation')

        for ax in axs:
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

        plt.tight_layout()
        plt.show()

    
