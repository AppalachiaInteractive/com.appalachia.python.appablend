import bpy
from appablend.common.basetypes.ui import PT_, UI
from appablend.common.core.enums import icons
from appablend.drivers.ops import DRV_OT_update_dependencies


class GRAPH_EDITOR_PT_UI_Tool_Dependencies(
    bpy.types.Panel, PT_, UI.GRAPH_EDITOR.UI.Drivers
):
    bl_label = "Dependencies"
    bl_idname = "GRAPH_EDITOR_PT_UI_Tool_Dependencies"
    bl_icon = icons.DRIVER

    @classmethod
    def do_poll(cls, context):
        return True

    def do_draw(self, context, scene, layout, obj):
        layout.alert = True
        layout.operator(
            DRV_OT_update_dependencies.bl_idname,
            icon=DRV_OT_update_dependencies.bl_icon,
        )


def register():
    pass


def unregister():
    pass
