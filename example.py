import mne
from snipandstitch import Functions as ssFunc
import numpy as np
import matplotlib.pyplot as plt

#load eyetracker data
et_fpath = mne.datasets.eyelink.data_path() / "eeg-et" / "sub-01_task-plr_eyetrack.asc"
raw = mne.io.read_raw_eyelink(et_fpath, create_annotations=["saccades", "blinks"]) #create annotations for saccades and blinks
raw.pick(['pupil_right', 'ypos_right', 'xpos_right']) #only right-eye location and pupil size


#plot the raw data 
#raw.plot(scalings=dict(pupil=1), block=True) #plot the three channels

#we will now split the continuous data into segments. Critically, we set the segments so that there is always a saccade at t=0

#make a nx3 events array from all saccade events
trialAnnots = raw.annotations[raw.annotations.description=='saccade']
eventIdx = raw.time_as_index(trialAnnots.onset)
eventsArray = np.zeros([len(eventIdx), 3], dtype=int)
eventsArray[: , 0] = eventIdx


#make epochs object from events
tmin = -0.1
tmax = 0.2
epochs = mne.Epochs(raw, events=eventsArray, 
                    tmin = tmin, tmax=tmax, baseline=None, 
                    reject_by_annotation=True)

#correct epoch using snipandstitch functionality
epochs_sns = ssFunc.SnipAndStitch_MNEEpochs(epochs=epochs, channel = 'pupil_right', 
                                            interpolateDPup = True, residualErrorCorrection=False, 
                                            onNoSaccades = 'raise', match='saccade', inplace=False)

#get the annotations from the epochs object again to plot saccade durations inside epochs
#this latter list of annotations also no longer includes blinks, as these have been removed due to reject_by_annotation=True
epochSaccs = epochs.get_annotations_per_epoch()

#loop over epochs and plot each one
for idx in range(len(epochs)):
    fig, ax = plt.subplots(1)

    #plot uncorrected data
    ax.plot(epochs.times, epochs.get_data(['pupil_right'])[idx, 0, :], color='gray', label='uncorrected')
    #plot corrected data
    ax.plot(epochs.times, epochs_sns.get_data(['pupil_right'])[idx, 0, :], color='black', label='corrected')

    #additionally, plot relevant saccades as shaded area

    #get all saccades belonging to this epoch
    _epSaccs = epochSaccs[idx]
    
    #ylims are needed to plot saccades as shaded area
    ylims = ax.get_ylim()

    #loop over saccades, plot them if they fit the epoch
    for saccOnset, saccDur, _ in _epSaccs:

        #don't plot saccade if it starts before epoch (these are not corrected)
        if saccOnset <= tmin:
            continue

        #don't plot saccade if it ends after epoch
        saccEnd = saccOnset + saccDur
        if saccEnd >= tmax:
            continue

        #plot saccade using onset, duration, and ylims
        ax.fill_between([saccOnset, saccOnset + saccDur], ylims[0], ylims[1], color='red', alpha=0.2)


    ax.legend()
    plt.show()
