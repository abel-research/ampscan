# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 14:54:40 2018

@author: js22g12
"""
import numpy as np
cimport numpy as np
cimport cython


cpdef np.ndarray[int] logEuPath_cy(int [:, :] arr):
    cdef int vmax = arr.shape[0]
    cdef list rows = list(range(vmax))
    order_np = np.zeros([vmax], dtype=int)
    cdef int [:] order = order_np
    cdef int i = 0
    cdef int x, n, xmax
    cdef int val = arr[i, 0]
    cdef int nmax = vmax-1
    for n in range(nmax):
        del rows[i]
        order[n] = val
        i=0
        xmax = vmax - n + 1
        for x in rows: 
            if arr[x, 0] == val:
                val = arr[x, 1]
                break
            if arr[x, 1] == val:
                val = arr[x, 0]
                break
            i+=1
    order[n+1] = val
    return order_np

cpdef np.ndarray[float, ndim=2] planeEdgeIntersect_cy(float [:, :] arr, float plane, int axisInd):
    cdef int emax = arr.shape[0]
    intersectPoints_np = np.zeros((emax, 3), dtype=np.float32)
    cdef float [:, :] intersectPoints = intersectPoints_np
    intersectPoints[:, axisInd] = plane
    cdef float e1, e2, e3, e4
    cdef Py_ssize_t i, j
    for i in range(emax):
        for j in range(2):
            e1 = arr[i, j]
            e2 = arr[i, axisInd]
            e3 = arr[i, j+3]
            e4 = arr[i, axisInd+3]
            intersectPoints[i, j] = e1 + (plane - e2) * (e3 - e1) / (e4 - e2)
    return intersectPoints_np