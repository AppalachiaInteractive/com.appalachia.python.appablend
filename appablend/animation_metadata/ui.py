import bpy
from appablend.animation_metadata import core, ops
from appablend.common.basetypes.ui import PT_, UI
from appablend.common.core.enums import icons
from appablend.common.core.polling import DOIF


class AM_PT_AnimationMetadata:
    bl_label = "Animation Metadata"
    bl_icon = icons.ANIM_DATA

    @classmethod
    def do_poll(cls, context):
        return DOIF.ACTIVE.TYPE.IS_ARMATURE(context) and DOIF.ACTIVE.HAS.ACTION(context)

    def do_draw(self, context, scene, layout, obj):
        action = obj.animation_data.action

        action.animation_metadata.draw(
            context, layout, ops.AM_OT_check_properties.bl_idname
        )


class VIEW_3D_PT_UI_Tool_AM_AnimationMetadata(
    UI.VIEW_3D.UI.Tool, AM_PT_AnimationMetadata, PT_, bpy.types.Panel
):
    bl_idname = (
        "VIEW_3D_UVIEW_3D_PT_UI_Tool_AM_AnimationMetadataI_Tool_AM_PT_AnimationMetadata"
    )


class DOPESHEET_EDITOR_PT_UI_AM_AnimationMetadata(
    UI.DOPESHEET_EDITOR.UI, AM_PT_AnimationMetadata, PT_, bpy.types.Panel
):
    bl_idname = "DOPESHEET_EDITOR_PT_UI_AM_AnimationMetadata"


class NLA_EDITOR_PT_UI_Tool_AM_AnimationMetadata(
    UI.NLA_EDITOR.UI.Tool, AM_PT_AnimationMetadata, PT_, bpy.types.Panel
):
    bl_idname = "NLA_EDITOR_PT_UI_Tool_AM_AnimationMetadata"


def register():
    bpy.types.Action.animation_metadata = bpy.props.PointerProperty(
        name="Animation Metadata", type=core.AnimationMetadata
    )


def unregister():
    del bpy.types.Action.animation_metadata
