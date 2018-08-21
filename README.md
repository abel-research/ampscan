AmpScan
=======

AmpScan is a Python package that provides matrix manipulation tools specifically for 
the design of prosthetic sockets. It provides functions for handling common design workflows 
such as importing, aligning and registering meshes. AmpScan relies heavily on [NumPy](http://www.numpy.org/) 
and [SciPy](https://www.scipy.org/) to perform mathematical operations with vizualisation handled by 
[PyQt](https://riverbankcomputing.com/software/pyqt/intro) and [VTK](https://www.vtk.org/). The package is 
still under development by researchers at the University of Southampton.

Installation
------------

AmpScan has a number of dependencies, we recommend using conda to deal with these. To create a new 
environment to run AmpScan in:  

``conda create -n env_name python=3 numpy scipy pyqt matplotlib``

``conda install -c conda-forge vtk=8.1.0``

For the most up to date version of AmpScan, clone directly from the gitlab repository into a virtual environment using:

``git clone https://git.soton.ac.uk/js22g12/AmpScan.git``

Navigate to the `AmpScan/` directory and run a pip install using:

``pip install -e .``

A pip installation is also available through test PyPI (not latest version) using:

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
