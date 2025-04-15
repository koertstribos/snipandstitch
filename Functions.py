import numpy as np

#SetLinearCorrection 
#this function corrects for linear accumulation of leftover error
#apply this function on a set of trials 
#    collected from one participant by one tracker
#    where the start and end position of gaze in each trial is roughtly the same 

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
