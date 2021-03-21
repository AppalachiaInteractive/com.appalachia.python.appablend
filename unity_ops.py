import bpy, cspy
from bpy.types import Operator
from cspy.ops import OPS_OPTIONS, OPS_, OPS_MODAL
from cspy.polling import POLL
from cspy.unity import *

class UNITY_OT_refresh_clip_data(Operator, OPS_):
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

class UNITY_OT_refresh_clip_data_all(Operator, OPS_):
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

        cspy.unity.UnityClipMetadata.parse_files(context, path, key_offset)

        return {'FINISHED'}

class UNITY_OT_clear_clip_data(Operator, OPS_):
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

class UNITY_OT_clear_clip_data_all(Operator, OPS_):
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


class UNITY_OT_clamp_to_clip(Operator, OPS_):
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
        
        context.scene.frame_current = active_clip.start_frame
        context.scene.frame_start = active_clip.start_frame
        context.scene.frame_end = active_clip.stop_frame

        return {'FINISHED'}

class UNITY_OT_clamp_to_clip_and_play(Operator, OPS_):
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
        
        context.scene.frame_current = active_clip.start_frame
        context.scene.frame_start = active_clip.start_frame
        context.scene.frame_end = active_clip.stop_frame
        if not context.screen.is_animation_playing:
            bpy.ops.screen.animation_play()

        return {'FINISHED'}

class UNITY_OT_decorate_action(Operator, OPS_):
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

class UNITY_OT_decorate_action_all(Operator, OPS_):
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

class UNITY_OT_sync_actions_with_clips(Operator, OPS_):
    """Syncs each unity clip's action property with its action owner"""
    bl_idname = "unity.unity_ot_sync_actions_with_clips"
    bl_label = "Sync Action and Clip Properties"

    @classmethod
    def do_poll(cls, context):
        return POLL.active_object_action(context)
            
    def do_execute(self, context):
        action = context.active_object.animation_data.action

        for clip in action.unity_clips:
            clip.action = action

        return {'FINISHED'}


class UNITY_OT_sort_clip_data(Operator, OPS_):
    """Sorts animation clip metadata from Unity for this action"""
    bl_idname = "unity.sort_clip_data"
    bl_label = "Sort Clip Data"
    
    @classmethod
    def do_poll(cls, context):
        return POLL.active_object_action
            
    def do_execute(self, context):
        obj = context.active_object
        
        action = obj.animation_data.action

        cspy.collectionprops.sort(action.unity_clips, 'start_frame')

        return {'FINISHED'}

class UNITY_OT_sort_clip_data_all(Operator, OPS_):
    """Sorts animation clip metadata from Unity for all actions"""
    bl_idname = "unity.sort_clip_data_all"
    bl_label = "Sort (All)"
    
    @classmethod
    def do_poll(cls, context):
        return len(bpy.data.actions) > 0 
            
    def do_execute(self, context):
        
        for action in bpy.data.actions:
            cspy.collectionprops.sort(action.unity_clips, 'start_frame')

        return {'FINISHED'}
