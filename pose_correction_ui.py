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
        pose = arm.pose
        bone = context.active_pose_bone

        if bone:
            layout.label(text=bone.name,icon=cspy.icons.BONE_DATA)


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
        
        layout.prop(pose_correction, 'location_correction_type')

        row = layout.row(align=True)
        row.alignment = 'RIGHT'

        alerting = pose_correction.get_poll_alert(arm, bone)
        valid = pose_correction.get_poll_valid(context)

        if pose_correction.location_correction_type == 'LOCK':
            
            row.label(text='Ref. Location')
            row.prop(pose_correction, 'reference_location', text='')
            row = layout.row(align=True)
            row.operator(PC_OT_record_reference_location_from_bone.bl_idname)
            row.operator(PC_OT_snap_cursor_to_reference_location.bl_idname)

            row = layout.row()

            row.alert = alerting
            row.label(text='Correction Bone')
            row.prop_search(pose_correction, 'location_handle_bone_name', pose, 'bones', text='')

        elif pose_correction.location_correction_type == 'NEGATE':

            row.alert = alerting
            row.label(text='Negate Bone')
            row.prop_search(pose_correction, 'location_negate_bone_name', pose, 'bones', text='')

        box = layout.box()

        row = box.row(align=True)
        row.label(text="Location")
        row.prop(pose_correction, 'influence_location')

        row = box.row(align=True)
        row.alert = alerting
        row.enabled = not row.alert and valid
        
        rwall = row.operator(PC_OT_correct_pose_location.bl_idname, text='', icon=cspy.icons.PREV_KEYFRAME)
        rw    = row.operator(PC_OT_correct_pose_location.bl_idname, text='', icon=cspy.icons.REW)
        cur   = row.operator(PC_OT_correct_pose_location.bl_idname)
        ff    = row.operator(PC_OT_correct_pose_location.bl_idname, text='', icon=cspy.icons.FF)
        ffall = row.operator(PC_OT_correct_pose_location.bl_idname, text='', icon=cspy.icons.NEXT_KEYFRAME)
        
        rwall.loop, rwall.advance, rwall.forward = True,  True,  False
        rw.loop,    rw.advance,    rw.forward = False, True,  False
        ff.loop,    ff.advance,    ff.forward = False, True,  True
        ffall.loop, ffall.advance, ffall.forward = True,  True,  True

def register():
    bpy.types.PoseBone.pose_correction = bpy.props.PointerProperty(type=PoseCorrection)

def unregister():
    del bpy.types.PoseBone.pose_correction