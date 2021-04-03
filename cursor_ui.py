
import bpy
import cspy
from cspy.ops import OPS_, OPS_DIALOG
from cspy.polling import POLL
from cspy.ui import PT_OPTIONS, PT_, UI
from cspy.actions import *
from cspy.actions_ops import *
from cspy.cursor import *
from cspy.cursor_ops import *


class VIEW_3D_PT_UI_Tool_Cursor(bpy.types.Panel, PT_, UI.VIEW_3D.UI.Tool):
    bl_label = "Cursor"
    bl_idname = "VIEW_3D_PT_UI_Tool_Cursor"
    bl_icon = cspy.icons.CURSOR

    @classmethod
    def do_poll(cls, context):
        #return POLL.active_object_animation_data(context)
        return True

    def do_draw(self, context, scene, layout, obj):
        box = layout.box()
        grid = box.grid_flow(align=True, columns=3)

        grid.operator(CURSOR_OT_set_world.bl_idname,  icon=CURSOR_OT_set_world.bl_icon)
        grid.operator(CURSOR_OT_set_active.bl_idname, icon=CURSOR_OT_set_active.bl_icon)       
        grid.operator(CURSOR_OT_set_active_bone.bl_idname, icon=CURSOR_OT_set_active_bone.bl_icon)        


def register():
    pass

def unregister():
    pass
