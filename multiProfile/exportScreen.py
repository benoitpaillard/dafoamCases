# trace generated using paraview version 5.13.0
#import paraview
#paraview.compatibility.major = 5
#paraview.compatibility.minor = 13

#### import the simple module from the paraview
from paraview.simple import *
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

# create a new 'Open FOAM Reader'
paraviewfoam = OpenFOAMReader(registrationName='paraview.foam', FileName='paraview.foam')

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

# update the view to ensure updated data information
renderView1.Update()

#change interaction mode for render view
renderView1.InteractionMode = '2D'

# Properties modified on paraviewfoam
paraviewfoam.CaseType = 'Decomposed Case'

# get animation scene
animationScene1 = GetAnimationScene()

# update animation scene based on data timesteps
animationScene1.UpdateAnimationUsingDataTimeSteps()

# set scalar coloring
ColorBy(paraviewfoamDisplay, ('CELLS', 'U', 'Magnitude'))

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

animationScene1.GoToLast()

animationScene1.GoToPrevious()

# get layout
layout1 = GetLayout()

# layout/tab size in pixels
layout1.SetSize(1373, 779)

# current camera placement for renderView1
renderView1.InteractionMode = '2D'
renderView1.CameraPosition = [0.679265022277832, 0.0, 100.1350939270431]
renderView1.CameraFocalPoint = [0.679265022277832, 0.0, 0.05000000074505806]
renderView1.CameraParallelScale = 0.7041256638924053

# save screenshot
SaveScreenshot(filename='output.png', viewOrLayout=renderView1, location=16, ImageResolution=[1373, 779])

#================================================================
# addendum: following script captures some of the application
# state to faithfully reproduce the visualization during playback
#================================================================

#--------------------------------
# saving layout sizes for layouts

# layout/tab size in pixels
layout1.SetSize(1373, 779)

#-----------------------------------
# saving camera placements for views

# current camera placement for renderView1
renderView1.InteractionMode = '2D'
renderView1.CameraPosition = [0.679265022277832, 0.0, 100.1350939270431]
renderView1.CameraFocalPoint = [0.679265022277832, 0.0, 0.05000000074505806]
renderView1.CameraParallelScale = 0.7041256638924053


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
# SaveScreenshot("path/to/screenshot.png")
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
