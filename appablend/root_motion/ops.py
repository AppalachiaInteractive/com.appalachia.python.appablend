import math

import bpy
from appablend.common.actions import insert_keyframe
from appablend.common.armature import in_pose_position
from appablend.common.basetypes.ops import OPS_
from appablend.common.bones import (get_pose_bone_matrix_world,
                                    get_pose_bone_rest_matrix_world)
from appablend.common.core.enums import INTERPOLATION, icons
from appablend.common.core.polling import DOIF
from appablend.common.models.root_motion import RootMotionMetadata
from appablend.common.models.unity import (get_unity_action_and_clip,
                                           get_unity_target)
from appablend.common.utils import hierarchy, iters
from appablend.root_motion.core import apply_pose_to_frame
from appablend.root_motion.mech import *
from appablend.unity.clips import (get_action_mode_clip, get_scene_mode_clip,
                                   sync_with_clip)
from bpy.types import Operator
from mathutils import Matrix


class RM_OT_apply_pose(OPS_, Operator):
    """Applies the pose library pose to the specified frame"""

    bl_idname = "rm.apply_pose"
    bl_label = "Apply Pose"

    pose_name: bpy.props.StringProperty(name="Pose Name")
    frame: bpy.props.IntProperty(name="Frame")
    rooted: bpy.props.BoolProperty(name="Rooted")

    @classmethod
    def do_poll(cls, context):
        return DOIF.UNITY.TARGET.HAS.SOME_UNITY_CLIPS(context)

    def do_execute(self, context):
        obj = get_unity_target(context)
        action = obj.animation_data.action

        for bone in obj.data.bones:
            if bone.parent is None and not self.rooted:
                bone.select = False
            else:
                bone.select = True

        apply_pose_to_frame(context, obj, self.pose_name, self.frame)

        return {"FINISHED"}


class RM_OT_new_pose(OPS_, Operator):
    """Adds the specified frame to the pose library"""

    bl_idname = "rm.new_pose"
    bl_label = "New Pose"

    frame: bpy.props.IntProperty(name="Frame")
    start: bpy.props.BoolProperty(name="Start?")

    @classmethod
    def do_poll(cls, context):
        return DOIF.UNITY.TARGET.HAS.SOME_UNITY_CLIPS(context)

    def do_execute(self, context):
        obj = get_unity_target(context)
        action = obj.animation_data.action
        clip = action.unity_clips[action.unity_metadata.clip_index]

        bpy.ops.poselib.pose_add(frame=self.frame)

        new_pose = obj.pose_library.pose_markers["Pose"]
        new_pose.name = "{0} {1}".format(clip.name, "Start" if self.start else "End")

        if self.start:
            clip.pose_start = new_pose.name
        else:
            clip.pose_end = new_pose.name

        return {"FINISHED"}


class RM_OT_refresh_settings(OPS_, Operator):
    bl_idname = "rm.refresh_settings"
    bl_label = "Refresh and Transfer Root Motion Settings"

    @classmethod
    def do_poll(cls, context):
        return DOIF.DATA.ACTIONS(context)

    def do_execute(self, context):
        for action in bpy.data.actions:
            if action.unity_clips:
                for clip in action.unity_clips:
                    clip.root_motion.copy_from_clip(clip)
        for armature in bpy.data.armatures:
            if armature.root_motion_settings:
                armature.root_motion_settings.copy_from_armature(armature)


class RM_OT_create_root_motion_setup(OPS_, Operator):
    bl_idname = "rm.create_root_motion_setup"
    bl_label = "Create Root Motion Mech Rig"

    @classmethod
    def do_poll(cls, context):
        ao = get_unity_target(context)
        if not ao:
            return False
        s = ao.data.root_motion_settings
        if not s:
            return False

        if s.original_root_bone == "":
            return False

        return True

    def do_execute(self, context):
        bpy.ops.rm.settings_to_curves_all()

        create_root_motion_setup(context, get_unity_target(context))


class RM_OT_common:
    group_name = "Root Motion Settings"

    def generate_root_motion_curves(self, context, armature, action):
        if len(action.unity_clips) != 1:
            return

        clip = action.unity_clips[0]

        for ci, fcurve in iters.reverse_enumerate(action.fcurves):
            if fcurve.group and fcurve.group.name == RM_OT_common.group_name:
                for ki, key in iters.reverse_enumerate(fcurve.keyframe_points):
                    fcurve.keyframe_points.remove(key)
                action.fcurves.remove(fcurve)

        root_motion_keys = RootMotionMetadata.root_motion_keys

        updated_paths = []

        for data_path in root_motion_keys:
            value = getattr(clip.root_motion, data_path)
            has_length = getattr(value, "__len__", None)
            index_values = []

            if has_length:
                for i, v in enumerate(value):
                    index_values.append((i, v))
            else:
                index_values.append((-1, value))

            for i, v in index_values:
                base_path = data_path

                is_start = False
                is_end = False

                if data_path.endswith("_start"):
                    is_start = True
                    base_path = base_path.replace("_start", "")
                elif data_path.endswith("_end"):
                    is_end = True
                    base_path = base_path.replace("_end", "")

                path = base_path
                if i != -1:
                    path = "{0}_{1}".format(base_path, i)

                updated_paths.append(path)
                fcurve = action.fcurves.find(path, index=-1)

                if not fcurve:
                    fcurve = action.fcurves.new(
                        path, index=-1, action_group=self.group_name
                    )

                if not getattr(bpy.types.Object, path, None):
                    setattr(bpy.types.Object, path, bpy.props.FloatProperty(name=path))

                setattr(armature, path, v)

                s = clip.frame_start
                e = clip.frame_end

                frames = []

                if is_start:
                    frames.append(s)
                elif is_end:
                    frames.append(e)
                else:
                    frames.append(s)
                    frames.append(e)

                for f in frames:
                    k = insert_keyframe(fcurve, f, v, needed=False, fast=True)
                    k.interpolation = INTERPOLATION.LINEAR

                if is_end:
                    blend_key = (
                        base_path.replace("rotation", "")
                        .replace("location", "")
                        .strip("_")
                    )

                    if hasattr(clip.root_motion, "{0}_blend_low".format(blend_key)):
                        rm = clip.root_motion
                        prop_low = "{0}_blend_low".format(blend_key)
                        prop_mid = "{0}_blend_mid".format(blend_key)
                        prop_high = "{0}_blend_high".format(blend_key)

                        blend_low = getattr(rm, prop_low)
                        blend_mid = getattr(rm, prop_mid)
                        blend_high = getattr(rm, prop_high)

                        if blend_low == 0.0 and blend_mid == 0.5 and blend_high == 1.0:
                            continue

                        duration = e - s
                        midpoint = s + (duration / 2.0)
                        val_low = fcurve.evaluate(s)
                        val_mid = fcurve.evaluate(midpoint)
                        val_high = fcurve.evaluate(e)

                        frame_low = int(s + (blend_low * duration))
                        frame_mid = int(s + (blend_mid * duration))
                        frame_high = int(s + (blend_high * duration))

                        if frame_low != s:
                            k = insert_keyframe(
                                fcurve, frame_low, val_low, needed=False, fast=True
                            )
                            k.interpolation = INTERPOLATION.LINEAR

                        k = insert_keyframe(
                            fcurve, frame_mid, val_mid, needed=False, fast=True
                        )
                        k.interpolation = INTERPOLATION.LINEAR

                        if frame_high != e:
                            k = insert_keyframe(
                                fcurve, frame_high, val_high, needed=False, fast=True
                            )
                            k.interpolation = INTERPOLATION.LINEAR

        for data_path in updated_paths:
            fcurve = action.fcurves.find(data_path, index=-1)
            if fcurve is None:
                continue
            fcurve.update()

    def print_loc(prefix, loc):
        string = "[{0}]  x:{1}m,  y:{2}m,  z:{3}m".format(prefix, loc.x, loc.y, loc.z)
        print(string)

    def print_quat(prefix, quat, order="XYZ"):
        euler = quat.to_euler(order)
        string = "[{0}]  x:{1},  y:{2},  z:{3}".format(
            prefix, math.degrees(euler.x), math.degrees(euler.y), math.degrees(euler.z)
        )
        print(string)

    @classmethod
    def initiate_poll(cls, context):
        c = context
        s = c.scene
        has_clips = DOIF.UNITY.TARGET.HAS.SOME_UNITY_CLIPS(c)

        return c, s, has_clips

    def initiate_execute(self, context):
        c = context
        s = c.scene
        original_frame = s.frame_current
        s.frame_set(1)

        armature = get_unity_target(c)

        return (
            c,
            s,
            armature,
            original_frame,
        )

    def complete_execute(self, context, original_frame):
        context.scene.frame_set(original_frame)


class RM_OT_current_clip(RM_OT_common):
    @classmethod
    def do_poll(cls, context):
        c, s, has_clips = cls.initiate_poll(context)
        return has_clips

    def do_execute(self, context):
        c, s, armature, original_frame = self.initiate_execute(context)

        action, clip, clip_index = get_unity_action_and_clip(context)

        self.sync_clip(context, clip)
        self.process_clip(c, armature, clip, clip_index)
        self.generate_root_motion_curves(context, armature, clip.action)

        self.complete_execute(c, original_frame)

        return {"FINISHED"}

    def get_clips(self, context):
        action, clip, clip_index = get_unity_action_and_clip(context)
        return action.unity_clips

    def sync_clip(self, context, clip):
        s = context.scene
        if s.unity_settings.mode == "SCENE":
            sync_with = get_action_mode_clip(context, clip)
        else:
            sync_with = get_scene_mode_clip(context, clip)

        sync_with_clip(context, clip, sync_with)


class RM_OT_all_clips(RM_OT_common):
    @classmethod
    def do_poll(cls, context):
        c, s, has_clips = cls.initiate_poll(context)
        return has_clips

    def do_execute(self, context):
        c, s, armature, original_frame = self.initiate_execute(context)
        osi = s.unity_settings.clip_index

        rms = armature.data.root_motion_settings

        clips = self.get_clips(c)

        for clip_index in range(len(clips)):
            clip = clips[clip_index]

            s.unity_settings.active_action = clip.action

            self.set_clip_index(context, clip, clip_index)

            self.sync_clip(c, clip)
            self.process_clip(c, armature, clip, clip_index)
            self.generate_root_motion_curves(context, armature, clip.action)

        s.unity_settings.clip_index = osi
        self.complete_execute(c, original_frame)
        return {"FINISHED"}

    def get_clips(self, context):
        s = context.scene
        if s.unity_settings.mode == "SCENE":
            return s.all_unity_clips
        elif s.unity_settings.mode == "TARGET":
            return [clip for action in bpy.data.actions for clip in action.unity_clips]
        else:
            action, clip, clip_index = get_unity_action_and_clip(context)
            return action.unity_clips

    def set_clip_index(self, context, clip, clip_index):
        s = context.scene
        if s.unity_settings.mode == "SCENE":
            s.unity_settings.clip_index = clip_index
        else:
            s.active_action.unity_settings.clip_index = clip_index

    def sync_clip(self, context, clip):
        s = context.scene

        if s.unity_settings.mode == "SCENE":
            action_clip = get_action_mode_clip(context, clip)
            sync_with_clip(context, clip, action_clip)
        else:
            scene_clip = get_scene_mode_clip(context, clip)
            sync_with_clip(context, clip, scene_clip)


class RM_OT_settings_to_curves(RM_OT_current_clip, OPS_, Operator):
    """Adds animation curves for root motion settings."""

    bl_idname = "rm.settings_to_curves"
    bl_label = "To Curves"

    def process_clip(self, context, armature, clip, clip_index):
        pass


class RM_OT_settings_to_curves_all(RM_OT_all_clips, OPS_, Operator):
    """Adds animation curves for root motion settings to all actions."""

    bl_idname = "rm.settings_to_curves_all"
    bl_label = "To Curves (All)"

    def process_clip(self, context, armature, clip, clip_index):
        pass


class RM:
    @classmethod
    def _get_value_variations(cls, value):
        options = [
            value,
            value.lower(),
            value.upper(),
            value.capitalize(),
            value.strip("s"),
            value.lower().strip("s"),
            value.capitalize().strip("s"),
            value + "s",
            value.lower() + "s",
            value.capitalize() + "s",
        ]

        return options

    @classmethod
    def parse(cls, values, value):
        options = cls._get_value_variations(value)

        for option in options:
            if option in values:
                return option

        raise ValueError(value)

    class OPERATION:
        REST = "set_to_rest"
        CURSOR_SET = "set_to_cursor"
        CURSOR_START = "start_at_cursor"
        RESET = "reset"

        @classmethod
        def parse(cls, value):
            return RM.parse(
                [cls.REST, cls.CURSOR_SET, cls.CURSOR_START, cls.RESET], value
            )

    class TARGET:
        ORIGIN = "origin"
        SETTINGS = "settings"
        ROOT = "Root"
        HIPS = "Hips"

        @classmethod
        def parse(cls, value):
            return RM.parse([cls.ORIGIN, cls.SETTINGS, cls.ROOT, cls.HIPS], value)

    class PHASE:
        START = "start"
        END = "end"

        @classmethod
        def parse(cls, value):
            return RM.parse([cls.START, cls.END], value)


class RM_OT_options:
    target: bpy.props.StringProperty("Target")
    operation: bpy.props.StringProperty("Operation")
    phase: bpy.props.StringProperty("Phase")

    @classmethod
    def operator(cls, layout, icon, text, target, operation, phase):
        o = layout.operator(cls.bl_idname, icon=icon, text=text)
        o.target, o.operation, o.phase = target, operation, phase.lower()
        return o

    @classmethod
    def rest_operator(cls, layout, target, phase):
        return cls.operator(
            layout, icons.POSE_HLT, "Rest", target, RM.OPERATION.REST, phase
        )

    @classmethod
    def reset_operator(cls, layout, target, phase):
        return cls.operator(
            layout, icons.CANCEL, "Reset", target, RM.OPERATION.RESET, phase
        )

    @classmethod
    def cursor_set_operator(cls, layout, target, phase):
        return cls.operator(
            layout, icons.CURSOR, "Cursor", target, RM.OPERATION.CURSOR_SET, phase
        )

    @classmethod
    def cursor_start_operator(cls, layout, target, phase):
        return cls.operator(
            layout,
            icons.ORIENTATION_CURSOR,
            "Cursor Offset",
            target,
            RM.OPERATION.CURSOR_START,
            phase,
        )

    def raise_exception(self, message=""):
        prefix = "" if message == "" else "{0}: ".format(message)
        raise ValueError(
            "{0}{1}".format(
                prefix, ", ".join([self.target, self.operation, self.phase])
            )
        )

    def get_options(self):
        print("[RM]: {0}".format("get_options"))
        target = RM.TARGET.parse(self.target)
        operation = RM.OPERATION.parse(self.operation)
        phase = RM.PHASE.parse(self.phase)

        return target, operation, phase

    def get_current_matrix(self, context, armature, clip):
        target, operation, phase = self.get_options()
        print(
            "[RM]: {0} | {1}".format(
                "get_current_matrix", ", ".join([target, operation, phase])
            )
        )
        rms = armature.data.root_motion_settings
        rm = clip.root_motion

        if operation == RM.OPERATION.RESET:
            return Matrix.Identity(4)

        elif (
            operation == RM.OPERATION.CURSOR_SET
            or operation == RM.OPERATION.CURSOR_START
        ):

            if target == RM.TARGET.SETTINGS:
                self.raise_exception("TARGET")

            elif target == RM.TARGET.ORIGIN:
                return rms.root_final.matrix_world

            elif target == RM.TARGET.ROOT:
                return rms.root_bone_offset.matrix_world

            elif target == RM.TARGET.HIPS:
                return rms.hip_bone_offset.matrix_world

            else:
                self.raise_exception("TARGET")

        elif operation == RM.OPERATION.REST:

            if target == RM.TARGET.SETTINGS:
                self.raise_exception("TARGET")

            elif target == RM.TARGET.ORIGIN:
                return rms.root_node.matrix_world

            elif target == RM.TARGET.ROOT:
                return get_pose_bone_matrix_world(armature, target)

            elif target == RM.TARGET.HIPS:
                return get_pose_bone_matrix_world(armature, target)
            else:
                self.raise_exception("TARGET")

        self.raise_exception()

    def get_target_matrix(self, context, armature, clip):
        target, operation, phase = self.get_options()
        print(
            "[RM]: {0} | {1}".format(
                "get_target_matrix", ", ".join([target, operation, phase])
            )
        )
        rms = armature.data.root_motion_settings
        rm = clip.root_motion

        if operation == RM.OPERATION.RESET:
            return Matrix.Identity(4)

        elif (
            operation == RM.OPERATION.CURSOR_SET
            or operation == RM.OPERATION.CURSOR_START
        ):
            if target == RM.TARGET.SETTINGS:
                self.raise_exception("TARGET")

            elif target == RM.TARGET.ORIGIN:
                return context.scene.cursor.matrix

            elif target == RM.TARGET.ROOT:
                return context.scene.cursor.matrix

            elif target == RM.TARGET.HIPS:
                return context.scene.cursor.matrix

            else:
                self.raise_exception("OPERATION")

        elif operation == RM.OPERATION.REST:
            if target == RM.TARGET.SETTINGS:
                self.raise_exception("TARGET")

            elif target == RM.TARGET.ORIGIN:
                return armature.matrix_world

            elif target == RM.TARGET.ROOT:
                return get_pose_bone_rest_matrix_world(armature, target)

            elif target == RM.TARGET.HIPS:
                return get_pose_bone_rest_matrix_world(armature, target)
            else:
                self.raise_exception("TARGET")

        self.raise_exception()

    def get_matrices(self, context, armature, clip):
        print("[RM]: {0}".format("get_matrices"))
        return self.get_current_matrix(context, armature, clip), self.get_target_matrix(
            context, armature, clip
        )

    def get_assignment(self, context, armature, clip):
        target, operation, phase = self.get_options()
        print(
            "[RM]: {0} | {1}".format(
                "get_assignment", ", ".join([target, operation, phase])
            )
        )
        rms = armature.data.root_motion_settings
        rm = clip.root_motion

        if target == RM.TARGET.SETTINGS:
            self.raise_exception("TARGET")

        elif target == RM.TARGET.ORIGIN:
            return rm.root_node_start_location, rm.root_node_start_rotation

        elif target == RM.TARGET.ROOT:
            if phase == RM.PHASE.START:
                return (
                    rm.root_bone_offset_location_start,
                    rm.root_bone_offset_rotation_start,
                )

            elif phase == RM.PHASE.END:
                return (
                    rm.root_bone_offset_location_end,
                    rm.root_bone_offset_rotation_end,
                )

            else:
                self.raise_exception("PHASE")

        elif target == RM.TARGET.HIPS:
            if phase == RM.PHASE.START:
                return (
                    rm.hip_bone_offset_location_start,
                    rm.hip_bone_offset_rotation_start,
                )

            elif phase == RM.PHASE.END:
                return rm.hip_bone_offset_location_end, rm.hip_bone_offset_rotation_end

            else:
                self.raise_exception("PHASE")

        self.raise_exception("TARGET")

    def set_offset(self, context, armature, clip, clip_index):
        target, operation, phase = self.get_options()
        print(
            "[RM]: {0} | {1}".format(
                "set_offset", ", ".join([target, operation, phase])
            )
        )
        rms = armature.data.root_motion_settings
        rm = clip.root_motion

        if phase == RM.PHASE.START and context.scene.frame_current != clip.frame_start:
            context.scene.frame_set(clip.frame_start)
        elif phase == RM.PHASE.END and context.scene.frame_current != clip.frame_end:
            context.scene.frame_set(clip.frame_end)

        current_matrix, target_matrix = self.get_matrices(context, armature, clip)

        current_loc, current_quat, _ = current_matrix.decompose()
        target_loc, target_quat, _ = target_matrix.decompose()

        target_euler = target_quat.to_euler("XYZ")

        diff_loc = target_loc - current_loc
        diff_rot = current_quat.rotation_difference(target_quat)
        diff_euler = diff_rot.to_euler("XYZ")

        set_loc, set_rot = self.get_assignment(context, armature, clip)

        print(
            "[RM]: {0} | {1}".format(
                "assignment", ", ".join([target, operation, phase])
            )
        )

        if operation == RM.OPERATION.RESET:
            print(
                "[RM]: {0} | {1}".format(
                    "assignment: RESET", ", ".join([target, operation, phase])
                )
            )
            set_loc.x, set_loc.y, set_loc.z = target_loc.x, target_loc.y, target_loc.z
            set_rot.x, set_rot.y, set_rot.z = (
                target_euler.x,
                target_euler.y,
                target_euler.z,
            )

        elif operation == RM.OPERATION.CURSOR_SET:
            print(
                "[RM]: {0} | {1}".format(
                    "assignment: RESET", ", ".join([target, operation, phase])
                )
            )
            set_loc += diff_loc

        elif operation == RM.OPERATION.CURSOR_START:
            print(
                "[RM]: {0} | {1}".format(
                    "assignment: RESET", ", ".join([target, operation, phase])
                )
            )
            set_loc += diff_loc

        elif operation == RM.OPERATION.REST:
            print(
                "[RM]: {0} | {1}".format(
                    "assignment: RESET", ", ".join([target, operation, phase])
                )
            )
            if target == RM.TARGET.ROOT:
                set_loc.x, set_loc.y, set_loc.z = diff_loc.x, diff_loc.y, diff_loc.z
                set_rot.x, set_rot.y, set_rot.z = (
                    diff_euler.x,
                    diff_euler.y,
                    diff_euler.z,
                )

            elif target == RM.TARGET.HIPS:
                set_loc += diff_loc
                set_rot.rotate(diff_euler)

            elif target == RM.TARGET.ORIGIN:
                set_loc += diff_loc
                set_rot.rotate(diff_euler)

            else:
                self.raise_exception()
        else:
            print(
                "[RM]: {0} | {1}".format(
                    "assignment: EXCEPTION", ", ".join([target, operation, phase])
                )
            )
            self.raise_exception()

        rm.update_disabled = False
        print(
            "[RM]: {0} | {1}".format(
                "assignment: COMPLETE", ", ".join([target, operation, phase])
            )
        )


class RM_OT_set_offset(RM_OT_options, RM_OT_current_clip, OPS_, Operator):
    """Sets the root motion offset in the specified manner."""

    bl_idname = "rm.set_offset"
    bl_label = "RM: Set Offset"

    def process_clip(self, context, armature, clip, clip_index):
        target, operation, phase = self.get_options()

        if target == RM.TARGET.SETTINGS:
            clip.root_motion.root_motion_x_offset = 0
            clip.root_motion.root_motion_y_offset = 0
            clip.root_motion.root_motion_z_offset = 0
            clip.root_motion.root_motion_rot_offset = 0
        else:
            self.set_offset(context, armature, clip, clip_index)


class RM_OT_set_offset_all(RM_OT_options, RM_OT_all_clips, OPS_, Operator):
    """Sets the root motion offset to return the root to its rest position for all scene clips."""

    bl_idname = "rm.set_offset_all"
    bl_label = "RM: To Rest (All)"

    def process_clip(self, context, armature, clip, clip_index):
        self.set_offset(context, armature, clip, clip_index)


class RM_OT_push_rotation_offsets(RM_OT_current_clip, OPS_, Operator):
    """Pushes rotation offsets to be applied to the root and hip bones for correction."""

    bl_idname = "rm.push_rotation_offsets"
    bl_label = "RM: Push Rotation Offset"
    bl_icon = icons.CON_ROTLIKE

    def process_clip(self, context, armature, clip, index):
        r = math.radians(clip.root_motion.root_motion_rot_offset)
        clip.root_motion.root_bone_offset_rotation_start.z = r
        clip.root_motion.root_bone_offset_rotation_end.z = r
        clip.root_motion.hip_bone_offset_rotation_start.z = r
        clip.root_motion.hip_bone_offset_rotation_end.z = r


class RM_OT_push_location_offsets(RM_OT_current_clip, OPS_, Operator):
    """Pushes location offsets to be applied to the root and hip bones for correction."""

    bl_idname = "rm.push_location_offsets"
    bl_label = "RM: Push Location Offset"
    bl_icon = icons.CON_LOCLIKE

    def process_clip(self, context, armature, clip, index):
        rm = clip.root_motion

        rm.hip_bone_offset_location_start.x = rm.root_node_start_location.x
        rm.hip_bone_offset_location_start.y = rm.root_node_start_location.y
        rm.hip_bone_offset_location_end.x = rm.root_node_start_location.x
        rm.hip_bone_offset_location_end.y = rm.root_node_start_location.y


class RM_OT_push_rotation_offsets_all(RM_OT_all_clips, OPS_, Operator):
    """Pushes rotation offsets to be applied to the root and hip bones for correction."""

    bl_idname = "rm.push_rotation_offsets_all"
    bl_label = "RM: Push Rotation Offsets (All)"
    bl_icon = icons.CON_ROTLIKE

    def process_clip(self, context, armature, clip, index):
        r = math.radians(clip.root_motion.root_motion_rot_offset)
        clip.root_motion.root_bone_offset_rotation_start.z = r
        clip.root_motion.root_bone_offset_rotation_end.z = r
        clip.root_motion.hip_bone_offset_rotation_start.z = r
        clip.root_motion.hip_bone_offset_rotation_end.z = r


class RM_OT_push_location_offsets_all(RM_OT_all_clips, OPS_, Operator):
    """Pushes location offsets to be applied to the root and hip bones for correction."""

    bl_idname = "rm.push_location_offsets_all"
    bl_label = "RM: Push Location Offsets (All)"
    bl_icon = icons.CON_LOCLIKE

    def process_clip(self, context, armature, clip, index):
        rm = clip.root_motion

        rm.hip_bone_offset_location_start.x = rm.root_node_start_location.x
        rm.hip_bone_offset_location_start.y = rm.root_node_start_location.y
        rm.hip_bone_offset_location_end.x = rm.root_node_start_location.x
        rm.hip_bone_offset_location_end.y = rm.root_node_start_location.y


class RM_OT_reset_offsets_all(RM_OT_all_clips, OPS_, Operator):
    """Resets all offsets."""

    bl_idname = "rm.reset_offsets_all"
    bl_label = "RM: Reset All Offsets"
    bl_icon = icons.CANCEL

    def process_clip(self, context, armature, clip, index):
        rm = clip.root_motion

        rm.root_node_start_location = [0, 0, 0]
        rm.root_node_start_rotation = [0, 0, 0]
        rm.root_bone_offset_location_start = [0, 0, 0]
        rm.root_bone_offset_location_end = [0, 0, 0]
        rm.hip_bone_offset_location_start = [0, 0, 0]
        rm.hip_bone_offset_location_end = [0, 0, 0]
        rm.root_bone_offset_rotation_start = [0, 0, 0]
        rm.root_bone_offset_rotation_end = [0, 0, 0]
        rm.hip_bone_offset_rotation_start = [0, 0, 0]
        rm.hip_bone_offset_rotation_end = [0, 0, 0]


class RM_OT_refresh_childof_constraints(RM_OT_current_clip, OPS_, Operator):
    """Refreshes the childof matrices for root motion mech devices."""

    bl_idname = "rm.refresh_childof_constraints"
    bl_label = "RM: Refresh Child Of Constraint Matrices"
    bl_icon = icons.CON_CHILDOF

    def process_clip(self, context, armature, clip, index):
        collection = "Root Motion"

        restore_pose_position = in_pose_position(armature)

        to_rest_position(armature)
        all_objects = reversed(hierarchy.get_collection_hierarchy(collection))

        for obj in all_objects:
            for constraint in obj.constraints:
                if constraint.type == "CHILD_OF":
                    constraint.inverse_matrix = (
                        constraint.target.matrix_world.inverted()
                    )
                    print(
                        "{0}: {1} consstraint matrix reset.".format(
                            obj.name, constraint.name
                        )
                    )

        if restore_pose_position:
            to_pose_position(armature)
