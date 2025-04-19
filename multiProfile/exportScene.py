# trace generated using paraview version 5.13.0
#import paraview
#paraview.compatibility.major = 5
#paraview.compatibility.minor = 13

#### import the simple module from the paraview
from paraview.simple import *
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

import sys
step = int(sys.argv[-1])

# create a new 'Open FOAM Reader'
paraviewfoam = OpenFOAMReader(registrationName='paraview.foam', FileName='/home/jony/dafoamCases/multiProfile/iter'+str(step)+'/paraview.foam')

# get animation scene
animationScene1 = GetAnimationScene()

# update animation scene based on data timesteps
animationScene1.UpdateAnimationUsingDataTimeSteps()

# get active view
renderView1 = GetActiveViewOrCreate('RenderView')

# show data in view
paraviewfoamDisplay = Show(paraviewfoam, renderView1, 'UnstructuredGridRepresentation')

# trace defaults for the display properties.
paraviewfoamDisplay.Representation = 'Surface'

# reset view to fit data
renderView1.ResetCamera(False, 0.9)

# get the material library
materialLibrary1 = GetMaterialLibrary()

# show color bar/color legend
paraviewfoamDisplay.SetScalarBarVisibility(renderView1, True)

# update the view to ensure updated data information
renderView1.Update()

# get color transfer function/color map for 'p'
pLUT = GetColorTransferFunction('p')

# get opacity transfer function/opacity map for 'p'
pPWF = GetOpacityTransferFunction('p')

# get 2D transfer function for 'p'
pTF2D = GetTransferFunction2D('p')

# set scalar coloring
ColorBy(paraviewfoamDisplay, ('CELLS', 'U', 'Magnitude'))

# Hide the scalar bar for this color map if no visible data is colored by it.
HideScalarBarIfNotNeeded(pLUT, renderView1)

# rescale color and/or opacity maps used to include current data range
paraviewfoamDisplay.RescaleTransferFunctionToDataRange(True, False)

# show color bar/color legend
paraviewfoamDisplay.SetScalarBarVisibility(renderView1, True)

# get color transfer function/color map for 'U'
uLUT = GetColorTransferFunction('U')

# get opacity transfer function/opacity map for 'U'
uPWF = GetOpacityTransferFunction('U')

# get 2D transfer function for 'U'
uTF2D = GetTransferFunction2D('U')

# set scalar coloring
ColorBy(paraviewfoamDisplay, ('POINTS', 'U', 'Magnitude'))

# Hide the scalar bar for this color map if no visible data is colored by it.
HideScalarBarIfNotNeeded(uLUT, renderView1)

# rescale color and/or opacity maps used to include current data range
paraviewfoamDisplay.RescaleTransferFunctionToDataRange(True, False)

# show color bar/color legend
paraviewfoamDisplay.SetScalarBarVisibility(renderView1, True)

#change interaction mode for render view
renderView1.InteractionMode = '2D'

# Rescale transfer function
uLUT.RescaleTransferFunction(0.0, 12.0)

# Rescale transfer function
uPWF.RescaleTransferFunction(0.0, 12.0)

# Rescale 2D transfer function
uTF2D.RescaleTransferFunction(0.0, 12.0, 0.0, 1.0)

# get layout
layout1 = GetLayout()

# layout/tab size in pixels
layout1.SetSize(1410, 543)

# current camera placement for renderView1
renderView1.InteractionMode = '2D'
renderView1.CameraPosition = [1.2533333550908676, -0.18190950273424622, 3.586671592182968]
renderView1.CameraFocalPoint = [1.2533333550908676, -0.18190950273424622, -54.5237374988029]
renderView1.CameraParallelScale = 0.7619374573295581

# save screenshot
SaveScreenshot(filename='results/iteration'+str(step)+'.png', viewOrLayout=renderView1, location=16, ImageResolution=[1280, 720])

#================================================================
# addendum: following script captures some of the application
# state to faithfully reproduce the visualization during playback
#================================================================

#--------------------------------
# saving layout sizes for layouts

# layout/tab size in pixels
layout1.SetSize(1280,720)

#-----------------------------------
# saving camera placements for views

# current camera placement for renderView1
renderView1.InteractionMode = '2D'
renderView1.CameraPosition = [1.2533333550908676, -0.18190950273424622, 3.586671592182968]
renderView1.CameraFocalPoint = [1.2533333550908676, -0.18190950273424622, -54.5237374988029]
renderView1.CameraParallelScale = 0.7619374573295581


##--------------------------------------------
## You may need to add some code at the end of this python script depending on your usage, eg:
#
## Render all views to see them appears
# RenderAllViews()
#
## Interact with the view, usefull when running from pvpython
# Interact()
#
## Save a screenshot of the active view
#SaveScreenshot("results/iter0.png")
#
## Save a screenshot of a layout (multiple splitted view)
# SaveScreenshot("path/to/screenshot.png", GetLayout())
#
## Save all "Extractors" from the pipeline browser
# SaveExtracts()
#
## Save a animation of the current active view
# SaveAnimation()
#
## Please refer to the documentation of paraview.simple
## https://www.paraview.org/paraview-docs/latest/python/paraview.simple.html
##--------------------------------------------
