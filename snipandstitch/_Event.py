# This file is part of the 'snipandstitch' package.
#This file contains the class for the event object
#See Event.py for public methods

class _E():
    def __init__(self, start, end):
        self.start = start
        self.end = end

    # # # # # # # # # 
    #protected methods

    #Draw
    #draws the event on a mpl plot
    #arguments:
    #   ax: the axis to draw the event on
    #   relativeStart: the index at which the plot starts, relative to trial start
    #   resolution: the number of indeces per plotpoint
    #returns:
    #   None
    def Draw(self, ax, ylims, resolution):
        start = (self.start) // resolution
        end = (self.end) // resolution

        col = [0.8, 0.8, 0.8]
        linestyle = '--'

        ax.axvline(start, c=col, linestyle=linestyle)
        ax.axvline(end, c=col, linestyle=linestyle)
        ax.fill_between([start, end], ylims[0], ylims[1], color=col, alpha=0.5)

