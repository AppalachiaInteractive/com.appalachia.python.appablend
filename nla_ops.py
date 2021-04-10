import bpy, cspy
from bpy.types import Operator
from cspy.ops import OPS_, OPS_DIALOG
from cspy.polling import DOIF
from cspy.nla import *
from cspy.unity_clips import *
from cspy.root_motion import *

class NLA_OT_actions_to_strip(OPS_, Operator):
    """Creates NLA strips for each action."""
    bl_idname = "nla.actions_to_strip"
    bl_label = "Actions To Strip"

    @classmethod
    def do_poll(cls, context):
        return DOIF.DATA.ACTIONS(context)

    def do_execute(self, context):
        obj = context.active_object
        anim_data = obj.animation_data
        track = get_nla_track(obj)
        clear_nla_track(track)

        padding = 5
        start, first = add_bind_pose_for_strip_population(context, track, padding)

        for action in bpy.data.actions:
            if first and action == first:
                continue
            if action.name.endswith('_Layer') or  'PoseLib' in action.name:
                continue
            track.strips.new(action.name, start, action)
            start += action.frame_range[1] + padding
        return {'FINISHED'}

class NLA_OT_strips_from_clips(OPS_, Operator):
    """Seperates actions onto the NLA using the unity clip metadata"""
    bl_idname = "nla.strips_from_clips"
    bl_label = "Strips From Clips"

    @classmethod
    def do_poll(cls, context):
        return DOIF.DATA.ACTIONS(context)

    def do_execute(self, context):
        obj = context.active_object
        scene = context.scene
        scene.frame_start = 1

        clear_nla_tracks(obj)

        track = get_nla_track(obj)

        key_offset = 1
        padding = 5
        start, first = add_bind_pose_for_strip_population(context, track, padding)

        for action in bpy.data.actions:
            for clip in action.unity_clips:

                strip = track.strips.new(clip.name, start, action)
                strip.name = clip.name

                strip.action_frame_start = clip.frame_start
                strip.action_frame_end =  clip.frame_end
                strip.frame_end = strip.frame_start + (strip.action_frame_end - strip.action_frame_start)
                strip.use_animated_time_cyclic = clip.loop_time

                start = strip.frame_end + padding

        scene.frame_end = start
        return {'FINISHED'}

class NLA_OT_strips_from_text(OPS_, Operator):
    """Seperates actions onto the NLA using the specified text"""
    bl_idname = "nla.strips_from_text"
    bl_label = "Strips From Text"

    @classmethod
    def do_poll(cls, context):
        return DOIF.DATA.ACTIONS(context)

    def do_execute(self, context):
        obj = context.active_object
        scene = context.scene
        group_name = 'Root Motion Settings'

        clear_nla_tracks(obj)

        track = get_nla_track(obj)

        key_offset = 1
        padding = 5
        start, first = add_bind_pose_for_strip_population(context, track, padding)

        for action in bpy.data.actions:
            for data_path in RootMotionMetadata.root_motion_keys:
                fcurve = action.fcurves.find(data_path, index=-1)
                if fcurve:
                    action.fcurves.remove(fcurve)

        path = bpy.path.abspath(scene.unity_settings.sheet_dir_path)

        metadatas = UnityClipMetadata.parse_clip_files(context, path, key_offset)

        for metadata in metadatas:

            action = metadata.action
            group = action.groups.find(group_name)

            if not group:
                group = action.groups.new(group_name)

            strip = track.strips.new(metadata.clip_name, start, action)
            strip.name = metadata.clip_name

            strip.action_frame_start = metadata.frame_start
            strip.action_frame_end =  metadata.frame_end
            strip.frame_end = strip.frame_start + (strip.action_frame_end - strip.action_frame_start)
            strip.use_animated_time_cyclic = loop_time

            start = strip.frame_end + padding

            obj.animation_data.action = action
            for data_path in RootMotionMetadata.root_motion_keys:

                fcurve = action.fcurves.find(data_path, index=-1)
                if not fcurve:
                    fcurve = action.fcurves.new(data_path, index=-1, action_group=group_name)

                s = metadata.frame_start
                e = metadata.frame_end+1
                for frame in range(s, e):
                    value = getattr(metadata, data_path)

                    if frame == s or frame == e:
                        k = cspy.actions.insert_keyframe(fcurve, frame, value, needed=False, fast=True)
                    else:
                        k = cspy.actions.insert_keyframe_breakdown(fcurve, frame, value, needed=False, fast=True)

                fcurve.update()

        scene.frame_end = start
        return {'FINISHED'}

class NLA_OT_import_strips(OPS_, Operator):
    """Imports strips from FBX files"""
    bl_idname = "nla.import_strips"
    bl_label = "Import Strips From FBX"

    @classmethod
    def do_poll(cls, context):
        obj = context.active_object
        return obj and obj.animation_data and obj.animation_data.action and obj.animation_data.action.unity_clips

    def do_execute(self, context):
        obj = context.active_object
        scene = context.scene

        path = bpy.path.abspath(scene.unity_settings.sheet_dir_path)
        fbx_filepaths = cspy.files.get_files_in_dir(path, endswith='.fbx',case_sensitive=False)

        for fbx_filepath in fbx_filepaths:
            bpy.ops.object.empty_add()
            holder = bpy.context.active_object
            holder.name = cspy.files.base_name(fbx_filepath)

            objs_from_file = cspy.imports.import_fbx(filepath=fbx_filepath, automatic_bone_orientation=True)

            for f in objs_from_file:
                if f.name == 'ROOT' and len(f.children) == 0:
                    bpy.data.objects.remove(f)
                    continue
                if not f.parent:
                    f.parent = holder

        return {'FINISHED'}
