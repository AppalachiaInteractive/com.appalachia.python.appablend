
import bpy
import cspy
from cspy.ui import PT_OPTIONS, PT_, UI
from cspy.polling import DOIF
from cspy.nla import *
from cspy.nla_ops import *
import cspy.unity_ul
from cspy.unity_ul import *


def draw_general_nla(layout, scene):
    col = layout.column(align=True, heading='NLA Strips')

    col.operator(NLA_OT_actions_to_strip.bl_idname)
    col.operator(NLA_OT_strips_from_clips.bl_idname)

    col.separator(factor=2.0)

    col.prop(scene.unity_settings, 'sheet_dir_path')
    col.operator(NLA_OT_strips_from_text.bl_idname)
    col.operator(NLA_OT_import_strips.bl_idname)

class NLA_EDITOR_PT_UI_Tool_NLA(bpy.types.Panel, PT_, UI.NLA_EDITOR.UI.Tool):
    bl_label = "NLA"
    bl_idname = "NLA_EDITOR_PT_UI_Tool_NLA"
    bl_icon = cspy.icons.NLA

    @classmethod
    def do_poll(cls, context):
        return True

    def do_draw(self, context, scene, layout, obj):
        box = layout.box()
        box.label(text='NLA')
        draw_general_nla(box, scene)
        box = layout.box()
        box.operator('pose.transforms_clear')
