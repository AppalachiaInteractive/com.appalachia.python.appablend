import bpy
from appablend.common.basetypes.ui import PT_, UI
from appablend.common.core.enums import icons
from appablend.timeline.ops import *
from appablend.textures.ops import TEXTURES_OT_TextureToMesh


class TEXTURES_PT_Textures:
    bl_label = "Textures"
    bl_icon = icons.TEXTURE

    @classmethod
    def do_poll(cls, context):
        return True

    def do_draw(self, context, scene, layout, obj):
        self.draw_texture_buttons(layout, context)

    def draw_texture_buttons(self, layout, context):
        box = layout.box()
        row = box.row(align=True)

        row.separator()


class TEXTURES_VIEW_3D_PT_UI_Tool_TextureToMesh(
    TEXTURES_PT_Textures, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel
):
    bl_idname = "TEXTURES_VIEW_3D_PT_UI_Tool_TextureToMesh"
    bl_label = "Texture To Mesh"
    bl_icon = icons.TEXTURE

    def draw(self, _context):
        layout = self.layout
        box = layout.box()

        row = box.row()

        row.operator(
            TEXTURES_OT_TextureToMesh.bl_idname,
            icon=TEXTURES_OT_TextureToMesh.bl_icon,
            text=TEXTURES_OT_TextureToMesh.bl_label,
        )
