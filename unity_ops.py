import bpy, cspy
from bpy.types import Operator
from cspy.ops import OPS_, OPS_DIALOG
from cspy.polling import POLL
from cspy.unity import *
from cspy.timeline import *

class UNITY_OT_refresh_clip_data(OPS_, Operator):
    """Refreshes animation clip metadata from Unity"""
    bl_idname = "unity.refresh_clip_data"
    bl_label = "Refresh Clip Data"

    @classmethod
    def do_poll(cls, context):
        return POLL.active_object_action and context.scene.unity_sheet_dir_path != ''

    def do_execute(self, context):
        obj = context.active_object
        scene = context.scene
        key_offset = 1

        path = bpy.path.abspath(scene.unity_sheet_dir_path)
        action = context.active_object.animation_data.action

        cspy.unity.UnityClipMetadata.parse_files(context, path, key_offset, action)

        return {'FINISHED'}

class UNITY_OT_refresh_clip_data_all(OPS_, Operator):
    """Refreshes animation clip metadata from Unity"""
    bl_idname = "unity.refresh_clip_data_all"
    bl_label = "Refresh (All)"

    @classmethod
    def do_poll(cls, context):
        return len(bpy.data.actions) > 0 and context.scene.unity_sheet_dir_path != ''

    def do_execute(self, context):
        obj = context.active_object
        scene = context.scene
        key_offset = 1

        path = bpy.path.abspath(scene.unity_sheet_dir_path)

        for action in bpy.data.actions:
            action.unity_index = 0

        cspy.unity.UnityClipMetadata.parse_files(context, path, key_offset)

        return {'FINISHED'}

class UNITY_OT_clear_clip_data(OPS_, Operator):
    """Clears animation clip metadata from Unity for this action"""
    bl_idname = "unity.clear_clip_data"
    bl_label = "Clear Clip Data"

    @classmethod
    def do_poll(cls, context):
        return POLL.active_object_action and not context.active_object.animation_data.action.unity_clips_protected and context.scene.unity_sheet_dir_path != ''

    def do_execute(self, context):
        obj = context.active_object

        action = obj.animation_data.action

        action.unity_clips.clear()

        return {'FINISHED'}

class UNITY_OT_clear_clip_data_all(OPS_, Operator):
    """Clears animation clip metadata from Unity for all actions"""
    bl_idname = "unity.clear_clip_data_all"
    bl_label = "Clear (All)"

    @classmethod
    def do_poll(cls, context):
        return len(bpy.data.actions) > 0 and context.scene.unity_sheet_dir_path != ''

    def do_execute(self, context):

        for action in bpy.data.actions:
            if action.unity_clips_protected:
                continue
            action.unity_clips.clear()

        return {'FINISHED'}


class UNITY_OT_clamp_to_clip(OPS_, Operator):
    """Clamps scene play region to unity clip"""
    bl_idname = "unity.clamp_to_clip"
    bl_label = "Clamp To Clip"

    action_name: bpy.props.StringProperty(name="Action Name")
    clip_name: bpy.props.StringProperty(name="Clip Name")

    @classmethod
    def do_poll(cls, context):
        try:
            return context.active_object.animation_data.action.unity_clips
        except:
            return False

    def do_execute(self, context):
        active_clip = bpy.data.actions[self.action_name].unity_clips[self.clip_name]

        clamp_to_unity_clip(context, active_clip)

        return {'FINISHED'}

class UNITY_OT_clamp_to_clip_and_play(OPS_, Operator):
    """Clamps scene play region to unity clip"""
    bl_idname = "unity.clamp_to_clip_and_play"
    bl_label = "Clamp & Play"

    action_name: bpy.props.StringProperty(name="Action Name")
    clip_name: bpy.props.StringProperty(name="Clip Name")

    @classmethod
    def do_poll(cls, context):
        try:
            return context.active_object.animation_data.action.unity_clips
        except:
            return False

    def do_execute(self, context):
        active_clip = bpy.data.actions[self.action_name].unity_clips[self.clip_name]

        clamp_to_unity_clip(context, active_clip, True)

        return {'FINISHED'}

class UNITY_OT_decorate_action(OPS_, Operator):
    """Decorates actions with unity clip metadata"""
    bl_idname = "unity.decorate_action"
    bl_label = "Decorate Action"

    clip_name: bpy.props.StringProperty(name="Clip Name")

    @classmethod
    def do_poll(cls, context):
        try:
            return context.active_object.animation_data.action.unity_clips
        except:
            return False

    def do_execute(self, context):
        action = context.active_object.animation_data.action
        clip = action.unity_clips[clip_name]

        clip.decorate_action(action)

        return {'FINISHED'}

class UNITY_OT_decorate_action_all(OPS_, Operator):
    """Decorates actions with all relevant unity clip metadata"""
    bl_idname = "unity.decorate_action_all_clips"
    bl_label = "Decorate Using All Clips"

    @classmethod
    def do_poll(cls, context):
        try:
            return context.active_object.animation_data.action.unity_clips
        except:
            return False

    def do_execute(self, context):
        action = context.active_object.animation_data.action

        for clip in action.unity_clips:
            clip.decorate_action(action)

        return {'FINISHED'}

class UNITY_OT_sync_actions_with_clips(OPS_, Operator):
    """Syncs each unity clip's action property with its action owner"""
    bl_idname = "unity.sync_actions_with_clips"
    bl_label = "Sync Action and Clip Properties"

    @classmethod
    def do_poll(cls, context):
        return POLL.active_object_action(context)

    def do_execute(self, context):
        action = context.active_object.animation_data.action

        for clip in action.unity_clips:
            clip.action = action

        return {'FINISHED'}


class UNITY_OT_sort_clip_data(OPS_, Operator):
    """Sorts animation clip metadata from Unity for this action"""
    bl_idname = "unity.sort_clip_data"
    bl_label = "Sort Clip Data"

    @classmethod
    def do_poll(cls, context):
        return POLL.active_object_action

    def do_execute(self, context):
        obj = context.active_object

        action = obj.animation_data.action

        cspy.collectionprops.sort(action.unity_clips, 'frame_start')

        return {'FINISHED'}

class UNITY_OT_sort_clip_data_all(OPS_, Operator):
    """Sorts animation clip metadata from Unity for all actions"""
    bl_idname = "unity.sort_clip_data_all"
    bl_label = "Sort (All)"

    @classmethod
    def do_poll(cls, context):
        return len(bpy.data.actions) > 0

    def do_execute(self, context):

        for action in bpy.data.actions:
            cspy.collectionprops.sort(action.unity_clips, 'frame_start')

        return {'FINISHED'}

class UNITY_OT_copy_clips_from_template(OPS_, Operator):
    """Copy unity clip metadata from a template """
    bl_idname = "unity.demarcatecopy_clips_from_template_clips"
    bl_label = "Copy Clips From Template"

    @classmethod
    def do_poll(cls, context):
        return POLL.active_object_action(context)

    def do_execute(self, context):
        action = context.active_object.animation_data.action
        template = action.unity_clip_template

        action.unity_clips.clear()

        for clip in template.unity_clips:
            new_clip = action.unity_clips.add()
            new_clip.copy_from(clip)
            new_clip.action = action

        return {'FINISHED'}

class UNITY_OT_demarcate_clips(OPS_, Operator):
    """Use unity clip metadata """
    bl_idname = "unity.demarcate_clips"
    bl_label = "Demarcate Clips"

    @classmethod
    def do_poll(cls, context):
        return POLL.active_object_action(context) and context.active_object.animation_data.action.unity_clips

    def do_execute(self, context):
        action = context.active_object.animation_data.action

        for fcurve in action.fcurves:
            for clip in action.unity_clips:
                clip.demarcate(fcurve)

        for fcurve in action.fcurves:
            fcurve.update()

        return {'FINISHED'}

class UNITY_OT_get_current(OPS_, Operator):
    """Get the current clip based on the frame """
    bl_idname = "unity.get_current"
    bl_label = "Get Current"

    @classmethod
    def do_poll(cls, context):
        return POLL.active_object_action(context) and context.active_object.animation_data.action.unity_clips

    def do_execute(self, context):
        action = context.active_object.animation_data.action

        for fcurve in action.fcurves:
            for clip in action.unity_clips:
                clip.demarcate(fcurve)

        for fcurve in action.fcurves:
            fcurve.update()

        return {'FINISHED'}


class UNITY_OT_update_master_clip_metadata(OPS_, Operator):
    """Use unity clip metadata to update the master action."""
    bl_idname = "unity.update_master_clip_metadata"
    bl_label = "Update Master Clip"

    @classmethod
    def do_poll(cls, context):
        return 'MASTER' in bpy.data.actions

    def do_execute(self, context):
        master_action_name = 'MASTER'
        master_action = bpy.data.actions[master_action_name]
        obj = context.active_object

        padding = 10
        round_to_nearest = 10

        master_action.unity_clips_protected = True
        master_action.unity_clips.clear()
        for marker in reversed(master_action.pose_markers):
            master_action.pose_markers.remove(marker)

        start = 1

        for action in bpy.data.actions:
            if action == master_action or action.name.endswith('Action') or action.name.endswith('_Layer') or 'PoseLib' in action.name:
                continue
                
            print('Getting metadata for action {0}'.format(action.name))

            if start != 1:
                start += padding                    # 47 + 10 = 57
                overlap = start % round_to_nearest  # 57 %  5 =  2
                offset = round_to_nearest - overlap #  5 -  2 =  3
                start += offset                     # 57 +  3 = 60  - clean frame start

            action_start = action.frame_range[0]
            action_end = action.frame_range[1]

            start -= action_start

            if action.unity_clips:
                for unity_clip in action.unity_clips:
                    new_clip = master_action.unity_clips.add()
                    new_clip.copy_from(unity_clip)

                    new_clip.action = master_action

                    new_clip.frame_start += start
                    new_clip.frame_end += start    
            
            start += (action_end - action_start) + 1

        #print('Decorating {0} clips'.format(len(master_action.unity_clips)))
        #for clip in master_action.unity_clips:
        #    clip.decorate(master_action)

        for fc in master_action.fcurves:
            fc.update()

        return {'FINISHED'}

class UNITY_OT_remove_non_clip_keys(OPS_, Operator):
    """Delete keyframes not included in unity clips."""
    bl_idname = "unity.remove_non_clip_key"
    bl_label = "Remove Non-Clip Keys"

    @classmethod
    def do_poll(cls, context):
        return POLL.active_object_action

    def do_execute(self, context):
        action = context.active_object.animation_data.action

        for fcurve in action.fcurves:
            for keyframe_point in reversed(fcurve.keyframe_points):
                f = keyframe_point.co[0]

                found = False
                for clip in action.unity_clips:
                    if f >= clip.frame_start and f <= clip.frame_end:
                        found = True
                    if found:
                        break
                
                if not found:
                    fcurve.keyframe_points.remove(keyframe_point)
        
        for fcurve in action.fcurves:
            fcurve.update()

        return {'FINISHED'}

class UNITY_OT_Set_By_Current_Frame(OPS_, Operator):
    """Sets the current clip to the one shown on screen."""
    bl_idname = "unity.set_by_current_frame"
    bl_label = "Set By Frame"

    action_name: bpy.props.StringProperty(name="Action Name")
    clip_name: bpy.props.StringProperty(name="Clip Name")

    @classmethod
    def do_poll(cls, context):
        return POLL.active_object_action

    def do_execute(self, context):
        action = context.active_object.animation_data.action

        f = context.scene.frame_current
        for index, clip in enumerate(action.unity_clips):
            if f >= clip.frame_start and f <= clip.frame_end:
                action.unity_index = index
                active_clip = clip
                break
        
        clamp_to_unity_clip(context, active_clip, True)

        return {'FINISHED'}


class UNITY_OT_apply_pose(OPS_, Operator):
    """Applies the pose library pose to the specified frame"""
    bl_idname = "unity.apply_pose"
    bl_label = "Apply Pose"

    pose_name: bpy.props.StringProperty(name='Pose Name')
    frame: bpy.props.IntProperty(name='Frame')
    rooted: bpy.props.BoolProperty(name='Rooted')

    @classmethod
    def do_poll(cls, context):
        return POLL.active_object_unity_clips

    def do_execute(self, context):
        obj = context.active_object
        action = obj.animation_data.action

        for bone in obj.data.bones:
            if bone.parent is None and not self.rooted:
                bone.select = False
            else:
                bone.select = True
                    
        
        apply_pose_to_frame(context, obj, self.pose_name, self.frame)

        return {'FINISHED'}


class UNITY_OT_new_pose(OPS_, Operator):
    """Adds the specified frame to the pose library"""
    bl_idname = "unity.new_pose"
    bl_label = "New Pose"

    frame: bpy.props.IntProperty(name='Frame')
    start: bpy.props.BoolProperty(name='Start?')

    @classmethod
    def do_poll(cls, context):
        return POLL.active_object_unity_clips

    def do_execute(self, context):
        obj = context.active_object
        action = obj.animation_data.action
        clip = action.unity_clips[action.unity_index]
        
        bpy.ops.poselib.pose_add(frame=self.frame)

        new_pose = obj.pose_library.pose_markers['Pose']
        new_pose.name = '{0} {1}'.format(clip.name, 'Start' if self.start else 'End')

        if self.start:
            clip.pose_start = new_pose.name
        else:
            clip.pose_end = new_pose.name
        

        return {'FINISHED'}


class UNITY_OT_delete_clip(OPS_, Operator):
    """Delete the active clip."""
    bl_idname = "unity.delete_clip"
    bl_label = "Delete"

    @classmethod
    def do_poll(cls, context):
        return POLL.active_object_unity_clips

    def do_execute(self, context):
        obj = context.active_object
        action = obj.animation_data.action
        
        action.unity_clips.remove(action.unity_index)
        
        if action.unity_index > 0:
            action.unity_index -= 1

        return {'FINISHED'}

