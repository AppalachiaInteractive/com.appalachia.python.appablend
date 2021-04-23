
import bpy
from appablend.common.actions import (copy_from_action_range,
                                      insert_keyframe_extreme)
from appablend.common.core.subtypes import *
from appablend.common.models.root_motion import RootMotionMetadata
from appablend.common.utils import files, objects


def get_unity_target(context):
    obj = None
    if context.scene.unity_settings.mode == "SCENE":
        obj = context.scene.unity_settings.target_armature
    elif context.scene.unity_settings.mode == "TARGET":
        obj = context.scene.unity_settings.target_armature
    else:
        obj = context.active_object

    if obj is None:
        return None
    if obj.animation_data is None:
        obj.animation_data_create()

    return obj


def apply_clip_by_index(context, clip_index):
    if clip_index < 0:
        return
    scene = context.scene
    clip = scene.all_unity_clips[clip_index]
    action = clip.action

    scene.unity_settings.active_action = action

    obj = get_unity_target(context)

    obj.animation_data.action = action
    context.scene.frame_start = clip.frame_start
    context.scene.frame_end = clip.frame_end

    context.scene.frame_set(clip.frame_start)


def get_unity_action_and_clip(context):
    try:
        scene = context.scene
        settings = scene.unity_settings

        obj = get_unity_target(context)

        action = None
        clip = None
        index = 0

        if not obj or not obj.animation_data or not obj.animation_data.action:
            return action, clip, index

        if (
            scene.unity_settings.mode == "SCENE"
            and scene.all_unity_clips
            and len(scene.all_unity_clips) > 0
        ):
            clip = scene.all_unity_clips[scene.unity_settings.clip_index]
            action = clip.action
            index = settings.clip_index
        else:
            action = settings.active_action
            if (
                action is not None
                and action.unity_clips
                and len(action.unity_clips) > 0
            ):
                clip = action.unity_clips[action.unity_metadata.clip_index]
                index = action.unity_metadata.clip_index

        return action, clip, index
    except Exception as inst:
        print("get_unity_action_and_clip: {0}".format(inst))
        raise


def update_clip_index(self, context):
    action, clip, clip_index = get_unity_action_and_clip(context)
    if self.id_data != action:
        return
    clip = action.unity_clips[action.unity_metadata.clip_index]

    context.scene.frame_start = clip.frame_start
    context.scene.frame_end = clip.frame_end
    context.scene.frame_set(clip.frame_start)
    bpy.ops.timeline.view_clip()

def update_clip_index_scene(self, context):
    scene = context.scene
    apply_clip_by_index(context, scene.unity_settings.clip_index)

    bpy.ops.timeline.view_clip()


class UnityActionMetadata(bpy.types.PropertyGroup):
    clips_protected: bpy.props.BoolProperty(name="Clip Data Protected")
    clips_hidden: bpy.props.BoolProperty(name="Clips Hidden")
    master_action: bpy.props.BoolProperty(name="Master Action")
    clip_template: bpy.props.PointerProperty(
        name="Unity Clip Template", type=bpy.types.Action
    )
    clip_index: bpy.props.IntProperty(
        name="Unity Index", default=-1, min=-1, update=update_clip_index
    )
    split_from: bpy.props.PointerProperty(name="Action", type=bpy.types.Action)


class UnityClipMetadata(bpy.types.PropertyGroup):
    can_edit: bpy.props.BoolProperty(name="Can Edit")
    fbx_name: bpy.props.StringProperty(name="FBX Name")
    name: bpy.props.StringProperty(name="Clip Name")
    action: bpy.props.PointerProperty(name="Action", type=bpy.types.Action)
    frame_start: bpy.props.IntProperty(name="Frame Start")
    frame_end: bpy.props.IntProperty(name="Frame End")
    source_action: bpy.props.PointerProperty(
        name="Source Action", type=bpy.types.Action
    )
    source_frame_start: bpy.props.IntProperty(name="Source Frame Start")
    source_frame_end: bpy.props.IntProperty(name="Source Frame End")
    source_frame_shift: bpy.props.IntProperty(name="Source Frame Shift")

    root_motion: bpy.props.PointerProperty(name="Root Motion", type=RootMotionMetadata)

    pose_start: bpy.props.StringProperty(name="Pose Start")
    pose_end: bpy.props.StringProperty(name="Pose End")
    pose_start_rooted: bpy.props.BoolProperty(name="Pose Start Rooted")
    pose_end_rooted: bpy.props.BoolProperty(name="Pose End Rooted")
    loop_time: bpy.props.BoolProperty(name="Loop Time")

    root_node_start_location: bpy.props.FloatVectorProperty(
        name="Root Node Start Location",
        subtype=ST_FloatVectorProperty.Subtypes.TRANSLATION,
        size=3,
    )
    root_node_start_rotation: bpy.props.FloatVectorProperty(
        name="Root Node Start Rotation",
        subtype=ST_FloatVectorProperty.Subtypes.EULER,
        size=3,
        default=[0, 0, 0],
    )

    root_motion_rot_bake_into: bpy.props.BoolProperty(
        name="Root Rotation - Bake Into Pose"
    )
    root_motion_x_bake_into: bpy.props.BoolProperty(
        name="Root Position X - Bake Into Pose"
    )
    root_motion_y_bake_into: bpy.props.BoolProperty(
        name="Root Position Y - Bake Into Pose"
    )
    root_motion_z_bake_into: bpy.props.BoolProperty(
        name="Root Position Z - Bake Into Pose"
    )

    root_motion_x_limit_neg: bpy.props.BoolProperty(name="X Limit Neg.")
    root_motion_x_limit_neg_val: bpy.props.FloatProperty(
        name="X Limit Neg. Val", unit=ST_FloatProperty.Units.LENGTH
    )
    root_motion_x_limit_pos: bpy.props.BoolProperty(name="X Limit Pos.")
    root_motion_x_limit_pos_val: bpy.props.FloatProperty(
        name="X Limit Pos. Val", unit=ST_FloatProperty.Units.LENGTH
    )
    root_motion_y_limit_neg: bpy.props.BoolProperty(name="Y Limit Neg.")
    root_motion_y_limit_neg_val: bpy.props.FloatProperty(
        name="Y Limit Neg. Val", unit=ST_FloatProperty.Units.LENGTH
    )
    root_motion_y_limit_pos: bpy.props.BoolProperty(name="Y Limit Pos.")
    root_motion_y_limit_pos_val: bpy.props.FloatProperty(
        name="Y Limit Pos. Val", unit=ST_FloatProperty.Units.LENGTH
    )
    root_motion_z_limit_neg: bpy.props.BoolProperty(name="Z Limit Neg.")
    root_motion_z_limit_neg_val: bpy.props.FloatProperty(
        name="Z Limit Neg. Val", unit=ST_FloatProperty.Units.LENGTH
    )
    root_motion_z_limit_pos: bpy.props.BoolProperty(name="Z Limit Pos.")
    root_motion_z_limit_pos_val: bpy.props.FloatProperty(
        name="Z Limit Pos. Val", unit=ST_FloatProperty.Units.LENGTH
    )

    root_motion_rot_offset: bpy.props.FloatProperty(name="Root Rotation -  Offset")
    root_motion_x_offset: bpy.props.FloatProperty(name="Root Offset X")
    root_motion_y_offset: bpy.props.FloatProperty(name="Root Offset Y")
    root_motion_z_offset: bpy.props.FloatProperty(name="Root Offset Z")

    root_bone_offset_location_start: bpy.props.FloatVectorProperty(
        name="Root Bone Offset Location Start",
        subtype=ST_FloatVectorProperty.Subtypes.TRANSLATION,
        size=3,
    )
    root_bone_offset_rotation_start: bpy.props.FloatVectorProperty(
        name="Root Bone Offset Rotation Start",
        subtype=ST_FloatVectorProperty.Subtypes.EULER,
        size=3,
        default=[0, 0, 0],
    )
    root_bone_offset_location_end: bpy.props.FloatVectorProperty(
        name="Root Bone Offset Location End",
        subtype=ST_FloatVectorProperty.Subtypes.TRANSLATION,
        size=3,
    )
    root_bone_offset_rotation_end: bpy.props.FloatVectorProperty(
        name="Root Bone Offset Rotation End",
        subtype=ST_FloatVectorProperty.Subtypes.EULER,
        size=3,
        default=[0, 0, 0],
    )

    hip_bone_offset_location_start: bpy.props.FloatVectorProperty(
        name="Hip Bone Offset Location Start",
        subtype=ST_FloatVectorProperty.Subtypes.TRANSLATION,
        size=3,
    )
    hip_bone_offset_rotation_start: bpy.props.FloatVectorProperty(
        name="Hip Bone Offset Rotation Start",
        subtype=ST_FloatVectorProperty.Subtypes.EULER,
        size=3,
        default=[0, 0, 0],
    )
    hip_bone_offset_location_end: bpy.props.FloatVectorProperty(
        name="Hip Bone Offset Location End",
        subtype=ST_FloatVectorProperty.Subtypes.TRANSLATION,
        size=3,
    )
    hip_bone_offset_rotation_end: bpy.props.FloatVectorProperty(
        name="Hip Bone Offset Rotation End",
        subtype=ST_FloatVectorProperty.Subtypes.EULER,
        size=3,
        default=[0, 0, 0],
    )

    def update_root_motion_settings(self):
        self.root_motion.copy_from_clip(self)

    def copy_from(self, other):
        objects.copy_from_to(other, self)

    @classmethod
    def parse_clip_row(cls, row, key_offset):
        obj_name = row["obj_name"]
        obj_name = obj_name.replace("Avatar", "")
        clip_name = row["clip_name"]
        frame_start = int(row["start_frame"]) + key_offset
        frame_end = int(row["stop_frame"]) + key_offset
        loop_time = True if row["loop_time"] == "True" else False
        rot_bake_into = True if row["rot_bake_into"] == "True" else False
        rot_offset = float(row["rot_offset"])
        y_bake_into = True if row["y_bake_into"] == "True" else False
        y_offset = float(row["y_offset"])
        xz_bake_into = True if row["xz_bake_into"] == "True" else False

        return (
            obj_name,
            clip_name,
            frame_start,
            frame_end,
            loop_time,
            rot_bake_into,
            rot_offset,
            y_bake_into,
            y_offset,
            xz_bake_into,
        )

    @classmethod
    def process_clip_row(
        cls, row, key_offset, action, new_clips, existing_clips, discarded_clips
    ):
        (
            obj_name,
            clip_name,
            frame_start,
            frame_end,
            loop_time,
            rot_bake_into,
            rot_offset,
            y_bake_into,
            y_offset,
            xz_bake_into,
        ) = UnityClipMetadata.parse_clip_row(row, key_offset)

        potential_action_names = [
            obj_name,
            clip_name,
            "{0}_{1}".format(obj_name, clip_name),
        ]

        matching_metadatas = []
        existing = False

        if action is not None:
            found = False
            for potential_name in potential_action_names:
                if action.name == potential_name:
                    found = True

            if not found:
                discarded_clips.append("{0}: {1}".format(obj_name, clip_name))
                return None

            metadata = action.unity_clips.get(clip_name)

            if not metadata:
                metadata = action.unity_clips.get(action.name)
            else:
                existing = True

            if not metadata:
                metadata = action.unity_clips.add()

            matching_metadatas.append(metadata)
        else:
            processed = False
            for potential_name in potential_action_names:
                if processed or not potential_name in bpy.data.actions:
                    continue

                processed = True
                action = bpy.data.actions[potential_name]

                metadata = action.unity_clips.get(clip_name)

                if not metadata:
                    metadata = action.unity_clips.get(action.name)
                else:
                    existing = True

                if not metadata:
                    metadata = action.unity_clips.add()

                matching_metadatas.append(metadata)

        if len(matching_metadatas) == 0:
            discarded_clips.append("{0}: {1}".format(obj_name, clip_name))
            return matching_metadatas

        for metadata in matching_metadatas:

            if not existing:
                new_clips.append("{0}: {1}".format(obj_name, clip_name))
                metadata.action = action
                metadata.fbx_name = obj_name
                metadata.name = clip_name
                metadata.frame_start = frame_start
                metadata.frame_end = frame_end
                metadata.pose_start = "Default"
                metadata.pose_end = "Default"
                metadata.root_motion.root_motion_x_offset = 0
                metadata.root_motion.root_motion_y_offset = 0
                metadata.root_motion.root_motion_x_bake_into = xz_bake_into
            else:
                existing_clips.append("{0}: {1}".format(obj_name, clip_name))

            metadata.root_motion.loop_time = loop_time
            metadata.root_motion.root_motion_rot_bake_into = rot_bake_into
            if xz_bake_into:
                metadata.root_motion.root_motion_x_bake_into = xz_bake_into
            metadata.root_motion.root_motion_y_bake_into = xz_bake_into
            metadata.root_motion.root_motion_z_bake_into = y_bake_into
            metadata.root_motion.root_motion_rot_offset = rot_offset
            metadata.root_motion.root_motion_z_offset = y_offset

        return matching_metadatas

    @classmethod
    def parse_clip_files(
        cls, context, dir_path, key_offset, action=None, clear_clips=False
    ):
        filepaths = [
            path
            for path in files.get_files_in_dir(dir_path, "", "", ".txt")
            if not ".keys." in path
        ]

        headers, rows = files.parse_csvs(filepaths)

        metadatas = []

        if action and clear_clips:
            action.unity_clips.clear()

        new_clips, existing_clips, discarded_clips = [], [], []

        for row in rows:
            metadatas = UnityClipMetadata.process_clip_row(
                row, key_offset, action, new_clips, existing_clips, discarded_clips
            )

            if metadatas:
                metadatas.extend(metadatas)

        print("      NEW CLIPS: {0}".format(new_clips))
        print(" EXISTING CLIPS: {0}".format(existing_clips))
        print("DISCARDED CLIPS: {0}".format(discarded_clips))
        return metadatas

    def decorate(self, action):

        start_marker_name = self.name
        stop_marker_name = "{0}.end".format(start_marker_name)

        start_marker = action.pose_markers.get(start_marker_name)
        stop_marker = action.pose_markers.get(stop_marker_name)

        if not start_marker:
            start_marker = action.pose_markers.new(start_marker_name)
        if not stop_marker:
            stop_marker = action.pose_markers.new(start_marker_name)

        start_marker.frame = self.frame_start
        stop_marker.frame = self.frame_end

        for fc in action.fcurves:
            self.demarcate(fc)

    def demarcate(self, fcurve):
        s = self.frame_start
        e = self.frame_end

        sv = fcurve.evaluate(s)
        ev = fcurve.evaluate(e)
        insert_keyframe_extreme(fcurve, s, sv, needed=False, fast=True)
        insert_keyframe_extreme(fcurve, e, ev, needed=False, fast=True)

    @classmethod
    def handle_split(
        cls, master_action, new_action, old_clip_name, new_clip_name, frame_shift
    ):
        for clip in master_action.unity_clips:
            if clip.name != old_clip_name:
                continue

            new_clip = new_action.unity_clips.add()
            new_clip.copy_from(clip)

            new_clip.action = new_action
            new_clip.name = new_clip_name

            new_clip.source_action = master_action
            new_clip.source_frame_start = new_clip.frame_start
            new_clip.source_frame_end = new_clip.frame_end
            new_clip.source_frame_shift = frame_shift

            new_clip.action = new_action
            new_clip.frame_start -= frame_shift
            new_clip.frame_end -= frame_shift
            break

        new_action.unity_metadata.split_from = master_action
        master_action.unity_metadata.clips_protected = True
        return new_clip

    def full_frame_range(self):
        self.frame_start = self.action.frame_range[0]
        self.frame_end = self.action.frame_range[1]

    def refresh_keys(self):
        copy_from_action_range(
            self.source_action,
            self.action,
            self.source_frame_start,
            self.source_frame_end,
            self.source_frame_shift,
        )
