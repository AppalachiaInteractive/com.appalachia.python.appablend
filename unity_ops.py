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

        cspy.collectionprops.sort(action.unity_clips, 'start_frame')

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
            cspy.collectionprops.sort(action.unity_clips, 'start_frame')

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
                s = clip.start_frame
                e = clip.stop_frame

                sv = fcurve.evaluate(s)
                ev = fcurve.evaluate(e)
                cspy.actions.insert_keyframe_extreme(fcurve, s, sv, fast=True)
                cspy.actions.insert_keyframe_extreme(fcurve, e, ev, fast=True)
        

        for fcurve in action.fcurves:
            fcurve.update()

        return {'FINISHED'}
