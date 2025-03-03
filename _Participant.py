# This file is part of the 'snipandstitch' package.
#this file contains private and internal definitions for the Participant class
#see Participant.py for public methods
import matplotlib.pyplot as plt
import math
from . import _SnipStitch
import inspect
import numpy as np
from collections import namedtuple

#underlying class for Participant
#internal use only
#see Participant.py for public methods
class _P():
    def __init__(self, trials, setupInfo, pupsizeIndex, xIndex, yIndex):
        self._trials = trials

        for trial in self._trials:
            trial._LinkParticipant(self)

        self._setupInfo = setupInfo
        self._indexing = {'pupsize': pupsizeIndex, 'x': xIndex, 'y': yIndex} 

        self._MakeSnipStitches()
        self._SetCorrectionSettings(estimateSlope = True, participantCorrection = True)

    def __getitem__(self, index):
        if index < 0:
            raise ValueError("Negative indexing not supported")
        for trial in self._trials:
            if index >= len(trial):
                index -= len(trial)
            else:
                return trial[index]
            
    def __len__(self):
        return sum([len(t) for t in self._trials])
            
    @property
    def trialCount(self):
        return len(self._trials)
            
    def Pupsize(self, index):
        return self[index][self._indexing['pupsize']]
    
    def _CorrectedPupsize(self, index):
        value = self.Pupsize(index)
        #get corresponding trial
        trial = None
        for t in self._trials:
            if index >= len(t):
                index -= len(t)
            else:
                trial = t
                break

        if trial is None:
            raise ValueError(f"Index {index} not found in full trace of length {len(self)})")
             
        res = trial.Correct(index, value)
        return res
    
    def Pos(self, index):
        return (self[index][self._indexing['x']], self[index][self._indexing['y']])
            
    def RelativeStart(self, trial):
        index = self._trials.index(trial)
        if index == -1:
            raise ValueError("Trial not found")
        
        startIndex = 0
        for i in range(index):
            startIndex += len(self._trials[i])

        return startIndex
    
    def _MakeSnipStitches(self):
        for trial in self._trials:
            trial._MakeSnipStitches()      
    
    def _SetCorrectionSettings(self, estimateSlope, participantCorrection):
        for trial in self._trials:
            trial._SetSnipStitchSettings(doInterpolateSlope = estimateSlope,
                                          participantCorrectionValue = [0,self.pCorr][participantCorrection])

    @property
    def pCorr(self):
        if hasattr(self, '_pCorr'):
            return self._pCorr
        else:
            self._CalculatePCorr()
            return self._pCorr

    def _CalculatePCorr(self):
        totalDeviation = sum([trial.residualCorrection for trial in self._trials])
        totalEvents = sum([trial.eventCount for trial in self._trials])

        self._pCorr = totalDeviation / totalEvents

    def View(self, index, viewer):
        trial = self._trials[index]
        startIndex = self.RelativeStart(trial) - viewer.extraViewingWidth
        if startIndex < 0:
            startIndex = 0
        endIndex = startIndex + len(trial) + viewer.extraViewingWidth
        if endIndex > len(self):
            endIndex = len(self)

        print(f"Viewing trial {index+1} with the following corrections:")
        [print(repr(ss)) for ss in trial._SnipStitches]
        
        fig, axs = plt.subplots(2)

        res = {'samps': [], 'raw': [], 'corr':[], 'dist':[]}

        for i in range(startIndex, endIndex, viewer.viewingResolution):
            res['samps'].append(i-startIndex)
            res['raw'].append(self.Pupsize(i))
            res['dist'].append(viewer.setupInfo.Distance(self.Pos(i), viewer.setupInfo.centre))
            res['corr'].append(self.CorrectedPupsize(i))

        axs[0].plot(res['samps'], res['raw'], c= [0,    0,  0])
        axs[0].plot(res['samps'], res['corr'], c=[190/255, 131/255,   181/255])
        axs[1].plot(res['samps'], res['dist'], c=[0,    0,  0])

        #plot events
        for event in trial._events:
            [event.Draw(ax, relativeStart = viewer.extraViewingWidth, resolution = viewer.viewingResolution)
             for ax in axs]

        #plot trial start and end as red lines if the plot extends beyond the trial
        if viewer.extraViewingWidth > 0:
            trialStart_inPlot = viewer.extraViewingWidth // viewer.viewingResolution
            axs[0].axvline(x=trialStart_inPlot, color=[1, 0, 0])
            trialEnd_inPlot = (len(trial) + viewer.extraViewingWidth) // viewer.viewingResolution
            axs[0].axvline(x=trialEnd_inPlot, color=[1, 0, 0])

        #plot centre radius as horizontal dashed line
        axs[1].axhline(y=viewer.setupInfo.centreRadius, color=[0, 0, 0], linestyle='--')

        axs[0].set_title(f"trial {index+1} / {self.trialCount}")

        axs[0].set(xlabel='samples', ylabel='pupil size')

        axs[1].get_xaxis().set_visible(False)
        axs[1].set(ylabel = 'gaze dist.')

        for ax in axs:
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

        plt.tight_layout()
        plt.show()
