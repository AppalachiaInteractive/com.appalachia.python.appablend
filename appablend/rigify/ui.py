import re

import bpy
from appablend.common.basetypes.ui import PT_, UI
from appablend.common.core.enums import icons
from appablend.rigify.ops import RTU_OT_convert_human


class RTU_PT_Convert_Human(PT_, UI.PROPERTIES.WINDOW.DATA, bpy.types.Panel):
    bl_label = "Rigify to Unity converter"
    bl_icon = icons.FILE_3D

    @classmethod
    def poll(self, context):
        return (
            context.object.type == "ARMATURE"
            and "DEF-upper_arm.L.001" in bpy.context.object.data.bones
        )

    def draw(self, context):
        self.layout.operator(RTU_OT_convert_human.bl_idname)


def register():
    bpy.types.Armature.unity_safe_armature = bpy.props.PointerProperty(
        name="Unity Safe Armature", type=bpy.types.Object
    )


def unregister():
    del bpy.types.Armature.unity_safe_armature
