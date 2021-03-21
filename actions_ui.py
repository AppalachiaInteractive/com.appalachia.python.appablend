
import bpy
import cspy
from cspy.ops import OPS_OPTIONS, OPS_, OPS_MODAL
from cspy.polling import POLL
from cspy.ui import PT_OPTIONS, PT_, UI
from cspy.actions import *  
from cspy.actions_ops import *


def draw_globals(layout, scene):
    col = layout.column(align=True, heading='Globals')
    row = col.row(align=True)
    row.operator(ACT_OT_clean_fcurves.bl_idname)
    row.operator(ACT_OT_clean_fcurves_all.bl_idname)
    row = col.row(align=True)
    row.operator(ACT_OT_simplify_fcurves.bl_idname)
    row.operator(ACT_OT_simplify_fcurves_all.bl_idname)
    row = col.row(align=True)
    row.operator(ACT_OT_sample_fcurves.bl_idname)
    row.operator(ACT_OT_sample_fcurves_all.bl_idname)
    row = col.row(align=True)
    row.operator(ACT_OT_decorate_fcurves.bl_idname)
    row.operator(ACT_OT_decorate_fcurves_all.bl_idname)

def draw_interpolation(layout, scene):
    grid = layout.grid_flow(align=True, columns=5)

    for interp in INTERPOLATION.ALL:
        grid.operator(ACT_OT_interpolation_mode.bl_idname, text=interp.capitalize()).interpolation = interp

def draw_interpolation_all(layout, scene):
    grid = layout.grid_flow(align=True, columns=5)

    for interp in INTERPOLATION.ALL:
        grid.operator(ACT_OT_interpolation_mode_all.bl_idname, text=interp.capitalize()).interpolation = interp

def draw_keyframe(layout, scene):
    grid = layout.grid_flow(align=True, columns=3)

    for keyframe_type in KEYFRAME.ALL:
        grid.operator(ACT_OT_keyframe_type.bl_idname, text=keyframe_type.capitalize()).keyframe_type = keyframe_type

def draw_keyframe_all(layout, scene):
    grid = layout.grid_flow(align=True, columns=3)

    for keyframe_type in KEYFRAME.ALL:
        grid.operator(ACT_OT_keyframe_type_all.bl_idname, text=keyframe_type.capitalize()).keyframe_type = keyframe_type


def draw_baking(layout, scene):
    col = layout.column(align=True, heading='Baking')    
    row = col.row(align=True)
    row.operator(ACT_OT_bake_selected_to_action.bl_idname)
    row.operator(ACT_OT_bake_selected_to_action_all.bl_idname)

def draw_general_action(layout, scene):
    col = layout.column(align=True, heading='Actions')
    col.operator(ACT_OT_clamp_to_action.bl_idname)

class VIEW_3D_PT_UI_Tool_Actions(bpy.types.Panel, PT_, UI.VIEW_3D.UI.Tool):
    bl_label = "Actions"
    bl_idname = "VIEW_3D_PT_UI_Tool_Actions"
    bl_icon = cspy.icons.ACTION

    @classmethod
    def do_poll(cls, context):
        #return POLL.active_object_animation_data(context)
        return True

    def do_draw(self, context, scene, layout, obj):
        col = layout.column()

        action_op_helper = obj.action_op_helper
        col.prop(action_op_helper, 'action_loop_sync', toggle=True)

        col.operator(ACT_OT_Action_Euler_To_Quaternion.bl_idname)
        col.operator(ACT_OT_Group_Actions_By_Bone.bl_idname)
        
        col.operator(ACT_OT_combine_all_actions.bl_idname)
        


class DOPESHEET_EDITOR_PT_UI_Tool_Actions(bpy.types.Panel, PT_, UI.DOPESHEET_EDITOR.UI):
    bl_label = "Actions"
    bl_idname = "DOPESHEET_EDITOR_PT_UI_Tool_Actions"
    bl_icon = cspy.icons.ACTION

    @classmethod
    def do_poll(cls, context):
        return True

    def do_draw(self, context, scene, layout, obj):
        box = layout.box()
        draw_general_action(box, scene)

        box = layout.box()
        box.label(text='Globals')
        draw_globals(box, scene)
        
        box = layout.box()
        box.label(text='Baking')
        draw_baking(box, scene)

class DOPESHEET_EDITOR_PT_UI_Tool_Interpolation(bpy.types.Panel, PT_, UI.DOPESHEET_EDITOR.UI):
    bl_label = "Interpolation"
    bl_idname = "DOPESHEET_EDITOR_PT_UI_Tool_Interpolation"
    bl_icon = cspy.icons.IPO_BEZIER

    @classmethod
    def do_poll(cls, context):
        return True

    def do_draw(self, context, scene, layout, obj):
        box = layout.box()
        box.label(text='Interpolation')
        draw_interpolation(box, scene)

        box = layout.box()
        box.label(text='Interpolation (All)')
        draw_interpolation_all(box, scene)

class DOPESHEET_EDITOR_PT_UI_Tool_Keyframe(bpy.types.Panel, PT_, UI.DOPESHEET_EDITOR.UI):
    bl_label = "Keyframe"
    bl_idname = "DOPESHEET_EDITOR_PT_UI_Tool_Keyframe"
    bl_icon = cspy.icons.KEYTYPE_KEYFRAME_VEC

    @classmethod
    def do_poll(cls, context):
        return True

    def do_draw(self, context, scene, layout, obj):
        box = layout.box()
        box.label(text='Keyframe')
        draw_keyframe(box, scene)

        box = layout.box()
        box.label(text='Keyframe (All)')
        draw_keyframe_all(box, scene)

def register():  
    bpy.types.Object.action_op_helper = bpy.props.PointerProperty(type=ActionOpHelper)

def unregister():
    del bpy.types.Object.action_op_helper
