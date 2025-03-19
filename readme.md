Welcome to the snipandstitch repository

The snipandstitch is a simple, universal correction for the Pupil Foreshortening Error in Saccades
the correction works by discarding unexpected change in pupil size observed during saccades

usage:

before using the correction one needs:

1. gaze and pupil data, as a list of tuples or dicts where each sample is saved like (x,y,pupilSize)
2. a list of to-be-corrected saccades

the correction is performed by following the next steps:

1. Define relevant information regarding the setup used to collect data. This is stored using a SetupInfo object. Define this object by calling:
SetupInfo.SetupInfo(screenSize,screenDistance, resolution, sampleRate)   where 
    screenSize:     physical size of the display in cm (w,h)
    screenDistance: distance between participant and display in cm
    resolution:     resolution of the display in pixels (w,h)
    sampleRate:     sampling rate of the data in Hz

2. separate the gaze and pupil data into trials. Each trial should start and end with gaze position at roughly the same position on the screen. (e.g., a central fixation).
for each trial, also get all relevant saccade events.

get the events ready for processing by constructing Event objects. These can be constructed by calling
Event.Event(start, end)
    start:  start index of the event, relative to the corresponding trial
    end:    end index of the event, relative to the corresponding trial

Trial objects can be constructed using
Trial.Trial(trace, events, setupInfo)
    trace       list of tuples or dicts that contain the eyetracking data. 
                The norm for this is (x, y, pupilSize)
    events      list of Event objects 
    setupInfo   SetupInfo object


3. you can now get corrected gaze position from a Trial object by calling 
trial.CorrectedPupsize(index)
    index:  index of sample relative to trial

additionally, you can observe method performance by constructing a Viewer:

Viewer.Viewer(trials)

moreover, you can change whether the snipandstitch interpolates intrasaccadic pupil size change, and whether the snipandstitch corrects for linear per-participant error accumulation.
participant.SetCorrection(estimateSlope, participantCorrection)
    estimateSlope:          bool, whether to interpolate intrasaccadic pupil size
    participantCorrection:  bool, whether to correct for linear participant accumulation