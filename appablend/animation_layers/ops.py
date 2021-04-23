import bpy
from appablend.animation_layers.core import (action_search,
                                             add_substract_layer,
                                             check_handler, delete_layers,
                                             redraw_areas, register_layers,
                                             remove_handler,
                                             scene_update_callback,
                                             select_layer_bones,
                                             start_animlayers, unique_name,
                                             use_animated_influence,
                                             visible_layers)
from bpy.app import driver_namespace


class ANIM_bones_in_layer(bpy.types.Operator):
    """Select bones with keyframes in the current layer"""

    bl_idname = "anim.bones_in_layer"
    bl_label = "Select layer bones"
    bl_icon = "BONE_DATA"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.object.mode == "POSE"

    def execute(self, context):
        select_layer_bones(self, context)
        return {"FINISHED"}


class ClearNLA(bpy.types.Operator):
    bl_idname = "message.warning"
    bl_label = "WARNING!"
    bl_icon = "ERROR"

    confirm: bpy.props.BoolProperty(default=True)

    def execute(self, context):
        obj = bpy.context.object
        if self.confirm:
            for track in obj.animation_data.nla_tracks:
                track.select = True
            delete_layers(obj)
        start_animlayers(obj)
        return {"FINISHED"}

    def invoke(self, context, event):

        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=500)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        obj_name = bpy.context.object.name
        col.label(
            text=obj_name
            + " has already tracks in the NLA editor, which have been created before using animation layers."
        )
        row = col.row()
        row.alignment = "CENTER"
        row.prop(self, "confirm", text="Remove NLA tracks")


def setup_new_layer(obj, new_track, Duplicate, blend_type):
    # check if the object already has an action and if it exists in the NLA, if not create a new one
    if (
        action_search(obj.animation_data.action, obj.animation_data.nla_tracks)
        and not Duplicate
    ):
        new_action = bpy.data.actions.new(name=new_track.name)
    else:
        new_action = obj.animation_data.action

    # strip settings
    new_strip = new_track.strips.new(name="new_track", start=0, action=new_action)
    new_strip.action_frame_start = 0
    scene_update_callback(bpy.context.scene)
    new_strip.blend_type = blend_type
    use_animated_influence(new_strip)

    return new_action


def add_animlayer(layer_name="Anim_Layer", duplicate=False, index=1, blend_type="ADD"):
    """Add an animation layer"""

    obj = bpy.context.object
    nla_tracks = obj.animation_data.nla_tracks
    previous = None if index == 0 else nla_tracks[obj.track_list_index]
    # if index == 0: #if it's the first layer created
    #    new_track = nla_tracks.new()
    # else:
    new_track = nla_tracks.new(prev=previous)
    new_track.name = layer_name
    new_track.lock = True
    new_action = setup_new_layer(obj, new_track, duplicate, blend_type)
    # register_layers(nla_tracks)
    # obj.track_list_index += index

    return new_track


# adding a new track, action and strip
class AddAnimLayer(bpy.types.Operator):
    """Add animation layer"""

    bl_idname = "anim.add_anim_layer"
    bl_label = "Add Animation Layer"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        handler_key = "animlayers_checks"
        remove_handler(handler_key, bpy.app.handlers.depsgraph_update_pre)

        obj = bpy.context.object
        if not hasattr(obj.animation_data, "action"):
            obj.animation_data_create()
        nla_tracks = obj.animation_data.nla_tracks
        if obj.animation_data.action == None:
            start_animlayers(obj)
            flag = False
        else:
            flag = True
        if not len(nla_tracks):
            add_animlayer("Base_Layer", index=0, blend_type="REPLACE")
            # base_track.strips[0].
            # using a temporary variable instead of calling update_track_list all the time with obj.track_list_index
            index = 0
            if flag:
                add_animlayer("Anim_Layer")
                index += 1
            add_substract_layer(nla_tracks, obj.animation_data.action)
        else:
            # layer_names = [layer.name for layer in context.object.Anim_Layers if layer != self]
            add_animlayer(unique_name(obj.Anim_Layers, "Anim_Layer"))
            index = obj.track_list_index + 1

        register_layers(nla_tracks)

        obj.track_list_index = index

        if handler_key not in driver_namespace:
            bpy.app.handlers.depsgraph_update_pre.append(check_handler)
            driver_namespace[handler_key] = check_handler

        return {"FINISHED"}


class DuplicateAnimLayer(bpy.types.Operator):
    """Duplicate animation layer"""

    bl_idname = "anim.duplicate_anim_layer"
    bl_label = "Duplicate Animation Layer"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        handler_key = "animlayers_checks"
        remove_handler(handler_key, bpy.app.handlers.depsgraph_update_pre)

        obj = bpy.context.object
        anim_data = obj.animation_data
        nla_tracks = obj.animation_data.nla_tracks

        blend = nla_tracks[obj.track_list_index].strips[0].blend_type
        track_name = nla_tracks[obj.track_list_index].name
        strip_name = nla_tracks[obj.track_list_index].strips[0].name

        name = unique_name(obj.Anim_Layers, track_name)
        new_track = add_animlayer(layer_name=name, duplicate=True, blend_type=blend)
        # new_track.strips[0].blend_type = blend
        # new_track.strips[0].name = strip_name

        if obj.als.linked == False:
            # anim_data.action = anim_data.action.copy()
            new_action = anim_data.action.copy()
            new_track.strips[0].action = anim_data.action = new_action

        register_layers(nla_tracks)

        obj.track_list_index += 1
        if handler_key not in driver_namespace:
            bpy.app.handlers.depsgraph_update_pre.append(check_handler)
            driver_namespace[handler_key] = check_handler

        return {"FINISHED"}


class RemoveAnimLayer(bpy.types.Operator):
    """Remove animation layer"""

    bl_idname = "anim.remove_anim_layer"
    bl_label = "Remove Animation Layer"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        anim_data = context.object.animation_data
        if hasattr(anim_data, "nla_tracks"):
            return len(context.object.animation_data.nla_tracks)

    def execute(self, context):
        obj = bpy.context.object

        nla_tracks = obj.animation_data.nla_tracks
        nla_tracks.remove(nla_tracks[obj.track_list_index])
        visible_layers(obj)
        # update the ui list item's index
        if obj.track_list_index != 0:
            obj.track_list_index -= 1

        else:
            obj.track_list_index = 0

        # If nothing is left then remove also the sub_track
        if len(nla_tracks) == 1:
            nla_tracks.remove(nla_tracks[0])
            # remove_handler("baselayer_checks", bpy.app.handlers.depsgraph_update_pre)

        return {"FINISHED"}


def move_layer(dir):
    window = bpy.context.window
    old_area = window.screen.areas[0].type
    screen = window.screen
    bpy.context.window_manager.windows[0].screen.areas[0].type = "NLA_EDITOR"
    area = screen.areas[0]
    override = {"window": window, "screen": screen, "area": area}
    obj = bpy.context.object
    bpy.ops.anim.channels_select_all(override, action="DESELECT")
    obj.animation_data.nla_tracks[obj.track_list_index].select = True
    bpy.ops.anim.channels_move(override, direction=dir)

    bpy.context.window_manager.windows[0].screen.areas[0].type = old_area

    visible_layers(bpy.context.object)


class MoveAnimLayerUp(bpy.types.Operator):
    """Move the selected layer up"""

    bl_idname = "anim.layer_move_up"
    bl_label = "Move selected Animation layer up"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        anim_data = context.object.animation_data
        if hasattr(anim_data, "nla_tracks"):
            return len(context.object.animation_data.nla_tracks) > 2

    def execute(self, context):
        handler_key = "animlayers_checks"
        remove_handler(handler_key, bpy.app.handlers.depsgraph_update_pre)

        obj = bpy.context.object
        if obj.track_list_index < len(obj.animation_data.nla_tracks) - 2:

            lock = obj.Anim_Layers[obj.track_list_index].lock
            lock_01 = obj.Anim_Layers[obj.track_list_index + 1].lock
            move_layer("UP")
            # Switch the properties
            (
                obj.Anim_Layers[obj.track_list_index].solo,
                obj.Anim_Layers[obj.track_list_index + 1].solo,
            ) = (
                obj.Anim_Layers[obj.track_list_index + 1].solo,
                obj.Anim_Layers[obj.track_list_index].solo,
            )
            (
                obj.Anim_Layers[obj.track_list_index].mute,
                obj.Anim_Layers[obj.track_list_index + 1].mute,
            ) = (
                obj.Anim_Layers[obj.track_list_index + 1].mute,
                obj.Anim_Layers[obj.track_list_index].mute,
            )
            obj.Anim_Layers[obj.track_list_index].lock = lock_01
            obj.Anim_Layers[obj.track_list_index + 1].lock = lock
            obj.track_list_index += 1

        if handler_key not in driver_namespace:
            bpy.app.handlers.depsgraph_update_pre.append(check_handler)
            driver_namespace[handler_key] = check_handler

        return {"FINISHED"}


class MoveAnimLayerDown(bpy.types.Operator):
    """Move the selected layer down"""

    bl_idname = "anim.layer_move_down"
    bl_label = "Move selected Animation layer down"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        anim_data = context.object.animation_data
        if hasattr(anim_data, "nla_tracks"):
            return len(context.object.animation_data.nla_tracks) > 2

    def execute(self, context):
        handler_key = "animlayers_checks"
        remove_handler(handler_key, bpy.app.handlers.depsgraph_update_pre)

        obj = bpy.context.object
        if obj.track_list_index > 0:

            lock = obj.Anim_Layers[obj.track_list_index].lock
            lock_01 = obj.Anim_Layers[obj.track_list_index - 1].lock
            move_layer("DOWN")
            (
                obj.Anim_Layers[obj.track_list_index].solo,
                obj.Anim_Layers[obj.track_list_index - 1].solo,
            ) = (
                obj.Anim_Layers[obj.track_list_index - 1].solo,
                obj.Anim_Layers[obj.track_list_index].solo,
            )
            (
                obj.Anim_Layers[obj.track_list_index].mute,
                obj.Anim_Layers[obj.track_list_index - 1].mute,
            ) = (
                obj.Anim_Layers[obj.track_list_index - 1].mute,
                obj.Anim_Layers[obj.track_list_index].mute,
            )
            obj.Anim_Layers[obj.track_list_index].lock = lock_01
            obj.Anim_Layers[obj.track_list_index - 1].lock = lock
            obj.track_list_index -= 1

        if handler_key not in driver_namespace:
            bpy.app.handlers.depsgraph_update_pre.append(check_handler)
            driver_namespace[handler_key] = check_handler

        return {"FINISHED"}


def copy_modifiers(modifier, mod_list):
    attr = {}
    for key in dir(modifier):  # add all the attributes into a dictionary
        value = getattr(modifier, key)
        attr.update({key: value})
    mod_list.append(attr)

    return mod_list


def paste_modifiers(fcu, mod_list):

    for mod in mod_list:
        new_mod = fcu.modifiers.new(mod["type"])
        for attr, value in mod.items():
            if type(value) is float or type(value) is int or type(value) is bool:
                if not new_mod.is_property_readonly(attr):
                    setattr(new_mod, attr, value)


class CyclicFcurves(bpy.types.Operator):
    """Apply Cyclic Fcurve modifiers to all the selected bones and objects"""

    bl_idname = "anim.layer_cyclic_fcurves"
    bl_label = "Cyclic_Fcurves"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.object.animation_data.action is not None

    def execute(self, context):

        transform_types = ["location", "rotation_euler", "rotation_quaternion", "scale"]
        for obj in context.selected_objects:
            for fcu in obj.animation_data.action.fcurves:
                if (
                    obj.type == "ARMATURE" and obj.mode == "POSE"
                ):  # apply only to selected bones
                    bones = [
                        bone.path_from_id() for bone in context.selected_pose_bones
                    ]
                    if fcu.data_path.split("].")[0] + "]" not in bones:
                        continue
                else:
                    if fcu.data_path not in transform_types:
                        continue
                cycle_mod = False
                mod_list = []
                if len(fcu.modifiers):
                    # i = 0
                    while len(fcu.modifiers):
                        modifier = fcu.modifiers[0]
                        if modifier.type == "CYCLES":
                            cycle_mod = True
                            break
                        else:  # if its a different modifier then store and remove it
                            mod_list = copy_modifiers(modifier, mod_list)
                            fcu.modifiers.remove(fcu.modifiers[0])
                            # fcu.modifiers.update()
                if cycle_mod:
                    continue
                fcu.modifiers.new("CYCLES")
                fcu.update()
                if not len(mod_list):
                    continue  # restore old modifiers
                paste_modifiers(fcu, mod_list)
                fcu.modifiers.update()

            redraw_areas(["GRAPH_EDITOR", "VIEW_3D"])
            #    if area.type == 'GRAPH_EDITOR' or area.type == 'VIEW_3D':
            #        area.tag_redraw()

        return {"FINISHED"}


class RemoveFcurves(bpy.types.Operator):
    """Remove Cyclic Fcurve modifiers from all the selected bones and objects"""

    bl_idname = "anim.layer_cyclic_remove"
    bl_label = "Cyclic_Remove"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.object.animation_data.action is not None

    def execute(self, context):

        transform_types = ["location", "rotation_euler", "rotation_quaternion", "scale"]
        for obj in context.selected_objects:
            for fcu in obj.animation_data.action.fcurves:
                if (
                    obj.type == "ARMATURE" and obj.mode == "POSE"
                ):  # apply only to selected bones
                    bones = [
                        bone.path_from_id() for bone in context.selected_pose_bones
                    ]
                    if fcu.data_path.split("].")[0] + "]" not in bones:
                        continue
                else:
                    if fcu.data_path not in transform_types:
                        continue
                # cycle_mod = False
                if len(fcu.modifiers):
                    for mod in fcu.modifiers:

                        if mod.type == "CYCLES":
                            fcu.modifiers.remove(mod)
                            fcu.update()
                            for area in context.window_manager.windows[0].screen.areas:
                                if (
                                    area.type == "GRAPH_EDITOR"
                                    or area.type == "VIEW_3D"
                                ):
                                    area.tag_redraw()
                            break
                # fcu.modifiers.update()
        return {"FINISHED"}


class ResetLayerKeyframes(bpy.types.Operator):
    """Add keyframes with 0 Value to the selected object/bones in the current layer, usefull for additive layers"""

    bl_idname = "anim.layer_reset_keyframes"
    bl_label = "Reset_Layer_Keyframes"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return len(context.object.Anim_Layers)

    def execute(self, context):
        obj = context.object
        anim_data = obj.animation_data
        transform_types = ["location", "rotation_euler", "rotation_quaternion", "scale"]
        fcurves = anim_data.action.fcurves
        frame_current = context.scene.frame_current
        for fcu in fcurves:
            if obj.type == "ARMATURE":  # apply only to selected bones
                if obj.mode == "POSE" and fcu.data_path in transform_types:  # skip
                    continue
                elif obj.mode == "POSE":
                    bones = [
                        bone.path_from_id() for bone in context.selected_pose_bones
                    ]
                    if (
                        fcu.data_path.split("].")[0] + "]" not in bones
                    ):  # and fcu.data_path not in transform_types:
                        continue
                elif obj.mode == "OBJECT" and fcu.data_path not in transform_types:
                    continue

            value = 0
            key_exists = False
            blend_types = {"REPLACE", "COMBINE"}
            if (
                "scale" in fcu.data_path
                and anim_data.nla_tracks[obj.track_list_index].strips[0].blend_type
                in blend_types
            ):
                value = 1
            # check if a key already exists on in the current frame
            for key in fcu.keyframe_points:
                if key.co[0] == frame_current:
                    key.co[1] = value
                    key_exists = True
                    fcu.update()
                    continue
            if key_exists:
                continue
            # if key doesnt exists then add keyframes in current frame
            fcu.keyframe_points.add(1)
            fcu.keyframe_points[-1].co = (frame_current, value)
            fcu.update()
        return {"FINISHED"}
