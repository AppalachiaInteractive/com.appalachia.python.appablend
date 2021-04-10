
import bpy
import cspy
from cspy.polling import DOIF
from cspy.ui import PT_OPTIONS, PT_, UI
from cspy.drivers import *
from cspy.drivers_ops import *

class GRAPH_EDITOR_PT_UI_Tool_Dependencies(bpy.types.Panel, PT_, UI.GRAPH_EDITOR.UI.Drivers):
    bl_label = "Dependencies"
    bl_idname = "GRAPH_EDITOR_PT_UI_Tool_Dependencies"
    bl_icon = cspy.icons.DRIVER

    @classmethod
    def do_poll(cls, context):
        return True

    def do_draw(self, context, scene, layout, obj):
        layout.alert = True
        layout.operator(DRV_OT_update_dependencies.bl_idname, icon=DRV_OT_update_dependencies.bl_icon)
        
        

def register():
    pass

def unregister():
    pass
