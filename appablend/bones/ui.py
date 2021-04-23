import bpy
from appablend.common.basetypes import ui
from appablend.common.basetypes.ui import PT_, UI
from appablend.common.core.enums import icons
from appablend.common.core.polling import DOIF


class _PT_POSEBONE_:
    @classmethod
    def do_poll(cls, context):
        return DOIF.MODE.IS_POSE(context) and DOIF.ACTIVE.POSE_BONE(context)


class VIEW_3D_PT_PoseBone(_PT_POSEBONE_, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel):
    bl_label = "Pose Bone"
    bl_idname = "VIEW_3D_PT_PoseBone"
    bl_icon = icons.BONE_DATA

    def do_draw(self, context, scene, layout, obj):
        layout = self.layout
        col = layout.column()

        bone = context.active_pose_bone
        col.label(text=bone.name)

        row = col.row(align=True)

        row.prop(bone, "location")

        row = col.row(align=True)
        if bone.rotation_mode == "QUATERNION":
            row.prop(bone, "rotation_quaternion")
        elif bone.rotation_mode == "AXISANGLE":
            row.prop(bone, "rotation_axis_angle")
        else:
            row.prop(bone, "rotation_euler")

        row = col.row(align=True)
        row.prop(bone, "scale")

        ui.layout_euler(layout, bone)
