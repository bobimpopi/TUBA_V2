#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 02:34:03 2016

@author: frenell
"""
import collections
import numpy as np
import external.euclid as eu
import logging

import tuba_vars_and_funcs as tub
import tuba.define_geometry as tuba_geom


class ParaPost:
    def __init__(self,my_directory):
        self.my_directory=my_directory
        self.lines=[]


    def write(self,dict_tubavectors,dict_tubapoints):

        #Point Functions
        self._base(dict_tubapoints) 
        self._deformation_Warp()
        self._ELNO_Mesh()
        self._deformation_Vector()
        self._force_Vector()
        self._finalize()

               
#==============================================================================
#  Write PostBase
#==============================================================================
    def _base(self,dict_tubapoints):
        self.lines=self.lines+("""
        
# ======== Select a file for opening:
import Tkinter,tkFileDialog

root = Tkinter.Tk()
file = tkFileDialog.askopenfilename(parent=root,
                                    initialdir=" """+self.my_directory+ """ ",
                                    filetypes=[("Result Files","*.rmed")])        
              
root.destroy()
        
import pvsimple
pvsimple.ShowParaviewView()
#### import the simple module from the paraview
from pvsimple import *
#### disable automatic camera reset on 'Show'
pvsimple._DisableFirstRenderCameraReset()
        
# create a new 'MED Reader'
new_casermed = MEDReader(FileName=file)

# Properties modified on new_casermed
new_casermed.AllArrays = ['TS1/MAIL/ComSup0/MAX_VMISUT01_ELNO@@][@@GSSNE', 
                          'TS1/MAIL/ComSup0/RESU____DEPL@@][@@P1', 
                          'TS1/MAIL/ComSup0/RESU____FORC_NODA@@][@@P1', 
                          'TS1/MAIL/ComSup0/RESU____REAC_NODA@@][@@P1', 
                          'TS1/MAIL/ComSup0/RESU____SIEF_ELGA@@][@@GAUSS', 
                          'TS1/MAIL/ComSup0/RESU____SIEQ_ELNO@@][@@GSSNE']        

renderView1 = GetActiveViewOrCreate('RenderView')
        
# Properties modified on new_casermed
new_casermed.GenerateVectors = 1        
       """).split("\n")
       
       
    def _deformation_Warp(self): 
        self.lines=self.lines+("""

# create a new 'Warp By Vector'
warpByVector1 = WarpByVector(Input=new_casermed)
# show data in view
warpByVector1Display = Show(warpByVector1, renderView1)
# hide data in view
Hide(new_casermed, renderView1)
# set scalar coloring
ColorBy(warpByVector1Display, ('POINTS', 'RESU____DEPL'))
# rescale color and/or opacity maps used to include current data range
warpByVector1Display.RescaleTransferFunctionToDataRange(True)
# show color bar/color legend
warpByVector1Display.SetScalarBarVisibility(renderView1, True)
# get color transfer function/color map for 'RESUDEPL'
rESUDEPLLUT = GetColorTransferFunction('RESUDEPL')
# get opacity transfer function/opacity map for 'RESUDEPL'
rESUDEPLPWF = GetOpacityTransferFunction('RESUDEPL')

RenameSource('DeformedShape', warpByVector1)
      """).split("\n")
       
    def _deformation_Vector(self): 
        self.lines=self.lines+("""

# set active source
SetActiveSource(new_casermed)

# create a new 'Glyph'
glyph1 = Glyph(Input=new_casermed,
    GlyphType='Arrow')

# Properties modified on glyph1
glyph1.Vectors = ['POINTS', 'RESU____DEPL_Vector']
glyph1.GlyphMode = 'All Points'

# show data in view
glyph1Display = Show(glyph1, renderView1)

# show color bar/color legend
glyph1Display.SetScalarBarVisibility(renderView1, True)

# get color transfer function/color map for 'FamilyIdNode'
familyIdNodeLUT = GetColorTransferFunction('FamilyIdNode')

# get opacity transfer function/opacity map for 'FamilyIdNode'
familyIdNodePWF = GetOpacityTransferFunction('FamilyIdNode')

# Properties modified on glyph1
glyph1.ScaleMode = 'vector'

# Properties modified on glyph1
glyph1.ScaleFactor = 1.0

# set scalar coloring
ColorBy(glyph1Display, ('POINTS', 'RESU____DEPL'))

# rescale color and/or opacity maps used to include current data range
glyph1Display.RescaleTransferFunctionToDataRange(True)

# show color bar/color legend
glyph1Display.SetScalarBarVisibility(renderView1, True)

# reset view to fit data
renderView1.ResetCamera()

# set active source
SetActiveSource(new_casermed)

# set active source
SetActiveSource(glyph1)

# rename source object
RenameSource('Deformation_Arrows', glyph1)
      """).split("\n")





    def _ELNO_Mesh(self): 
        self.lines=self.lines+("""
       
# create a new 'ELNO Mesh'
eLNOMesh1 = ELNOMesh(Input=new_casermed)
# show data in view
eLNOMesh1Display = Show(eLNOMesh1, renderView1)
# hide data in view
Hide(new_casermed, renderView1)
# set scalar coloring
ColorBy(eLNOMesh1Display, ('POINTS', 'MAX_VMISUT01_ELNO'))
# rescale color and/or opacity maps used to include current data range
eLNOMesh1Display.RescaleTransferFunctionToDataRange(True)
# show color bar/color legend
eLNOMesh1Display.SetScalarBarVisibility(renderView1, True)
# get color transfer function/color map for 'MAXVMISUT01ELNO'
mAXVMISUT01ELNOLUT = GetColorTransferFunction('MAXVMISUT01ELNO')
# get opacity transfer function/opacity map for 'MAXVMISUT01ELNO'
mAXVMISUT01ELNOPWF = GetOpacityTransferFunction('MAXVMISUT01ELNO')
#change array component used for coloring
mAXVMISUT01ELNOLUT.RGBPoints = [102.55225199846132, 0.231373, 0.298039, 0.752941, 3135.7733391499924, 0.865003, 0.865003, 0.865003, 6168.994426301523, 0.705882, 0.0156863, 0.14902]
mAXVMISUT01ELNOLUT.VectorMode = 'Component'
# Properties modified on mAXVMISUT01ELNOPWF
mAXVMISUT01ELNOPWF.Points = [102.55225199846132, 0.0, 0.5, 0.0, 6168.994426301523, 1.0, 0.5, 0.0]       

RenameSource('VMIS_Stress', eLNOMesh1)     
     """).split("\n")

    def _force_Vector(self): 
        self.lines=self.lines+("""
SetActiveSource(new_casermed)

# create a new 'Glyph'
glyph1_1 = Glyph(Input=new_casermed,
    GlyphType='Arrow')

# Properties modified on glyph1_1
glyph1_1.Scalars = ['POINTS', 'None']
glyph1_1.Vectors = ['POINTS', 'RESU____FORC_NODA_Vector']
glyph1_1.ScaleMode = 'vector'
glyph1_1.ScaleFactor = 0.0020176490811640107

# show data in view
glyph1_1Display = Show(glyph1_1, renderView1)

# Properties modified on glyph1_1
glyph1_1.GlyphMode = 'All Points'

# Properties modified on glyph1_1Display
glyph1_1Display.SelectUncertaintyArray = [None, 'FamilyIdNode']

# Properties modified on glyph1_1Display
glyph1_1Display.SelectInputVectors = ['POINTS', 'GlyphVector']

# set scalar coloring
ColorBy(glyph1_1Display, ('POINTS', 'RESU____FORC_NODA'))

# rescale color and/or opacity maps used to include current data range
glyph1_1Display.RescaleTransferFunctionToDataRange(True)

# show color bar/color legend
glyph1_1Display.SetScalarBarVisibility(renderView1, True)

# rename source object
RenameSource('Reaction_Forces', glyph1_1)

# hide data in view
Hide(glyph1, renderView1)

# set active source
SetActiveSource(glyph1)

# show data in view
glyph1Display = Show(glyph1, renderView1)

# show color bar/color legend
glyph1Display.SetScalarBarVisibility(renderView1, True)

# hide data in view
Hide(glyph1, renderView1)

# show data in view
glyph1Display = Show(glyph1, renderView1)

# show color bar/color legend
glyph1Display.SetScalarBarVisibility(renderView1, True)

# set active source
SetActiveSource(glyph1)
     """).split("\n")

      
    def _finalize(self): 
        self.lines=self.lines+("""      
if salome.sg.hasDesktop():
  salome.sg.updateObjBrowser(1)
      """).split("\n")      