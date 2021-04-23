import bpy
from appablend.armature.core import ArmatureModification
from appablend.armature.ops import AM_Integrate_Empties
from appablend.common.basetypes import ui
from appablend.common.basetypes.ui import PT_, UI
from appablend.common.core.enums import icons
from appablend.common.core.polling import DOIF


class VIEW_3D_PT_UI_Tool_Armature(bpy.types.Panel, PT_, UI.VIEW_3D.UI.Tool):
    bl_label = "Armature"
    bl_idname = "VIEW_3D_PT_UI_Tool_Armature"
    bl_icon = icons.ARMATURE_DATA

    @classmethod
    def do_poll(cls, context):
        return DOIF.ACTIVE.TYPE.IS_ARMATURE(context)

    def do_draw(self, context, scene, layout, obj):

        ui.layout_euler(layout, obj)

        col = layout.column()
        armature_mod = context.active_object.armature_mod
        col.prop(armature_mod, "root_motion_mute", toggle=True)
        col.operator(AM_Integrate_Empties.bl_idname)


def register():
    bpy.types.Object.armature_mod = bpy.props.PointerProperty(type=ArmatureModification)


def unregister():
    del bpy.types.Object.armature_mod
