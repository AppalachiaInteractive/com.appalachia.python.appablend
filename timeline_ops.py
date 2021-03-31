import bpy, cspy
from bpy.types import Operator
from cspy.ops import OPS_, OPS_DIALOG
from cspy.polling import POLL
from cspy.timeline import *

class TIMELINE_OT_clamp_to_strip(OPS_, Operator):
    """Clamps scene play region to selected strips"""
    bl_idname = "timeline.clamp_to_strip"
    bl_label = "Clamp To Strips"

    @classmethod
    def do_poll(cls, context):
        return len(cspy.nla.get_selected_strips()) > 0

    def do_execute(self, context):
        clamp_to_strips(context)
        return {'FINISHED'}

class TIMELINE_OT_clamp_to_strip(OPS_, Operator):
    """Clamps scene play region to selected strip"""
    bl_idname = "timeline.clamp_to_strip"
    bl_label = "Clamp To Strip"

    @classmethod
    def do_poll(cls, context):
        return len(cspy.nla.get_selected_strips()) > 0

    def do_execute(self, context):
        clamp_to_strip(context)
        return {'FINISHED'}

class TIMELINE_OT_clamp_to_strips(OPS_, Operator):
    """Clamps scene play region to strips"""
    bl_idname = "timeline.clamp_to_strips"
    bl_label = "Clamp To Strips"

    @classmethod
    def do_poll(cls, context):
        return len(cspy.nla.get_selected_strips()) > 0

    def do_execute(self, context):
        clamp_to_strips(context)
        return {'FINISHED'}

class TIMELINE_OP_SCENE:
    @classmethod
    def do_poll(cls, context):
        return True

class TIMELINE_OP:
    @classmethod
    def do_poll(cls, context):
        return POLL.active_object_action(context)

class TIMELINE_OT_clamp_to_action(TIMELINE_OP, OPS_, Operator):
    """Clamps scene play region to selected action"""
    bl_idname = "timeline.clamp_to_action"
    bl_label = "Clamp To Action"

    def do_execute(self, context):
        clamp_to_action(context)
        return {'FINISHED'}

class TIMELINE_OT_clamp_start_to_current(TIMELINE_OP_SCENE, OPS_, Operator):
    """Clamps scene play region start to current frame"""
    bl_idname = "timeline.clamp_start_to_current"
    bl_label = "Clamp Start To Current"

    def do_execute(self, context):
        clamp_timeline_start_to_current(context)
        return {'FINISHED'}

class TIMELINE_OT_clamp_end_to_current(TIMELINE_OP_SCENE, OPS_, Operator):
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

class TIMELINE_OT_view:
    @classmethod
    def do_poll(cls, context):
        return True

    def do_execute(self, context):
        for window in context.window_manager.windows:
            screen = window.screen
            for area in screen.areas:
                for region in area.regions:

                    override = {'window': window, 'screen': screen, 'area': area, 'region': region}
                    self.do_apply(context, override)

        return {'FINISHED'}

class TIMELINE_OT_view_frame(OPS_, TIMELINE_OT_view, Operator):
    """Clamp all areas to the current frame."""
    bl_idname = "timeline.view_frame"
    bl_label = "View Frame"

    def do_apply(self, context, override):
        if override['area'].type == 'DOPESHEET_EDITOR':
            bpy.ops.action.view_frame(override)
        elif override['area'].type == 'NLA_EDITOR':
            bpy.ops.nla.view_frame(override)

class TIMELINE_OT_view_clip(OPS_, TIMELINE_OT_view, Operator):
    """Clamp all areas to the current clip."""
    bl_idname = "timeline.view_clip"
    bl_label = "View Clip"

    def do_apply(self, context, override):
        f = context.scene.frame_current
        s = context.scene.frame_start
        e = context.scene.frame_end

        context.scene.frame_current = (s + e) / 2

        if override['area'].type == 'DOPESHEET_EDITOR':
            bpy.ops.action.view_frame(override)
        elif override['area'].type == 'NLA_EDITOR':
            bpy.ops.nla.view_frame(override)

        context.scene.frame_current = f

class TIMELINE_OT_view_selected(OPS_, TIMELINE_OT_view, Operator):
    """Clamp all areas to the selected range."""
    bl_idname = "timeline.view_selected"
    bl_label = "View Selected"

    def do_apply(self, context, override):
        if override['area'].type == 'DOPESHEET_EDITOR':
            bpy.ops.action.view_selected(override)
        elif override['area'].type == 'NLA_EDITOR':
            bpy.ops.nla.view_selected(override)

class TIMELINE_OT_view_all(OPS_, TIMELINE_OT_view, Operator):
    """Clamp all areas to the full key range."""
    bl_idname = "timeline.view_all"
    bl_label = "View All"

    def do_apply(self, context, override):
        if override['area'].type == 'DOPESHEET_EDITOR':
            bpy.ops.action.view_all(override)
        elif override['area'].type == 'NLA_EDITOR':
            bpy.ops.nla.view_all(override)

class TIMELINE_OT_select_keys(OPS_, Operator):
    """Select keys in current range."""
    bl_idname = "timeline.select_keys"
    bl_label = "Select Keys"

    selected_bones: bpy.props.BoolProperty(name='Selected Bones')

    @classmethod
    def do_poll(cls, context):
        return POLL.active_object_action(context)

    def do_execute(self, context):
        obj = context.active_object
        action = obj.animation_data.action
        s = context.scene.frame_start
        e = context.scene.frame_end

        bones = []
        for bone in obj.data.bones:
            if bone.select:
                bones.append(bone.name)

        for fcurve in action.fcurves:

            found = False
            for bone in bones:
                if 'pose.bones["{0}"].'.format(bone) in fcurve.data_path:
                    found = True
                    break

            if not found:
                continue

            for key in fcurve.keyframe_points:
                f = key.co[0]
                key.select_control_point = f >= s and f <= e


class TIMELINE_OT_clear():
    @classmethod
    def do_poll(cls, context):        
        s = context.scene
        return POLL.active_object_action(context) and s.frame_current >= s.frame_start and s.frame_current <= s.frame_end

    def next(self, context):
        context.scene.frame_set(context.scene.frame_current+1)

    def prev(self, context):
        context.scene.frame_set(context.scene.frame_current-1)


class TIMELINE_OT_clear_all_prev(TIMELINE_OT_clear, OPS_, Operator):
    """Clears all components of the selected bones, and moves to the previous frame."""
    bl_idname = "timeline.clear_all_prev"
    bl_label = "Clear All Prev"

    def do_execute(self, context):
        bpy.ops.pose.transforms_clear()
        self.prev(context)

class TIMELINE_OT_clear_all_next(TIMELINE_OT_clear, OPS_, Operator):
    """Clears all components of the selected bones, and moves to the next frame."""
    bl_idname = "timeline.clear_all_next"
    bl_label = "Clear All Next"

    def do_execute(self, context):
        bpy.ops.pose.transforms_clear()
        self.next(context)

class TIMELINE_OT_clear_loc_prev(TIMELINE_OT_clear, OPS_, Operator):
    """Clears location of the selected bones, and moves to the previous frame."""
    bl_idname = "timeline.clear_loc_prev"
    bl_label = "Clear Loc Prev"

    def do_execute(self, context):
        bpy.ops.pose.loc_clear()
        self.prev(context)

class TIMELINE_OT_clear_loc_next(TIMELINE_OT_clear, OPS_, Operator):
    """Clears loc components of the selected bones, and moves to the next frame."""
    bl_idname = "timeline.clear_loc_next"
    bl_label = "Clear Loc Next"

    def do_execute(self, context):
        bpy.ops.pose.loc_clear()
        self.next(context)

class TIMELINE_OT_clear_rot_prev(TIMELINE_OT_clear, OPS_, Operator):
    """Clears rot components of the selected bones, and moves to the previous frame."""
    bl_idname = "timeline.clear_rot_prev"
    bl_label = "Clear Rot Prev"

    def do_execute(self, context):
        bpy.ops.pose.rot_clear()
        self.prev(context)

class TIMELINE_OT_clear_rot_next(TIMELINE_OT_clear, OPS_, Operator):
    """Clears rot components of the selected bones, and moves to the next frame."""
    bl_idname = "timeline.clear_rot_next"
    bl_label = "Clear Rot Next"

    def do_execute(self, context):
        bpy.ops.pose.rot_clear()
        self.next(context)

class TIMELINE_OT_clear_sca_prev(TIMELINE_OT_clear, OPS_, Operator):
    """Clears sca components of the selected bones, and moves to the previous frame."""
    bl_idname = "timeline.clear_sca_prev"
    bl_label = "Clear Sca Prev"

    def do_execute(self, context):
        bpy.ops.pose.scale_clear()
        self.prev(context)

class TIMELINE_OT_clear_sca_next(TIMELINE_OT_clear, OPS_, Operator):
    """Clears sca components of the selected bones, and moves to the next frame."""
    bl_idname = "timeline.clear_sca_next"
    bl_label = "Clear Sca Next"

    def do_execute(self, context):
        bpy.ops.pose.scale_clear()
        self.next(context)

class TIMELINE_OT_clear_user_prev(TIMELINE_OT_clear, OPS_, Operator):
    """Clears user components of the selected bones, and moves to the previous frame."""
    bl_idname = "timeline.clear_user_prev"
    bl_label = "Clear User Prev"

    def do_execute(self, context):
        bpy.ops.pose.user_transforms_clear()
        self.prev(context)

class TIMELINE_OT_clear_user_next(TIMELINE_OT_clear, OPS_, Operator):
    """Clears user components of the selected bones, and moves to the next frame."""
    bl_idname = "timeline.clear_user_next"
    bl_label = "Clear User Next"

    def do_execute(self, context):
        bpy.ops.pose.user_transforms_clear()
        self.next(context)
