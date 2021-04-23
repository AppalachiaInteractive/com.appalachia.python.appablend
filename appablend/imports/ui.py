import bpy
from appablend.common.basetypes.ui import PT_, UI
from appablend.common.core.enums import icons
from appablend.imports.core import *
from appablend.imports.ops import *


class IMPORT_PANEL:
    bl_label = "Import"
    bl_icon = icons.FILE_NEW

    @classmethod
    def do_poll(cls, context):
        return True

    def do_draw(self, context, scene, layout, obj):
        settings = context.scene.import_settings

        row = layout.row()
        row.prop(settings, "import_dir")
        row.prop(
            settings, "import_recursive", text="", icon=icons.FILE_REFRESH, toggle=True
        )

        layout.operator(IMPORTS_OT_import_directory.bl_idname)

        layout.row().prop(settings, "maya_mode")

        row = layout.row()
        row.prop(settings, "maya_template")
        row.prop(settings, "maya_import_dir")
        row.prop(
            settings,
            "maya_import_recursive",
            text="",
            icon=icons.FILE_REFRESH,
            toggle=True,
        )

        layout.row().prop(settings, "maya_rot_bone_name")
        layout.row().prop(settings, "maya_rot_value")

        layout.prop(settings, "maya_export_dir")
        layout.operator(IMPORTS_OT_generate_maya_import_export_commands.bl_idname)


class VIEW_3D_PT_UI_Tool_Import(IMPORT_PANEL, PT_, UI.VIEW_3D.UI.Tool, bpy.types.Panel):
    bl_idname = "VIEW_3D_PT_UI_Tool_Import"

    @classmethod
    def poll(cls, context):
        return True


def register():
    bpy.types.Scene.import_settings = bpy.props.PointerProperty(
        name="Import Settings", type=ImportSettings
    )


def unregister():
    del bpy.types.Scene.import_settings
