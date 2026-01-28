"""This file is part of the 'snipandstitch' package.

This module contains the internal Event class. See Event.py for public methods.
"""

class _E():
    """Internal Event class."""
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def Draw(self, ax, ylims, resolution):
        """Draw the event on a matplotlib plot.
        
        Args:
            ax: the axis to draw the event on
            ylims: ylims to be passed to fill_between
            resolution: the number of indices per plot point
        """
        start = (self.start) // resolution
        end = (self.end) // resolution

        col = [0.8, 0.8, 0.8]
        linestyle = '--'

        ax.axvline(start, c=col, linestyle=linestyle)
        ax.axvline(end, c=col, linestyle=linestyle)
        ax.fill_between([start, end], ylims[0], ylims[1], color=col, alpha=0.5)


