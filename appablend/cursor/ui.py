import bpy
from appablend.common.basetypes.ui import PT_, UI
from appablend.common.core.enums import icons
from appablend.cursor.ops import (CURSOR_OT_set_active,
                                  CURSOR_OT_set_active_bone,
                                  CURSOR_OT_set_world)


class VIEW_3D_PT_UI_Tool_Cursor(bpy.types.Panel, PT_, UI.VIEW_3D.UI.Tool):
    bl_label = "Cursor"
    bl_idname = "VIEW_3D_PT_UI_Tool_Cursor"
    bl_icon = icons.CURSOR

    @classmethod
    def do_poll(cls, context):
        return True

    def do_draw(self, context, scene, layout, obj):
        box = layout.box()
        grid = box.grid_flow(align=True, columns=3)

        grid.operator(CURSOR_OT_set_world.bl_idname, icon=CURSOR_OT_set_world.bl_icon)
        grid.operator(CURSOR_OT_set_active.bl_idname, icon=CURSOR_OT_set_active.bl_icon)
        grid.operator(
            CURSOR_OT_set_active_bone.bl_idname, icon=CURSOR_OT_set_active_bone.bl_icon
        )


def register():
    pass


def unregister():
    pass
