from __future__ import division
import numpy as np
from vector_maths import normalize



def BlinnPhong_specular(incident_vector, view_vector, surface_norm, shininess_exponent):
    """ Return the Blinn-Phong specular intensity for a given light reflection into a viewpoint on a surface with a shininess factor.
    Source adapted from: http://ruh.li/GraphicsPhongBlinnPhong.html
    Ref: Blinn, James F. (1977): Models of light reflection for computer synthesized pictures 
    """
    specularIntensity = 0.0
    """ Should the view_vector be negated? I see it is in various places.
    """
    #view_vector = -view_vector
    
    if (np.dot(incident_vector, surface_norm) > 0.0):
        halfwayVector       = normalize(incident_vector + view_vector)
        specTmp             = max(np.dot(surface_norm, halfwayVector), 0.0)
        specularIntensity   = pow(specTmp, shininess_exponent)
    return specularIntensity
    


def Lambert_diffuse( incident_vector, surface_norm ):
    """ 
    Adapted from source: http://pyopengl.sourceforge.net/context/tutorials/shader_5.html
    """
    normalized_incident_vec = normalize(incident_vector)
    return max( 0.0, np.dot(surface_norm , normalized_incident_vec) )
    
