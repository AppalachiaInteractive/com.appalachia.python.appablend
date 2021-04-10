import bpy
from bpy.types import Menu, UIList
from cspy.polling import DOIF
from cspy.ui import PT_OPTIONS, PT_, UI
from cspy.animation_metadata import *
from cspy.animation_metadata_ops import *

class AM_PT_AnimationMetadata():
    bl_label = 'Animation Metadata'
    bl_icon = cspy.icons.ANIM_DATA

    @classmethod
    def do_poll(cls, context):
        return DOIF.ACTIVE.TYPE.IS_ARMATURE(context) and DOIF.ACTIVE.HAS.ACTION(context)

    def do_draw(self, context, scene, layout, obj):
        action = obj.animation_data.action

        action.animation_metadata.draw(context, layout, AM_OT_check_properties.bl_idname)

class VIEW_3D_PT_UI_Tool_AM_AnimationMetadata(UI.VIEW_3D.UI.Tool, AM_PT_AnimationMetadata, PT_, bpy.types.Panel):
    bl_idname='VIEW_3D_UVIEW_3D_PT_UI_Tool_AM_AnimationMetadataI_Tool_AM_PT_AnimationMetadata'

class DOPESHEET_EDITOR_PT_UI_AM_AnimationMetadata(UI.DOPESHEET_EDITOR.UI, AM_PT_AnimationMetadata, PT_, bpy.types.Panel):
    bl_idname='DOPESHEET_EDITOR_PT_UI_AM_AnimationMetadata'

class NLA_EDITOR_PT_UI_Tool_AM_AnimationMetadata(UI.NLA_EDITOR.UI.Tool, AM_PT_AnimationMetadata, PT_, bpy.types.Panel):
    bl_idname='NLA_EDITOR_PT_UI_Tool_AM_AnimationMetadata'

def register():
    bpy.types.Action.animation_metadata = bpy.props.PointerProperty(name='Animation Metadata', type=AnimationMetadata)

def unregister():
    del bpy.types.Action.animation_metadata