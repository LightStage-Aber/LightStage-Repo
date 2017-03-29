import numpy as np

def iqr( x ):
    q75, q25 = np.percentile(x, [75, 25])
    iqr = q75 - q25
    return iqr