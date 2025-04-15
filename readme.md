Welcome to the snipandstitch repository

The snipandstitch is a simple, universal correction for the Pupil Foreshortening Error in Saccades
the correction works by discarding unexpected change in pupil size observed during saccades

usage:

before using the correction one needs:

0. download this package, and put the full folder in your python working directory
1. gaze and pupil data, as a list of tuples or dicts where each sample is saved like (x,y,pupilSize)
2. a list of to-be-corrected saccades

the correction is performed by following the next steps:

1: Import the snipandstitch package

    from snipandstitch import *

2: Define relevant information regarding the setup used to collect data. This is stored using a SetupInfo object. Define this object by calling:

    SetupInfo.SetupInfo(screenSize,screenDistance, resolution, sampleRate)
    -------------------------------------
    screenSize:     physical size of the display in cm (w,h)
    screenDistance: distance between participant and display in cm
    resolution:     resolution of the display in pixels (w,h)
    sampleRate:     sampling rate of the data in Hz

3: Separate the gaze and pupil data into trials. 
Get the events ready for processing by constructing Event objects. These can be constructed by calling

    Event.Event(start, end)
    -------------------------------------
    start:  start index of the event, relative to the corresponding trial
    end:    end index of the event, relative to the corresponding trial

Trial objects can be constructed using 
    
    Trial.Trial(trace, events, setupInfo)
    -------------------------------------
    trace:      list of tuples that contain the eyetracking data. 
                Should be provided as [(x_0, y_0, pupilSize_0), (x_1, y_1, pupilSize_1), ... , (x_n, y_n, pupilSize_n)]
    events:     list of Event objects 
    setupInfo:  SetupInfo object


4: you can now get corrected gaze position from a Trial object by calling:

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

