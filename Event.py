# This file is part of the 'snipandstitch' package.
# This file contains the Event class
# The Event class contains information of one (saccade) event

from . import _Event

#Event class
#this class contains information of one (saccade) event
#   initialisation
#event = Event(start, end)
#start: start index of the event (relative to the trial)
#end: end index of the event (relative to the trial)
class Event(_Event._E):
    def __init__(self, start, end):
        super().__init__(start, end)