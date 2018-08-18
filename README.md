AmpScan
=======

AmpScan is a Python package that provides matrix manipulation tools specifically for 
the design of prosthetic sockets. It provides functions for handling common design workflows 
such as importing, aligning and registering meshes. AmpScan relies heavily on `NumPy`_ and 
`SciPy`_ to perform mathematical operations with vizualisation handled by `PyQt`_ and `VTK`_. 
The package is still under active development by researchers at the University of Southampton 
- this documentation should be considered the 'go-to' for anyone interested in using or 
developing AmpScan.

.. _numpy: http://www.numpy.org/
.. _SciPy: https://www.scipy.org/
.. _PyQt: https://riverbankcomputing.com/software/pyqt/intro
.. _VTK: https://www.vtk.org/


Installation
------------

For the most up to date version of AmpScan, clone directly from the gitlab repository using:

``git clone https://git.soton.ac.uk/js22g12/AmpScan.git``

A pip installation is also available through test PyPI using:

``$ pip install --index-url https://test.pypi.org/simple/ AmpScan``


## How to acknowledge

Find license [here](../LICENSE)

## Structure

    AmpObject
    	data
    		faces
    		vert
    		norms
    		edges
    		faceEdges
    		edgeFaces
    		vNorms
    		values
    		stype
    		name
    		actor
    		# New structure means no deep copy needed?
    			data
    				mesh
    				points
    				polys
    				mapper
    				cmap
    			methods
    				setVert
    				setFaces
    				setNorm
    				setValues
    				setColour
    				setOpacity
    				setCMap
    				setCRange
    				setShading
    				display
    				getIm
    				saveScreenshot
    	methods
    		importSTL(fh)
    		importFE(FE)
    		importPressSensor(pressureSensor)
    		unifyVert()
    		computeEdges()
    		calcNorm()
    		transform(T)
    		translate(tx, ty, tz)
    		rotate(rx, ry, rz)
    		centre()
    		smooth(method)
    		analyse()
    		trim(method)
    		genActor()
    		getData() #Pulls all data as dictionary - send to MATLAB
    Alignment
    	ICP
    	P2P
    Registration
    	registration
    ampVis
    	vtkWin
    		data
    			actors
    			renders
    			cams
    			style
    			axes
    			scalarBar
    		methods
    			setActors([])
    			setRender()
    			setView()
    			setBackground()
    			setScalarBar()
    			setAxes()
    			setViewports()
    	qtvtkWin	
    Analysis #Routines for analysis 
    	compareScans
    AmpScanGUI
    	data
    		vtkWidget
    		vtkRW
    		ampObjects
    	methods
    	
## Example

```python
import AmpScan as amps
import AmpScan.align as aa
import AmpScan.registration as ar

baseline = amps.AmpObj(fname1, stype='limb')
target = amps.AmpObj(fname2, stype='socket')
aligned = amps.align(baseline, target, method='ICP')
register = amps.register(baseline, aligned, method='')
feResult = amps.AmpObj(fname3, stype='FE')
```
