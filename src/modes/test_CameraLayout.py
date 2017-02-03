from modes import *


def test():
    #CameraLayout.register(CameraLayout_RealisticBias)
    
    camera_layout = CameraLayout_RealisticBias( 8.0 )
    print( camera_layout.getCameraPositions() )
    cameraPos = camera_layout.getDefaultCameraPos()
    print( cameraPos )
    
    
    camera_layout = CameraLayout_EvenBias( 8.0 )
    print( camera_layout.getCameraPositions() )
    cameraPos = camera_layout.getDefaultCameraPos()
    print( cameraPos )

if __name__ == "__main__":
    test()
