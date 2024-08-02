import srtm
import numpy as np
from rdp import rdp

def optimize_points(points,  epsilon = 0.0001):
    arr = np.array([[x[0], x[1]] for x in points])
    mask = rdp(arr, algo="iter", return_mask=True, epsilon=epsilon)
    parr = np.array(points)
    final = []
    for i in list(parr[mask]):
        final.append(tuple(i.tolist()))
    return final

