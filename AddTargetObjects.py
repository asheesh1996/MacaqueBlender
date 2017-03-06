
#=================== EditTargetObjects.py =======================
# These functions are used to add or remove target objects to or 
# from the scene. 
#

import bpy
import math
import numpy as np
import mathutils as mu

def AddTargetObjects():
    
    #================= Set target appearance
    SphereRad       = 0.01                                              # Set sphere radius (meters)
    SphereDepth     = -0.2
    SphereEcc       = 0.15
    SphereNumber    = 8
    SpherePolAng    = np.linspace(0,2*math.pi, SphereNumber+1)
    SphereLocs      = np.zeros((SphereNumber,3))
    for sph in range(0,SphereNumber):
        SphereLocs[sph][0] = SphereEcc*math.sin(SpherePolAng[sph])
        SphereLocs[sph][2] = SphereEcc*math.cos(SpherePolAng[sph])
        SphereLocs[sph][1] = SphereDepth
        
    SphereColor    = (0,0,1)                # Set target colors (RGB)

    #================= Create material
    AllMats = [mat for mat in bpy.data.materials if mat.name.startswith("Target")]
    if all(AllMats):
        mat                     = bpy.data.materials.new("TargetMat")       # Create new material
        mat.diffuse_color       = SphereColor                               # Set material color
        mat.specular_intensity  = 0                                         # Set intensity of specular reflection (0-1)
    elif not(all(AllMats)):
        mat = AllMats[0]

    #================= Create targets
    bpy.ops.group.create(name="Targets")
    #bpy.ops.object.group_link(group="Targets")
    for sph in range(0, len(SphereLocs)):
        if sph == 0:
            bpy.ops.mesh.primitive_ico_sphere_add(
                subdivisions    = 100,
                size            = SphereRad,
                calc_uvs        = False,
                view_align      = False,
                enter_editmode  = False,
                location        = SphereLocs[sph],
                rotation        = (0,0,0))
            bpy.data.objects['Icosphere'].active_material   = mat                           # Set target color
            bpy.data.objects['Icosphere'].name              = "Target %d" % sph             # Rename object as target ID
        elif sph  > 0:
            d = bpy.data.objects['Target 0'].copy()
            bpy.context.scene.objects.link(d)
            d.location      = SphereLocs[sph]
            d.name          = "Target %d" % sph  
            
            
    bpy.context.scene.objects["Target %d" % sph].select = True
    bpy.ops.object.group_link(group="Targets")    
    bpy.context.scene.objects["Target %d"  % sph].select = False
    #bpy.context.scene.objects.active = d
    #bpy.ops.group.objects_add_active(group = "Targets")
    return SphereLocs
        
        
def RemoveTargetObjects():
    scene        = bpy.context.scene
    AllTargets   = [obj for obj in scene.objects if obj.name.startswith("Target")]  # Find all objects in scene with 'Target' in name
    for t in range(0,len(AllTargets)):
        AllTargets[t].select = True         # Select next target object
        bpy.ops.object.delete()             # Delete target object
        

def EditTargetObjects(Add):
    
    if Add == 1:
        Locs = AddTargetObjects()
    elif Add == 0:
        RemoveTargetObjects()
        
def MonkeyLookAt(HeadLoc, GazeLoc):
    bpy.data.objects["HeaDRig"].pose.bones['EyesTracker'].location = mu.Vector((GazeLoc)) - bpy.data.objects["HeaDRig"].location
    bpy.data.objects["HeaDRig"].pose.bones['HeadTracker'].location = mu.Vector((HeadLoc[0],HeadLoc[2],HeadLoc[1])) - bpy.data.objects["HeaDRig"].location
        
        
        
def RenderAllViews(Locs):
    GazeLoc = (0, 0.03, 0.2)
    RenderDir = 'P:\murphya\Blender\Renders\CuedAttention'
    for l in range(0, len(Locs)):
        MonkeyLookAt(Locs[l], GazeLoc)
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        Filename = "CuedLocation_V1_headLoc%s.png" % (l)
        print("Now rendering: " + Filename + " . . .\n")
        #bpy.context.scene.render.filepath = RenderDir + "/" + Filename
        #bpy.ops.render.render(write_still=True, use_viewport=True)
    
        
#RemoveTargetObjects()
Locs = AddTargetObjects()
RenderAllViews(Locs)

#Loc = [0.15,0.2,0]
#MonkeyLookAt(Locs[3], Locs[3])
    


    
    
    