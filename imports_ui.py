import cspy
from cspy.imports import *
from cspy.imports_ops import *
from cspy.ui import PT_OPTIONS, PT_, UI
from cspy.polling import POLL
from cspy import subtypes
from cspy.unity import *

class IMPORT_PANEL:
    bl_label = "Import"
    bl_icon = cspy.icons.FILE_NEW

    @classmethod
    def do_poll(cls, context):
        return True

    def do_draw(self, context, scene, layout, obj):
        obj = get_active_unity_object(context)
        unity_settings = scene.unity_settings

        col = layout.column(align=True)
        row = col.row(align=True)

        row.prop(unity_settings, 'mode')

        row.prop(unity_settings, 'draw_sheets', toggle=True, text='', icon=unity_settings.icon_sheets)
        row.prop(unity_settings, 'draw_keyframes', toggle=True, text='', icon=unity_settings.icon_keys)
        row.prop(unity_settings, 'draw_clips', toggle=True, text='', icon=unity_settings.icon_clips)

        if unity_settings.mode != 'ACTIVE':
            row = col.row(align=True)
            row.prop(unity_settings, 'target_armature')


class VIEW_3D_PT_UI_Tool_Import(IMPORT_PANEL, PT_, UI.VIEW_3D.UI.Tool, bpy.types.Panel):
    bl_idname = "VIEW_3D_PT_UI_Tool_Import"

    @classmethod
    def poll(cls, context):
        return True

def register():
    bpy.types.Scene.import_dir = bpy.props.StringProperty(name="Import Directory", subtype=subtypes.StringProperty.Subtypes.DIR_PATH)

def unregister():
    del bpy.types.Scene.import_dir