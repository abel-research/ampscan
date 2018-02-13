AmpScan ReadME File 
--------------------

Author: Joshua Steer 

To install the package, open the cmd prompt and type the following script

J:
cd J:\Shared Resources\AmpScan IfLS Team\100 PYTHON\Code
pip install .

To use the package 

	import AmpScan
	import os
	
	read_filename = '01_PhantomShell_ICEM_3mm.stl'
	write_filename = '01_PhantomShell_ICEM_3mm_write.stl'

    Data = AmpObject(target, 'limb')
    Data.addData(baseline, 'socket')
    Data.lp_smooth()
    Data.man_rot([5,5,5])
    Reg = regObject(Data)
    Reg.registration(steps=5, baseline='socket', target='limb', reg = 'reglimb')
    Reg.save(saveStr, stype='reglimb')
    Reg.plot_slices()
    


Structure:

AmpScan structure

core.py
	class AmpObject(Data, stype)
		func addData
		func read_stl
		func unify_vertices
		func computeEdges
		func save
		func calc_norm
		func man_trans
		func man_rot
		func centre
smooth.py
	class smoothMixin
		func lp_smooth
autoAlign.py
	class alignMixin
		func icp
		func calcDistError
trim.py
	class trimMixin
		func planarTrim
analyse.py
	class analyseMixin
		func plot_slices
		func create_slice
		func planeEdgeIntersect
ampVis.py
	class visMixin
		func genIm
		func addActor
		class ampActor
			func setVert
			func setFaces
			func setRect
			func setColor
			func setOpacity
			func setCMap
	class vtkRender
	class vtkWindow
		func render
		func setScalarBar
		func setViewports
		func addAxes
registration.py
	class regObject
		func registration
TSBSocketDesign.py
	class mplCanvas
	class dragSpline
		func connect
		func on_press
		func on_motion
		func on_release
		func disconnect
		func bezierCurve
SocketDesignGUI.py
	class GUI
		func plotRect
		func chooseOpenFile
		func createActions
		func createMenus
AmpScanGUI
	class GUI
		func chooseOpenFile
		func chooseSocket
		func align
		func register
		func analyse
		func createActions
		func createMenus
