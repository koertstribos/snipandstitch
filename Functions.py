import scipy.linalg as la
import numpy as np

def SetLinearCorrection(trials):
    y = np.array([trial.residualCorrection for trial in trials])
    x = np.array([trial.eventCount for trial in trials])

    print(f"residual errors: {x}")
    print(f"event counts: {y}")

    # Calculate the slope using the least-squares formula
    numerator = np.sum(x * y)
    denominator = np.sum(x ** 2)
    val = numerator / denominator

    print(f"Linear correction value: {val}")

    for trial in trials:
        trial._SetSnipStitchSettings(participantCorrectionValue = val)