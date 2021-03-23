import bpy, cspy
from cspy.ui import PT_OPTIONS, PT_, UI
from cspy.polling import POLL
from cspy.bones_ops import *
from cspy.bones import *

class _PT_POSEBONE_:
    @classmethod
    def do_poll(cls, context):
        return POLL.mode_POSE(context) and POLL.active_pose_bone(context)

class VIEW_3D_PT_PoseBone(_PT_POSEBONE_, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel):
    bl_label = "Pose Bone"
    bl_idname = "VIEW_3D_PT_PoseBone"
    bl_icon = cspy.icons.BONE_DATA

    def do_draw(self, context, scene, layout, obj):
        layout = self.layout
        col = layout.column()

        bone = context.active_pose_bone
        col.label(text=bone.name)
        col.separator()
        cspy.ui.layout_euler(layout, bone)

class VIEW_3D_PT_Pose_Correction(_PT_POSEBONE_, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel):
    bl_label = "Pose Correction"
    bl_idname = "VIEW_3D_PT_Pose_Correction"
    bl_icon = cspy.icons.GROUP_BONE

    def do_draw(self, context, scene, layout, obj):
        arm = context.active_object
        pose = arm.pose
        bone = context.active_pose_bone
        pose_correction = bone.pose_correction
        box = layout.box()

        row = box.row()
        row.enabled=False
        row.prop(context, 'active_pose_bone')
        row.label(text='',icon=cspy.icons.BONE_DATA)
        row.label(text=bone.name)
        row = box.row()
        row.label(text='Reference Point')
        row.prop(pose_correction, 'reference_point', text='')
        row = box.row()
        row.operator(BONES_OT_record_reference_from_bone.bl_idname)
        row.operator(BONES_OT_record_reference_from_cursor.bl_idname)
        row.operator(BONES_OT_snap_cursor_to_reference.bl_idname)
        
        if pose_correction.bone_name == '':
            return
        
        row = box.row()        
        if pose_correction_invalid(arm, bone, pose_correction):
            row.alert = True

        row.label(text='Correction Bone')
        row.prop_search(pose_correction, 'correction_handle_bone_name', pose, 'bones', text='')
        
        row = box.row()        
        row.prop(pose_correction, 'location')
        row = box.row()
        row.prop(pose_correction, 'correction')

        #box.separator()
        row = box.row()
        row.prop(pose_correction, 'influence')
        row = box.row()
        row.operator(BONES_OT_correct_pose.bl_idname)
        row = box.row()
        row.operator(BONES_OT_correct_pose_clip.bl_idname)
        


def register():
    bpy.types.PoseBone.pose_correction = bpy.props.PointerProperty(type=PoseCorrection)

def unregister():
    del bpy.types.PoseBone.pose_correction