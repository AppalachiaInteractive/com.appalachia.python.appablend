import bpy, cspy
from cspy.ui import PT_OPTIONS, PT_, UI
from cspy.polling import POLL

class VIEW_3D_PT_PoseBone(bpy.types.Panel, PT_, UI.VIEW_3D.UI.Tool):
    bl_label = "Pose Bone"
    bl_idname = "VIEW_3D_PT_posebone"
    bl_icon = cspy.icons.BONE_DATA

    @classmethod
    def do_poll(cls, context):
        return POLL.mode_POSE(context) and POLL.active_pose_bone(context)

    def do_draw(self, context, scene, layout, obj):
        layout = self.layout
        col = layout.column()

        bone = context.active_pose_bone
        col.label(text=bone.name)
        col.separator()
        cspy.ui.layout_euler(layout, bone)
        