# This file is part of the 'snipandstitch' package.
#this file contains private and internal definitions for the SetupInfo class
#see SetupInfo.py for public methods

import math

#underlying class for SetupInfo
#internal use only
#see SetupInfo.py for public methods
class _SetupInfo():
    def __init__(self, 
                 screenSize, 
                 screenDistance, 
                 resolution, 
                 sampleRate
                 ):
        
        PixPerCm = (resolution[0] / (2*screenSize[0])) + (resolution[1] / (2*screenSize[1]))
        self.screenDistancePix = screenDistance * PixPerCm
        self.screenDistance = screenDistance
        self.screenSize = screenSize
        self.resolution = resolution
        self.sampleRate = sampleRate

        self.centre = (resolution[0]/2, resolution[1]/2) #screen midpoint coordinates
        self.centreRadius = self.Convert_toPixels(3) #dva, convert to pixels
        
    # # # # # # # 

    #protected methods

    #Distance
    #returns the distance between two points
    #arguments:
    #   p1: tuple or list of the x and y coordinates of the first point
    #   p2: tuple or list of the x and y coordinates of the second point
    #returns:
    #   the distance between the two points, in the same units as the input
    def Distance(self, p1, p2):
        return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5

    #AtCentre
    #checks if a point is contained within the central reference region
    #arguments:
    #   p1: tuple or list of the x and y coordinates of the point
    #returns:
    #   True if the point is within the central reference region, False otherwise
    def AtCentre(self, p1):
        return self.Distance(p1, self.centre) <= self.centreRadius
    
    #Milliseconds
    #converts indeces to milliseconds
    #arguments:
    #   indeces: the number of indeces
    #returns:
    #   the number of milliseconds
    def Milliseconds(self, indeces):
        return int(indeces / self.sampleRate * 1000)
    
    #Indeces
    #converts milliseconds to indeces
    #arguments:
    #   milliseconds: the number of milliseconds
    #returns:
    #   the number of indeces
    def Indeces(self, milliseconds):
        return int(milliseconds / 1000 * self.sampleRate)
    
    # # # # # # #

    #private methods

    #_SetCentrePoint
    #for setting the central reference point
    #arguments:
    #   newCentre: the new central reference point
    #returns:
    #   None
    def _SetCentrePoint(self, newCentre):
        self.centre = newCentre
        
    #_SetCentreRadius
    #for setting the central reference radius
    #arguments:
    #   newRadius: the new central reference radius in pixels
    #returns:
    #   None
    def _SetCentreRadius(self, newRadius):
        self.centreRadius = newRadius
     
    #_Pix
    #converts degrees of visual angle to pixels
    #arguments:
    #   degrees: the distance in visual angle
    #returns:
    #   the distance in pixels
    def _Pix(self, degrees):
        rad = degrees/360 * math.tau
        pix = math.tan((rad)) * self.screenDistancePix
        return pix

    #_VA
    #converts pixels to degrees of visual angle
    #arguments:
    #   pixels: the distance in pixels
    #returns:
    #   the distance in visual angle
    def _VA(self, pixels):
        rad = math.atan(pixels / self.screenDistancePix)
        return rad * 360 / math.tau
    

        
        