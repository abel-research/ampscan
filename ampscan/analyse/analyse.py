# -*- coding: utf-8 -*-
"""
Package for dealing with analysis methods of the ampObject and generating 
reports 
Copyright: Joshua Steer 2020, Joshua.Steer@soton.ac.uk
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as clr
import matplotlib.colorbar as clb
from mpl_toolkits.mplot3d import Axes3D
from collections import defaultdict
from .output import getPDF
from math import floor
#from .cython_ext import planeEdgeIntersect_cy, logEuPath_cy
import os

# The file path used in doc examples
filename = os.path.join(os.getcwd(), "tests", "stl_file.stl")

def calc_volume_closed(amp_in, return_closed=False):
    r"""
    Calculates the volume of a closed surface. If the surface is not closed the algorithm fills in the holes using a simple
    hole filling algorithm, the surface without holes can be accessed if return_closed is set to True.


    Parameters
    ----------
    amp: AmpObject 
        The AmpObject to analyse
    return_closed: bool, default False
        Indicate whether to return the shape with holes filled in  

    Returns
    -------
    vol: float
        The volume of the AmpObject
    amp: AmpObject
        If return_closed is True, then the closed shape is returned 
    """
    amp = amp_in.close()
    # Calculate the area of each face in the array using vector cross product
    v01 = amp.vert[amp.faces[:, 1], :] - amp.vert[amp.faces[:, 0], :]
    v02 = amp.vert[amp.faces[:, 2], :] - amp.vert[amp.faces[:, 0], :]
    cp = np.square(np.cross(v01, v02))
    area = 0.5 * np.sqrt(cp.sum(axis=1))
    # Get surface volume contributions 
    sVC = area * amp.vert[amp.faces, 2].mean(axis=1) * amp.norm[:, 2]
    if return_closed is True:
        return sVC.sum(), amp
    else:
        return sVC.sum()



def create_slices(amp, *args,  typ='slices', axis = 2, order=True):
    r"""
    Generate polygons from planar slices through the AmpObject. The slices are either defined as a 
    list of positions in some axis
    
    Parameters
    ----------
    amp: AmpObject 
        The AmpObject to analyse
    slices: array_like
        An array of the slice positions to take in the specified axis
    limits: array_like
        The limits of the slices, either in real world units or normalised depending on that specified in typ
    intervals: float
        The distance between slices, use in conjunction with 
    typ: str, 'slices', 'real_intervals', 'norm_intervals'
        The height of the slice planes
    axis: int, default 2
        The index of the axis to take the slices along
    
    Returns
    -------
    polys: list
        A list of numpy arrays, each array contains the vertices of the 
        polygon generated from the slice

    Examples
    -------
    >>> amp = AmpObject(filename)
    >>> polys = create_slices(amp, [0.05, 0.95], 0.01, typ='norm_intervals', axis=2)
    >>> polys = create_slices(amp, [-150, -100, -50, 0], typ='slices', axis=2)
    >>> polys = create_slices(amp, [-150, 0], 10, typ='real_intervals', axis=2)
    """
    # Setup the slices array 
    if typ == 'slices':
        # Return error if no slices given provided 
        slices = args[0]
    elif typ == 'real_intervals':
        lim = args[0]
        intervals = args[1]
        slices = np.arange(lim[0], lim[1], intervals)
        slices = np.append(slices, lim[1])
    elif typ == 'norm_intervals':
        # Get the minimum and maximum of the limb
        limb_min = amp.vert[:, axis].min()
        limb_max = amp.vert[:, axis].max()
        limb_len = limb_max - limb_min
        lim = args[0]
        intervals = args[1]
        slices = np.arange(lim[0], lim[1], intervals)
        slices = np.append(slices, lim[1])
        slices = limb_min + (slices * limb_len)
        
    else: 
        return
        # Return error that typ is an invalid value 
    
    # Now start to calculate the polyons on each slice
    
    # Get the vertices on each edges 
    vE = amp.vert[:, axis][amp.edges]
    # Find all vertices below plane 
    polys = []
    for plane in slices:
        try:
            ind = vE <= plane
            # Select edges with one vertex above and one below the slice plane 
            validEdgeInd = np.where(np.logical_xor(ind[:,0], ind[:,1]))[0]
            validfE = amp.faceEdges[validEdgeInd, :].astype(int)
            faceOrder = logEuPath(validfE)
            # Get array of three edges attached to each face
            validEdges = amp.edgesFace[faceOrder, :]
            # Remove the edge that is not intersected by the plane
            edges = validEdges[np.isin(validEdges, validEdgeInd)].reshape([-1,2])
            # Remove the duplicate edge from order 
            e = edges.flatten()
            sortE = []
            for ed in e:
                if ed not in sortE:
                    sortE.append(ed)
            sortE.append(sortE[0])
            # Add first edge to end of array
    #            sortE = np.append(sortE, sortE[0])
            sortE = np.asarray(sortE)
            polyEdge = amp.edges[sortE]
            EdgePoints = np.c_[amp.vert[polyEdge[:,0], :], 
                                amp.vert[polyEdge[:,1], :]]
            #Create poly from 
            polys.append(planeEdgeIntersect_cy(EdgePoints, plane, axis))
        except:
            continue
    return polys

def calc_perimeter(polys):
    r"""
    Calculate the perimeter of each polygon from the slicing of the AmpObject  

    Parameters
    ----------
    polys: list
        A list of numpy arrays, each array contains the vertices of the 
        polygon generated from the slice. Generate using ampscan.analyse.create_slices()

    Returns
    -------
    perimeter: array_like
        Returns the perimeter of the limb in mm along the axis 
    """
    perimeter = np.zeros(len(polys))
    # Iterate over each polygon
    for i, p in enumerate(polys):
        # Get the distances in each dimension between adjacent points 
        d = p[1:, :] - p[:-1, :]
        # Calculate the normalised distance between points 
        dist = np.linalg.norm(d, axis=1)
        # Sum the distances to get the perimeter
        perimeter[i] = dist.sum()
    # Return the perimeter and distance of limb over which perimeter calculated
    return perimeter



def calc_widths(polys):
    r"""
    Calculate the coronal and sagittal widths of each polygon from the slicing of the AmpObject  

    Assumes that coronal width corresponds with the x-axis 

    Parameters
    ----------
    polys: list
        A list of numpy arrays, each array contains the vertices of the 
        polygon generated from the slice. Generate using ampscan.analyse.create_slices()

    Returns
    -------
    cor_width: array_like
        Returns the coronal width in mm along the axis
    sag_width: array_like
        Returns the sagittal width in mm along the axis 
    """
    cor_width = np.zeros(len(polys))
    sag_width = np.zeros(len(polys))
    # Automatically check the axis of slicing by finding the axis with minimal deviation
    # The correct axis should have 0 deviation
    ix = np.argmin(polys[0].max(axis=0) - polys[0].min(axis=0))
    # Remove from list the index for slicing axis 
    ind = [0,1,2]
    ind.remove(ix)
    for i, p in enumerate(polys):
        # Get the widths through min - max 
        cor_width[i], sag_width[i] = p[:, ind].max(axis=0) - p[:, ind].min(axis=0)
    return cor_width, sag_width

def calc_csa(polys):
    r"""
    Calculate the cross sectional area of each polygon from the slicing of the AmpObject  

    Parameters
    ----------
    polys: list
        A list of numpy arrays, each array contains the vertices of the 
        polygon generated from the slice. Generate using ampscan.analyse.create_slices()

    Returns
    -------
    csa: array_like
        Returns the cross-sectional area of the limb in mm^2 along the axis 
    """
    csa = np.zeros(len(polys))
    # Automatically check the axis of slicing by finding the axis with minimal deviation
    # The correct axis should have 0 deviation
    ix = np.argmin(polys[0].max(axis=0) - polys[0].min(axis=0))
    # Remove from list the index for slicing axis 
    ind = [0,1,2]
    ind.remove(ix)
    # Iterate over each poly to calculcate cross sectional area 
    for i, p in enumerate(polys):
        csa[i] = 0.5*np.abs(
                            np.dot(
                                   p[:,ind[0]], 
                                   np.roll(p[:,ind[1]], 1)
                                  ) 
                            -
                            np.dot(
                                   p[:,ind[1]], 
                                   np.roll(p[:,ind[0]], 1)
                                   )
                            )
    return csa

def est_volume(polys):
    r"""
    Estimate the volume of the limb using bounds of the slices 

    Parameters
    ----------
    polys: list
        A list of numpy arrays, each array contains the vertices of the 
        polygon generated from the slice. Generate using ampscan.analyse.create_slices()

    Returns
    -------
    Volume: float
        Returns the estimated volume of the limb in mm^3 along the axis 
    """
    # Automatically check the axis of slicing by finding the axis with minimal deviation
    # The correct axis should have 0 deviation
    ix = np.argmin(polys[0].max(axis=0) - polys[0].min(axis=0))
    # Remove from list the index for slicing axis 
    ind = [0,1,2]
    ind.remove(ix)
    # Calculate the csa
    csa = calc_csa(polys)
    # Get the distance between each slice 
    d = []
    for p in polys: 
        d.append(p[:, ix].mean())
    d = np.asarray(d)
    # Get distance between each slice 
    dist = np.abs(d[1:]- d[:-1])
    # Calculate volume between each slice by mutliplying the 
    # mean cross sectional area by the distance 
    vol = np.c_[csa[1:], csa[:-1]]
    vol = np.mean(vol, axis=1) * dist
    return vol.sum()
    

def logEuPath(arr):
    """
    Calculate the eularian path for an array of edges so the vertices all connect
    """
    vmax = arr.shape[0]
    rows = list(range(vmax))
    # order = np.zeros([vmax], dtype=int)
    order = [];
    i = 0
    val = arr[i, 0]
    nmax = vmax-1
    for n in range(nmax):
        del rows[i]
        # order[n] = val
        order.append(val)
        i=0
        for x in rows: 
            if arr[x, 0] == val:
                val = arr[x, 1]
                break
            if arr[x, 1] == val:
                val = arr[x, 0]
                break
            i+=1
    # order[n+1] = val
    order.append(val)
    order = np.asarray(order, dtype=int)
    return order


def planeEdgeIntersect_cy(arr, plane, axisInd):
    r"""
    Calculate the intersection between a an array of edges and a plane
    
    Parameters 
    ----------
    edges: array_like 
        The edge array which have been calculated to cross the plane
    plane: float
        The height of the plane
    axis: int, default 2
        The index of the axis of the slice
    
    Returns
    -------
    intersectPoints: ndarray
        The intersection points between the edges and the plane
    
    """
    emax = arr.shape[0]
    intersectPoints = np.zeros((emax, 3), dtype=np.float32)
    intersectPoints[:, axisInd] = plane
    for i in range(emax):
        for j in range(2):
            e1 = arr[i, j]
            e2 = arr[i, axisInd]
            e3 = arr[i, j+3]
            e4 = arr[i, axisInd+3]
            intersectPoints[i, j] = e1 + (plane - e2) * (e3 - e1) / (e4 - e2)
    return intersectPoints

def planeEdgeintersect(edges, plane, axis=2):
    r"""
    Calculate the intersection between a an array of edges and a plane
    
    Parameters 
    ----------
    edges: array_like 
        The edge array which have been calculated to cross the plane
    plane: float
        The height of the plane
    axis: int, default 2
        The index of the axis of the slice
    
    Returns
    -------
    intersectPoints: ndarray
        The intersection points between the edges and the plane
    
    """
    # Allocate intersect points array
    intersectPoints = np.zeros((edges.shape[0], 3))
    # Define the plane of intersect points
    intersectPoints[:, axis] = plane
    axesInd = np.array([0,1,2])[np.array([0,1,2]) != axis]
    for i in axesInd:
        intersectPoints[:, i] = (edges[:, i] +
                                    (plane - edges[:, axis]) *
                                    (edges[:, i+3] - edges[:, i]) /
                                    (edges[:, axis+3] - edges[:, axis]))
    return intersectPoints


def visualise_slices(amp):
    r"""
    Create an mpl figure with the 3D rendering, slices, slice height and cross sectional area
    """
    fig = plt.figure()
    fig.set_size_inches(8, 8)
    ax = plt.axes(projection="3d")
    X = amp.vert[:, 0]
    Y = amp.vert[:, 1]
    Z = amp.vert[:, 2]
    ax.view_init(elev=0., azim=-90)
    ax.axis('off')
    ax.set_proj_type('ortho')
    ax.set_aspect('equal')
    ax.plot_trisurf(X, Y, Z, triangles=amp.faces, color=(1.0, 1.0, 1.0), 
                    shade=False, edgecolor='none', linewidth=0, antialiased=False)
    plt.savefig('test1.png', dpi=600)
    plt.close(fig)

def plot_slices(amp, axis=2, slWidth=10):
    r"""
    Generate a mpl figure with information about the AmpObject
    
    Top Left - Slices
    Top Right - Change in cross sectional area through slices
    Bottom Left - Rendering of shape
    Bottom Right - Rendering of shape with values 
    
    TODO: Split this up so each figure is it's own function, top level 
    function to tailor figure to user 
    
    Parameters
    ----------
    axis: int, default 2
        Axis along which to take slices
    slWidth: float, default 10
        Distance between slices
    
    Returns
    -------
    fig: mpl figure
        The mpl figure generated by the function
    ax: tuple
        A tuple of axes used for each subplot in the figure

    """
    # Find the brim edges 
    ind = np.where(amp.faceEdges[:,1] == -99999)[0]
    # Define max Z from lowest point on brim
    maxZ = amp.vert[amp.edges[ind, :], 2].min()
    # Create slices
    slices = np.arange(amp.vert[:,2].min() + slWidth,
                        maxZ, slWidth)
    # Create polys 
    polys = create_slices(amp, slices, axis)
    # Plot each poly
    fig = plt.figure()
    fig.set_size_inches(6, 4.5)
    ax1 = fig.add_subplot(221, projection='3d')
    for p in polys:
        ax1.plot(p[:,0],
                 p[:,1],
                 p[:,2],
                 c='b')
    extents = np.array([getattr(ax1, 'get_{}lim'.format(dim))() for dim in 'xyz'])
    sz = extents[:,1] - extents[:,0]
    centers = np.mean(extents, axis=1)
    maxsize = max(abs(sz))
    r = maxsize/2
    for ctr, dim in zip(centers, 'xyz'):
        getattr(ax1, 'set_{}lim'.format(dim))(ctr - r, ctr + r)
    ax1.set_axis_off()

    # Calculate the area along the length of the limb 
    PolyArea = calc_csa(polys)
    # Plot area along limb 
    ax2 = fig.add_subplot(222)
    ax2.plot(slices-slices[0], PolyArea)

    # Rendering of the limb scan
    ax3 = fig.add_subplot(2,2,3)
    Im = amp.genIm()[0]
    ax3.imshow(Im, None)
    ax3.set_axis_off()

    # Rendering of the rectification map 
    ax4 = fig.add_subplot(2,2,4)
    amp.addActor(CMap = amp.CMapN2P)
    Im = amp.genIm()[0]
    ax4.imshow(Im, None)
    ax4.set_axis_off()
    plt.tight_layout()
    plt.show()
    return fig, (ax1, ax2, ax3, ax4)

def MeasurementsOut(amp, pos):
    """
    Calculates perimeter of limb/cast at intervals from mid-patella to the
    end of stump
    Takes position of mid-patella (x,y,z) coordinates as input
    Also creates images of limb views and graphs of CSA/Widths, which are
    used in the PDF.
    Calls the function responsible for adding the information to the PDF
    template.
    TODO: Split this into functions for each part i.e. Volume measure, CSA,
    widths

    Returns
    -------
    The path to the output file
    """
    # print(pos)
    maxZ = []
    for i in [0,1,2]:
        maxZ.append((amp.vert[:, i]).max() - (amp.vert[:, i]).min())
    #slice in longest axis of scan
    axis = maxZ.index(max(maxZ))
    maxZ = max(maxZ)
    zval = pos[axis]
    # Get 6 equally spaced pts between mid-patella and stump end
    slices = np.linspace(zval, (amp.vert[:, axis]).min()+0.1, 6)
    # uses create_slices
    polys = create_slices(amp, slices, axis=axis)
    # calc perimeter of slices
    perimeter = calc_perimeter(polys)
    # distance between slice and mid-patella
    lngth = (slices - zval) / 10
    #print(lngth, perimeter)
    #generate png files of anterior and lateral views
    amp.genIm(out='fh',fh='lat.png',az=-90)
    amp.genIm(mag=1,out='fh',fh='ant.png')

    #calculations at %length intervals of 10%
    L = maxZ - ((amp.vert[:,axis]).max()-zval)-10
    pL = np.linspace(0,1.2,13)
    slices2 = []
    for i in pL:
        slices2.append((amp.vert[:,axis]).min()+10+(i*L))
    # uses create_slices
    polys = create_slices(amp, slices2, axis=axis)

    PolyArea = calc_csa(polys)
    MLWidth, APWidth = calc_widths(polys)

    # Plot the figure 
    fig = plt.figure()
    fig.set_size_inches(7.5, 4.5)
    ax = fig.add_subplot(221)
    ax.plot(pL*100, PolyArea)
    ax.set_xlabel("% length")
    ax.set_ylabel("Area (cm^2)")
    ax2 = fig.add_subplot(222)
    ax2.plot(pL*100, MLWidth, 'ro',label='Medial-Lateral')
    ax2.plot(pL*100, APWidth, 'b.',label='Anterior-Posterior')
    ax2.set_xlabel("% length")
    ax2.set_ylabel("width (cm)")
    ax2.legend()
    fig.savefig("figure.png")
    return getPDF(lngth, perimeter, PolyArea, APWidth, MLWidth)  # PDF Creation function (in output.py)
    # Divided by 10 to convert to cms, assumes stl files are in mm
    # TODO: Some sort of metric conversion function?


def CMapOut(amp, colors):
    """
    Colour Map with 4 views (copied Josh's code)
    """
    titles = ['Anterior', 'Medial', 'Proximal', 'Lateral']
    fig,axes = plt.subplots(ncols=5)
    cmap = clr.ListedColormap(colors, name='Amp')
    norm = clr.Normalize(vmin=-10,vmax=10)
    cb1 = clb.ColorbarBase(axes[-1], cmap=cmap,norm=norm)
    cb1.set_label('Shape deviation / mm')
    for i, ax in enumerate(axes[:-1]):
        im = amp.genIm(size=[3200, 8000],crop=True, az = i*90)[0]
        ax.imshow(im)
        ax.set_title(titles[i])
        ax.set_axis_off()
    #plt.colorbar(CMap)
    fig.set_size_inches([12.5, 4])
    plt.savefig("Limb Views.png", dpi=600)

