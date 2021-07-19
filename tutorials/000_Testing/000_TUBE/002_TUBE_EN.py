#---UnitCalculator to use different input units---
from external.UnitCalculator import *
auto_converter(mmNS)

Material("S4306")  #Check the material library or autodoc for a complete list of available material properties.

#Sets the temperature of the vector objects. T_ref denotes the temperature at which thermal dilatation is supposed to be 0.


#Set the internal pressure of the piping. The unit bar() is a function from UnitCalculator which translates bar to N/mm2
#These unit functions can only be used if the UnitCalculator module is imported(first lines)
Pressure(2*bar())

#---------------------------------

Code("ASME B31.3")

Temperature(150,T_ref=20)
Pressure(2*bar())
SectionTube(30,3)

P(x=0,y=0,z=0,name="a") 										#equivalent to P(0,0,0,"a)
FixPoint()     													#equivalent to Block(x=0,y=0,z=0,rx=0,ry=0,rz=0)
V(2*m(),0,0)

Temperature(250,T_ref=20)
Pressure(3*bar())
SectionTube(40,4)

V_Reducer(90)
V(1*m(),0,0)
Bent(radius=250,angle_deg=90,orientation=90,mode="add")
Vc(length=500)

Temperature(100,T_ref=20)
Pressure(1*bar())
SectionTube(30,3)

V_Reducer(90)
Vc(length=500)
FixPoint()     													#equivalent to Block(x=0,y=0,z=0,rx=0,ry=0,rz=0)


Code("EN13480-3") # Flexibility stress will be based on current code: not supposed to be mixed

Temperature(150,T_ref=20)
Pressure(2*bar())
SectionTube(30,3)

P(x=0,y=1*m(),z=0,name="b")
FixPoint()
V(2*m(),0,0)

Temperature(250,T_ref=20)
Pressure(3*bar())
SectionTube(40,4)

V_Reducer(90)
V(1*m(),0,0)
Bent(radius=250,angle_deg=90,orientation=90,mode="add")
Vc(length=500)

Temperature(100,T_ref=20)
Pressure(1*bar())
SectionTube(30,3)

V_Reducer(90)
Vc(length=500)
FixPoint()


