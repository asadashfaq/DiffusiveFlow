from __future__ import division
import numpy as np

"""
A collection of commonly used functions.
"""

def nodeDegree(A, n):
    """
    Calculate node degree(s) from adjacency matrix. Input can be a single index
    or a list of indices.
    """
    if not (type(n) == int or type(n) == list):
        raise Exception('input type should be _int_ or _list_')
    if type(n) == int:
        return int(sum(A[n]))
    if type(n) == list:
        return np.array([nodeDegree(A,i) for i in n])

def norm(v):
    """
    Normalise input vector.
    """
    if sum(v) != 0:
        return v/sum(v)
    else:
        print('Sum of vector equals zero. Returning un-normalised vector')
        return v
