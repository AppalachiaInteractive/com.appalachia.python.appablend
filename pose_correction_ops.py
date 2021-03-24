import bpy
from bpy.types import Operator
import cspy
from cspy.ops import *
from cspy.polling import POLL
from cspy.bones import *
from cspy.pose_correction import *

class PC_OP:
    @classmethod
    def do_poll(cls, context):
        return POLL.mode_POSE(context) and POLL.active_pose_bone(context)

    def do_execute(self, context):
        bone = context.active_pose_bone
        pose_correction = bone.pose_correction

        pose_correction.bone_name = bone.name
        return self.bone_execute(context, bone, pose_correction)

class PC_OT_record_reference_location_from_bone(PC_OP, OPS_, Operator):
    """Record bone reference location from 3D position."""
    bl_idname = "pc.record_reference_location_from_bone"
    bl_label = "From Bone"

    def bone_execute(self, context, bone, pose_correction):
        arm = context.active_object
        pose_correction.reference_location = pose_correction.get_location()
        pose_correction.reference_location_frame = context.scene.frame_current
        context.scene.cursor.location = arm.matrix_world @ pose_correction.reference_location
        return {'FINISHED'}

class PC_OT_snap_cursor_to_reference_location(PC_OP, OPS_, Operator):
    """Snap cursor to the reference location."""
    bl_idname = "pc.snap_cursor_to_reference_location"
    bl_label = "Snap Cursor"

    def bone_execute(self, context, bone, pose_correction):
        arm = context.active_object
        context.scene.cursor.location = arm.matrix_world @ pose_correction.reference_location
        return {'FINISHED'}

class PC_OT_record_reference_rotation_from_bone(PC_OP, OPS_, Operator):
    """Record bone reference rotation from 3D position."""
    bl_idname = "pc.record_reference_rotation_from_bone"
    bl_label = "From Bone"

    def bone_execute(self, context, bone, pose_correction):
        arm = context.active_object
        pose_correction.reference_rotation = pose_correction.get_rotation()
        pose_correction.reference_rotation_frame = context.scene.frame_current
        return {'FINISHED'}

class PC_OT_record_reference_scale_from_bone(PC_OP, OPS_, Operator):
    """Record bone reference scale from 3D position."""
    bl_idname = "pc.record_reference_scale_from_bone"
    bl_label = "From Bone"

    def bone_execute(self, context, bone, pose_correction):
        arm = context.active_object
        pose_correction.reference_scale = pose_correction.get_scale()
        pose_correction.reference_scale_frame = context.scene.frame_current
        return {'FINISHED'}

class PC_OT_correct_pose_location(OPS_, Operator):
    bl_idname = "pc.correct_pose_location"
    bl_label = "Correct Pose"

    forward: bpy.props.BoolProperty(name='Forward')
    advance: bpy.props.BoolProperty(name='Advance')
    loop: bpy.props.BoolProperty(name='Loop')

    @classmethod
    def do_poll(cls, context):
        first = (POLL.mode_POSE(context) and
                POLL.active_pose_bone(context) and
                context.scene.frame_current > context.scene.frame_start and
                context.scene.frame_current < context.scene.frame_end)

        if not first:
            return False
            
        pc = context.active_pose_bone.pose_correction
        return pc.get_poll_valid(context)

    def do_apply(self, context, arm, bone, pose_correction):
        changed_bones = pose_correction.correct_pose_location(context, arm, bone)

        for b in changed_bones:
            path = get_bone_data_path(b, 'location')

            f = context.scene.frame_current
            for i in range(3):
                arm.keyframe_insert(path, index=i, frame=f)

    """Correct a pose bone using the reference"""
    def do_execute(self, context):
        arm = context.active_object
        bone = context.active_pose_bone
        pose_correction = bone.pose_correction
        pose_correction.bone_name = bone.name
        scene = context.scene

        if self.loop:                
            while self.do_poll(context):            
                self.do_apply(context, arm, bone, pose_correction)

                if self.forward:
                    scene.frame_set(scene.frame_current + 1)
                else:   
                    scene.frame_set(scene.frame_current - 1)
        else:
            self.do_apply(context, arm, bone, pose_correction)
            
            if self.advance:
                if self.forward:
                    scene.frame_set(scene.frame_current + 1)
                else:   
                    scene.frame_set(scene.frame_current - 1)

        return {'FINISHED'}