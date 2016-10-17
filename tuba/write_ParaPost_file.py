#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""

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
        Flag_3D=False
        Flag_TUYAU=False
        
        for tubavector in dict_tubavectors:
            if tubavector.model=="3D":
                Flag_3D=True
            if tubavector.model=="TUYAU":
                Flag_TUYAU=True
                
        #Point Functions
        if Flag_3D:        
            self._base3D(dict_tubapoints)
            self._ELNO_Mesh_3D()
        else:
            self._base(dict_tubapoints)
            
        self._deformation_Warp()

        if Flag_TUYAU:
            self._ELNO_Mesh_TUYAU(Flag_3D)
        self._deformation_Vector()
        self._force_Vector()

                
       # self._visualize_ddl(dict_tubapoints) 
        
        
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
                                    initialdir='"""+self.my_directory+ """',
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
       
    def _base3D(self,dict_tubapoints):       
        self.lines=self.lines+("""
        
# ======== Select a file for opening:
import Tkinter,tkFileDialog

root = Tkinter.Tk()
file = tkFileDialog.askopenfilename(parent=root,
                                    initialdir='"""+self.my_directory+ """',
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
new_casermed_2 = MEDReader(FileName=file)


# Properties modified on new_casermed
new_casermed.AllArrays = ['TS1/MAIL/ComSup1/RESU____DEPL@@][@@P1', 
                          'TS1/MAIL/ComSup1/RESU____FORC_NODA@@][@@P1', 
                          'TS1/MAIL/ComSup1/RESU____REAC_NODA@@][@@P1', 
                          'TS1/MAIL/ComSup1/RESU____SIEF_ELGA@@][@@GAUSS', 
                          'TS1/MAIL/ComSup1/RESU____SIEQ_ELNO@@][@@GSSNE',
                          ]        
new_casermed_2.AllArrays =['TS1/MAIL/ComSup0/MAX_VMISUT01_ELNO@@][@@GSSNE']

renderView1 = GetActiveViewOrCreate('RenderView')
# show data in view
new_casermedDisplay = Show(new_casermed, renderView1)





        
# Properties modified on new_casermed
new_casermed.GenerateVectors = 1        
       """).split("\n")



       
    def _deformation_Warp(self): 
        self.lines=self.lines+("""
# set active source
SetActiveSource(new_casermed)

# create a new 'Warp By Vector'
warpByVector1 = WarpByVector(Input=new_casermed)

# show data in view
warpByVector1Display = Show(warpByVector1, renderView1)

# Properties modified on warpByVector1Display
warpByVector1Display.LineWidth = 4.0

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
# get color legend/bar for rESUDEPLPWF in view renderView1
rESUDEPLPWFColorBar = GetScalarBar(rESUDEPLPWF, renderView1)
# Properties modified on rESUDEPLPWFColorBar
rESUDEPLPWFColorBar.Title = 'Deformation'
# Properties modified on rESUDEPLPWFColorBar
rESUDEPLPWFColorBar.ComponentTitle = 'Magnitude (mm)'

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

# Properties modified on glyph1
glyph1.ScaleMode = 'vector'

# Properties modified on glyph1
glyph1.ScaleFactor = 1.0

# set scalar coloring
ColorBy(glyph1Display, ('POINTS', 'RESU____DEPL'))

# show color bar/color legend
glyph1Display.SetScalarBarVisibility(renderView1, True)


# rename source object
RenameSource('Deformation_Arrows', glyph1)

# get color legend/bar for rESUDEPLLUT in view renderView1
rESUDEPLLUTColorBar = GetScalarBar(rESUDEPLLUT, renderView1)
# Properties modified on rESUDEPLLUTColorBar
rESUDEPLLUTColorBar.Title = 'Deformation'
# Properties modified on rESUDEPLLUTColorBar
rESUDEPLLUTColorBar.ComponentTitle = 'Magnitude (mm)'

      """).split("\n")





    def _ELNO_Mesh_TUYAU(self,Flag_3D): 
        
        if Flag_3D:
            case="new_casermed_2"
        else:
            case="new_casermed"
            
        self.lines=self.lines+("""      
# create a new 'ELNO Mesh'        
eLNOMesh1 = ELNOMesh(Input="""+case+""")
       """).split("\n")
       
        
        self.lines=self.lines+("""
       
# create a new 'ELNO Mesh'
# show data in view
eLNOMesh1Display = Show(eLNOMesh1, renderView1)

# set scalar coloring
ColorBy(eLNOMesh1Display, ('POINTS', 'MAX_VMISUT01_ELNO'))
# rescale color and/or opacity maps used to include current data range
eLNOMesh1Display.RescaleTransferFunctionToDataRange(True)
# show color bar/color legend
eLNOMesh1Display.SetScalarBarVisibility(renderView1, True)
# Properties modified on warpByVector1Display
eLNOMesh1Display.LineWidth = 4.0


# get color transfer function/color map for 'MAXVMISUT01ELNO'
mAXVMISUT01ELNOLUT = GetColorTransferFunction('MAXVMISUT01ELNO')
# get opacity transfer function/opacity map for 'MAXVMISUT01ELNO'
mAXVMISUT01ELNOPWF = GetOpacityTransferFunction('MAXVMISUT01ELNO')


mAXVMISUT01ELNOLUT.VectorMode = 'Component'
# rescale color and/or opacity maps used to exactly fit the current data range
eLNOMesh1Display.RescaleTransferFunctionToDataRange(False)

RenameSource('VMIS_Stress_MAX', eLNOMesh1)  

# get color legend/bar for mAXVMISUT01ELNOLUT in view renderView1
mAXVMISUT01ELNOLUTColorBar = GetScalarBar(mAXVMISUT01ELNOLUT, renderView1)
# Properties modified on mAXVMISUT01ELNOLUTColorBar
mAXVMISUT01ELNOLUTColorBar.Title = 'VonMise Stress Max over Crosssection'
# Properties modified on mAXVMISUT01ELNOLUTColorBar
mAXVMISUT01ELNOLUTColorBar.ComponentTitle = 'Magnitude (MPa)'   
     """).split("\n")



    def _ELNO_Mesh_3D(self):

        self.lines=self.lines+("""


# create a new 'ELNO Mesh'
eLNOMesh1_2 = ELNOMesh(Input=new_casermed)

# show data in view
eLNOMesh1_2Display = Show(eLNOMesh1_2, renderView1)


# set scalar coloring
ColorBy(eLNOMesh1_2Display, ('POINTS', 'RESU____SIEQ_ELNO'))

# rescale color and/or opacity maps used to include current data range
eLNOMesh1_2Display.RescaleTransferFunctionToDataRange(True)

# show color bar/color legend
eLNOMesh1_2Display.SetScalarBarVisibility(renderView1, True)

# get color transfer function/color map for 'RESUSIEQELNO'
rESUSIEQELNOLUT = GetColorTransferFunction('RESUSIEQELNO')

# get opacity transfer function/opacity map for 'RESUSIEQELNO'
rESUSIEQELNOPWF = GetOpacityTransferFunction('RESUSIEQELNO')

#change array component used for coloring
rESUSIEQELNOLUT.VectorComponent = 0
rESUSIEQELNOLUT.VectorMode = 'Component'




RenameSource('VMIS_Stress_3D', eLNOMesh1_2) 

rESUSIEQELNOLUTColorBar = GetScalarBar(rESUSIEQELNOLUT, renderView1)
# Properties modified on rESUSIEQELNOLUTColorBar
rESUSIEQELNOLUTColorBar.Title = 'VonMise Stress'
# Properties modified on rESUSIEQELNOLUTColorBar
rESUSIEQELNOLUTColorBar.ComponentTitle = 'Magnitude (MPa)' 

# rescale color and/or opacity maps used to exactly fit the current data range
eLNOMesh1_2Display.RescaleTransferFunctionToDataRange(False)
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
glyph1_1Display.SelectInputVectors = ['POINTS', 'GlyphVector']

# set scalar coloring
ColorBy(glyph1_1Display, ('POINTS', 'RESU____FORC_NODA'))

# rescale color and/or opacity maps used to include current data range
glyph1_1Display.RescaleTransferFunctionToDataRange(True)

# show color bar/color legend
glyph1_1Display.SetScalarBarVisibility(renderView1, True)

# set active source
SetActiveSource(glyph1)

# show data in view
glyph1Display = Show(glyph1, renderView1)

# show color bar/color legend
glyph1Display.SetScalarBarVisibility(renderView1, True)

# set active source
SetActiveSource(glyph1)

# rename source object
RenameSource('Reaction_Forces', glyph1_1)

# get color transfer function/color map for 'RESUFORCNODA'
rESUFORCNODALUT = GetColorTransferFunction('RESUFORCNODA')

# get opacity transfer function/opacity map for 'RESUFORCNODA'
rESUFORCNODAPWF = GetOpacityTransferFunction('RESUFORCNODA')


# get color legend/bar for mAXVMISUT01ELNOPWF in view renderView1
rESUFORCNODALUTColorBar = GetScalarBar(rESUFORCNODALUT, renderView1)
# Properties modified on rESUFORCNODALUTColorBar
rESUFORCNODALUTColorBar.Title = 'Forces'
# Properties modified on rESUFORCNODALUTColorBar
rESUFORCNODALUTColorBar.ComponentTitle ='Magnitude (N)'



     """).split("\n")

      
    def _finalize(self): 
        self.lines=self.lines+(""" 

try:
    # create a new 'Legacy VTK Reader'
    legacyVTKReader1 = LegacyVTKReader(FileNames=['/"""+self.my_directory+"""/compound_paravis.vtk'])

    # set active source
    SetActiveSource(legacyVTKReader1)

    # show data in view
    legacyVTKReader1Display = Show(legacyVTKReader1, renderView1)

    # Properties modified on legacyVTKReader1Display
    legacyVTKReader1Display.Opacity = 0.2       
except:
    print("GEOM compound couldn't be loaded")

        
if salome.sg.hasDesktop():
  salome.sg.updateObjBrowser(1)
      """).split("\n")      
      
   
    def _visualize_ddl(self,dict_tubapoints):
        '''perhaps obsolete function'''

        for tubapoint in dict_tubapoints:
            
            if not tubapoint.ddl[0]=="x":     #x


                self.lines=self.lines+("""                
# create a new 'Cone'
"""+tubapoint.name+"""_x = Cone()
RenameSource('"""+tubapoint.name+"""_x', """+tubapoint.name+"""_x)
"""+tubapoint.name+"""_x.Direction = [1.0, 0.0, 0.0]
"""+tubapoint.name+"""_x.Height = 300.0
"""+tubapoint.name+"""_x.Resolution = 100
"""+tubapoint.name+"""_x.Radius = 100.0
"""+tubapoint.name+"""_x.Center = ["""+str(tubapoint.pos.x)+""","""+str(tubapoint.pos.y)+""","""+str(tubapoint.pos.z)+"""]

SetActiveSource("""+tubapoint.name+"""_x)
"""+tubapoint.name+"""_x_Display = Show("""+tubapoint.name+"""_x, renderView1)

                """).split("\n")
                
                
            if not tubapoint.ddl[1]=="x":     #y
 
                self.lines=self.lines+("""                
# create a new 'Cone'
"""+tubapoint.name+"""_y = Cone()
RenameSource('"""+tubapoint.name+"""_y', """+tubapoint.name+"""_y)
"""+tubapoint.name+"""_y.Direction = [1.0, 0.0, 0.0]
"""+tubapoint.name+"""_y.Height = 300.0
"""+tubapoint.name+"""_y.Resolution = 100
"""+tubapoint.name+"""_y.Radius = 100.0
"""+tubapoint.name+"""_y.Center = ["""+str(tubapoint.pos.x)+""","""+str(tubapoint.pos.y)+""","""+str(tubapoint.pos.z)+"""]

SetActiveSource("""+tubapoint.name+"""_y)
"""+tubapoint.name+"""_y_Display = Show("""+tubapoint.name+"""_y, renderView1)
                """).split("\n")
       
            if not tubapoint.ddl[2]=="x":     #z
            
                self.lines=self.lines+("""                
# create a new 'Cone'
"""+tubapoint.name+"""_z = Cone()
RenameSource('"""+tubapoint.name+"""_z', """+tubapoint.name+"""_z)
"""+tubapoint.name+"""_z.Direction = [0.0, 0.0, 1.0]
"""+tubapoint.name+"""_z.Height = 300.0
"""+tubapoint.name+"""_z.Resolution = 100
"""+tubapoint.name+"""_z.Radius = 100.0
"""+tubapoint.name+"""_z.Center = ["""+str(tubapoint.pos.x)+""","""+str(tubapoint.pos.y)+""","""+str(tubapoint.pos.z)+"""]
SetActiveSource("""+tubapoint.name+"""_z)
"""+tubapoint.name+"""_z_Display = Show("""+tubapoint.name+"""_z, renderView1)
                """).split("\n")            
            
            
            
    
