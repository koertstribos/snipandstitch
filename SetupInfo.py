# This file is part of the 'snipandstitch' package.
#this file contains the class SetupInfo
#the SetupInfo class contains information of the experimental setup used to collect eye tracking data

from ._SetupInfo import _SetupInfo
import math


#SetupInfo class
#this class contains information of the experimental setup used to collect eye tracking data
#   initialisation
#setupInfo = SetupInfo(screenSize, screenDistance, resolution, sampleRate)
#screenSize: physical size of the screen in cm (w,h)
#screenDistance: distance between the participant and the screen in cm
#resolution: resolution of the screen in pixels (w,h)
#sampleRate: sampling rate of the eye tracker in Hz
class SetupInfo(_SetupInfo):
    def __init__(self,
                 screenSize, screenDistance,
                 resolution, sampleRate):
        
        super().__init__(screenSize, screenDistance,
                         resolution, sampleRate)
        
    # # # # # # #
    #public methods

    #SetCentrePoint(newCentre)
    #defines the central reference point of the screen. 
    #   The central reference point is used to reset the PFE correction
    #arguments:
    #   newCentre: tuple or list of the x and y coordinates of the new central reference point
    #returns:
    #   None
    def SetCentrePoint(self, newCentre):
        self._SetCentrePoint(newCentre)
        
    #SetCentreRadius(newRadius)
    #defines the radius around the central reference point that is considered the central region of the screen
    #arguments:
    #   newRadius: the new radius in pixels
    #returns:
    #   None
    def SetCentreRadius(self, newRadius):
        self._SetCentreRadius(newRadius)

    #Convert_toVisualAngle(pixels)
    #converts a distance in pixels to a distance in visual angle
    #arguments:
    #   pixels: the distance in pixels
    #returns:
    #   the distance in visual angle
    def Convert_toVisualAngle(self, pixels):
        return self._VA(pixels)
    
    #Convert_toPixels(degrees)
    #converts a distance in visual angle to a distance in pixels
    #arguments:
    #   degrees: the distance in visual angle
    #returns:
    #   the distance in pixels
    def Convert_toPixels(self, degrees):
        return self._Pix(degrees)