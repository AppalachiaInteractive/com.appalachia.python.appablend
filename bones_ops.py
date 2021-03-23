import bpy
from bpy.types import Operator
import cspy
from cspy.ops import *
from cspy.polling import POLL
from cspy.bones import *

class BONE_OP:
    @classmethod
    def do_poll(cls, context):
        return POLL.mode_POSE(context) and POLL.active_pose_bone(context)

    def do_execute(self, context):    
        bone = context.active_pose_bone
        pose_correction = bone.pose_correction

        pose_correction.bone_name = bone.name
        return self.bone_execute(context, bone, pose_correction)

class BONES_OT_record_reference_from_bone(BONE_OP, OPS_, Operator):
    """Record bone reference point from 3D position."""
    bl_idname = "bones.record_reference_from_bone"
    bl_label = "From Bone"
    
    def bone_execute(self, context, bone, pose_correction):
        arm = context.active_object
        pose_correction.reference_point = pose_correction.get_location()
        context.scene.cursor.location = arm.matrix_world @ pose_correction.reference_point
        return {'FINISHED'}

class BONES_OT_record_reference_from_cursor(BONE_OP, OPS_, Operator):
    """Record bone reference point from current bone position."""
    bl_idname = "bones.record_reference_from_cursor"
    bl_label = "From Cursor"
    
    def bone_execute(self, context, bone, pose_correction): 
        arm = context.active_object
        pose_correction.reference_point = arm.matrix_world.inverted() @ context.scene.cursor.location        
        return {'FINISHED'}

class BONES_OT_snap_cursor_to_reference(BONE_OP, OPS_, Operator):
    """Snap cursor to the reference point."""
    bl_idname = "bones.snap_cursor_to_reference"
    bl_label = "Snap Cursor"
    
    def bone_execute(self, context, bone, pose_correction): 
        arm = context.active_object
        context.scene.cursor.location = arm.matrix_world @ pose_correction.reference_point
        return {'FINISHED'}


class BONES_OT_correct_pose(OPS_, Operator):
    """Correct a pose bone using the reference"""
    bl_idname = "bones.correct_pose"
    bl_label = "Correct Pose"
    
    @classmethod
    def do_poll(cls, context):
        return (POLL.mode_POSE(context) and POLL.active_pose_bone(context) and
            not pose_correction_invalid(context.active_object, context.active_pose_bone, context.active_pose_bone.pose_correction))

    def do_execute(self, context):    
        arm = context.active_object
        bone = context.active_pose_bone
        pose_correction = bone.pose_correction
        pose_correction.bone_name = bone.name

        control_bone = arm.pose.bones[pose_correction.correction_handle_bone_name]

        object_correction = pose_correction.get_correction()
        oc_matrix = Matrix.Translation(-object_correction)

        world_bone_matrix = arm.matrix_world @ oc_matrix @ control_bone.matrix

        print('Correction         (OBJE): [{0}]'.format(object_correction))
        control_bone.matrix = world_bone_matrix

        path = 'pose.bones["{0}"].location'.format(control_bone.name)
        f = context.scene.frame_current
        for i in range(3):            
            arm.keyframe_insert(path, index=i, frame=f)

        return {'FINISHED'}


class BONES_OT_correct_pose_clip(OPS_MODAL, Operator):
    """Correct all prepared pose bones using the first frame in the clip"""
    bl_idname = "bones.correct_pose_clip"
    bl_label = "Correct Pose (Full Clip)"
    
    @classmethod
    def do_poll(cls, context):
        return (POLL.mode_POSE(context) and POLL.active_pose_bone(context) and
            not pose_correction_invalid(context.active_object, context.active_pose_bone, context.active_pose_bone.pose_correction))

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
                pose_correction.reference_point = pose_correction.get_location()
                continue

            hn = pose_correction.correction_handle_bone_name

            if hn == '' or not hn in arm.pose.bones:
                continue
            
            control_bone = arm.pose.bones[hn]

            object_correction = pose_correction.get_correction()
            oc_matrix = Matrix.Translation(-object_correction)

            world_bone_matrix = arm.matrix_world @ oc_matrix @ control_bone.matrix

            print('Correction         (OBJE): [{0}]'.format(object_correction))
            control_bone.matrix = world_bone_matrix

            path = 'pose.bones["{0}"].location'.format(control_bone.name)
            f = context.scene.frame_current
            for i in range(3):            
                arm.keyframe_insert(path, index=i, frame=f)
        
        context.scene.frame_current += 1
