from __future__ import division
from abc import ABCMeta
from model_helpers import rotate_vector


class CameraLayout():
    """
    Abstract Base Class (ABC) for camera layouts.
    """
    __metaclass__ = ABCMeta
    def __init__(self, scale):
        self.cameraPos = (0,0,scale+1.5)
    def getCameraPositions(self):
        return []
    def getDefaultCameraPos(self):
        return self.cameraPos
    def getDescription(self):
        return ""
    def getShortDescription(self):
        return ""
        


class CameraLayout_RealisticBias(CameraLayout):
    """
    Strategy class to produce "realistically biased" camera positions.
    """
    def getDescription(self):
        return "Realistic bias. 6 cameras. 3 on equator 90 degrees apart. 2 at the front offset by 5 degrees. 1 top-down."
    def getShortDescription(self):
        return "Realistic bias"
    def getCameraPositions(self):
    
        cam0 = rotate_vector( self.cameraPos, (1,0,0), -5 )        # Add front-facing camera (just below equator)
        cam1 = rotate_vector( self.cameraPos, (1,0,0), 5 )         # Add front-facing camera (just above equator)
        cam2 = rotate_vector( self.cameraPos, (0,1,0), 90 )      # Add position on the equator
        cam3 = rotate_vector( cam2, (0,1,0), 90 )           # Add position on the equator
        cam4 = rotate_vector( cam3, (0,1,0), 90 )           # Add position on the equator
        cam5 = rotate_vector( self.cameraPos, (1,0,0), -90 )     # Add top-down camera
        
        camerasVertices = [cam0, cam1, cam2, cam3, cam4, cam5]
        return camerasVertices

class CameraLayout_EvenBias(CameraLayout):
    """
    Strategy class to produce "evenly biased" camera positions.
    """
    def getDescription(self):
        return "Even bias. 6 cameras. 4 on equator 90 degrees apart. 2 at the poles."
    def getShortDescription(self):
        return "Even bias"
    def getCameraPositions(self):
        cam1 = rotate_vector( self.cameraPos, (0,1,0), 0 )       # Add position on the equator
        cam2 = rotate_vector( self.cameraPos, (0,1,0), 90 )      # Add position on the equator
        cam3 = rotate_vector( cam2, (0,1,0), 90 )           # Add position on the equator
        cam4 = rotate_vector( cam3, (0,1,0), 90 )           # Add position on the equator
        cam5 = rotate_vector( self.cameraPos, (1,0,0), -90 )     # Add top-down camera
        cam6 = rotate_vector( self.cameraPos, (1,0,0), 90 )      # Add bottom-up camera
        
        camerasVertices = [cam1, cam2, cam3, cam4, cam5, cam6]
        return camerasVertices



