import bpy, cspy
from bpy.types import Operator
from cspy.ops import OPS_, OPS_DIALOG
from cspy.polling import POLL
from cspy.timeline import *

class TIMELINE_OT_clamp_to_strips(OPS_, Operator):
    """Clamps scene play region to selected strips"""
    bl_idname = "timeline.clamp_to_strips"
    bl_label = "Clamp To Strips"
    
    @classmethod
    def do_poll(cls, context):
        return len(cspy.nla.get_selected_strips()) > 0
            
    def do_execute(self, context):   
        clamp_to_strips(context)
        return {'FINISHED'}

class TIMELINE_OP:    
    @classmethod
    def do_poll(cls, context):
        return POLL.active_object_action

class TIMELINE_OT_clamp_to_action(TIMELINE_OP, OPS_, Operator):
    """Clamps scene play region to selected action"""
    bl_idname = "timeline.clamp_to_action"
    bl_label = "Clamp To Action"
            
    def do_execute(self, context):        
        clamp_to_action(context)
        return {'FINISHED'}

class TIMELINE_OT_clamp_start_to_current(TIMELINE_OP, OPS_, Operator):
    """Clamps scene play region start to current frame"""
    bl_idname = "timeline.clamp_start_to_current"
    bl_label = "Clamp Start To Current"
    
    def do_execute(self, context):    
        clamp_timeline_start_to_current(context)
        return {'FINISHED'}

class TIMELINE_OT_clamp_end_to_current(TIMELINE_OP, OPS_, Operator):
    """Clamps scene play region end to current frame"""
    bl_idname = "timeline.clamp_end_to_current"
    bl_label = "Clamp End To Current"
    
    def do_execute(self, context):    
        clamp_timeline_end_to_current(context)
        return {'FINISHED'}

class TIMELINE_OT_play_timeline(OPS_, Operator):
    """Stops scene playback"""
    bl_idname = "timeline.play_timeline"
    bl_label = "Play"
    
    @classmethod
    def do_poll(cls, context):
        return not is_playing(context)

    def do_execute(self, context):    
        play_timeline(context)
        return {'FINISHED'}

class TIMELINE_OT_stop_timeline(OPS_, Operator):
    """Begins scene playback"""
    bl_idname = "timeline.stop_timeline"
    bl_label = "Stop"
    
    @classmethod
    def do_poll(cls, context):
        return is_playing(context)

    def do_execute(self, context):    
        stop_timeline(context)
        return {'FINISHED'}


class TIMELINE_OT_rew_timeline(OPS_, Operator):
    """Rewind scene playback"""
    bl_idname = "timeline.rew_timeline"
    bl_label = "Rewind"
    
    @classmethod
    def do_poll(cls, context):
        return True

    def do_execute(self, context):    
        rew_timeline(context)
        return {'FINISHED'}

class TIMELINE_OT_ff_timeline(OPS_, Operator):
    """Fast-forward scene playback"""
    bl_idname = "timeline.ff_timeline"
    bl_label = "Fast Forward"
    
    @classmethod
    def do_poll(cls, context):
        return True

    def do_execute(self, context):    
        ff_timeline(context)
        return {'FINISHED'}

class TIMELINE_OT_guess_previous_start(TIMELINE_OP, OPS_, Operator):
    """Moves the play region to the best guess previous clip start"""
    bl_idname = "timeline.guess_previous_start"
    bl_label = "Guess Prev. Start"
    
    def do_execute(self, context):   
        action = context.active_object.animation_data.action
        context.scene.frame_start = get_previous_notable_frame_from_start(context, action)
        context.scene.frame_current = context.scene.frame_start
        return {'FINISHED'}

class TIMELINE_OT_guess_previous_end(TIMELINE_OP, OPS_, Operator):
    """Moves the play region to the best guess previous clip end"""
    bl_idname = "timeline.guess_previous_end"
    bl_label = "Guess Prev. End"
    
    def do_execute(self, context):   
        action = context.active_object.animation_data.action
        context.scene.frame_end = get_previous_notable_frame_from_end(context, action)
        context.scene.frame_current = context.scene.frame_start
        return {'FINISHED'}

class TIMELINE_OT_guess_next_start(TIMELINE_OP, OPS_, Operator):
    """Moves the play region to the best guess next clip start"""
    bl_idname = "timeline.guess_next_start"
    bl_label = "Guess Next Start"
    
    def do_execute(self, context):   
        action = context.active_object.animation_data.action
        context.scene.frame_start = get_next_notable_frame_from_start(context, action)
        context.scene.frame_current = context.scene.frame_start
        return {'FINISHED'}

class TIMELINE_OT_guess_next_end(TIMELINE_OP, OPS_, Operator):
    """Moves the play region to the best guess next clip end"""
    bl_idname = "timeline.guess_next_end"
    bl_label = "Guess Next End"
    
    def do_execute(self, context):   
        action = context.active_object.animation_data.action
        context.scene.frame_end = get_next_notable_frame_from_end(context, action)
        context.scene.frame_current = context.scene.frame_start        
        return {'FINISHED'}


class TIMELINE_OT_previous_clip(TIMELINE_OP, OPS_, Operator):
    """Moves the play region to the best previous current clip"""
    bl_idname = "timeline.previous_clip"
    bl_label = "Previous Clip"
    
    def do_execute(self, context):   
        action = context.active_object.animation_data.action
        context.scene.frame_start = get_previous_notable_frame_from_start(context, action)
        context.scene.frame_start = get_previous_notable_frame_from_start(context, action)
        context.scene.frame_end = get_previous_notable_frame_from_end(context, action)
        context.scene.frame_end = get_previous_notable_frame_from_end(context, action)
        context.scene.frame_current = context.scene.frame_start        
        return {'FINISHED'}

class TIMELINE_OT_guess_clip(TIMELINE_OP, OPS_, Operator):
    """Moves the play region to the best guess current clip"""
    bl_idname = "timeline.guess_clip"
    bl_label = "Guess Clip"
    
    def do_execute(self, context):   
        action = context.active_object.animation_data.action
        context.scene.frame_start = context.scene.frame_current
        context.scene.frame_end = context.scene.frame_current
        context.scene.frame_start = get_previous_notable_frame_from_start(context, action)
        context.scene.frame_end = get_next_notable_frame_from_end(context, action)
        context.scene.frame_current = context.scene.frame_start        
        return {'FINISHED'}

class TIMELINE_OT_next_clip(TIMELINE_OP, OPS_, Operator):
    """Moves the play region to the best next current clip"""
    bl_idname = "timeline.next_clip"
    bl_label = "Next Clip"
    
    def do_execute(self, context):   
        action = context.active_object.animation_data.action
        context.scene.frame_start = get_next_notable_frame_from_start(context, action)
        context.scene.frame_start = get_next_notable_frame_from_start(context, action)
        context.scene.frame_end = get_next_notable_frame_from_end(context, action)
        context.scene.frame_current = context.scene.frame_start              
        return {'FINISHED'}
