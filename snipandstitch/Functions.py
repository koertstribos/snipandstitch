
import numpy as np
from scipy import stats

#SetLinearCorrection 
#this function corrects for linear accumulation of leftover error
#apply this function on a set of trials 
#    collected from one participant by one tracker
#    where the start and end position of gaze in each trial is roughly the same 

#in: 
#trials: list of Trial objects
#
#out:
#None (edits trials in-place)
def SetLinearCorrection(trials):
    y = np.array([trial.residualCorrection for trial in trials])
    x = np.array([trial.eventCount for trial in trials])

    # Calculate the slope using the least-squares formula
    numerator = np.sum(x * y)
    denominator = np.sum(x ** 2)
    val = numerator / denominator

    print(f"Linear correction value: {val}")

    for trial in trials:
        trial._SetSnipStitchSettings(participantCorrectionValue = val)


def SnipAndStitch_MNERaw(raw, channel, saccAnnots, interpolateDPup = True):

    raw.load_data()
    
    trace = raw.get_data(picks=channel, return_times=False)[0]
    sfreq = raw.info['sfreq']

    interpolateWidth_s = 0.1 #seconds, width of interpolation
    interpolateWidth = int(sfreq * interpolateWidth_s) #samples, width of interpolation
    extend = 1 #sample, extend events by this many samples on each side
    medianWidth = 4 #samples, nr. of samples to use for median before and after event

    startIdxs = raw.time_as_index(saccAnnots.onset)
    endIdxs = startIdxs + raw.time_as_index(saccAnnots.duration) + extend
    startIdxs -= extend

    for start, end in zip(startIdxs, endIdxs):
        #dPFE, estimate of pupil change due to PFE
        dPFE = np.median(trace[end:end + medianWidth]) - np.median(trace[start - medianWidth:start])

        if interpolateDPup:
            #slice data
            interSlice = trace[start-interpolateWidth:start]
            slope, _, _, p, _ = stats.linregress(range(interpolateWidth), interSlice) #slope in units/sample

            durSamp = (end - start) / sfreq #event duration in samples

            dPFE -= slope * durSamp #correct dPFE for slope

        #correct channel values after event
        trace[end:] -= dPFE

        #interpolate values during event
        trace[start:end] = np.linspace(trace[start], trace[end], end - start)

    raw._data[raw.ch_names.index(channel)] = trace
    return raw

#function for snipping and stitching MNE Epochs
#in:
#epochs: MNE Epochs object
#channel: string, name of channel to correct
#saccAnnots: mne Annotation object, containing an annotation for each saccade per epoch
#interpolateDPup: bool, whether to interpolate dPup due to PFE
#residualErrorCorrection: bool, whether to apply linear correction for residual error accumulation
#out:
#epochs: same MNE Epochs object, with corrected data in specified channel
def SnipAndStitch_MNEEpochs(epochs, channel, interpolateDPup = True, residualErrorCorrection=False, onNoSaccades = 'raise', match='ssSacc'):
    from . import Trial, Event

    #cast match to list if string
    if isinstance(match, str):
        match=[match]

    epochs.load_data()
    data = epochs.get_data(picks=channel)[:, 0, :] #shape (n_epochs, n_times)

    sfreq = epochs.info['sfreq']

    trials = []
    for trialData, _saccAnnotTup in zip(data, epochs.get_annotations_per_epoch()):

        _saccAnnotTup = [_sAT for _sAT in _saccAnnotTup if _sAT in match]
        
        if len(_saccAnnotTup) == 0:
            if onNoSaccades == 'raise':
                raise ValueError(f"No annotations starting with '{match}' found for one of the epochs")
            elif onNoSaccades == 'skip':
                trials.append(None)
                continue

        #construct a trace (x and y set to zero because not used here)
        trialTrace = np.zeros([len(trialData), 3]) 
        trialTrace[:, 2] = trialData #pupil size in 3rd column


        events = []
        for onset, duration, _ in _saccAnnotTup:
            tEnd = onset + duration
            #convert onset and tEnd to sample indices
            o = int(onset * sfreq + 0.5)
            e = int(tEnd * sfreq + 0.5)
            if e > len(trialData) or o < 0:
                continue #skip events that are out of bounds
            events.append(Event.Event(start=o, end=e))

        trial = Trial.Trial(trialTrace, events, samplingRate=sfreq)

        trial._MakeSnipStitches()
        trial._SetSnipStitchSettings(doInterpolateSlope=interpolateDPup)

        trials.append(trial)

    if residualErrorCorrection:
        SetLinearCorrection([t for t in trials if t is not None])

    #write back to epochs
    for i, trial in enumerate(trials):
        if trial is None:
            continue
        data[i, :] = np.array([trial.CorrectedPupsize(j) for j in range(len(trial))])

    #is this how to set?
    epochs._data[:, epochs.ch_names.index(channel), :] = data
    return epochs
        



    










    

















