from cspy.ui import PT_OPTIONS, PT_, UI
from cspy.polling import POLL
from cspy.bones_ops import *
from cspy.bones import *
from cspy.pose_correction import *
from cspy.pose_correction_ops import *

class _PT_PC_:
    @classmethod
    def do_poll(cls, context):
        return POLL.mode_POSE(context)

class VIEW_3D_PT_Pose_Correction(_PT_PC_, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel):
    bl_label = "Pose Correction"
    bl_idname = "VIEW_3D_PT_Pose_Correction"
    bl_icon = cspy.icons.GROUP_BONE

    def do_draw(self, context, scene, layout, obj):
        arm = context.active_object

        row = layout.row(align=True)
        pose_library = obj.pose_library
        pose_index = pose_library.pose_markers.active_index
        pose_marker = pose_library.pose_markers[pose_index]
        row.label(text=pose_marker.name)
        row.operator('poselib.apply_pose').pose_index=pose_index

        pose = arm.pose
        bone = context.active_pose_bone
        if bone:
            row = layout.row(align=True)
            row.label(text='',icon=cspy.icons.BONE_DATA)
            row.label(text=bone.name)


class _PT_PC_AB:
    @classmethod
    def do_poll(cls, context):
        return POLL.mode_POSE(context) and POLL.active_pose_bone(context)

class VIEW_3D_PT_Pose_Correction_01_LOC(_PT_PC_AB, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel):
    bl_label = "Location"
    bl_idname = "VIEW_3D_PT_Pose_Correction_01_LOC"
    bl_icon = cspy.icons.CON_LOCLIKE
    bl_parent_id = VIEW_3D_PT_Pose_Correction.bl_idname

    def do_draw(self, context, scene, layout, obj):
        arm = context.active_object
        pose = arm.pose
        bone = context.active_pose_bone
        pose_correction = bone.pose_correction

        row = layout.row(align=True)
        row.alignment = 'RIGHT'
        row.label(text='Ref. Location')
        row.prop(pose_correction, 'reference_location', text='')
        row = layout.row(align=True)
        row.operator(PC_OT_record_reference_location_from_bone.bl_idname)
        row.operator(PC_OT_snap_cursor_to_reference_location.bl_idname)

        if pose_correction.bone_name != '':
            row = layout.row()
            row.alert = pose_correction_location_handle_invalid(arm, bone, pose_correction)

            row.label(text='Correction Bone')
            row.prop_search(pose_correction, 'location_handle_bone_name', pose, 'bones', text='')

            box = layout.box()
            row = box.row(align=True)
            row.label(text="Location")
            row.prop(pose_correction, 'influence_location')
            row = box.row(align=True)
            row.alert = pose_correction.reference_location_frame == context.scene.frame_current
            row.operator(PC_OT_correct_pose_location_prev.bl_idname, text='', icon=cspy.icons.REW)
            row.operator(PC_OT_correct_pose_location.bl_idname)
            row.operator(PC_OT_correct_pose_location_next.bl_idname, text='', icon=cspy.icons.FF)
            row.separator()
            row.operator(PC_OT_correct_pose_clip_location.bl_idname)

class VIEW_3D_PT_Pose_Correction_02_ROT(_PT_PC_AB, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel):
    bl_label = "Rotation"
    bl_idname = "VIEW_3D_PT_Pose_Correction_02_ROT"
    bl_icon = cspy.icons.CON_ROTLIKE
    bl_parent_id = VIEW_3D_PT_Pose_Correction.bl_idname

    def do_draw(self, context, scene, layout, obj):
        arm = context.active_object
        pose = arm.pose
        bone = context.active_pose_bone
        pose_correction = bone.pose_correction

        row = layout.row(align=True)
        row.alignment = 'RIGHT'
        row.label(text='Ref. Rotation')
        row.prop(pose_correction, 'reference_rotation', text='')
        row = layout.row(align=True)
        row.operator(PC_OT_record_reference_rotation_from_bone.bl_idname)

        box = layout.box()
        row = box.row(align=True)
        row.label(text="Rotation")
        row.prop(pose_correction, 'influence_rotation')
        row = box.row(align=True)
        row.alert = pose_correction.reference_rotation_frame == context.scene.frame_current
        row.operator(PC_OT_correct_pose_rotation_prev.bl_idname, text='', icon=cspy.icons.REW)
        row.operator(PC_OT_correct_pose_rotation.bl_idname)
        row.operator(PC_OT_correct_pose_rotation_next.bl_idname, text='', icon=cspy.icons.FF)
        row.separator()
        row.operator(PC_OT_correct_pose_clip_rotation.bl_idname)

class VIEW_3D_PT_Pose_Correction_03_SCA(_PT_PC_AB, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel):
    bl_label = "Scale"
    bl_idname = "VIEW_3D_PT_Pose_Correction_03_SCA"
    bl_icon = cspy.icons.CON_SIZELIKE
    bl_parent_id = VIEW_3D_PT_Pose_Correction.bl_idname

    def do_draw(self, context, scene, layout, obj):
        arm = context.active_object
        pose = arm.pose
        bone = context.active_pose_bone
        pose_correction = bone.pose_correction

        row = layout.row(align=True)
        row.alignment = 'RIGHT'
        row.label(text='Ref. Scale')
        row.prop(pose_correction, 'reference_scale', text='')
        row = layout.row(align=True)
        row.operator(PC_OT_record_reference_scale_from_bone.bl_idname)

        box = layout.box()
        row = box.row(align=True)
        row.label(text="Scale")
        row.prop(pose_correction, 'influence_scale')
        row = box.row(align=True)
        row.alert = pose_correction.reference_scale_frame == context.scene.frame_current
        row.operator(PC_OT_correct_pose_scale_prev.bl_idname, text='', icon=cspy.icons.REW)
        row.operator(PC_OT_correct_pose_scale.bl_idname)
        row.operator(PC_OT_correct_pose_scale_next.bl_idname, text='', icon=cspy.icons.FF)
        row.separator()
        row.operator(PC_OT_correct_pose_clip_scale.bl_idname)


def register():
    bpy.types.PoseBone.pose_correction = bpy.props.PointerProperty(type=PoseCorrection)

def unregister():
    del bpy.types.PoseBone.pose_correction