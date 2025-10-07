
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

#function for snipping and stitching MNE raw objects
#in:
#raw: MNE Raw object
#channel: string, name of channel to correct
#saccAnnots: mne Annotation object, containing an annotation for each saccade to be corrected (in temporal order please)
#interpolateDPup: bool, whether to interpolate dPup due to PFE
#inplace:         bool, whether to apply modifications to and return mne object that was given as 'raw' (True), or to apply edits to a copy thereof (False)
#out:
#MNE Raw object, with corrected data in specified channel. If 'inplace', is a reference to provided 'raw' object, edited inplace.  
def SnipAndStitch_MNERaw(raw, channel, saccAnnots, interpolateDPup = True, inplace=False):
    #pre-load data
    raw.load_data()

    #obtain pupil trace as np array
    trace = raw.get_data(picks=channel, return_times=False)[0]

    #if interpolation is required, set interpolation variables
    if interpolateDPup:
        sfreq = raw.info['sfreq']
        interpolateWidth_s = 0.1 #seconds, width of interpolation
        interpolateWidth = int(sfreq * interpolateWidth_s) #samples, width of interpolation

    #hard coded variables used in the Snip & Stitch algorithm
    extend = 1 #sample, extend events by this many samples on each side
    medianWidth = 4 #samples, nr. of samples to use for median before and after event

    #calculate start, and end indexes
    startIdxs = raw.time_as_index(saccAnnots.onset) - extend
    endIdxs = raw.time_as_index(saccAnnots.onset+saccAnnots.duration) + extend

    #loop over start and end indexes (saccade events)
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

#function for snipping and stitching MNE Epochs
#in:
#epochs:                  MNE Epochs object. 
#                        #Importantly, Raw.set_annotations() must have been called before making Epochs with events matching the key provided in 'match' 
#                        #(we here utilise mne.Epochs.get_annotations_per_epoch()
#channel:                 string, name of channel to correct
#interpolateDPup:         bool, whether to interpolate dPup due to PFE
#residualErrorCorrection: bool, whether to apply linear correction for residual error accumulation
#onNoSaccades:            string, 'raise' or 'skip', how to handle trials without saccades. 
#match:                   string, the key to look for when obtaining saccade events from Epochs object.
#inplace:                 bool, whether to apply modifications to and return mne object that was given as 'epochs' (True), or to apply edits to a copy thereof (False)
#out:
#MNE Epochs object, with corrected data in specified channel
def SnipAndStitch_MNEEpochs(epochs, channel, interpolateDPup = True, residualErrorCorrection=False, onNoSaccades = 'raise', match='ssSacc', inplace=False):
    #actually use the cool package this time
    from . import Trial, Event

    #ensure one of two options is provided
    assert (onNoSaccades == 'raise' or onNoSaccades == 'skip'), f"onNoSaccades argument must be (raise) or (omit), but {onNoSaccades} was provided" 

    #cast match to list if one string
    if isinstance(match, str):
        match=[match]
    #raise hell if not one string
    else:
        raise Exception(f"match must be of type str, but is type {type(match)}")

    #get data from channel
    data = epochs.get_data(picks=channel)[:, 0, :] #shape (n_epochs, n_times)

    #set sfreq if required. Else, set to None so that Snip&Stitch package can automatically detect no interpolation is required. 
    if interpolateDPup:
        sfreq = epochs.info['sfreq']
    else:
        sfreq = None

    #make a trials list and populate with Trial objects, or None
    trials = []
    for trialData, _saccAnnotTup in zip(data, epochs.get_annotations_per_epoch()):

        #read all annotations from this epoch annotations that match match in match (i.e., all provided saccade events)
        _saccAnnotTup = [_sAT for _sAT in _saccAnnotTup if _sAT in match]

        #if no saccades, do whatever was requested by argument 'onNoSaccades'
        if len(_saccAnnotTup) == 0:
            if onNoSaccades == 'raise':
                raise ValueError(f"No annotations starting with '{match}' found for one of the epochs")
            elif onNoSaccades == 'skip':
                trials.append(None)
                continue
            
        #construct a trace (x and y set to zero because not used here)
        trialTrace = np.zeros([len(trialData), 3]) 
        trialTrace[:, 2] = trialData #pupil size in 3rd column

        #construct list of Event objects, for each saccade annotation linked to this epoch
        events = []
        for onset, duration, _ in _saccAnnotTup:
            #get end time
            tEnd = onset + duration
            #convert onset and tEnd to sample indices
            o = int(onset * sfreq + 0.5)
            e = int(tEnd * sfreq + 0.5)
            if e > len(trialData) or o < 0:
                continue #skip events that are out of bounds
            events.append(Event.Event(start=o, end=e))

        #make Trial object
        trial = Trial.Trial(trialTrace, events, samplingRate=sfreq)

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
    if not inplace:
        epochs = epochs.copy()
    
    #write to (cloned) epochs object
    epochs._data[:, epochs.ch_names.index(channel), :] = data
    #return epochs object
    return epochs
        



    










    


















