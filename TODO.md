--------------------------------------------------------------------------------------------
Geometry:
-Reducer
--done--  Include/Correct local/global coordinate frame
-Change V1x,V2x to locol coordinat system
--------------------------------------------------------------------------------------------
-Bent between two vectors (no bending radius as input - also in TUBA old)
--------------------------------------------------------------------------------------------
Properties:
--done--  Include SIF as input and as property of bents (ASME 31.3)
-Windload

--------------------------------------------------------------------------------------------
-Cables
--------------------------------------------------------------------------------------------
Simulation:
-Include functionality of friction (multiple simulation to match deflection and friction forces)
-done- needs to be tested
--------------------------------------------------------------------------------------------
Postprocessing:
-better structuring while creating the parapost-file - done -- needs to be extended
--------------------------------------------------------------------------------------------
-Design a standarized txt-Output for Piping-Calculation
--------------------------------------------------------------------------------------------
Translate from old TUBA:
-Seismic Calculation

--------------------------------------------------------------------------------------------
General:

-Correct the Aster_Base_File so that visualization in EFICAS is as well possible
   --Change: included structelem in a developpermode

--done--  -Run CodeAster directly with popen()

-- create a TUBA manager
--------------------------------------------------------------------------------------------

Check if it is possible to make TUBA a SalomePlugin
/salome_meca/appli_V2016/share/salome/plugins/gui/demo/
--------------------------------------------------------------------------------------------
More Tutorials:
TJoint
creating support structure (bridge)
Lyre
--------------------------------------------------------------------------------------------

--------------------------------------------------------------------------------------------
Ideas in no particular order
- Include longitudinal stress from pressure for Tube sections
- Compare computed stress with allowable stress, results in %
- Reorganize salome geometry for easier visualisation (e.g. constraints are hidden into points)
- Add commands to tag pipes sections to be added to compounds, helps visualizing & debugging
- Propagate geometry groups to paraview results for filtering
- Modify salome geometry script to speed up mesh generation (geometry compound, then mesh)
- ISO and Schedule pipe sizes tables
- Commands to modify solver parameters (RESI_RELA, NPREC)
- Commands to modify characteristic length (use curvature refinement?)
- Command for tee generation with SIFs
- Make RhoFluid / Insulation do something (looks like it's not used)
- More robust tubapoint search by name (why not using the dictionary instead of list comprehension?)
- Issue an error or warning when a point name is defined twice
- Force / stress table output by point name, not by node name (or best, by point of interest)
- Using vector direction to create nicer boxes at fixed points
- ASME B31.3 material properties