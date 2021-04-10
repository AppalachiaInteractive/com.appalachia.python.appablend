
import bpy
import cspy
from cspy.ui import PT_OPTIONS, PT_, UI
from cspy.polling import DOIF
from cspy.timeline import *
from cspy.timeline_ops import *

class TIMELINE_PT_Timeline:
    bl_label = "Timeline"
    bl_icon = cspy.icons.FRAME_NEXT

    @classmethod
    def do_poll(cls, context):
        return True

    def do_draw(self, context, scene, layout, obj):
        self.draw_timeline_buttons(layout, context)

    def draw_timeline_buttons(self, layout, context):
        box = layout.box()
        row = box.row(align=True)
        tool_settings = bpy.context.scene.tool_settings
        row.prop(tool_settings, 'use_keyframe_insert_auto', icon=cspy.icons.REC, text='', toggle=True)
        row.separator()
        row.operator(TIMELINE_OT_rew_timeline.bl_idname, icon=cspy.icons.REW, text='')
        row.operator(TIMELINE_OT_play_timeline.bl_idname, icon=cspy.icons.PLAY, text='')
        row.operator(TIMELINE_OT_stop_timeline.bl_idname, icon=cspy.icons.PAUSE,text='')
        row.operator(TIMELINE_OT_ff_timeline.bl_idname, icon=cspy.icons.FF,text='')
        #row = box.row(align=True)
        #row.alignment='LEFT'
        row.label(text='Clip:')
        row.operator(TIMELINE_OT_guess_previous_start.bl_idname, text='', icon=cspy.icons.PREV_KEYFRAME)
        row.operator(TIMELINE_OT_guess_previous_end.bl_idname, text='', icon=cspy.icons.REW)
        row.operator(TIMELINE_OT_previous_clip.bl_idname, text='', icon=cspy.icons.PLAY_REVERSE)
        row.operator(TIMELINE_OT_guess_clip.bl_idname, text='', icon=cspy.icons.PAUSE)
        row.operator(TIMELINE_OT_next_clip.bl_idname, text='', icon=cspy.icons.PLAY)
        row.operator(TIMELINE_OT_guess_next_end.bl_idname, text='', icon=cspy.icons.FF)
        row.operator(TIMELINE_OT_guess_next_start.bl_idname, text='', icon=cspy.icons.NEXT_KEYFRAME)
        row = box.row(align=True)
        row.label(text='Clamp:')
        row.operator(TIMELINE_OT_clamp_start_to_current.bl_idname, text='Start')
        row.operator(TIMELINE_OT_clamp_end_to_current.bl_idname, text='End')
        row.operator(TIMELINE_OT_clamp_to_action.bl_idname, text='Action')
        row.operator(TIMELINE_OT_clamp_to_strip.bl_idname, text='Strip')
        row.operator(TIMELINE_OT_clamp_to_strips.bl_idname, text='Strips')

        row = box.row(align=True)

        if context.area.type == UI.DOPESHEET_EDITOR.bl_space_type:
            row.operator('action.view_frame', text='Current')
            row.operator(TIMELINE_OT_view_frame.bl_idname, text='Clip')
            row.operator('action.view_selected', text='Selected')
            row.operator('action.view_all', text='All')
        elif context.area.type == UI.NLA_EDITOR.bl_space_type:
            row.operator('nla.view_frame', text='Current')
            row.operator(TIMELINE_OT_view_frame.bl_idname, text='Clip')
            row.operator('nla.view_selected', text='Selected')
            row.operator('nla.view_all', text='All')
        else:
            row.operator(TIMELINE_OT_view_frame.bl_idname, text='Current')
            row.operator(TIMELINE_OT_view_frame.bl_idname, text='Clip')
            row.operator(TIMELINE_OT_view_selected.bl_idname, text='Selected')
            row.operator(TIMELINE_OT_view_all.bl_idname, text='All')

        row = box.row(align=True)
        row.operator(TIMELINE_OT_select_keys.bl_idname, text='Select Keys (By Bone)').selected_bones = True
        row.operator(TIMELINE_OT_select_keys.bl_idname)


class TIMELINE_VIEW_3D_PT_UI_Tool_Timeline(TIMELINE_PT_Timeline, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel):
    bl_idname = "TIMELINE_VIEW_3D_PT_UI_Tool_Timeline"

class TIMELINE_DOPESHEET_EDITOR_PT_UI_Timeline(TIMELINE_PT_Timeline, UI.DOPESHEET_EDITOR.UI, PT_, bpy.types.Panel):
    bl_idname = "TIMELINE_DOPESHEET_EDITOR_PT_UI_Timeline"

class TIMELINE_NLA_EDITOR_PT_UI_Tool_Timeline(TIMELINE_PT_Timeline, UI.NLA_EDITOR.UI.Tool, PT_, bpy.types.Panel):
    bl_idname = "TIMELINE_NLA_EDITOR_PT_UI_Tool_Timeline"

class TIMELINE_VIEW_3D_PT_UI_Tool_ClearTransforms(TIMELINE_PT_Timeline, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel):
    bl_idname = "TIMELINE_VIEW_3D_PT_UI_Tool_ClearTransforms"
    bl_label = "Clear Transform"
    bl_icon = cspy.icons.GHOST_ENABLED

    def draw(self, _context):
        layout = self.layout
        box = layout.box()

        row = box.row()

        row.operator(TIMELINE_OT_clear_all_next.bl_idname, text='', icon=cspy.icons.REW)
        row.operator("pose.transforms_clear", text="All")
        row.operator(TIMELINE_OT_clear_all_next.bl_idname, text='', icon=cspy.icons.FF)
        
        row = box.row()

        row.operator(TIMELINE_OT_clear_loc_next.bl_idname, text='', icon=cspy.icons.REW)
        row.operator("pose.loc_clear", text="Location")
        row.operator(TIMELINE_OT_clear_loc_next.bl_idname, text='', icon=cspy.icons.FF)
        row.separator()
        row.operator(TIMELINE_OT_clear_rot_next.bl_idname, text='', icon=cspy.icons.REW)
        row.operator("pose.rot_clear", text="Rotation")
        row.operator(TIMELINE_OT_clear_rot_next.bl_idname, text='', icon=cspy.icons.FF)
        row.separator()
        row.operator(TIMELINE_OT_clear_sca_next.bl_idname, text='', icon=cspy.icons.REW)
        row.operator("pose.scale_clear", text="Scale")
        row.operator(TIMELINE_OT_clear_sca_next.bl_idname, text='', icon=cspy.icons.FF)

        row = box.row()

        row.operator(TIMELINE_OT_clear_user_prev.bl_idname, text='', icon=cspy.icons.REW)
        row.operator("pose.user_transforms_clear", text="Reset Unkeyed")
        row.operator(TIMELINE_OT_clear_user_next.bl_idname, text='', icon=cspy.icons.FF)