# AmpScan

## Getting Started

Would be nice to have a "Hello AmpScan" type function described here.

## Building Docs Locally

The documentation was generated using [Sphinx](http://www.sphinx-doc.org/en/master/index.html) which provides 
a [makefile](../docs/Makefile). This enables documentation to be generated with a single command (`make html`). Makefile should not 
be altered.

1. Clone the repository onto your local machine.
2. Open a command prompt (anaconda) in the docs directory.
3. Type `make html` and press enter.

The documentation files will be generated in docs/_build/html. Note that one error should be produced during 
the make process - this is expected and can be ignored.

## How to acknowledge

Alex Dickinson, Alex Steer: Find license [here](../LICENSE)

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
