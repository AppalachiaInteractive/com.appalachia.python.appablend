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

class PC_OT_PC:
    @classmethod
    def do_poll(cls, context):
        return (POLL.mode_POSE(context))

class PC_OT_correct_pose_BASE(PC_OT_PC, OPS_):
    @classmethod
    def do_poll(cls, context):
        return (
                POLL.mode_POSE(context) and
                POLL.active_pose_bone(context) and
                context.scene.frame_current > context.scene.frame_start and
                context.scene.frame_current < context.scene.frame_end
            )

    """Correct a pose bone using the reference"""
    def do_execute(self, context):
        arm = context.active_object
        bone = context.active_pose_bone
        pose_correction = bone.pose_correction
        pose_correction.bone_name = bone.name

        self.do_apply(context, arm, bone, pose_correction)

        self.do_finish(context)
        return {'FINISHED'}

class PC_OT_correct_pose_location_BASE(PC_OT_correct_pose_BASE):
    def do_apply(self, context, arm, bone, pose_correction):
        control_bone = arm.pose.bones[pose_correction.location_handle_bone_name]

        if correct_pose_location(context, arm, bone):
            path = get_bone_data_path(control_bone.name, 'location')

            f = context.scene.frame_current
            for i in range(3):
                arm.keyframe_insert(path, index=i, frame=f)

class PC_OT_correct_pose_rotation_BASE(PC_OT_correct_pose_BASE):
    def do_apply(self, context, arm, bone, pose_correction):
        if correct_pose_rotation(context, arm, bone):
            path = get_bone_data_path(bone.name, 'rotation_quaternion')

            f = context.scene.frame_current
            for i in range(4):
                arm.keyframe_insert(path, index=i, frame=f)

class PC_OT_correct_pose_scale_BASE(PC_OT_correct_pose_BASE):
    def do_apply(self, context, arm, bone, pose_correction):
        if correct_pose_scale(context, arm, bone):
            path = get_bone_data_path(bone.name, 'scale')

            f = context.scene.frame_current
            for i in range(3):
                arm.keyframe_insert(path, index=i, frame=f)

class PC_OT_correct_pose_location(PC_OT_correct_pose_location_BASE, Operator):
    bl_idname = "pc.correct_pose_location"
    bl_label = "Correct Pose"

    def do_finish(self, context):
        pass

class PC_OT_correct_pose_location_prev(PC_OT_correct_pose_location_BASE, PC_OT_PC, OPS_, Operator):
    bl_idname = "pc.correct_pose_location_prev"
    bl_label = "Correct Pose"

    def do_finish(self, context):
        context.scene.frame_current -= 1

class PC_OT_correct_pose_location_next(PC_OT_correct_pose_location_BASE, PC_OT_PC, OPS_, Operator):
    bl_idname = "pc.correct_pose_location_next"
    bl_label = "Correct Pose"

    def do_finish(self, context):
        context.scene.frame_current += 1


class PC_OT_correct_pose_rotation(PC_OT_correct_pose_rotation_BASE, Operator):
    bl_idname = "pc.correct_pose_rotation"
    bl_label = "Correct Pose"

    def do_finish(self, context):
        pass

class PC_OT_correct_pose_rotation_prev(PC_OT_correct_pose_rotation_BASE, PC_OT_PC, OPS_, Operator):
    bl_idname = "pc.correct_pose_rotation_prev"
    bl_label = "Correct Pose"

    def do_finish(self, context):
        context.scene.frame_current -= 1

class PC_OT_correct_pose_rotation_next(PC_OT_correct_pose_rotation_BASE, PC_OT_PC, OPS_, Operator):
    bl_idname = "pc.correct_pose_rotation_next"
    bl_label = "Correct Pose"

    def do_finish(self, context):
        context.scene.frame_current += 1

class PC_OT_correct_pose_scale(PC_OT_correct_pose_scale_BASE, Operator):
    bl_idname = "pc.correct_pose_scale"
    bl_label = "Correct Pose"

    def do_finish(self, context):
        pass

class PC_OT_correct_pose_scale_prev(PC_OT_correct_pose_scale_BASE, PC_OT_PC, OPS_, Operator):
    bl_idname = "pc.correct_pose_scale_prev"
    bl_label = "Correct Pose"

    def do_finish(self, context):
        context.scene.frame_current -= 1

class PC_OT_correct_pose_scale_next(PC_OT_correct_pose_scale_BASE, PC_OT_PC, OPS_, Operator):
    bl_idname = "pc.correct_pose_scale_next"
    bl_label = "Correct Pose"

    def do_finish(self, context):
        context.scene.frame_current += 1

class PC_OT_correct_pose_clip_location(PC_OT_PC, OPS_MODAL, Operator):
    """Correct all prepared pose bones locations using the first frame in the clip"""
    bl_idname = "pc.correct_pose_clip_location"
    bl_label = "Correct Pose (Full Clip)"

    def do_start(self, context, event):
        context.scene.frame_current = context.scene.frame_start

    def do_continue(self, context, event):
        return context.scene.frame_current < context.scene.frame_end

    def do_iteration(self, context, event):
        arm = context.active_object

        for bone in arm.pose.bones:
            pose_correction = bone.pose_correction
            pose_correction.bone_name = bone.name
            control_bone = arm.pose.bones[pose_correction.location_handle_bone_name]

            if context.scene.frame_current == context.scene.frame_start:
                pose_correction.reference_location = pose_correction.get_location()
                continue

            if correct_pose_location(context, arm, bone):
                path = get_bone_data_path(control_bone.name, 'location')

                f = context.scene.frame_current
                for i in range(3):
                    arm.keyframe_insert(path, index=i, frame=f)

        context.scene.frame_current += 1

class PC_OT_correct_pose_clip_rotation(PC_OT_PC, OPS_MODAL, Operator):
    """Correct all prepared pose bones rotations using the first frame in the clip"""
    bl_idname = "pc.correct_pose_clip_rotation"
    bl_label = "Correct Pose (Full Clip)"

    def do_start(self, context, event):
        context.scene.frame_current = context.scene.frame_start

    def do_continue(self, context, event):
        return context.scene.frame_current < context.scene.frame_end

    def do_iteration(self, context, event):
        arm = context.active_object

        for bone in arm.pose.bones:
            pose_correction = bone.pose_correction
            pose_correction.bone_name = bone.name

            if context.scene.frame_current == context.scene.frame_start:
                pose_correction.reference_rotation = pose_correction.get_rotation()
                continue

            if correct_pose_rotation(context, arm, bone):
                path = get_bone_data_path(bone.name, 'rotation_quaternion')

                f = context.scene.frame_current
                for i in range(4):
                    arm.keyframe_insert(path, index=i, frame=f)

        context.scene.frame_current += 1

class PC_OT_correct_pose_clip_scale(PC_OT_PC, OPS_MODAL, Operator):
    """Correct all prepared pose bones scales using the first frame in the clip"""
    bl_idname = "pc.correct_pose_clip_scale"
    bl_label = "Correct Pose (Full Clip)"

    def do_start(self, context, event):
        context.scene.frame_current = context.scene.frame_start

    def do_continue(self, context, event):
        return context.scene.frame_current < context.scene.frame_end

    def do_iteration(self, context, event):
        arm = context.active_object

        for bone in arm.pose.bones:
            pose_correction = bone.pose_correction
            pose_correction.bone_name = bone.name

            if context.scene.frame_current == context.scene.frame_start:
                pose_correction.reference_scale = pose_correction.get_scale()
                continue

            if correct_pose_scale(context, arm, bone):
                path = get_bone_data_path(bone.name, 'scale')

                f = context.scene.frame_current
                for i in range(3):
                    arm.keyframe_insert(path, index=i, frame=f)

        context.scene.frame_current += 1
