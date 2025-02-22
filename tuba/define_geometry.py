"""
Created on Sun Mar 27 22:05:19 2016
"""
#import global_vars as glob
#from global_functions import *
import external.euclid as eu
import logging
import math
import readchar

import tuba.tuba_vars_and_funcs as tub

#==============================================================================
#==============================================================================
class TubaPoint:
    """Containes all information present at a POINT in the piping/rod network

    It is important to  note that each tubapoint inside a piping is always an
    attribute of two vectors, one time as start_tubapoint, one time as end_tubapoint.

    The only exception are start and endpoints of a piping system. For each point it is possibe 
    to check wether it is a element start or an end at the current time.
    """

    def __init__(self, x, y, z, name="", nocount=False):
        self.name = name
        self.pos = eu.Point3(x, y, z)              # Position of the Point
        self.ddl = ['x', 'x', 'x', 'x', 'x', 'x']  # Degree of Freedom/Deflection
        self.ddl_reference = "global"
        self.friction_coefficient=0.0
        self.stiffness = [0.0, 0.0, 0.0, 0.0,0.0, 0.0]  # Stiffness-Matrix of the Point
        self.stiffness_reference = "global"
        self.mass = 0.0                        # Discret Mass at the Point
        self.moment = []           # Sum of Moments applied at the Point
        self.force = []                      # List of Forces applied at the Point
        self.local_y=tub.local_y0          # Last noncolinear vector in the piping

        if self.is_element_start():
            self.local_x=tub.local_x0           # Direction of the following vector

        self.local_x.normalized()
        self.local_y.normalized()

        if nocount:
            pass
        else:
            tub.tubapoint_counter+=1
            tub.current_tubapoint=self
        logging.debug("Created Tubapoint: "+self.name)
        tub.dict_tubapoints.append(self)  #Write the object instance into the global point list
        tub.tubapoint_dict[self.name]=self
        
#------------------------------------------------------------------------------
    def is_element_start(self):
        '''checks if the given tubapoint is a start_tubapoint and as well end_tubapoint of a vector.
        If false, this means that it's the beginning of the piping'''

        same_names=[]
        for tubavector in tub.dict_tubavectors:
            if tubavector.__class__.__name__ == "TubaTShape3D":
                if tubavector.incident_end_tubapoint.name == self.name:
                    same_names.append(self.name)
            
            if tubavector.end_tubapoint.name == self.name:
                same_names.append(self.name)
        if same_names==[]:
            return True
        else:
            return False
#------------------------------------------------------------------------------
    def is_element_end(self):
        '''checks if the given tubapoint is a end_tubapoint and as well start_tubapoint of a vector.
        If false, this means that it's the end of the piping'''
        same_names=[tubavectors for tubavectors in tub.dict_tubavectors
                    if tubavectors.start_tubapoint.name == self.name]  #Points with the same name
        if same_names==[]:
            return True
        else:
            return False
#------------------------------------------------------------------------------
    def is_incident_end(self):
        '''checks if the given tubapoint is a icident_end_tubapoint and as well start_tubapoint of a vector.
        '''
        for tubavectors  in tub.dict_tubavectors:
            if tubavectors.__class__.__name__ == "TubaTShape3D":
                if tubavectors.incident_end_tubapoint.name == self.name:
                    return True
#------------------------------------------------------------------------------
    def get_last_vector(self):
        '''Finds the vector, where this tubapoint acts as an endpoint or
        incident_endpoint for TubaTShape3D'''

        for tubavector in tub.dict_tubavectors:
             if tubavector.end_tubapoint.name == self.name:
                 return tubavector
             if tubavector.__class__.__name__ == "TubaTShape3D":
                 if tubavector.incident_end_tubapoint.name == self.name:
                     return tubavector
#------------------------------------------------------------------------------
    def get_next_vector(self):
        '''Finds the vector, where this tubapoint acts as an endpoint'''

        for tubavector in tub.dict_tubavectors:
             if tubavector.start_tubapoint.name == self.name:
                 return tubavector
             
    def is_empty_point(self):
        """Checks if any ddls, stiffnesses, moments or forces are applied. If not
        the point is definded as empty. This function is needed to suppress empty start and endpoints
        for volume vectors and TJoints3D"""
        if (self.ddl == ['x', 'x', 'x', 'x', 'x', 'x'] and self.stiffness == [0.0, 0.0, 0.0, 0.0,0.0, 0.0]
            and self.mass == 0.0 and self.moment == [] and self.force == []):
            return True
        else:
            return False
        
        
#==============================================================================
#==============================================================================
class TubaVector:
    """TubVector is the Class to contain all information present on a LINE ELEMENT in the piping/rod network """

    def __init__(self,start_tubapoint,end_tubapoint,vector,name_vector):
        self.name = name_vector
        self.start_tubapoint = start_tubapoint
        self.end_tubapoint = end_tubapoint
        self.vector = vector
        self.model = tub.current_model
        self.section = tub.current_section
        self.section_orientation = tub.current_section_orientation
        self.material = tub.current_material
        self.temperature = [tub.current_temperature,tub.current_ref_temperature]
        self.pressure = tub.current_pressure
        self.linear_force = []
        self.sif = 1
        self.cflex = 1

        self.local_y=start_tubapoint.local_y

        self._update_attached_tubapoints()
        self._update_global_forces()

    def _update_attached_tubapoints(self):

#if the new vector is not colinear with the last one, both span a new reference plane and local_y can be changed
#   new_vect.start_tubapoint.local_y=
        if not self.start_tubapoint.is_element_start :
            if is_colinear(self.vector,self.start_tubapoint.local_x)==False:
                self.start_tubapoint.local_y=self.start_tubapoint.get_last_vector().vector.normalized()
                self.local_y=self.start_tubapoint.get_last_vector().vector.normalized()
            else:
                self.local_y=self.start_tubapoint.get_last_vector().local_y
# As start_tubapoint.local_x will always be overriden with the new vector, the case 
# where local_y and the new vector local_x are colinear ust be take care of. If not,
# m no referance plane would be spanned by local_y and local_x anymore
        else:
            if is_colinear(self.vector, self.start_tubapoint.local_y):
                self.start_tubapoint.local_y=self.start_tubapoint.local_x.normalized()
                self.local_y=self.start_tubapoint.local_y

        self.start_tubapoint.local_x=self.vector.normalized()
        self.end_tubapoint.local_x=self.vector.normalized()
        
    def _update_global_forces(self):

# Fluid Weight in Pipe
#--------------------------------------------
        if self.model in ["TUBE","TUYAU"]:
            if tub.current_rho_fluid:
                density_fluid=tub.current_rho_fluid
                outer_radius=self.section["outer_radius"]
                wall_thickness=self.section["wall_thickness"]
                force_grav_fluid= math.pi*(outer_radius-wall_thickness)**2*density_fluid*tub.G
                print("force_grav_fluid ",force_grav_fluid);
                logging.info("Fluid_Weight N/mm "+str(force_grav_fluid))
                self.linear_force.append(eu.Vector3(0,0,-force_grav_fluid))
                print("fluid ",force_grav_fluid);
                logging.info("Fluid_Weight N/mm "+ str(eu.Vector3(0,0,-force_grav_fluid)))

# Insulation of the Pipe
#--------------------------------------------
        if self.model in ["TUBE","TUYAU"]:
            if tub.current_insulation:
                [insulation_thickness, insulation_density]=tub.current_insulation
                outer_radius=self.section["outer_radius"]

                force_grav_insulation= math.pi*((outer_radius+insulation_thickness)**2-outer_radius**2)*insulation_density*9.81
                logging.info("Insulation_Weight N/mm"+ str(force_grav_insulation))
                self.linear_force.append(eu.Vector3(0,0,-force_grav_insulation))
 
# Wind Load
#--------------------------------------------                
        if self.model in ["TUBE","TUYAU"]:
            if tub.current_windload:
                [insulation_thickness, insulation_density]=tub.current_insulation
                outer_radius=self.section["outer_radius"]
                print("Do ",outer_radius," thickness ",insulation_thickness)
                #1/2 ρ v2 A
                tubavector=self.end_tubapoint.pos-self.start_tubapoint.pos
                tubavector.normalize()
                print("tubavector ",tubavector);
                wnorm=tub.current_windload.normalized()
                f=wnorm-(wnorm.dot(tubavector))*tubavector
                insulation_rad=2*(outer_radius+insulation_thickness) 
                cw=0.5*tub.current_windload.magnitude_squared()*insulation_rad*tub.air_density
                windload=cw*f
                print("wn ",wnorm," tn ",tubavector," f ",f," wload ",windload," mag ",windload.magnitude())
                logging.info("Windload N/mm"+ str(windload))
                self.linear_force.append(windload)
                #print("test")
                #w=eu.Vector3(0,1,0).normalize()
                #t=eu.Vector3(0,1,0).normalize()
                #f=w-(w.dot(t))*t
                #print("t ",t," w ",w," f",f)

                #print("press a key ")
                #c = readchar.readchar()
                #exit()

#--------------------------------------------        

# ==============================================================================
# ==============================================================================
class TubaBent(TubaVector):
    def __init__(self,start_tubapoint,end_tubapoint,center_tubapoint,
                 bending_radius,rotation_axis,angle_rad,name_vect):
        self.bending_radius=bending_radius
        self.center_tubapoint=center_tubapoint
        self.rotation_axis=rotation_axis    #Normal vector on plane containing CenterPoint, Start and end_tubapoint
        self.angle_bent=angle_rad   #in rad
        TubaVector.__init__(self,start_tubapoint,end_tubapoint,
                                start_tubapoint.local_x, name_vect)
        self._update_attached_tubapoints()
        self._calculate_SIF_and_Cflex()


    def _calculate_SIF_and_Cflex(self):
        """calculate Stress intensification and flexibility factor"""
        thickness=self.section["wall_thickness"]
        outerRadius=self.section["outer_radius"]

        h=(thickness*self.bending_radius)/math.pow((outerRadius-thickness/2),2)
        sif=0.9/(h**0.666666)
        cflex=1.65/h
        if sif < 1:
            sif = 1
        if cflex < 1:
            cflex = 1

        self.sif=sif
        self.cflex=cflex

        pass

    def _update_attached_tubapoints(self):
        logging.debug("Update attached tubapoints"+ str(self.rotation_axis)
                            +",  "+str(self.angle_bent/math.pi*180))

        self.end_tubapoint.local_x=self.start_tubapoint.local_x.rotate_around(
                                        self.rotation_axis, self.angle_bent)
        #max self.end_tubapoint.local_y=self.start_tubapoint.local_x
        self.end_tubapoint.local_y=self.start_tubapoint.local_y.rotate_around(  
                                        self.rotation_axis, self.angle_bent)

#==============================================================================
#==============================================================================
class TubaTShape3D(TubaVector):
    def __init__(self,start_tubapoint,end_tubapoint,incident_tubapoint,
                 incident_vector,incident_section,name_vect):
        self.incident_end_tubapoint=incident_tubapoint
        self.incident_vector=incident_vector
        self.incident_section=incident_section
        TubaVector.__init__(self,start_tubapoint,end_tubapoint,
                                end_tubapoint.pos-start_tubapoint.pos, name_vect)
        self.model="VOLUME"

        self._update_attached_tubapoints()


    def _update_attached_tubapoints(self):
        logging.debug("Update attached tubapoints")

        self.incident_end_tubapoint.local_x=self.incident_vector.normalized()
        self.incident_end_tubapoint.local_y=self.start_tubapoint.local_x
        self.end_tubapoint.local_x=self.start_tubapoint.local_x
        self.end_tubapoint.local_y=self.start_tubapoint.local_y

#==============================================================================
#==============================================================================
def P(x,y,z,name=""):
    '''Creates a tubapoint with the coordinates P(x,y,z,name)'''

    if not name:
        name="P"+str(tub.tubapoint_counter)

    if isinstance(x,eu.Point3):
        point=x
        x=point.x
        y=point.y
        z=point.z
#------------------------------------------------------------------------------
    TubaPoint(x,y,z,name=name)
#------------------------------------------------------------------------------

#==============================================================================
#==============================================================================
def Prel(ref_point,x,y,z,name_point=""):
    '''Creates a relative tubapoint using a reference + displacement vector. No connecting Tubavector is created.'''

    if not name_point:
        name_point="P"+str(tub.point_counter)
    #Finds the tubapoint with the attribute  .Name== ref_point and returns it
    ref_point=([point for point in tub.dict_tubapoints if point.name == "a"][0])

    x=ref_point.pos.x+x
    y=ref_point.pos.y+y
    z=ref_point.pos.z+z
#------------------------------------------------------------------------------
    name_point=TubaPoint(x,y,z,name_point) #Create a Point object
#------------------------------------------------------------------------------
    logging.info("Create Prel: " + name_point)
#==============================================================================
#==============================================================================
def gotoP(name_point):
    """The function allowes to changes the current Tubapoint used for the next vector creation"""

    logging.debug("GotoP")
    tub.current_tubapoint=([tubapoint for tubapoint in tub.dict_tubapoints
                                        if tubapoint.name == name_point][0])

    if tub.current_tubapoint.is_incident_end():

        last_vector=tub.current_tubapoint.get_last_vector()
        tub.current_section=last_vector.incident_section

    logging.info("gotoP: " + name_point)
#==============================================================================
#==============================================================================
def V(x,y,z,name=""):
    """Creates a vector and an end point starting from the specified tubapoint. If no tubapoint-name is specified, the vector will be created starting from the last created point. The direction is defined by the
    user input x,y,z.
    """
    if not name:
        name="P"+str(tub.tubapoint_counter)
    #Get start point of vector
    vector=eu.Vector3(x,y,z)
    start_tubapoint=tub.current_tubapoint
    end_pos=start_tubapoint.pos+vector
    #Create the new tubapoint-Object "end_tubapoint" for the Vector
#------------------------------------------------------------------------------
    end_tubapoint=TubaPoint(end_pos.x,end_pos.y,end_pos.z,name)
#------------------------------------------------------------------------------ 
    name_vector="V"+str(tub.tubavector_counter)
    #Create the TubaVector object containing all the informations of the line element (Material, Temperature, Pressure etc)
#------------------------------------------------------------------------------
    vect=TubaVector(start_tubapoint, end_tubapoint, vector, name_vector)
    
    tub.tubavector_counter += 1
    tub.dict_tubavectors.append(vect)
#------------------------------------------------------------------------------ 
    logging.debug("start_point connected?: "+str(start_tubapoint.local_x))
    return vect
    
def V_3D(x,y,z,name=""):
    vect=V(x,y,z,name)
    vect.model="VOLUME"
#==============================================================================
#==============================================================================
def Vc(length,name=""):
    """Creates a colinear vector in direction of the last vector.
    (The information for the colinear vector is contained in current_tubapoint.local_x)"""

    x=length*tub.current_tubapoint.local_x.x
    y=length*tub.current_tubapoint.local_x.y
    z=length*tub.current_tubapoint.local_x.z
    vect=V(x,y,z,name)
    return vect

def Vc_3D(length,name=""):
    vect=Vc(length,name)
    vect.model="VOLUME"
    return vect
#==============================================================================
def Vp(endpoint_name, startpoint_name=""):
    """Creates a vector from start_tubapoint to end_tubapoint. If no start_tubapoint is specified, the 
    current_tubapoint is used as startpoint
    """
    if not startpoint_name:
        start_tubapoint=tub.current_tubapoint
    else:   
        start_tubapoint=([tubapoint for tubapoint in tub.dict_tubapoints
                                            if tubapoint.name == startpoint_name][0])
    
    end_tubapoint=([tubapoint for tubapoint in tub.dict_tubapoints
                                            if tubapoint.name == endpoint_name][0])


    vector=end_tubapoint.pos-start_tubapoint.pos
    name_vector="V"+str(tub.tubavector_counter)

    vect=TubaVector(start_tubapoint, end_tubapoint, vector, name_vector)
    tub.tubavector_counter += 1
    tub.dict_tubavectors.append(vect)
    return vect

def Vp_3D(endpoint_name, startpoint_name=""):
    vect=Vp(endpoint_name, startpoint_name)
    vect.model="VOLUME"
    return vect

def V_Reducer(length,name=""):
    vect=Vc(length,name)
    new_section=tub.dict_tubavectors[-2].section
    old_section=tub.current_section
    print("Reducer",old_section,new_section)
    vect.section={"outer_radius_start":new_section["outer_radius"],"wall_thickness_start":new_section["wall_thickness"],
                  "outer_radius_end":old_section["outer_radius"],"wall_thickness_end":old_section["wall_thickness"]}
    
    
#==============================================================================
#==============================================================================
def Bent(radius,angle_deg=0.0,orientation="",vector="",mode="intersect",name=""):
    """There are 2 general ways to create a pipe bent:
    
#.  Bent(bending_radius,vector=Vector3): \n
    arg1 as a vector defines the new direction after the bent
    With this function, it's not possible to create 180°-bents as the bending plane
    is not defined. A workaround would be to define 2 consecutive 90°-bents or use the angle+orientaion mode \n

#.  Bent(bending_radius,angle=ang_Bent (in degree),orientation=ang_Orient(in degree) ): \n
    With the input arg1=bent angle and arg2=orientation angle (defined as a dihedral angle),
    the new direction after the bent can be calculated. \n

mode defines around which point the bent will be created.
For "add" the start_tubapoint of the Bent will be the end_tubapoint of the last vector.\n
For "intersect" the last vector will be changed. Its end_tubapoint will be defined as
intersection point of the current and new vector of the piping
    """

    if angle_deg==180.0:
        logging.debug("Spezial case angle=180")
        Bent(radius=radius,angle_deg=angle_deg/2,orientation=orientation,mode=mode,name=name)
        Bent(radius=radius,angle_deg=angle_deg/2,orientation=180.0,mode="add",name=name)
    elif angle_deg<0.0 or angle_deg>180.0 and vector=="":
        raise RuntimeError("Angle_deg has to be in between 0 and 180 degree.")
    else:
        if  vector!="": #2. version of bentfunction Bent(bending_radius,arg1=Vector3)
            new_direction=eu.Vector3(0, 0, 0) + vector
            bent_dot=tub.current_tubapoint.local_x.dot(new_direction.normalized())
            logging.debug("bent_dot: "+str(bent_dot))
            angle_deg=math.acos(bent_dot)*180.0/math.pi

        elif angle_deg!="" and orientation!="": 
            new_direction=dihedral_vector(tub.current_tubapoint.local_y,tub.current_tubapoint.local_x,
                                            angle_deg*math.pi/180.0,orientation*math.pi/180.0)

        if mode=="intersect":
            tub.current_tubapoint.pos=tub.current_tubapoint.pos - \
                                         tub.current_tubapoint.local_x*radius*math.tan(angle_deg/180.0*math.pi/2)
            start_tubapoint=tub.current_tubapoint
        elif mode=="add":
            start_tubapoint=tub.current_tubapoint
        else:
            raise RuntimeError("Only \"intersect\" or \"add\" is a valid argument for mode")
        #In Case of angle_bent=180degree the function would have problems to construct the arc. Therefore, its split in 2x90degree
    
           #The second version is the standard version. Version1 and Version3 are porcessed to be  handeled in Version2
        rotation_axis=start_tubapoint.local_x.cross(new_direction)    #normal vector of bent plane
    
    
        vector_start_center=rotation_axis.cross(start_tubapoint.local_x).normalized()#from start_tubapoint go to direction centerpoint
        logging.debug("vector_start_center"+str(vector_start_center))
        center_pos=start_tubapoint.pos+vector_start_center*radius
     
        name_center_tubapoint="P"+str(tub.tubapoint_counter-1)+"_"+str(tub.tubapoint_counter)+"_center"
        #------------------------------------------------------------------------------
        center_tubapoint=TubaPoint(center_pos.x,center_pos.y,center_pos.z,name=name_center_tubapoint,nocount=True)
        #------------------------------------------------------------------------------
    
        vector_center_end=-vector_start_center.rotate_around(rotation_axis,angle_deg*math.pi/180.0).normalized()
        end_pos=center_pos+vector_center_end*radius
    
        if name=="":
            name_end_tubapoint="P"+str(tub.tubapoint_counter)
        else:
            name_end_tubapoint = name
        #------------------------------------------------------------------------------
        end_tubapoint = TubaPoint(end_pos.x,end_pos.y,end_pos.z,name=name_end_tubapoint)
        #------------------------------------------------------------------------------
        #Create the BendObject and add it to the tub.dic_Vectors list  with (Tubastart_tubapoint,Tubaend_tubapoint,TubaCenterPoint)
        #TubaBent(TubaVector): __init__(self,start_tubapoint,end_tubapoint,CenterPoint,bending_radius,VdN,name_vect):
        name_vect = "V"+str(tub.tubavector_counter)+"_Bent"
        #------------------------------------------------------------------------------
        bent_tubavector = TubaBent(start_tubapoint,end_tubapoint,center_tubapoint
                           ,radius,rotation_axis,angle_deg*math.pi/180.0, name_vect)
        
        tub.tubavector_counter += 1
        tub.dict_tubavectors.append(bent_tubavector)       

        return bent_tubavector            
        #------------------------------------------------------------------------------
        logging.debug("===================================")
        logging.debug("                                   ")
        logging.debug("           tubabent                ")
        logging.debug("Start_Tubapoint "+str(bent_tubavector.start_tubapoint.name))
        logging.debug("End_Tubapoint "+str(bent_tubavector.end_tubapoint.name))
        logging.debug("bending_radius "+str(bent_tubavector.bending_radius))
        logging.debug("rotation_axis "+str(bent_tubavector.rotation_axis))
        logging.debug("angle_bent "+str(bent_tubavector.angle_bent))
        logging.debug("                                   ")
        logging.debug("start_tubapoint.local_x "+str(bent_tubavector.start_tubapoint.local_x))
        logging.debug("end_tubapoint.local_x "+str(bent_tubavector.end_tubapoint.local_x))
        logging.debug("                                   ")
        logging.debug("Tubabent:  "+str(bent_tubavector.__dict__))
        logging.debug("===================================")
 
def Bent_3D(radius,angle_deg="",orientation="",vector="",mode="intersect",name=""):
    bent=Bent(radius=radius,angle_deg=angle_deg,orientation=orientation,vector=vector,mode=mode,name=name)
    bent.model="VOLUME"
#==============================================================================
#==============================================================================        
def TShape_3D(incident_radius,incident_thickness,angle_orient,
             name_incident_end="",name_main_end="",
             incident_halflength=0,main_halflength=0,
             mode="add"):
    """Creates a TShape Object. The Main Section continues with the 
    before defines Cross-Section. The branche is defined by the user-arguments
    """

    if mode == "intersect":
        tub.current_tubapoint.pos = tub.current_tubapoint.pos - \
                                     tub.current_tubapoint.local_x*main_halflength
        start_tubapoint = tub.current_tubapoint
    elif mode == "add":
# The end_tubapoint of the last vector is as well the start_tubapoint of the bent.
# The intersection point in x=bentradius is created
        start_tubapoint=tub.current_tubapoint
    else:
        raise RuntimeError("Only \"intersect\" or \"add\" is a valid argument for mode")

    if incident_halflength == 0: incident_halflength=4*incident_radius
    if main_halflength == 0: main_halflength=4*float(tub.current_section["outer_radius"])

    center_pos = tub.current_tubapoint.pos + \
                                     tub.current_tubapoint.local_x*main_halflength 
    logging.debug("ceter_pos"+ str(center_pos))
    main_end_pos = tub.current_tubapoint.pos + \
                                     tub.current_tubapoint.local_x*2*main_halflength

    logging.debug("main_pos"+  str(main_end_pos))

    angle_orient = angle_orient*math.pi/180
    new_direction = dihedral_vector(start_tubapoint.local_y,
                                start_tubapoint.local_x,90*math.pi/180,angle_orient)
                                
    vector_center_incidentend = new_direction*incident_halflength 
                              
    incident_end_pos = center_pos+vector_center_incidentend
    logging.debug("Incident_end_pos"+ str(incident_end_pos))


    if not name_incident_end:
        name_incident_end="P"+str(tub.tubapoint_counter)
#------------------------------------------------------------------------------
    incident_end_tubapoint = TubaPoint(incident_end_pos.x,incident_end_pos.y,incident_end_pos.z,
                            name=name_incident_end)
#------------------------------------------------------------------------------     

    if not name_main_end:
        name_main_end = "P"+str(tub.tubapoint_counter)  
#------------------------------------------------------------------------------
    main_end_tubapoint = TubaPoint(main_end_pos.x,main_end_pos.y,main_end_pos.z,
                            name=name_main_end)

#------------------------------------------------------------------------------

    incident_section = {"outer_radius":incident_radius,"wall_thickness":incident_thickness}
    
    name = "V"+str(tub.tubavector_counter)+"_TShape"
#------------------------------------------------------------------------------
    vect=TubaTShape3D(start_tubapoint,main_end_tubapoint,incident_end_tubapoint,
                 vector_center_incidentend,incident_section,name)
    tub.tubavector_counter += 1
    tub.dict_tubavectors.append(vect)
    
#------------------------------------------------------------------------------
#==============================================================================
def dihedral_vector(local_y,local_x,thetad3x,thetad2x):
    '''calculates the dihedral vector. For more information check
    https://sites.google.com/site/pasceque/francais/b---logiciels-developpes/tuba/6-theorie/angles-dihedriques'''

    local_y = local_y.normalized()
    local_x = local_x.normalized()
    local_z = local_x.cross(local_y)

    v_firstrotation = local_x.rotate_around(local_z,thetad3x)
    v_secondrotation = v_firstrotation.rotate_around(local_x,thetad2x)

    v_final = v_secondrotation
    return v_final
#==============================================================================
def is_colinear(vector1,vector2):
    '''checks if both vector are colinear (cross-product==0) '''
    if round(vector1.cross(vector2).__abs__(),4) == 0:
        return True
    else:
        return False
#==============================================================================
