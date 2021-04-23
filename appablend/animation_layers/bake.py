import bpy
from appablend.animation_layers.core import (check_handler, register_layers,
                                             remove_handler,
                                             select_layer_bones, unique_name)
from appablend.animation_layers.ops import (add_animlayer, copy_modifiers,
                                            paste_modifiers)
from bpy.app import driver_namespace


def frame_start_end(scene):

    frame_start = 10000
    frame_end = 0

    for AL_item in scene.AL_objects:
        obj = AL_item.object
        if obj is None:
            continue
        if obj.animation_data is None:
            continue
        for track in obj.animation_data.nla_tracks:
            if len(track.strips) == 1:
                frame_start = min(frame_end, track.strips[0].action.frame_range[0])
                frame_end = max(frame_end, track.strips[0].action.frame_range[1])
    # if scene.use_preview_range:
    #    frame_start = scene.frame_preview_start
    #    frame_end = scene.frame_preview_end
    # else:
    #    frame_start = scene.frame_start
    #    frame_end = scene.frame_end
    return frame_start, frame_end


def smart_start_end(keyframes, frame_start, frame_end):
    """add the first and last frame of the scene if necessery"""
    if not len(keyframes):
        return keyframes
    frames = [key[0] for key in keyframes]
    if min(frames) < frame_start:
        keyframes.append(
            (
                frame_start,
                "LINEAR",
                "VECTOR",
                "VECTOR",
                keyframes[0][4],
                keyframes[0][5],
            )
        )
    if max(frames) > frame_end:
        keyframes.append(
            (
                frame_end,
                "LINEAR",
                "VECTOR",
                "VECTOR",
                keyframes[-1][4],
                keyframes[-1][5],
            )
        )
    keyframes.sort()
    return keyframes


def smart_cycle(keyframes, fcu, frame_start, frame_end):
    for mod in fcu.modifiers:
        if mod.type != "CYCLES" or mod.mute is True:
            continue
        fcu_range = int(fcu.range()[1] - fcu.range()[0])
        if not fcu_range:
            return keyframes
        if not mod.cycles_after and mod.mode_after != "None":
            # if it's an iternal cycle then duplicate the keyframes until the scene frame end
            cycle_end_dup = int((frame_end - fcu.range()[1]) / fcu_range) + 1
            if mod.use_restricted_range and mod.frame_end < frame_end:
                cycle_end_dup = int((mod.frame_end - fcu.range()[1]) / fcu_range) + 1
        elif mod.mode_after != "None":
            cycle_end_dup = mod.cycles_after
            if mod.use_restricted_range and mod.frame_end < (
                fcu.range()[1] + fcu_range * cycle_end_dup
            ):
                cycle_end_dup = int((mod.frame_end - fcu.range()[1]) / fcu_range) + 1

        # duplicate the keys on the cycle before
        keyframes_dup = []
        for key in keyframes[1:]:
            key = list(key)
            for i in range(cycle_end_dup):
                key[0] += fcu_range
                # duplicate the tangents tuple values
                key[4] = tuple((list(key[4])[0] + fcu_range, key[4][1]))
                key[5] = tuple((list(key[5])[0] + fcu_range, key[5][1]))
                if frame_end > key[0] > frame_start:
                    keyframes_dup.append(tuple(key))

        # if it's an iternal cycle then duplicate the keyframes before the cycle keyframes
        if not mod.cycles_before and mod.mode_before != "None":
            cycle_start_dup = int((fcu.range()[0] - frame_start) / fcu_range)
            if mod.use_restricted_range and mod.frame_start > frame_start:
                cycle_start_dup = (
                    int((fcu.range()[0] - mod.frame_start) / fcu_range) + 1
                )
        elif mod.mode_before != "None":
            cycle_start_dup = mod.cycles_before
            if mod.use_restricted_range and mod.frame_start > (
                fcu.range()[0] + fcu_range * cycle_start_dup
            ):
                cycle_start_dup = (
                    int((fcu.range()[0] - mod.frame_start) / fcu_range) + 1
                )
        # duplicate the keys on the cycle before
        for key in keyframes[:-1]:
            key = list(key)
            for i in range(cycle_start_dup):
                key[0] -= fcu_range
                # duplicate the tangents
                key[4] = tuple((list(key[4])[0] - fcu_range, key[4][1]))
                key[5] = tuple((list(key[5])[0] - fcu_range, key[5][1]))
                if frame_end > key[0] > frame_start:
                    keyframes_dup.append(tuple(key))

        # merge the keyframes from the cycle with the original keyframes
        keyframes.extend(keyframes_dup)

        if mod.use_restricted_range:
            keyframes = smart_start_end(keyframes, mod.frame_start, mod.frame_end)
            keyframes = smart_start_end(
                keyframes, mod.frame_start + 1, mod.frame_end - 1
            )

    return keyframes


def smart_bake(self, context):
    obj = bpy.context.object
    frame_start, frame_end = frame_start_end(context.scene)
    fcu_keys = {}
    # for i in range(obj.track_list_index+1):
    for track in obj.animation_data.nla_tracks:
        if track.mute:
            continue
        if len(track.strips) != 1 or track.strips[0].action is None:
            continue
        for fcu in track.strips[0].action.fcurves:
            if not fcu.is_valid or fcu.mute:
                continue
            keyframes = []
            for key in fcu.keyframe_points:
                if key.co not in keyframes:
                    keyframes.append(
                        (
                            key.co[0],
                            key.interpolation,
                            key.handle_left_type,
                            key.handle_right_type,
                            tuple(key.handle_left),
                            tuple(key.handle_right),
                        )
                    )
            if len(fcu.modifiers) and obj.als.mergefcurves:
                keyframes = smart_cycle(keyframes, fcu, frame_start, frame_end)

            # if the list of keyframes exists in a different track list then MERGE them
            if (fcu.data_path, fcu.array_index) in fcu_keys:
                keyframes = list(
                    set(fcu_keys[(fcu.data_path, fcu.array_index)] + keyframes)
                )
                keyframes.sort()
            smart_start_end(keyframes, frame_start, frame_end)
            fcu_keys.update({(fcu.data_path, fcu.array_index): keyframes})
    return fcu_keys


def mute_unbaked_layers(layer_index, nla_tracks, additive):
    obj = bpy.context.object
    # a list to record which layers that are not merged were muted
    mute_rec = []
    # mute the layers that are not going to be baked
    if obj.als.direction == "ALL":
        return mute_rec

    for index, track in enumerate(nla_tracks[:-1]):
        # if running into a replace layer during additive bake then exclude the rest of the layers from the bake
        if track.mute:
            mute_rec.append(track)
            continue
        if (
            additive
            and track.strips[0].blend_type == "REPLACE"
            and index >= layer_index
        ):
            layer_index = len(nla_tracks) - 1
        if obj.als.direction == "DOWN" and index > layer_index:
            track.mute = True
            track.select = False
        if obj.als.direction == "UP" and index < layer_index:
            track.mute = True
            track.select = False

    return mute_rec


def mute_modifiers(context, obj, nla_tracks, frame_start):
    # disable modifiers if merge fcurves is false
    modifier_rec = []
    # extrapolation = False
    global frame_current
    for track in nla_tracks:
        if len(track.strips) != 1 or track.strips[0].action is None:
            continue
        for fcu in track.strips[0].action.fcurves:
            if fcu.lock:
                fcu.lock = False
            if fcu.group is not None:
                if fcu.group.lock:
                    fcu.group.lock = False
            if not fcu.is_valid:
                continue
            if len(fcu.modifiers) > 0 and not obj.als.mergefcurves:
                for mod in fcu.modifiers:
                    if mod.mute == False:
                        modifier_rec.append(mod)
                        mod.mute = True

    return modifier_rec


def unmute_modifiers(obj, nla_tracks, modifier_rec):
    # Turn on fcurve modifiers if merge fcurves is false
    for fcu in nla_tracks[0].strips[0].action.fcurves:
        if not fcu.is_valid:
            continue
        if len(fcu.modifiers) > 0:
            for mod in fcu.modifiers:
                if mod in modifier_rec:
                    mod.mute = False
                elif obj.als.mergefcurves:
                    mod.mute = True


def invisible_layers(obj, b_layers):
    # Store the current invisible layer bones and make them visible for baking
    layers_rec = []
    for i in range(len(b_layers)):
        if b_layers[i] == False:
            layers_rec.append(i)
            b_layers[i] = True
    return layers_rec


def select_keyframed_bones(self, context, obj):
    # Select all keyframed bones in layers if not only selected
    if obj.als.onlyselected:
        return
    if obj.mode != "POSE":
        bpy.ops.object.posemode_toggle()
    bpy.ops.pose.select_all(action="DESELECT")
    for i in range(0, obj.track_list_index + 1):
        obj.track_list_index = i
        select_layer_bones(self, context)


def mute_constraints(obj):
    # Mute constraints if are not cleared during bake
    constraint_rec = []
    if obj.als.clearconstraints:
        return constraint_rec
    for bone in bpy.context.selected_pose_bones:
        for constraint in bone.constraints:
            if constraint.mute == False:
                constraint_rec.append(constraint)
                constraint.mute = True
    return constraint_rec


def smartbake_apply(obj, nla_tracks, fcu_keys):
    # smart bake - delete unnecessery keyframes:
    transform_types = ["location", "rotation_euler", "rotation_quaternion", "scale"]
    strip = nla_tracks[0].strips[0]
    for fcu in strip.action.fcurves:
        if not fcu.is_valid:
            continue

        fcu_key = (fcu.data_path, fcu.array_index)
        if fcu_key in fcu_keys.keys():

            # add keyframes that are missing from the bake but included in the smart bake
            for smart_key in fcu_keys[fcu_key]:
                key_exists = False
                for key in fcu.keyframe_points:
                    if key.co[0] == smart_key[0]:

                        key_exists = True
                        break
                if not key_exists:
                    value = fcu.evaluate(smart_key[0])
                    fcu.keyframe_points.add(1)
                    fcu.keyframe_points[-1].co = (smart_key[0], value)
                    fcu.update()

            # remove unnecessery keyframes
            for i in range(
                int(strip.action.frame_range[0]), int(strip.action.frame_range[1] + 1)
            ):
                key_exists = False
                for smart_key in fcu_keys[fcu_key]:
                    if i == smart_key[0]:
                        # if key was founded add the interpolation and handles
                        for key in fcu.keyframe_points:
                            if key.co[0] == i:
                                key.interpolation = smart_key[1]
                                key.handle_left_type = smart_key[2]
                                key.handle_right_type = smart_key[3]
                                break
                        key_exists = True
                        break
                # delete the keys that are not in the list
                if not key_exists:
                    if fcu.data_path.split(".")[-1] in transform_types:
                        obj.keyframe_delete(fcu_key[0], index=fcu_key[1], frame=i)
                    else:
                        try:
                            obj.keyframe_delete(fcu_key[0], frame=i)
                        except TypeError:
                            pass
        fcu.update()


def armature_restore(obj, b_layers, layers_rec, constraint_rec):
    if obj.type != "ARMATURE":
        return
    # Turn off previous invisible bone layers
    for i in range(len(b_layers)):
        if i in layers_rec:
            b_layers[i] = False

    # Turn on constraints
    if not obj.als.clearconstraints:
        for constraint in constraint_rec:
            constraint.mute = False


def AL_bake(frame_start, frame_end, nla_tracks, fcu_keys):
    frame_start = int(frame_start)
    frame_end = int(frame_end)
    # iterate through all the frames
    obj = bpy.context.object
    if obj is None:
        return
    baked_action = bpy.data.actions.new("Baked action")
    blend_types = {"ADD": "+", "SUBTRACT": "-", "MULTIPLY": "*"}
    # frame_current = bpy.context.scene.frame_current
    for fcu_key, values in fcu_keys.items():
        if obj.als.onlyselected:
            # filter selected bones if option is turned on
            transform_types = [
                "location",
                "rotation_euler",
                "rotation_quaternion",
                "scale",
            ]
            bones = [bone.path_from_id() for bone in bpy.context.selected_pose_bones]
            if (
                fcu_key[0].split("].")[0] + "]" not in bones
                and fcu_key[0] not in transform_types
            ):
                continue
        smart_keys = [keyframe[0] for keyframe in values]
        mod_list = []
        if not smart_keys:
            continue
        for frame in range(frame_start, frame_end + 1):
            if frame not in smart_keys and obj.als.smartbake:
                continue
            if frame > max(smart_keys) or frame < min(smart_keys):
                continue
            evaluate = 0
            # Evaluate the value of the current frame from all the unmuted tracks
            for track in nla_tracks[:-1]:
                if track.mute:
                    continue
                blend_type = track.strips[0].blend_type
                if blend_type == "COMBINE":
                    continue
                fcu = track.strips[0].action.fcurves.find(fcu_key[0], index=fcu_key[1])

                # get the influence value either from the attribute or the fcurve
                if not track.strips[0].fcurves[0].mute and len(
                    track.strips[0].fcurves[0].keyframe_points
                ):
                    influence = track.strips[0].fcurves[0].evaluate(frame)
                else:
                    influence = track.strips[0].influence

                # If there is no scale value on the replace layer, then evaluate the value directly from the channel
                if (
                    (fcu is None or fcu.mute)
                    and track.strips[0].blend_type == "REPLACE"
                    and not evaluate
                ):
                    if "scale" in fcu_key[0] or (
                        "rotation_quaternion" in fcu_key[0] and fcu_key[1] == 0
                    ):
                        if obj.type == "ARMATURE":
                            if "pose.bones" in fcu_key[0]:
                                bone = fcu_key[0].split('"')[1]
                                # evaluate = obj.pose.bones[bone].scale[fcu_key[1]]
                                # evaluate = evaluate * (1 - influence) + obj.pose.bones[bone].scale[fcu_key[1]] * influence
                                evaluate = evaluate * (1 - influence) + influence
                                continue
                        if fcu_key[0] == "scale" or fcu_key[0] == "rotation_quaternion":
                            # evaluate = obj.scale[fcu_key[1]]
                            # evaluate = evaluate * (1 - influence) + obj.pose.bones[bone].scale[fcu_key[1]] * influence
                            evaluate = evaluate * (1 - influence) + influence
                            continue

                if fcu is None or fcu.mute:
                    continue

                if hasattr(fcu, "group"):
                    group = fcu.group.name if fcu.group is not None else None
                else:
                    group = None

                if blend_type == "REPLACE":
                    # if not evaluate and 'scale' in fcu_key[0]:
                    #    evaluate = 1
                    evaluate = (
                        evaluate * (1 - influence) + fcu.evaluate(frame) * influence
                    )

                else:
                    # evaluate += fcu.evaluate(frame) * influence
                    evaluate = eval(
                        str(evaluate)
                        + blend_types[track.strips[0].blend_type]
                        + str(fcu.evaluate(frame))
                        + "*"
                        + str(influence)
                    )

                extrapolation = True if fcu.extrapolation == "LINEAR" else False

                # check for modifiers in the fcurve, copy and append them into mod_list. check for modifiers only one time not every frame
                if len(fcu.modifiers) and not obj.als.mergefcurves and not mod_list:
                    for mod in fcu.modifiers:
                        mod_list = copy_modifiers(mod, mod_list)

            # find or create the fcurve in the new action
            baked_fcu = baked_action.fcurves.find(fcu_key[0], index=fcu_key[1])
            if baked_fcu is None:
                if group is None:
                    baked_fcu = baked_action.fcurves.new(fcu_key[0], index=fcu_key[1])
                else:
                    baked_fcu = baked_action.fcurves.new(
                        fcu_key[0], index=fcu_key[1], action_group=group
                    )

            # add the fcurve evaluation to the current action
            baked_fcu.keyframe_points.add(1)
            keyframe = baked_fcu.keyframe_points[-1]
            keyframe.co = (frame, evaluate)
            # add interpolations to smarbake keys
            if obj.als.smartbake:
                for key in values:
                    if key[0] == frame:
                        interpolation = key
                        break

                # interpolation = [key for key in values if key[0] == frame][0]
                keyframe.interpolation = interpolation[1]
                keyframe.handle_left_type = interpolation[2]
                keyframe.handle_right_type = interpolation[3]
                if keyframe.handle_left_type == "ALIGNED":
                    keyframe.handle_left_type = "AUTO_CLAMPED"
                    # keyframe.handle_left = (interpolation[4][0], interpolation[4][1] + (evaluate - interpolation[0][1]))
                keyframe.handle_left = interpolation[4]
                if keyframe.handle_right_type == "ALIGNED":
                    keyframe.handle_left_type = "AUTO_CLAMPED"
                    # keyframe.handle_right = (interpolation[5][0], interpolation[5][1] + (evaluate - interpolation[0][1]))
                keyframe.handle_right = interpolation[5]

                if extrapolation:
                    baked_fcu.extrapolation = "LINEAR"

            # add in-betweener
            # frame_range / (frame_range * factor)

        baked_fcu.update()

        # paste the modifiers
        if len(mod_list):
            paste_modifiers(baked_fcu, mod_list)

    return baked_action


class MergeAnimLayerDown(bpy.types.Operator):
    """Merge and bake the layers from the current selected layer down to the base"""

    bl_idname = "anim.layers_merge_down"
    bl_label = "Merge_Layers_Down"
    bl_options = {"REGISTER", "UNDO"}

    # limited property of diretion for blender's bake
    direction: bpy.props.EnumProperty(
        name="",
        description="Select direction of merge",
        items=[
            ("DOWN", "Down", "Merge downwards", "TRIA_DOWN", 0),
            ("ALL", "All", "Merge all layers", 1),
        ],
    )

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=200)

    def draw(self, context):
        obj = context.object
        layout = self.layout
        box = layout.box()
        split = box.split(factor=0.5, align=True)
        split.label(text="Bake Type :")
        split.prop(obj.als, "baketype")
        split = box.split(factor=0.5, align=True)
        split.label(text="Bake Operator :")
        split.prop(obj.als, "operator")
        split = box.split(factor=0.5, align=True)
        split.label(text="Bake Direction :")
        if obj.als.baketype == "BLENDER":
            split.prop(self, "direction")
        else:
            split.prop(obj.als, "direction")
        if obj.als.baketype == "BLENDER":
            box.prop(obj.als, "clearconstraints")
        box.prop(obj.als, "mergefcurves")
        box.prop(obj.als, "smartbake")
        box.prop(obj.als, "onlyselected")

    def execute(self, context):
        obj = bpy.context.object
        if obj is None:
            return {"CANCELLED"}
        nla_tracks = obj.animation_data.nla_tracks

        if obj.als.direction == "DOWN" and not obj.track_list_index:
            return {"CANCELLED"}
        if obj.als.direction == "UP" and obj.track_list_index == len(nla_tracks) - 2:
            return {"CANCELLED"}

        handler_key = "animlayers_checks"
        remove_handler(handler_key, bpy.app.handlers.depsgraph_update_pre)

        # define the start and end frame of the bake, according to scene or preview length
        frame_start, frame_end = frame_start_end(bpy.context.scene)
        obj.als.view_all_keyframes = False

        layer_index = obj.track_list_index
        # append all the blend types

        if obj.als.baketype == "BLENDER":
            obj.als.direction = self.direction

        if (
            obj.als.direction == "UP"
            and nla_tracks[obj.track_list_index].strips[0].blend_type == "ADD"
            and obj.als.baketype == "AL"
        ):
            additive = True
            blend = "ADD"
        else:
            additive = False
            blend = "REPLACE"

        if obj.als.operator == "MERGE":
            if obj.als.direction == "DOWN":
                obj.track_list_index = 0
            action_name = obj.animation_data.action.name

        # if baking to a new layer then setup the new index and layer
        elif obj.als.operator == "NEW":
            blendings = [
                track.strips[0].blend_type
                for track in nla_tracks[layer_index:-1]
                if len(track.strips) == 1
            ]
            if obj.als.direction == "UP" and additive and "REPLACE" in blendings:
                obj.track_list_index = layer_index + blendings.index("REPLACE") - 1
            elif obj.als.direction == "UP" or obj.als.direction == "ALL":
                obj.track_list_index = len(obj.Anim_Layers) - 1
            baked_layer = add_animlayer(
                layer_name="Baked_Layer",
                duplicate=False,
                index=obj.track_list_index,
                blend_type=blend,
            )
            register_layers(nla_tracks)
            obj.track_list_index += 1

        mute_rec = mute_unbaked_layers(layer_index, nla_tracks, additive)
        fcu_keys = smart_bake(obj, context)

        # use internal bake
        if obj.als.baketype == "BLENDER":
            modifier_rec = mute_modifiers(context, obj, nla_tracks, frame_start)
            if obj.type == "ARMATURE":
                b_layers = obj.data.layers
                layers_rec = invisible_layers(obj, b_layers)

                select_keyframed_bones(self, context, obj)

                constraint_rec = mute_constraints(obj)

            bpy.ops.nla.bake(
                frame_start=frame_start,
                frame_end=frame_end,
                only_selected=True,
                visual_keying=True,
                clear_constraints=obj.als.clearconstraints,
                use_current_action=True,
                bake_types={"OBJECT", "POSE"},
            )
            unmute_modifiers(obj, nla_tracks, modifier_rec)
            if obj.als.smartbake:
                smartbake_apply(obj, nla_tracks, fcu_keys)
                armature_restore(obj, b_layers, layers_rec, constraint_rec)

        else:  # use anim layers bake
            action = AL_bake(frame_start, frame_end, nla_tracks, fcu_keys)
            obj.animation_data.action = action
            nla_tracks[obj.track_list_index].strips[0].action = action

        # removing layers after merge
        if obj.als.operator == "MERGE":
            nla_tracks[obj.track_list_index].strips[0].blend_type = blend
            if obj.als.baketype == "AL":
                # Rename the old action with a number
                bpy.data.actions[action_name].use_fake_user = False
                bpy.data.actions[action_name].name = unique_name(
                    bpy.data.actions, action_name
                )
                # Rename the current action to the old action
                action.name = action_name

            # delete the baked layers except for the base layer
            if obj.als.direction == "DOWN":
                while layer_index > 0:
                    nla_tracks.remove(nla_tracks[layer_index])
                    layer_index -= 1

            if obj.als.direction == "UP":
                layer_index += 1
                while layer_index < len(nla_tracks) - 1:
                    if (
                        additive
                        and nla_tracks[layer_index].strips[0].blend_type == "REPLACE"
                    ):
                        break
                    nla_tracks.remove(nla_tracks[layer_index])

            if obj.als.direction == "ALL":
                obj.track_list_index = 0
                index = 0
                merged_track = nla_tracks[layer_index]
                while len(nla_tracks) - 1 > 1:
                    if nla_tracks[index] != merged_track:
                        nla_tracks.remove(nla_tracks[index])
                    else:
                        index += 1

            # reset influence of merged layer
            strip = nla_tracks[obj.track_list_index].strips[0]
            while len(strip.fcurves[0].keyframe_points):
                strip.fcurves[0].keyframe_points.remove(
                    strip.fcurves[0].keyframe_points[0]
                )
            strip.influence = 1

        # turn the tracks back on if necessery
        if obj.als.direction != "ALL":
            for track in nla_tracks:
                if track in mute_rec:
                    track.mute = True
                else:
                    track.mute = False

        if obj.als.baketype == "BLENDER":
            unmute_modifiers(obj, nla_tracks, modifier_rec)
            if obj.als.smartbake:
                smartbake_apply(obj, nla_tracks, fcu_keys)
                armature_restore(obj, b_layers, layers_rec, constraint_rec)

        register_layers(nla_tracks)
        if handler_key not in driver_namespace:
            bpy.app.handlers.depsgraph_update_pre.append(check_handler)
            driver_namespace[handler_key] = check_handler

        return {"FINISHED"}
