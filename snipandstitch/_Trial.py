"""This file is part of the 'snipandstitch' package.

This module contains private and internal definitions for the Trial class.
See Trial.py for public methods.
"""

from . import _SnipStitch
import matplotlib.pyplot as plt
from math import dist

class _T():
    """Internal Trial class containing information of one trial.
    
    See subclass Trial (Trial.py) for public API.
    """
    def __init__(self, trace, events, samplingRate):
        """Initialize Trial object.
        
        Args:
            trace: List of samples, each containing x, y, and pupil size
            events: List of Event objects
            samplingRate: Sampling rate in Hz
        """
        self._trace = trace
        self._events = events
        self._samplingRate = samplingRate

        #check if events are in the trace
        end = self._events[-1].end
        if end > len(self._trace):
            raise ValueError(f"Events should be provided relative to each trial, but the last event ends at index {end} while the trace has length {len(self._trace)}")

        #call _MakeSnipStitches
        self._MakeSnipStitches()

    def _Correct(self, index, value):
        """Return corrected pupil size value at specified index.
        
        Args:
            index: int, representing index relative to trial
            value: float, value before correction
        
        Returns:
            float: value after correction
        """
        if not hasattr(self, '_SnipStitches'):
            raise ValueError("SnipStitches not set")
        
        for ss in self._SnipStitches:
            value = ss.Correct(index, value)
        return value

    def __getitem__(self, index):
        """Return a pupil size value at a given index.
        
        Corrects the pupil size value if corrections are set. If not, returns raw pupil size.
        
        Args:
            index: int, representing index relative to trial
        """
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
        """Return sum of correction values from each snipandstitch.
        
        This value should be near 0 for properly working methods, assuming that gaze
        starts and ends at roughly the same position.
        """
        if not hasattr(self, '_SnipStitches'):
            raise ValueError("SnipStitches not set when accessing residual error of a trial")
        return sum([ss.corrValue for ss in self._SnipStitches])

    @property
    def eventCount(self):
        """Return the number of events in this trial."""
        return len(self._events)

    def __len__(self):
        """Return the number of samples in this trial."""
        return len(self._trace)

    def __repr__(self):
        """Return string representation of Trial object."""
        return f"Trial"

    def _MakeSnipStitches(self):
        """Initializes SnipStitch objects for this trial."""
        self._SnipStitches = []

        if self._samplingRate is None:
            for event in self._events:
                self._SnipStitches.append(_SnipStitch.SnipStitch(self, event))
        else:
            for event in self._events:
                self._SnipStitches.append(_SnipStitch.SnipStitchSRate(self, event))

    #_SetSnipStitchSettings
    #see Functions.py for usage
    def _SetSnipStitchSettings(self, doInterpolateSlope = None, participantCorrectionValue = None):
        """Set the settings of each SnipStitch belonging to this trial.
        Args:
            doInterpolateSlope : Bool or None. If not None, determines whether intra-saccadic dPup is estimated
            participantCorrectionValue : float or None. Per-saccade buildup value. 0 or None for no buildup correction
        """
        for ss in self._SnipStitches:
            ss.SetCorrectionSettings(doInterpolateSlope, participantCorrectionValue)

    #_ClampIndex
    #clamps an index, ensuring that no out-of-bounds indeces are used
    #args:
    #    Index:    Int, representing index relative to trial
    #out:
    #    Int, Index clamped between 0 and len(self)-1
    def _ClampIndex(self, index):
        """Clamp an index to be within valid range of the trial."""
        return max(0, min(len(self)-1, index))

    #_RawPupsize
    #gets uncorrected pupil size at index
    #args:
    #    index:    Int, representing index relative to trial
    #out:
    #    float, raw pupil size at index
    def _RawPupsize(self, index):
        """Return raw pupil size at specified index.""" 
        return self._trace[self._ClampIndex(index)][2]

    #_Pos
    #gets position arguments at index
    #args:
    #    index:    Int, representing index relative to trial
    #out:
    #    tuple (x,y), gaze coordinates at index. Type depends on user definition.
    def _Pos(self, index):
        """Return gaze position at specified index."""
        return self._trace[self._ClampIndex(index)][:2]

    #_CorrectedPupsize
    #gets corrected pupil size at index
    #args:
    #    index:    Int, representing index relative to trial
    #out:
    #    float, corrected pupil size from that index
    def _CorrectedPupsize(self, index):
        """Return corrected pupil size at specified index."""
        return self[self._ClampIndex(index)]

    #_View
    #makes a Viewer object show this trial
    #args:
    #    viewer:    Viewer object
    #out:
    #    None
    def _View(self, viewer):
        """Visualize this trial using the provided viewer object.
        args:
        viewer: a Viewer object"""
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

    
