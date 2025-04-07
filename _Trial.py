# This file is part of the 'snipandstitch' package.
#this file contains private and internal definitions for the Trial class
#see Trial.py for public methods

from . import _SnipStitch
import matplotlib.pyplot as plt

#one trial
class _T():
    def __init__(self, trace, events, setupInfo):
        self._trace = trace
        self._events = events
        self._setupInfo = setupInfo

        #check if events are in the trace
        end = self._events[-1].end
        if end > len(self._trace):
            raise ValueError(f"Events should be provided relative to each trial, but the last event ends at index {end} while the trace has length {len(self._trace)}")
        
        self._MakeSnipStitches()

    def _Correct(self, index, value):
        if not hasattr(self, '_SnipStitches'):
            raise ValueError("SnipStitches not set")
        
        for ss in self._SnipStitches:
            value = ss.Correct(index, value)
        return value

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

    @property
    def residualCorrection(self):
        if not hasattr(self, '_SnipStitches'):
            raise ValueError("SnipStitches not set when accessing residual error of a trial")
        return sum([ss.corrValue for ss in self._SnipStitches])
    
    @property
    def eventCount(self):
        return len(self._events)
    
    def __len__(self):
        return len(self._trace)
    
    def __repr__(self):
        return f"Trial"
    
    def _MakeSnipStitches(self):
        self._SnipStitches = []
        for event in self._events:
            self._SnipStitches.append(_SnipStitch.SnipStitch(self, event))

    def _SetSnipStitchSettings(self, doInterpolateSlope = None, participantCorrectionValue = None):
        for ss in self._SnipStitches:
            ss.SetCorrectionSettings(doInterpolateSlope, participantCorrectionValue)

    def _ClampIndex(self, index):
        return max(0, min(len(self)-1, index))

    def _RawPupsize(self, index):
        return self._trace[self._ClampIndex(index)][2]
    
    def _Pos(self, index):
        return self._trace[self._ClampIndex(index)][:2]
    
    def _CorrectedPupsize(self, index):
        return self[self._ClampIndex(index)]
    
    def _View(self, viewer):
        startIndex = 0
        endIndex = len(self)
        
        fig, axs = plt.subplots(2)

        res = {'samps': [], 'raw': [], 'corr':[], 'dist':[]}

        for i in range(startIndex, endIndex, viewer.viewingResolution):
            res['samps'].append(i-startIndex)
            res['raw'].append(self.RawPupsize(i))
            res['dist'].append(self._setupInfo.Distance(self.Pos(i), self._setupInfo.centre))
            res['corr'].append(self.CorrectedPupsize(i))

        axs[0].plot(res['samps'], res['raw'], c= [0,    0,  0])
        axs[0].plot(res['samps'], res['corr'], c=[190/255, 131/255,   181/255])
        axs[1].plot(res['samps'], res['dist'], c=[0,    0,  0])

        #plot events
        #before plotting events, get ylims because using axhline will change them
        ylims = axs[0].get_ylim()
        for event in self._events:
            [event.Draw(ax, ylims = ylims, resolution = viewer.viewingResolution)
             for ax in axs]

        #plot centre radius as horizontal dashed line
        axs[1].axhline(y=self._setupInfo.centreRadius, color=[0, 0, 0], linestyle='--')

        axs[0].set_title(f"")

        axs[0].set(xlabel='samples', ylabel='pupil size')

        axs[1].get_xaxis().set_visible(False)
        axs[1].set(ylabel = 'gaze dist.')

        for ax in axs:
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

        plt.tight_layout()
        plt.show()

    
