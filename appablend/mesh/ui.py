import bpy
from appablend.common.basetypes.ui import PT_, UI
from appablend.common.core.polling import DOIF


class VIEW_3D_PT_Object_DisplayType(bpy.types.Panel, PT_, UI.VIEW_3D.UI.Tool):
    bl_label = "Object"
    bl_idname = "VIEW_3D_PT_Object_DisplayType"

    @classmethod
    def do_poll(cls, context):
        return DOIF.ACTIVE.TYPE.IS_MESH(context)

    def do_draw(self, context, scene, layout, obj):
        self.layout.prop(context.active_object, "display_type")
