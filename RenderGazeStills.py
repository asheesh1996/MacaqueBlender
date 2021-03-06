
#==================== RenderHumanGaze.py =====================
# This script loads human face models (meshes and texture maps) from
# the specified folder, sets up lighting and camera position in the
# scene, and then renders all requested stimuli.

import glob
import bpy
import os
import math
import mathutils as mu
import numpy as np
from GenerateLightArray import GenerateLightArray
from InitBlendScene import InitBlendScene

#============= Get children objects
def getChildren(myObject):
    children = [] 
    for ob in bpy.data.objects: 
        if ob.parent == myObject: 
            children.append(ob) 
    return children 

#============= Set eye tracker position from gaze angle
def GazeLookAt(Az, El, Rad):
    Y   = -np.cos(math.radians(Az))*np.cos(math.radians(El))*Rad
    X   = np.sin(math.radians(Az))*np.cos(math.radians(El))*Rad
    Z   = np.sin(math.radians(El))*Rad
    GazeXYZ = mu.Vector((X, Y, Z))
    return GazeXYZ    

#============= Set model import parameters
Prefix          = 'Q:'
RenderDir       = Prefix + '/murphya/Stimuli/MacaqueAvatar/3D_Renders/HumanGaze/'
ModelDir        = Prefix + '/murphya/AdaptationExp/HumanModel/'
ModelsToUse     = ['01','04','033','035','036']
ModelExpStrings = ['Neutral']#,'Yawn','Rage','Coo','Smile']
ModelScale      = (0.1,0.1,0.1)
MeshFormat      = '.OBJ'
TexFormat       = '.jpg'
MeshPrefix      = 'Male03_'

#============= Set model pose and appearance parameters
HeadAzmuths     = [-60, -30, 0, 30, 60]
HeadElevations  = [0]
GazeAzmuths     = [-30, -15, 0, 15, 30]
GazeElevations  = [0]


#============= Setup camera and lighting
Scene               = bpy.data.scenes['Scene']

StereoFormat        = 1
ViewingDistance     = 90
InitBlendScene(2, StereoFormat, ViewingDistance)

Cam             = bpy.data.objects["Camera"]
Lighting        = bpy.data.worlds["World"].light_settings
Lighting.use_environment_light  = True              # Turn environemnt lighting on
Lighting.environment_energy     = 1                 # Set to normal energy 

#if bpy.data.objects.get('Lamp_7') is None:
#    Lamps = GenerateLightArray('SPOT','circle',(0,0,0))                                   # Generate a hemisphere of spotlight lamp objects in scene


#============= Load meshes and textures into scene
EyeTracker  = bpy.data.objects['EyeTracker']
MeshFile    = []
TexFile     = []
for m in range(0, len(ModelsToUse)):
    
    if bpy.data.objects.get(MeshPrefix + ModelExpStrings[m]) is not None:
        print('Mesh already in scene: ' + ModelsToUse[m])
        HeadObj     = bpy.data.objects[MeshPrefix + ModelExpStrings[m]]
        HeadObj.hide           = False          # Make mesh visible in preview
        HeadObj.hide_render    = False          # Make mesh visible in render output
        
        EyeObj = getChildren(HeadObj)           # Get handles of eye objects parented to current mesh
        for eye in EyeObj:
            eye.hide         = False            # Make eyes visible
            eye.hide_render  = False 
        
    else:
        print('Importing mesh file ' + ModelsToUse[m])
        MeshFile     = glob.glob(ModelDir + ModelsToUse[m] + '*/' + MeshPrefix + ModelsToUse[m] + '_*' + MeshFormat)
        TexFile      = glob.glob(ModelDir + ModelsToUse[m] + '*/' + MeshPrefix + ModelsToUse[m] + '_*' + TexFormat)
        
        #======== Import mesh object
        path, filename      = os.path.split(MeshFile)                                   # Get filename and path
        objh                = bpy.ops.import_scene.obj(filepath=MeshFile[0])            # Load .obj mesh
        bpy.context.selected_objects[0].name = MeshPrefix + ModelExpStrings[m]          # Rename the imported mesh
        HeadObj                 = bpy.data.objects[MeshPrefix + ModelExpStrings[m]]
        HeadObj.scale           = ModelScale;
        HeadObj.rotation_euler  = (90, 0, math.radians(180))


    if bpy.data.materials.get(ModelExpStrings[m] + '_mat') is not None:
        print('Material already in scene: ' + ModelsToUse[m])
        
    else:
        
        #======== Create new material
        bpy.context.scene.objects.active = obj
        matname = ModelExpStrings[m] + '_mat'
        if not matname in bpy.data.materials:
            material                                = bpy.data.materials.new(matname)
            material.diffuse_color                  = (1, 1, 1)
            material.specular_intensity             = 0.25
            HeadObj.data.materials.append(material)
        
        #======== Import texture image
        TexName     = ModelExpStrings[m] + '_tex'
        TexUV       = bpy.data.textures.new(TexName, type='IMAGE')
        Image       = bpy.data.images.load(TexFile[0])
        TexUV.image = Image
        
        #======== Link texture to material
        bpy.data.materials[matname].texture_slots.add()
        bpy.data.materials[matname].active_texture                  = TexUV
        bpy.data.materials[matname].texture_slots[0].texture_coords = "UV"
        bpy.data.materials[matname].texture_slots[0].mapping        = "FLAT"
        bpy.data.materials[matname].subsurface_scattering.use       = True
        bpy.data.materials[matname].subsurface_scattering.ior       = 1.5
        bpy.data.materials[matname].subsurface_scattering.scale     = 0.01
        bpy.data.materials[matname].subsurface_scattering.color     = (1,1,1)  
    

    #=========== Loop through head orientations
    StartRot = HeadObj.rotation_euler
    for Haz in HeadAzmuths:
        for Hel in HeadElevations:
            HeadObj.rotation_euler = (math.radians(Hel), math.radians(Haz), 0)
            
             #=========== Loop through gaze angles
            for Gaz in GazeAzmuths:
                for Gel in GazeElevations:
                    GazeXYZ = GazeLookAt(Gaz, Gel, ViewingDistance/100)
                    EyeTracker.location = GazeXYZ

                    #=========== Loop through lighting directions
                    lon = 1;
                    #for lon in Lamps:
                    #    for loff in Lamps:
                    #        Lamps[loff].hide_render = True
                    #    Lamps[lon].hide_render = False
                        
                    #=========== Render image and save to file
                    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
                    RenderFilename = "Human_%s_%s_Haz%d_Hel%d_Gaz%d_Gel%d_Lamp%d.png" % (MeshPrefix, ModelExpStrings[m], Haz, Hel, Gaz, Gel, lon)
                    if os.path.isfile(RenderDir + "/" + RenderFilename) == 0:
                        print("Now rendering: " + RenderFilename + " . . .\n")
                        bpy.context.scene.render.filepath = RenderDir + "/" + RenderFilename
                        bpy.ops.render.render(write_still=True, use_viewport=True)
                    elif os.path.isfile(RenderDir + "/" + RenderFilename) == 1:
                        print("File " + RenderFilename + " already exists. Skipping . . .\n")


    #=========== Turn off expression mesh
    obj.hide           = True          # Make mesh invisible in preview
    obj.hide_render    = True          # Make mesh invisible in render output
    
    EyeObjs = [obj for obj in Scene.objects if obj.name.startswith("eye")]  # Get list of eye objects
    for eyes in EyeObjs:
        eyes.hide            = True
        eyes.hide_render     = True 


#=========== Finished
print("Rendering completed!\n")