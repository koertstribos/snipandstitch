Welcome to the snipandstitch repository

The snipandstitch is a simple, universal correction for the Pupil Foreshortening Error in Saccades
the correction works by discarding unexpected change in pupil size observed during saccades

usage:

before using the correction one needs:

0. "pip install git+https://github.com/koertstribos/snipandstitch", or download this package, and put the full folder in your python working directory
1. gaze and pupil data, as a list of tuples or dicts where each sample is saved like (x,y,pupilSize), x and y may be dummy values 0.
2. a list of to-be-corrected saccades

- - - mne implementation - -
We provide functions to apply our correction using the popular mne library. To apply our correction, perform the following steps:

1: Import snipandstitch.Functions

    from snipandstitch import Functions as ssFunc

2: Separate the gaze and pupil data into trials and prepare saccade events.

mne requires a list of saccade onsets, list or durations, and list of descriptions (e.g. 'ssSacc'). All in recording time. 
Critically, snipandstitch expects either a list of annotations to be snipped (raw function), or that the annotations are linked to 

    annots = mne.Annotations(onset, duration, description)
        onset:        list of onsets in seconds mne time
        duration:     list of durations in seconds mne time
        description:  list of descriptions, should be a unique description if operating on Epochs object, ensure that descriptions all match, e.g. all 'ssSacc'

    mne_raw = mne.Raw(...)
       
        see mne documentation 

    mne_raw.set_annotations(annots) #required if processing with Epochs

        annots:    previously constructed Annotations object

if using and Epochs object, 

Create Epochs objects for each trial. Alternatively, you can do the correction for all saccades in a single recording in one go (not recommended due to drift)

    epochs = mne.Epochs(...) 

        see mne documentation 

3: You can now call the SnipandStitch correction on an Epochs object by calling

    ssFunc.SnipAndStitch_MNEEpochs(epochs, channelName, interpolateDPup, residualErrorCorrection, match)

    epochs                    MNE epochs object, discontinuous data structure to-be-corrected
    channelName               string, name of channel to-be-corrected, e.g. 'pupsize'
    interpolateDpup           boolean, wether to interpolate intra-saccadic pupil size. Default=True
    residualErrorCorrection   boolean, wether to perform a residual error correction using all Epochs. Default=False
    match                     string, name of events to be removed. e.g. 'ssSacc'

or, for one-recording data

    ssFunc.SnipAndStitch_MNERaw(mneRaw, channelName, annotations)

    mneRaw        MNE raw object, continuous data structure to-be-corrected
    channelName   string, name of channel to-be-corrected, e.g. 'pupsize'
    annotations   MNE Annotations object containing all saccade events


- - - python tuple implementation - - -

the correction is performed by following the next steps:

1: Import the snipandstitch package

    from snipandstitch import *

2: Separate the gaze and pupil data into trials and prepare saccade events.

Get the events ready for processing by constructing Event objects. These can be constructed by calling

    Event.Event(start, end)
    -------------------------------------
    start:  start index of the event, relative to the corresponding trial
    end:    end index of the event, relative to the corresponding trial

Trial objects can be constructed using 
    
    Trial.Trial(trace, events, samplingRate)
    -------------------------------------
    trace:      list of tuples that contain the eyetracking data. X and Y values may be dummy (0)
                Should be provided as [(x_0, y_0, pupilSize_0), (x_1, y_1, pupilSize_1), ... , (x_n, y_n, pupilSize_n)]
    events:     list of Event objects 
    sRate:      sampling rate (samples per second). Needs to be provided in order to estimate intra-saccadic pupil size change.

3: you can now get corrected gaze position from a Trial object by calling:

    trial.CorrectedPupsize(index)
    -------------------------------------
    index:  index of sample relative to trial

By default, intra-saccadic pupil size change is interpolated using linear regression. To turn this feature off, use:

    trial.SetInterpolateSlope(False)

Moreover, you can perform a drift correction on a subset of trials. 
In our experiments, we observed error to accumulate at a linear rate different for measurement of each participant.
Correcting this drift requires trials to start and end with gaze at (roughly) the same position. 
You can perform the drift correction on a list of trials by calling:

    Functions.SetLinearCorrection(trials)
    -------------------------------------
    trials:    list of Trial objects to be corrected

To verify correction behaviour, you can observe method performance by constructing a Viewer:

    Viewer.Viewer(trials)
    -------------------------------------
    trials:    list of Trial objects

