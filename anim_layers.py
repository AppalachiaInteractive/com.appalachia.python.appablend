import bpy

from bpy.app.handlers import persistent
from bpy.app import driver_namespace
from cspy import anim_layers_bake

def check_handler(self, context):
    '''A main function that performs a series of checks using a handler'''
    
    obj = bpy.context.object
    if obj is None:
        return
    anim_data = obj.animation_data
            
    if anim_data is None or not len(obj.Anim_Layers) or not hasattr(anim_data, 'action'):
        return
    
    if obj.select_get() == False or not hasattr(anim_data, 'nla_tracks') or not obj.als.track_list:
        return
    
    nla_tracks = anim_data.nla_tracks
    
    #check if a new track was added within the NLA
    if len(nla_tracks[:-1]) > len(obj.Anim_Layers):
        check_new_track(nla_tracks, obj)
        return
    
    #check if a new track was removed within the NLA
    if len(nla_tracks[:-1]) < len(obj.Anim_Layers):           
        check_del_track(nla_tracks, obj)
        return
    
    #check if subtrack was removed
    if bpy.context.active_operator is not None:
        if bpy.context.active_operator.name in ['Add Action Strip', 'Delete Strips', 'Move Channels']:
            if nla_tracks[-1] != sub_track or len(sub_track.strips) != 1:
                nla_tracks.remove(sub_track)
            register_layers(nla_tracks)
            return
        if bpy.context.active_operator.name in ['Transform', 'Delete Keyframes'] and obj.als.edit_all_keyframes:
            edit_all_keyframes()
    
    #continue if locked
    if obj.Anim_Layers[obj.track_list_index].lock:
        return   

    check_influence(nla_tracks[obj.track_list_index])
    
    if anim_data.action_blend_type != 'ADD':
        anim_data.action_blend_type = 'ADD' 
        
    if obj.als.view_all_keyframes:
        hide_view_all_keyframes(obj, anim_data)
        check_selected_bones(obj)

    #check if an action was changed, created or removed within all the objects with animation layers
    scene = bpy.context.scene
    for i, AL_item in enumerate(scene.AL_objects):
        obj = AL_item.object
        if obj not in list(scene.objects):
            scene.AL_objects.remove(i)
            continue
        update_action(obj)
        #checking the value for comparison before the intial keyframe is set, because of the scale reseting to 0 bug
        check_fcurves(AL_item, obj)        
        
def base_initial_key(obj, anim_data):
    '''Checks the transformation on the Replace layer and the first keyframe and comparing it to the value before it was added'''
    bones = []
    if obj.type == 'ARMATURE':
        bones = [bone.name for bone in obj.pose.bones]
    transform_types = ['location', 'rotation_euler', 'rotation_quaternion', 'scale']
    
    for fcu in anim_data.action.fcurves:
        if len(fcu.keyframe_points) != 1:
            continue  
        transform = fcu.data_path.split('.')[-1]
        if transform == 'location':
            continue
        #reduce the added the values from the other layers
        added_value = 0
        frame = bpy.context.scene.frame_current
        for i, track in enumerate(anim_data.nla_tracks[0:-1]):
            if len(track.strips) != 1 or i == obj.track_list_index or track.strips[0].action is None or track.mute:
                continue
            if track.strips[0].blend_type != 'ADD':
                continue
            fcu_track = track.strips[0].action.fcurves.find(fcu.data_path,  index = fcu.array_index)
            if fcu_track is None:
                continue
            if fcu_track.data_path == fcu.data_path and fcu_track.array_index == fcu.array_index:
                #get the influence value either from the attribute or the fcurve
                if not track.strips[0].fcurves[0].mute and len(track.strips[0].fcurves[0].keyframe_points):
                    influence = track.strips[0].fcurves[0].evaluate(frame)
                else:
                    influence = track.strips[0].influence
                added_value += fcu_track.evaluate(frame)*influence
       
        #check if the fcurve is from a bone and not the object and get the value of the property
        if obj.type == 'ARMATURE' and fcu.data_path not in transform_types:
            bone = fcu.data_path.split('"')[1]
            #if the fcurve has transformation then get the original value
            if transform in dir(obj.pose.bones[bone]):
                if transform in transform_types: #if it's a vector transform then get the value with array index
                    obj_transform = getattr(obj.pose.bones[bone], transform)
                    value = obj_transform[fcu.array_index]
                else: #if it's not a vector transform type then get the value of the property
                    value = getattr(obj.pose.bones[bone], transform)
            else: #if it's not a tranformation then check if it's a property in the items of the bone
                prop = fcu.data_path.split('"')[-2]
                for item in obj.pose.bones[bone].items():
                    if prop == item[0]:
                        value = item[1]
        else:
            obj_transform = getattr(obj, transform)
            value = obj_transform[fcu.array_index]
        
        #apply the original value to the initial keyframe of the fcurve minus the value of the other layers
        if value != fcu.keyframe_points[0].co[1]:
            
            fcu.keyframe_points[0].co[1] = value - added_value
            fcu.keyframe_points.update()
           
    return {'FINISHED'}
                
def check_fcurves(AL_item, obj):
    '''checks if there are new fcurves'''
    if obj is None:
        return
    if not len(obj.Anim_Layers) or obj not in bpy.context.selected_objects:
        return
    anim_data = obj.animation_data
    action = anim_data.action
    blend_types = {'REPLACE', 'COMBINE'}
    if anim_data.nla_tracks[obj.track_list_index].strips[0].blend_type not in blend_types:
        return
    
    if action:
        if AL_item.fcurves != len(action.fcurves):
            base_initial_key(obj, anim_data)
        AL_item.fcurves = len(action.fcurves)
        return
    AL_item.fcurves = 0

def check_new_track(nla_tracks, obj):
    '''checks if a new track was added and removes it if necessery'''
    global sub_track
    try:
        sub_track
    except NameError:
        #add the default sub track
        register_layers(nla_tracks)
    for i, track in enumerate(nla_tracks):
        if len(track.strips) and track.strips[0].action:
            action = track.strips[0].action
        #if the sub_track moved then delete it and create a new one
        if track == sub_track and i != len(nla_tracks)-1:
            nla_tracks.remove(track)
            sub_track = add_substract_layer(nla_tracks, action)
            register_layers(nla_tracks)
        #of the sub_track is still in the same location then keep it
        elif track == sub_track and i == len(nla_tracks)-1:
            register_layers(nla_tracks)
                      
#check if a track was deleted outside of animation layers
def check_del_track(nla_tracks, obj):
    '''Check if a layer was deleted outside of animation layers, keep only subtract'''
    if not len(nla_tracks):
        obj.Anim_Layers.clear()
        visible_layers(obj) 
        return    
    try:
        global sub_track
    except NameError:
        register_layers(nla_tracks)
    
    if len(nla_tracks)==1 and sub_track == nla_tracks[0]:
        obj.Anim_Layers.clear()
        nla_tracks.remove(nla_tracks[0])
        return
    
    #check if sub_track is still there
    if sub_track == nla_tracks[-1]:
        if obj.track_list_index > len(nla_tracks)-2:
            obj.track_list_index = len(nla_tracks)-2
        visible_layers(obj)
        return
    
    #if sub_track is not there then update it and all the tracks
    register_layers(nla_tracks)
    if obj.track_list_index > len(obj.Anim_Layers)-1 and obj.track_list_index:
        obj.track_list_index = len(obj.Anim_Layers)-1
                           
def check_influence(track):
    '''check and update the influence property. 
    influence is a bit buggy and didn't update in realtime so I've added it an extra callback'''
    global keys 
    if track.strips[0].fcurves[0].mute or not len(track.strips[0].fcurves[0].keyframe_points) or bpy.context.scene.tool_settings.use_keyframe_insert_auto:
        if 'keys' in globals():
            del keys
        return  #when the fcurve doesnt have keyframes, or when autokey is turned on, then return
    try:
        keys
    except NameError:
        keys = [tuple(key.co) for key in track.strips[0].fcurves[0].keyframe_points]
        return
    #check if the keyframe points values have changed
    if keys != [tuple(key.co) for key in track.strips[0].fcurves[0].keyframe_points]:
        track.strips[0].fcurves[0].update()
    keys = [tuple(key.co) for key in track.strips[0].fcurves[0].keyframe_points]    

def update_action(obj):
    '''Check if a different action was selected or added in the action editor and update it into the current layer'''
    if obj is None or not hasattr(obj, 'animation_data'):
        return
    anim_data = obj.animation_data
    if anim_data is None:
        return
    if len(anim_data.nla_tracks) <= 1:
        return
    if anim_data.action == anim_data.nla_tracks[obj.track_list_index].strips[0].action and anim_data.action == anim_data.nla_tracks[-1].strips[0].action:
        return
    if obj.Anim_Layers[obj.track_list_index].lock:
        return
    #update the subtract track strip
    anim_data.nla_tracks[-1].strips[0].action = anim_data.action
    #update the layer strip with the current action
    anim_data.nla_tracks[obj.track_list_index].strips[0].action = anim_data.action
    return 
          
def update_sub_track(nla_tracks, obj):
    if len(nla_tracks[-1].strips) and len(nla_tracks) > 1:
        if nla_tracks[-1].strips[0].blend_type == 'SUBTRACT':
            sub_track = nla_tracks[-1]
            return sub_track
           
    #If tracks were removed then update track_list_index into index property
    if obj.track_list_index > len(nla_tracks)-1:
        index = len(nla_tracks)-1
    else:
        index = obj.track_list_index
        
    #make sure there is a strip with an action before adding a subtrack
    if len(nla_tracks[index].strips):
        action = nla_tracks[index].strips[0].action
    else:
        action = None
    sub_track = add_substract_layer(nla_tracks, action)
    return sub_track

def use_animated_influence(strip):
    if strip.use_animated_influence:
        return
    strip.use_animated_influence = True
    strip.keyframe_delete(strip.fcurves[0].data_path, frame=0)
    strip.influence = 1 
    for fcu in strip.fcurves:
        if 'influence' in fcu.data_path:
            fcu.mute = True                                                                                   
    
def register_layers(nla_tracks):
    obj = bpy.context.object
    global sub_track

    #check if the top track can be assigned as a subtrack
    sub_track = update_sub_track(nla_tracks, obj)
    
    #subscribe to the name of the track
    bpy.msgbus.clear_by_owner(obj)
    subscribe_to_track_name(obj)
    visible_layers(obj)

    #apply the correct setup for the strips. If there are more then one strip then lock the layer
    for i, track in enumerate(nla_tracks[:-1]):
        if track.is_solo:
            track.is_solo = False
            obj.Anim_Layers[i].solo = True
            
        if len(track.strips) != 1 or track.strips[0].type == 'META' and len(obj.Anim_Layers) > i+1:
            obj.Anim_Layers[i].lock = True
            continue
        strip = track.strips[0]
        strip.action_frame_start = 0
        strip.frame_start = 0
        strip.use_sync_length = False
        use_animated_influence(strip)
        
      
#updating the ui list with the nla track names
def visible_layers(obj):
    '''Creates a list of all the tracks without the top subtrack for the UI List'''
    nla_tracks = obj.animation_data.nla_tracks    
    mute = []
    lock = []
    solo = []

    #store all the layer properties
    for layer in obj.Anim_Layers:
        mute.append(layer.mute)
        lock.append(layer.lock)
        solo.append(layer.solo)
    
    #check if a layer was removed and adjust the stored properties
    if len(nla_tracks[:-1]) < len(obj.Anim_Layers):
        removed = 0
        for i, layer in enumerate(obj.Anim_Layers):
            if layer.name not in nla_tracks:
                mute.pop(i - removed)
                lock.pop(i - removed)
                solo.pop(i - removed)
                removed += 1
               
    #check if a layer was added and adjust the stored properties
    if len(nla_tracks[:-1]) > len(obj.Anim_Layers):
        obj.Anim_Layers.update()
        for i, track in enumerate(nla_tracks[:-1]):
            if track.name not in obj.Anim_Layers:   
                mute.insert(i, False)
                lock.insert(i, False)
                solo.insert(i, False)  
                    
    #write layers             
    obj.Anim_Layers.clear()
    
    for i, track in enumerate(nla_tracks[:-1]):
        layer = obj.Anim_Layers.add()
        layer.name = track.name

        if mute:
            layer.mute = mute[i]
            layer.lock = lock[i]
            if solo[i]:
                layer.solo = solo[i]  
    

def layer_mute(self, context):
    obj = context.object
    index = list(obj.Anim_Layers).index(self)
    obj.animation_data.nla_tracks[index].mute = self.mute
    
    #Exclude muted layers from view all keyframes
    if obj.als.view_all_keyframes:
        obj.als.view_all_keyframes = True
    
def layer_solo(self, context):
 
    obj = context.object
    index = list(obj.Anim_Layers).index(self)

    #added a skip boolean so that when layer.solo = False it doesnt iterate through all the layers because of the call
    global skip
    try:
        if skip:
            return
    except NameError:
        skip = False

    if self.solo:
        for i, layer in enumerate(obj.Anim_Layers):
            if layer != self:
                skip = True
                layer.solo = False
                #layer.mute = True
                obj.animation_data.nla_tracks[i].mute = True
            else:
                #layer.mute = True
                obj.animation_data.nla_tracks[i].mute = False
        skip = False
    else:
        #when turned off restore track mute from the layers mute property
        for i, track in enumerate(obj.animation_data.nla_tracks[:-1]):
            track.mute = obj.Anim_Layers[i].mute
            
    #obj.select_set(True)
    
def layer_lock(self, context):

    obj = context.object
    index = list(obj.Anim_Layers).index(self)
    nla_tracks = obj.animation_data.nla_tracks
    
    if not self.lock:
        if len(nla_tracks[index].strips) != 1 or nla_tracks[index].strips[0].type == 'META':# and not self.lock:
            self.lock = True
    if index == obj.track_list_index:
        obj.track_list_index = obj.track_list_index
        
    #Exclude locked layers from view all keyframes
    if obj.als.view_all_keyframes:
        obj.als.view_all_keyframes = True
         
def unique_name(collection, name):
    '''add numbers to tracks if they have the same name'''
    if name not in collection:
        return name
    nr = 1
    if '.' in name:
        end = name.split('.')[-1]
        if end.isnumeric():
            nr = int(end)
            name = '.'.join(name.split('.')[:-1])
    while name + '.' + str(nr).zfill(3) in collection:
        nr += 1
    return name + '.' + str(nr).zfill(3)

def layer_name_update(self, context):
    
    #if layer name exists then add a unique name
    layer_names = [layer.name for layer in context.object.Anim_Layers if layer != self]
    if self.name in layer_names:
        self.name = unique_name(layer_names, self.name)
    
    nla_tracks = context.object.animation_data.nla_tracks
    index = list(context.object.Anim_Layers).index(self)
    if self.name == nla_tracks[index].name:
        return
    nla_tracks[index].name = self.name
    
def animlayers_undo_pre(self, context):
    '''clear scene end subsciption because it was adding a subsciption on every undo'''
    bpy.msgbus.clear_by_owner(bpy.context.scene)
   
def animlayers_undo_post(self, context):
    '''clear scene end subsciption because it was adding a subsciption on every undo'''
    obj = bpy.context.object
    if len(bpy.context.scene.AL_objects):
        subscribe_to_frame_end(bpy.context.scene)
        subscribe_to_influence(bpy.context.scene)
        if obj.als.track_list:
            obj.als.track_list = True
            return
    else:
        check_animlayers_clear()

#Callback function for Scene frame end
def scene_update_callback(scene):
    '''End the strips at the end of the scene or scene preview'''
    scene = bpy.context.scene
    if scene.frame_preview_end > scene.frame_end:
        frame_end = bpy.context.scene.frame_preview_end
    else:
        frame_end = bpy.context.scene.frame_end

    for AL_item in scene.AL_objects:
        obj = AL_item.object
        if obj is None:
            continue
        if obj.animation_data is None:
            continue
        for track in obj.animation_data.nla_tracks:
            if len(track.strips) == 1:
                frame_end = max(frame_end, track.strips[0].action.frame_range[1])

    for AL_item in scene.AL_objects:
        obj = AL_item.object
        if obj is None:
            continue
        if obj.animation_data is None:
            continue
        for track in obj.animation_data.nla_tracks:
            if len(track.strips) == 1:
                track.strips[0].action_frame_end = frame_end
                track.strips[0].frame_end = frame_end
            

#Subscribe to the scene frame_end
def subscribe_to_frame_end(scene):
    '''subscribe_to_frame_end and frame preview end'''
    
    subscribe_end = scene.path_resolve("frame_end", False)
    subscribe_preview_end = scene.path_resolve("frame_preview_end", False)
    
    bpy.msgbus.subscribe_rna(
        key=subscribe_end,
        # owner of msgbus subcribe (for clearing later)
        owner=scene,
        # Args passed to callback function (tuple)
        args=(scene,),
        # Callback function for property update
        notify=scene_update_callback,)
        
    bpy.msgbus.subscribe_rna(
        key=subscribe_preview_end,
        owner=scene,
        args=(scene,),
        notify=scene_update_callback,)
        
    bpy.msgbus.publish_rna(key=subscribe_end)
    bpy.msgbus.publish_rna(key=subscribe_preview_end)
    
    #global frame_end
    #frame_end = True

def track_update_callback(*args):
    '''update layers with the tracks name'''
    obj = bpy.context.object
    nla_tracks = obj.animation_data.nla_tracks
    
    for i, track in enumerate(nla_tracks[:-1]):
        if track.name != obj.Anim_Layers[i].name:
            obj.Anim_Layers[i].name = track.name
    
def subscribe_to_track_name(obj):
    '''Subscribe to the name of track'''
    
    #subscribe_track = nla_track.path_resolve("name", False)
    subscribe_track = (bpy.types.NlaTrack, 'name')
    
    bpy.msgbus.subscribe_rna(
        key=subscribe_track,
        # owner of msgbus subcribe (for clearing later)
        owner=obj,
        # Args passed to callback function (tuple)
        args=(obj,obj.animation_data.nla_tracks,),
        # Callback function for property update
        notify=track_update_callback,)
        
    bpy.msgbus.publish_rna(key=subscribe_track)

def influence_update_callback(*args):
    '''update influence'''
    obj = bpy.context.object
    #checking if the object has nla tracks, when I used undo it was still calling the property on an object with no nla tracks
    if obj is None:
        return
    if obj.animation_data is None:
        return
    if not len(obj.animation_data.nla_tracks):
        return 
    
    track = obj.animation_data.nla_tracks[obj.track_list_index]
    keyframes = track.strips[0].fcurves[0].keyframe_points
    
    if track.strips[0].fcurves[0].mute or not len(keyframes):
        track.strips[0].fcurves[0].update()
        return
    
    if bpy.context.scene.tool_settings.use_keyframe_insert_auto:
        track.strips[0].keyframe_insert(track.strips[0].fcurves[0].data_path, -1)
        track.strips[0].fcurves[0].update()
    
        
def subscribe_to_influence(scene):
    '''Subscribe to the influence of the track'''
    subscribe_influence = (bpy.types.NlaStrip, 'influence')
    bpy.msgbus.subscribe_rna(
        key=subscribe_influence,
        # owner of msgbus subcribe (for clearing later)
        owner=scene,
        # Args passed to callback function (tuple)
        args=(scene,),
        # Callback function for property update
        notify=influence_update_callback,)
        
    bpy.msgbus.publish_rna(key=subscribe_influence)

def update_track_list(self, context):
    '''select the new action clip when there is a new selection in the ui list and make all the updates for this Layer'''
    obj = self
    if obj is None:
        return
    anim_data = obj.animation_data
    if not len(obj.Anim_Layers):
        return

    #check first if the layer is locked turn off everything and return when locked
    if obj.Anim_Layers[obj.track_list_index].lock:
        anim_data.action = None
        anim_data.action_influence = 0
        if len(anim_data.nla_tracks[-1].strips):
            anim_data.nla_tracks[-1].strips[0].action = None
        return
        
    #activate the current action of the layer
    anim_data.action_influence = 1
    current_action = anim_data.nla_tracks[obj.track_list_index].strips[0].action
    anim_data.action = current_action
    anim_data.nla_tracks[-1].strips[0].action = current_action
    use_animated_influence(anim_data.nla_tracks[obj.track_list_index].strips[0])
    obj.als.view_all_keyframes = obj.als.view_all_keyframes

    if obj.name in context.scene.AL_objects:
        if current_action is not None:
            context.scene.AL_objects[obj.name].fcurves = len(anim_data.action.fcurves)
        else:
            context.scene.AL_objects[obj.name].fcurves = 0

def remove_handler(handler_key, handler):
    if handler_key in driver_namespace:
        if driver_namespace[handler_key] in handler:
            handler.remove(driver_namespace[handler_key])
        del driver_namespace[handler_key] 

def add_obj_to_animlayers(obj, anim_layer_objects):
    '''Add the current object to the scene animation layers'''
    if obj in anim_layer_objects or obj is None or not obj.als.track_list:
        return
    new_obj = bpy.context.scene.AL_objects.add()
    new_obj.object = obj
    new_obj.name = new_obj.object.name
    if obj.animation_data is None:
        return
    anim_data = new_obj.object.animation_data
    if anim_data.action is not None:
        new_obj.fcurves = len(new_obj.object.animation_data.action.fcurves)
    else:
        if not len(anim_data.nla_tracks):
            return
        track = anim_data.nla_tracks[obj.track_list_index]
        if len(track.strips) != 1:
            return
        anim_data.action = track.strips[0].action
    
def check_animlayers_clear():
    if len(bpy.context.scene.AL_objects):
        return        
    #clear all handlers and subsciptions
    remove_handler("animlayers_checks", bpy.app.handlers.depsgraph_update_pre)      
    bpy.msgbus.clear_by_owner(bpy.context.scene)

@persistent        
def loadanimlayers(self, context):
    '''When loading a file check if the current selected object is with animlayers, if not then check if there is something else turned on'''
    #obj = bpy.context.object
    scene = bpy.context.scene
 
    anim_layer_objects = [AL_item.object for AL_item in scene.AL_objects]
    #if the current object is not turned on, then check if another object is turned on
    subscribe = False
    for obj in bpy.context.scene.objects:
        if obj is None:
            continue               
        if obj.als.track_list:
            add_obj_to_animlayers(obj, anim_layer_objects)
            subscribe = True

    if bpy.context.object.als.track_list:
        bpy.context.object.als.track_list = True
    elif subscribe:
        subscribe_to_frame_end(scene)
        subscribe_to_influence(scene)
        handler_key = "animlayers_checks"
        remove_handler(handler_key, bpy.app.handlers.depsgraph_update_pre)
        if handler_key not in driver_namespace:
            bpy.app.handlers.depsgraph_update_pre.append(check_handler)
            driver_namespace[handler_key] = check_handler
    
def turn_animlayers_on(self, context):
    '''Turning on and off the NLA with obj.als.track_list property'''
    #obj = bpy.context.object
    scene = bpy.context.scene
    #iterate through all selected objects, in case both were checked with alt + click
    for obj in bpy.context.selected_objects:
        if obj is None: #if active is deselected then return
                return
        anim_data = obj.animation_data
        if obj.als.track_list:
            if hasattr(obj.animation_data, 'nla_tracks'):
                if len(obj.Anim_Layers)>0 and len(obj.animation_data.nla_tracks)==0:
                    obj.Anim_Layers.clear()
                #If there are already tracks in the NLA before animation layer, prompt to delete them.
                if len(obj.Anim_Layers) == 0 and len(obj.animation_data.nla_tracks)>0:
                    bpy.ops.message.warning('INVOKE_DEFAULT')
                else:
                    start_animlayers(obj)      
        elif obj.animation_data.use_nla:
            #remove_handler("baselayer_checks", bpy.app.handlers.depsgraph_update_pre)
            if hasattr(anim_data, 'nla_tracks'):
                obj.animation_data.use_nla = False
                for track in anim_data.nla_tracks[:-1]:
                    if not len(track.strips):
                        continue
                    if track.strips[0].blend_type == 'REPLACE':
                        anim_data.action = track.strips[0].action
                        break

            for i, AnimLayers in enumerate(scene.AL_objects):
                if AnimLayers.object == obj:
                    #if AnimLayers.object == obj:
                    scene.AL_objects.remove(i)
                    bpy.msgbus.clear_by_owner(obj)
                    break
                   
        #check if anim layers on all the objects are turned off before removing the check handler
        check_animlayers_clear()
        
def start_animlayers(obj):
    #obj = bpy.context.object
    obj.animation_data.use_nla = True
    obj.animation_data.action_blend_type = 'ADD'
    scene = bpy.context.scene
    handler_key = "animlayers_checks"
    remove_handler(handler_key, bpy.app.handlers.depsgraph_update_pre)
                
    AnimLayer_objects = [AnimLayers.object for AnimLayers in scene.AL_objects]
    #check if there is already animlayer objects with subscriptions
    if not len(scene.AL_objects):
        #add_obj_to_animlayers(obj, AnimLayer_objects)
        subscribe_to_frame_end(scene)
        subscribe_to_influence(scene)
        bpy.msgbus.clear_by_owner(obj)
        subscribe_to_track_name(obj)
    if obj not in AnimLayer_objects:
        add_obj_to_animlayers(obj, AnimLayer_objects)
    scene_update_callback(bpy.context.scene)

    if hasattr(obj.animation_data, 'nla_tracks'):
        if len(obj.animation_data.nla_tracks):
            obj.animation_data.nla_tracks[0].is_solo = False
            
            #check for tracks with duplicated names
            nla_tracks = obj.animation_data.nla_tracks
            track_names = [track.name for track in nla_tracks]
            for i, name in enumerate(track_names):
                if track_names.count(name) > 1:
                    track_names[i] = unique_name(track_names, name)
                    nla_tracks[i].name = track_names[i]
            
            register_layers(nla_tracks)
   
    if animlayers_undo_pre not in bpy.app.handlers.undo_pre:
        bpy.app.handlers.undo_pre.append(animlayers_undo_pre)
    if animlayers_undo_post not in bpy.app.handlers.undo_post:
        bpy.app.handlers.undo_post.append(animlayers_undo_post)
 
    if len(obj.Anim_Layers):
        #update_track_list(self, context)
        obj.track_list_index = obj.track_list_index

    if handler_key not in driver_namespace:
        bpy.app.handlers.depsgraph_update_pre.append(check_handler)
        driver_namespace[handler_key] = check_handler
        
def add_substract_layer(nla_tracks, action):
    sub_track = nla_tracks.new()
    sub_track.name = "Subtract_Layer"
    #if the action is empty then add a temporary action for creating the strip and then remove it
    if action is None:
        action = bpy.data.actions[0]
        remove = True
    else:
        remove = False
    sub_strip = sub_track.strips.new(name='Subtract_strip',start=0, action=action)
    #If there was no action then remove it
    if remove:
        sub_strip.action = None
    sub_strip.name = 'Subtract_strip'
    sub_strip.action_frame_start = 0
    scene_update_callback(bpy.context.scene)
    sub_strip.blend_type = 'SUBTRACT'
    sub_track.lock = True
    return sub_track
 
#checks if the object has an action and if it exists in the NLA
def action_search(action, nla_tracks):
    if action != None:
        for track in nla_tracks:
            for strip in track.strips:
                if strip.action == action:
                    return True                   
    else:
        return True
    
    return False



def store_keyframes(fcu, keyframes):
    for key in fcu.keyframe_points:
        if key.co[0] not in keyframes:
            keyframes.append(key.co[0])
            
    return keyframes

def hide_view_all_keyframes(obj, anim_data):
    '''hide view all keyframes in the graph editor, to avoid the user changing the values
    and lock channels when edit all keyframes is turned off'''
    
    for i, layer in enumerate(obj.Anim_Layers):
        if layer.lock or obj.track_list_index == i:
            continue
        fcu = anim_data.action.fcurves.find(layer.name, index = i)
        if fcu is None:
            continue
        
        if not obj.als.edit_all_keyframes and not fcu.group.lock: #lock the groups if edit is not selected
            fcu.group.lock = True
        
        if bpy.context.area:    
            if bpy.context.area.type != 'GRAPH_EDITOR': #hide the channels when using graph editor
                return
        
        if not fcu.hide:
            fcu.hide = True

def unlock_edit_keyframes(self, context):
    '''Lock or unlock the fcurves of the Multiple layers with the edit all keyframes property'''
    obj = context.object
    if not self.view_all_keyframes or obj is None:
        return
    anim_data = obj.animation_data
    for i, layer in enumerate(obj.Anim_Layers): #look for the Anim Layers fcurve
        if layer.lock or anim_data.action is None or i == obj.track_list_index:
            continue
        fcu = anim_data.action.fcurves.find(layer.name, index = i)
        if self.edit_all_keyframes:
            fcu.group.lock = False
        else:
            fcu.group.lock = True
        return
    
def check_selected_bones(obj):
    '''running in the handler and checking if the selected bones were changed'''
    if not obj.als.only_selected_bones:
        return
    global selected_bones
    try: 
        selected_bones
    except NameError:
        selected_bones = bpy.context.selected_pose_bones
        return
    else:
        if selected_bones != bpy.context.selected_pose_bones:
            selected_bones = bpy.context.selected_pose_bones
            obj.als.view_all_keyframes = True    
        
def fcurve_bones_path(obj, fcu):
    '''if only selected bones is used then check for the bones path in the fcurves data path'''
    if obj.als.only_selected_bones and obj.mode == 'POSE':
        selected_bones_path = [bone.path_from_id() for bone in bpy.context.selected_pose_bones]
        if fcu.data_path.split('].')[0]+']' not in selected_bones_path:
            return True
    return False
            
def only_selected_bones(self,context):
    '''assign selected bones to a global variable that will be checked in the handler'''
    if self.only_selected_bones:
        global selected_bones
        selected_bones = context.selected_pose_bones
        view_all_keyframes(self, context)
    else:
        view_all_keyframes(self, context)
        del selected_bones
    
def edit_all_keyframes():
    obj = bpy.context.object
    anim_data = obj.animation_data
    
    for i, layer in enumerate(obj.Anim_Layers): #look for the Anim Layers fcurve
        if layer.lock or anim_data.action is None or i == obj.track_list_index:
            continue
        fcu = anim_data.action.fcurves.find(layer.name, index = i)
        if fcu is None or not len(fcu.keyframe_points):
            continue
        
        #check if keyframes were deleted
        if len(fcu_layers[fcu.data_path]) != len(fcu.keyframe_points) and bpy.context.active_operator.name == 'Delete Keyframes':
            keyframes = store_keyframes(fcu, [])
            del_keys = list(set(fcu_layers[fcu.data_path]) - set(keyframes))
            for fcurve in anim_data.nla_tracks[i].strips[0].action.fcurves: #delete the relative keyframes in the action
                if fcurve_bones_path(obj, fcurve):
                    continue
                if fcurve.group is not None:
                    if fcurve.group.name == 'Anim Layers':
                        continue
                #del_keyframes = [keyframe for keyframe in fcurve.keyframe_points if keyframe.co[0] in del_keys]
                keyframe_points = list(fcurve.keyframe_points)
                while keyframe_points: # remove the keyframes from the original action
                    if keyframe_points[0].co[0] in del_keys:
                        fcurve.keyframe_points.remove(keyframe_points[0])
                        keyframe_points = list(fcurve.keyframe_points)
                    else:
                        keyframe_points.pop(0)
                fcurve.update()
            keyframes = [key for key in keyframes if key not in del_keys]
            fcu_layers.update({fcu.data_path : keyframes})
            continue
            
        #check if keyframes were moved to a different location
        old_keys = {}
        for key in fcu.keyframe_points: #creates dictionary of the old key frame values with their difference
            if key.co[0] != key.co[1]:
                old_keys.update({key.co[1] : key.co[0] - key.co[1]})
                key.co[1] = key.co[0]  # reset the keyframe
                
        #iterate through the fcurves in the original action    
        for fcurve in anim_data.nla_tracks[i].strips[0].action.fcurves:
            if fcurve_bones_path(obj, fcurve):
                continue
            for keyframe in fcurve.keyframe_points:
                if keyframe.co[0] not in old_keys:
                    continue
                difference = old_keys[keyframe.co[0]]
                keyframe.co[0] = keyframe.co[0] + difference
                if keyframe.interpolation == 'BEZIER':
                    keyframe.handle_left[0] += difference
                    keyframe.handle_right[0] += difference
            #fcurve.update()
                
def view_all_keyframes(self, context):
    '''Creates new fcurves with the keyframes from the all the layers'''
    obj = bpy.context.object
    anim_data = obj.animation_data
    #if animation layers is still not completly loaded then return
    if len(anim_data.nla_tracks[:-1]) != len(obj.Anim_Layers) or anim_data.action is None:
        return
    #remove old Anim Layers fcurves 
    for i, track in enumerate(anim_data.nla_tracks[:-1]):
        fcu = anim_data.action.fcurves.find(track.name, index=i)    
        if fcu: #remove all the fcurves/channels in the group and mark as removed
            if fcu.group.name == 'Anim Layers':
                fcu.group.lock = False
                for fcu_remove in fcu.group.channels:
                    anim_data.action.fcurves.remove(fcu_remove)
                break
    if not self.view_all_keyframes: #If the option is uncheck then finish edit and return
        self.edit_all_keyframes = False
        return
    global fcu_layers        
    fcu_layers = {}      
    for i, track in enumerate(anim_data.nla_tracks[:-1]):
        if i == obj.track_list_index or track.strips[0].action is None or not len(track.strips[0].action.fcurves) or obj.Anim_Layers[i].lock:
            continue
        #create a new fcurve with the name of the track
        fcu_layer = anim_data.action.fcurves.new(track.name, index=i, action_group='Anim Layers')
        fcu_layer.update()
        fcu_layer.is_valid = True
        keyframes = []
        #store all the keyframe locations from the fcurves of the layer
        for fcu in track.strips[0].action.fcurves:
            if fcu.group is not None:
                if fcu.group.name == 'Anim Layers': 
                    continue
            #if only selected bones is used then check for the bones
            if obj.als.only_selected_bones and obj.mode == 'POSE':
                selected_bones = [bone.path_from_id() for bone in context.selected_pose_bones]
                if fcu.data_path.split('].')[0]+']' not in selected_bones:
                    continue
                
            keyframes = store_keyframes(fcu, keyframes)          
        if not keyframes:
            continue
        for key in keyframes: #create new keyframes for all the stored keys
            fcu_layer.keyframe_points.add(1)
            fcu_layer.keyframe_points[-1].co[0] = key
            fcu_layer.keyframe_points[-1].co[1] = key
            fcu_layer.keyframe_points[-1].interpolation = 'LINEAR'
            fcu_layer.keyframe_points[-1].type = self.view_all_type    
        fcu_layer.hide = True
        fcu_layer.update()
        #store the fcurves and keyframes
        fcu_layers.update({fcu_layer.data_path : keyframes})
        
        
        #Make sure lock is turned off when selecting new layer and edit is turned on
        if fcu_layer is not None and self.edit_all_keyframes:
            fcu_layer.group.lock = False 
                
def redraw_areas(areas):
    for area in bpy.context.window_manager.windows[0].screen.areas:
        if area.type in areas:
            area.tag_redraw()

def delete_layers(obj):
    for track in obj.animation_data.nla_tracks:
        if track.select == True:
            obj.animation_data.nla_tracks.remove(track)
    visible_layers(obj)

def select_layer_bones(self, context):
    obj = bpy.context.object
    strips = obj.animation_data.nla_tracks[obj.track_list_index].strips
    if len(strips) != 1 or strips[0].action is None:
        return
    for fcu in strips[0].action.fcurves:
        if 'pose.bones' in fcu.data_path:
            bone = fcu.data_path.split('"')[1]
            if bone in obj.data.bones:
                obj.data.bones[bone].select = True
        

class AnimLayersSettings(bpy.types.PropertyGroup):

    track_list: bpy.props.BoolProperty(name="Turn Animation Layers On", description="View all actions UI", default=False, options={'HIDDEN'}, update=turn_animlayers_on)
    linked: bpy.props.BoolProperty(name="Linked", description="Duplicate a layer with a linked action", default=False, options={'HIDDEN'})
    smartbake: bpy.props.BoolProperty(name="Smart Bake", description="Stay with the same amount of keyframes after merging and baking", default=False, options={'HIDDEN'})
    onlyselected: bpy.props.BoolProperty(name="Only selected Bones", description="Bake only selected Armature controls", default=False, options={'HIDDEN'})
    clearconstraints: bpy.props.BoolProperty(name="Clear constraints", description="Clear constraints during bake", default=False, options={'HIDDEN'})
    mergefcurves: bpy.props.BoolProperty(name="Merge Fcurve modifiers", description="Include Fcurve modifiers in the bake", default=False, options={'HIDDEN'})
    view_all_keyframes: bpy.props.BoolProperty(name="View", description="View keyframes from multiple layers, use lock and mute to exclude layers", default=False, update=view_all_keyframes)
    edit_all_keyframes: bpy.props.BoolProperty(name="Edit", description="Edit keyframes from multiple layers", default=False, update = unlock_edit_keyframes)
    only_selected_bones: bpy.props.BoolProperty(name="Only Selected Bones", description="Edit and view only selected bones", default=False, update = only_selected_bones)
    view_all_type: bpy.props.EnumProperty(name="Type", description="Select visibiltiy type of keyframes", update=view_all_keyframes,
        items = [
            ('BREAKDOWN', 'Breakdown', 'select Breakdown visibility'),
            ('JITTER', 'Jitter', 'select Jitter visibility'),
            ('MOVING_HOLD', 'Moving Hold', 'select Moving Hold visibility'),
            ('EXTREME', 'Extreme', 'select Extreme visibility'),
            ('KEYFRAME', 'Keyframe', 'select Keyframe visibility')
        ]
    )
    baketype : bpy.props.EnumProperty(name = '', description="Type of Bake", items = [('AL', 'Anim Layers','Use Animation Layers Bake',0), ('BLENDER', 'Blender Bake', 'Use Blender internal Bake',1)])
    direction: bpy.props.EnumProperty(name = '', description="Select direction of merge", items = [('UP', 'Up','Merge upwards','TRIA_UP',1), ('DOWN', 'Down', 'Merge downwards','TRIA_DOWN',0), ('ALL', 'All', 'Merge all layers')])
    operator : bpy.props.EnumProperty(name = '', description="Type of bake", items = [('NEW', 'New Baked Layer','Bake into a New Layer','NLA',1), ('MERGE', 'Merge', 'Merge Layers','NLA_PUSHDOWN',0)])

class AnimLayersItems(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="AnimLayer", update=layer_name_update)
    mute: bpy.props.BoolProperty(name="Mute", description="Mute Animation Layer", default=False, options={'HIDDEN'}, update=layer_mute)
    lock: bpy.props.BoolProperty(name="Lock", description="Lock Animation Layer", default=False, options={'HIDDEN'}, update=layer_lock)
    solo: bpy.props.BoolProperty(name="Solo", description="Solo Animation Layer", default=False, options={'HIDDEN'}, update=layer_solo)
    
class AnimLayersObjects(bpy.types.PropertyGroup):
    object: bpy.props.PointerProperty(name = "object", description = "objects with animation layers turned on", type=bpy.types.Object)
    fcurves: bpy.props.IntProperty(name='fcurves', description='helper to check if fcurves are changed', default=0)
 