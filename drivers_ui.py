
import bpy
import cspy
from cspy.polling import POLL
from cspy.ui import PT_OPTIONS, PT_, UI
from cspy.drivers import *
from cspy.drivers_ops import *

class GRAPH_EDITOR_PT_UI_Tool_Dependencies(bpy.types.Panel, PT_, UI.GRAPH_EDITOR.UI.Tool):
    bl_label = "Dependencies"
    bl_idname = "GRAPH_EDITOR_PT_UI_Tool_Dependencies"
    bl_icon = cspy.icons.DRIVER

    @classmethod
    def do_poll(cls, context):
        return POLL.active_ARMATURE(context)

    def do_draw(self, context, scene, layout, obj):

        cspy.ui.layout_euler(layout, obj)

        col = layout.column()
        armature_mod = context.active_object.armature_mod
        col.prop(armature_mod, 'root_motion_mute', toggle=True)
        col.operator(AM_Integrate_Empties.bl_idname)

def register():
    pass

def unregister():
    pass
