import mne
from mne.datasets.eyelink import data_path
from mne.preprocessing.eyetracking import read_eyelink_calibration
from mne.viz.eyetracking import plot_gaze

et_fpath = data_path() / "eeg-et" / "sub-01_task-plr_eyetrack.asc"
#eeg_fpath = data_path() / "eeg-et" / "sub-01_task-plr_eeg.mff"

raw_et = mne.io.read_raw_eyelink(et_fpath, create_annotations=["blinks"])
#raw_eeg = mne.io.read_raw_egi(eeg_fpath, events_as_annotations=True).load_data()
#raw_eeg.filter(1, 30)

raw_et.info

print(raw_et.annotations[0]["ch_names"])  # a blink in the right eye

ps_scalings = dict(pupil=4e3)
raw_et.plot(scalings=ps_scalings)