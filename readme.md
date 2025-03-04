Welcome to the snipandstitch repository

The snipandstitch is a simple, universal correction for the Pupil Foreshortening Error in Saccades
the correction works by discarding unexpected change in pupil size observed during saccades

usage:

before using the correction one needs:

1. gaze and pupil data, as a list of tuples or dicts
2. a list of to-be-corrected saccades

the correction is performed by following the next steps:

1. Define relevant information regarding the setup used to collect data. This is stored using a SetupInfo object. Define this object by calling:
SetupInfo.SetupInfo(screenSize,screenDistance, resolution, sampleRate)   where

        screenSize:     physical size of the display in cm (w,h)
   
        screenDistance: distance between participant and display in cm
   
        resolution:     resolution of the display in pixels (w,h)
   
        sampleRate:     sampling rate of the data in Hz

   

3. separate the gaze and pupil data into trials. Each trial should start and end with gaze position at roughly the same position on the screen. (e.g., a central fixation).
for each trial, also get all relevant saccade events.Get the events ready for processing by constructing Event objects. These can be constructed by calling
Event.Event(start, end)
        
        start:  start index of the event, relative to the corresponding trial
        
        end:    end index of the event, relative to the corresponding trial
    

Trial objects can be constructed using Trial.Trial(trace, events)

        trace:   list of tuples or dicts that contain the eyetracking data. 
        The norm for this is (x, y, pupilSize)
        
        events:  list of Event objects 

finally, neatly pack all trials per participant by constructing Participant objects
Participant(trials, setupInfo, pupsizeIndex=2, xIndex=0, yIndex=1)

        trials:         list of Trial objects
        
        setupInfo:      SetupInfo object
        
        pupsizeIndex:   key or index that refers to pupilsize in a trace, defaults to 2
        
        xIndex:         key or index that refers to x value of gaze coordinate in a trace, defaults to 0
        
        yIndex:         key or index that refers to y value of gaze coordinate in a trace, defaults to 1
    

3. you can now get corrected gaze position from a Trial object by calling 
trial.CorrectedPupsize(index)
        
        index:  index of sample relative to trial

additionally, you can observe method performance by constructing a Viewer:

Viewer.Viewer(trials)

moreover, you can change whether the snipandstitch interpolates intrasaccadic pupil size change, and whether the snipandstitch corrects for linear per-participant error accumulation. (these settings can also be changed using the viewer)
participant.SetCorrection(estimateSlope, participantCorrection)
        
        estimateSlope:          bool, whether to interpolate intrasaccadic pupil size
        
        participantCorrection:  bool, whether to correct for linear participant accumulation


See the code hereunder for an example of the full process

    #load a participant dm
    part = get.ParticipantDM(partNo = 1, experimentNo = 2)

    #make ss setupinfo 
    screensize = part.screenSize
    screendist = part.screenDist
    resolution = part.screenDims
    samplerate = part.samplingRate
    setup = ss.SetupInfo.SetupInfo(screensize, screendist, resolution, samplerate)
    #set the centrepoint explicitly as I am correcting gaze position so that (0,0) is the centre
    setup.SetCentrePoint((0,0))

    #turn my trials into ss Trial objects
    triallist = []
    for trial in part.trials[:5]:
        start, end = trial._startIndex, trial._endIndex
        #turn the trace into something useable
        trace = []
        for i in range(start, end):
            x, y = part.GetPos(part[i])
            pupsize = part[i].Size(part.eyeUsedShort)
            trace.append((x, y, pupsize))

        #turn the events into ss Event objects
        events = []
        for event in trial.EventInstances(I2MCSaccade):
            start_ = part.MillisecondsToIndex(event.timeStamp) - start
            end_ = part.MillisecondsToIndex(event.timeStampEnd) - start

            #make sure the saccade is within the trial
            if start_ < 0 or end_ > len(trace):
                continue
            
            events.append(ss.Event.Event(start_, end_))
            
        #construct Trial object and add to list
        triallist.append(ss.Trial.Trial(trace, events))
        
    #make Participant object
    participant = ss.Participant.Participant(triallist, setup)

    #make a viewer
    viewer = ss.Viewer.Viewer(participant)

    #or, access a trial directly
    trial = triallist[0]
    
    for i in range(len(trial)):
        #get uncorrected pupil size for illustration purposes
        rawPupsize = trial.Pupsize(index=i)
        
        #get corrected pupil size
        correctedPupsize = trial.CorrectedPupsize(index=i)

        print(f"@{i}:{rawPupsize}->{correctedPupsize}")
