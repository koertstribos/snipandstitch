"""Functions for snip-and-stitch correction of saccadic pupil-size artifacts in MNE objects."""
import numpy as np
from scipy import stats

def SetLinearCorrection(trials):
    """Correct for linear accumulation of leftover error and return corrected list of Trials  
    Keyword arguments:
    trials: list of Trial objects (collected from one participant by one tracker. Also, the start and end position of gaze in each trial is roughly the same )
    """
    y = np.array([trial.residualCorrection for trial in trials])
    x = np.array([trial.eventCount for trial in trials])

    # Calculate the slope using the least-squares formula
    numerator = np.sum(x * y)
    denominator = np.sum(x ** 2)
    val = numerator / denominator

    print(f"Linear correction value: {val}")

    for trial in trials:
        trial._SetSnipStitchSettings(participantCorrectionValue = val)

def SnipAndStitch_MNERaw(raw, channel, interpolateDPup = True, match='saccade', inplace=False):
    """Snip and stitch MNE raw objects to correct for saccadic pupil-size artifacts.
    Args:
        raw: MNE Raw object
        channel: string, name of channel to correct
        interpolateDPup: bool, whether to interpolate dPup when correcting PFE
        match: string, the key to look for when obtaining saccade events from Epochs object
        inplace: bool, whether to apply modifications to and return mne object that was given as 'raw' (True), or to apply edits to a copy thereof (False)
    Returns:
        MNE Raw object, with corrected data in specified channel. If 'inplace', is a reference to provided 'raw' object, edited inplace.
    """

    #obtain all saccade annotations
    saccAnnots = raw.annotations[raw.annotations.description == match]

    raw.load_data()

    trace = raw.get_data(picks=channel, return_times=False)[0]

    if interpolateDPup:
        sfreq = raw.info['sfreq']
        interpolateWidth_s = 0.1
        interpolateWidth = int(sfreq * interpolateWidth_s)

    extend = 1
    medianWidth = 4

    startIdxs = raw.time_as_index(saccAnnots.onset) - extend
    endIdxs = raw.time_as_index(saccAnnots.onset+saccAnnots.duration) + extend

    for start, end in zip(startIdxs, endIdxs):
        
        #dPFE, estimate of pupil change due to PFE
        dPFE = np.median(trace[end:end + medianWidth]) - np.median(trace[start - medianWidth:start])

        #do pupil size interpolation if required
        if interpolateDPup:
            #slice data
            interSlice = trace[start-interpolateWidth:start]
            slope, _, _, p, _ = stats.linregress(range(interpolateWidth), interSlice) #slope in units/sample
            durSamp = (end - start) / sfreq #event duration in samples
            #modify PFE estimate
            dPFE -= slope * durSamp #correct dPFE for slope

        #correct channel values after event
        trace[end:] -= dPFE

        #interpolate values during event by interpolating between corrected(!) start, and end samples
        trace[start:end] = np.linspace(trace[start], trace[end], end - start)

    #make clone if requested
    if not inplace:
        raw = raw.copy()

    #apply edits to (cloned) Raw object, and return
    raw._data[raw.ch_names.index(channel)] = trace
    return raw

def SnipAndStitch_MNEEpochs(epochs, channel, interpolateDPup = True, residualErrorCorrection=False, onNoSaccades = 'raise', match='saccade', inplace=False):
    """Snip and stitch MNE Epochs to correct for saccadic artifacts.
    Args:
        epochs: MNE Epochs object. Importantly, Raw.set_annotations() must have been called before making Epochs with events matching the key provided in 'match' (utilizes mne.Epochs.get_annotations_per_epoch())
        channel: string, name of channel to correct
        interpolateDPup: bool, whether to interpolate dPup due to PFE
        residualErrorCorrection: bool, whether to apply linear correction for residual error accumulation
        onNoSaccades: string, 'raise' or 'skip', how to handle trials without saccades
        match: string, the key to look for when obtaining saccade events from Epochs object
        inplace: bool, whether to apply modifications to and return mne object that was given as 'epochs' (True), or to apply edits to a copy thereof (False)
    Returns:
        MNE Epochs object, with corrected data in specified channel
    """
    from . import Trial, Event

    #ensure one of two options is provided
    assert (onNoSaccades == 'raise' or onNoSaccades == 'skip'), f"onNoSaccades argument must be 'raise' or 'omit', but {onNoSaccades} was provided" 

    #cast match to list if one string
    if isinstance(match, str):
        match=[match]
    #raise hell if not one string
    else:
        raise Exception(f"match must be of type str, but is type {type(match)}")
    
    #ensure that epochs have tmin great enough to contain _SnipStitch.INTERPOLATION_WIDTH (if this is not the case, interpolation is not possible)
    if interpolateDPup:
        from ._SnipStitch import INTERPOLATION_WIDTH
        assert -epochs.times[0] * 1000 >= INTERPOLATION_WIDTH, f"epochs use tmin {epochs.times[0]} s which is not enough to contain pre-saccadic interpolation window of {INTERPOLATION_WIDTH/1000} s"


    #load epochs data
    epochs.load_data()

    #get data from channel
    data = epochs.get_data(picks=channel)[:, 0, :] #shape (n_epochs, n_times)

    #set sfreq 
    sfreq = epochs.info['sfreq']
    #copy sfreq to argument for Trial initialisation, set to None if interpolateDPup is set to False to let the Trial object know no interpolation is required
    trial_sfreqArg = sfreq if interpolateDPup else None

    #make a trials list and populate with Trial objects, or None
    trials = []
    for trialData, _saccAnnotTup in zip(data, epochs.get_annotations_per_epoch()):


        #read all annotations from this epochs' annotations that match match in match (i.e., all provided saccade events)
        _saccAnnotTup = [_sAT for _sAT in _saccAnnotTup if _sAT[2] in match]

        #construct a trace (x and y set to zero because they are not used in this scope)
        trialTrace = np.zeros([len(trialData), 3]) 
        trialTrace[:, 2] = trialData #pupil size in 3rd column

        #construct list of Event objects, for each saccade annotation linked to this epoch
        events = []
        for onset, duration, _ in _saccAnnotTup:

            #if saccade begins before trial onset (t=0), skip this saccade
            if onset < 0:
                continue

            #subtract epoch tmin from onset for conversion to sample indices
            onset -= epochs.times[0]

            #get end time relative to epoch onset
            tEnd = onset + duration
            #convert onset and tEnd to sample indices
            o = int(onset * sfreq + 0.5)
            e = int(tEnd * sfreq + 0.5)

            if e > len(trialData):
                continue #skip events that are out of bounds
            events.append(Event.Event(start=o, end=e))

        #if no saccades were succesfully turned into events, do whatever was requested by argument 'onNoSaccades'
        if len(events) == 0:
            if onNoSaccades == 'raise':
                raise ValueError(f"No annotations starting with '{match}' found for one of the epochs. To skip these errors instead of raising, change the 'onNoSaccades' argument to 'skip'")
            elif onNoSaccades == 'skip':
                trials.append(None)
                continue

        #make Trial object
        trial = Trial.Trial(trialTrace, events, samplingRate=trial_sfreqArg)

        #append to list
        trials.append(trial)

    #apply our linear error correction if requested
    if residualErrorCorrection:
        SetLinearCorrection([t for t in trials if t is not None])

    #write back to epochs, first set a np array for all data
    for i, trial in enumerate(trials):
        if trial is None:
            continue
        data[i, :] = np.array([trial.CorrectedPupsize(j) for j in range(len(trial))])

    #clone epochs object if requested
    if inplace:
        _epochs = epochs #set reference
    else:
        _epochs = epochs.copy() #set copy
    
    #write to (cloned) epochs object
    _epochs._data[:, epochs.ch_names.index(channel), :] = data

    #return (cloned) epochs object
    return _epochs
        



    










    


















