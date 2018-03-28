# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 14:54:40 2018

@author: js22g12
"""
import numpy as np
cimport numpy as np
cimport cython

cpdef testValue(int [:, :] arr, list rows, int val):
    cdef int i, x, y, newval
    i = 0
    for x in rows:
        for y in range(2):
            newval = arr[x,y]
            if newval == val:
                val = arr[x, 1-y]
                return (val, i)
        i+=1

cpdef np.ndarray[int] logEuPath(int [:, :] arr):
    cdef int vmax = arr.shape[0]
    rows = list(range(vmax))
    cdef int i, x
    cdef list order = []
    i = 0
    x = 0
    cdef int val = arr[i, 0]
    cdef int val2
    for n in range(vmax-1):
        del rows[i]
        order.append(val)
        (val, i) = testValue(arr, rows, val)
    order.append(val)
    return np.array(order)
