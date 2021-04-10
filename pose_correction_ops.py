import bpy
from bpy.types import Operator
import cspy
from cspy.ops import *
from cspy.polling import DOIF
from cspy.bones import *
from cspy.pose_correction import *
from cspy.actions import *

class PC_OP:
    @classmethod
    def do_poll(cls, context):
        return DOIF.MODE.IS_POSE(context) and DOIF.ACTIVE.POSE_BONE(context)

    def do_execute(self, context):
        bone = context.active_pose_bone
        pose_correction = bone.pose_correction

        pose_correction.bone_name = bone.name
        return self.bone_execute(context, bone, pose_correction)

class PC_OT_insert_anchor_keyframe(PC_OP, OPS_, Operator):
    """Inserts a keyframe for the referenced bones as an anchor."""
    bl_idname = "pc.insert_anchor_keyframe"
    bl_label = "Insert Anchor Keyframe"

    def bone_execute(self, context, bone, pose_correction):
        arm = context.active_object
        frame = context.scene.frame_current

        if pose_correction.location_correction_type == 'NEGATE':
            action = arm.animation_data.action

            for fcurve in action.fcurves:
                value = fcurve.evaluate(frame)
                insert_keyframe(fcurve, frame, value, replace=False, needed=False, fast=True, keyframe_type=KEYFRAME.KEYFRAME)

            for fcurve in action.fcurves:
                fcurve.update()

        return {'FINISHED'}

class PC_OT_record_reference_from_bone(PC_OP, OPS_, Operator):
    """Record bone reference location from 3D position."""
    bl_idname = "pc.record_reference_from_bone"
    bl_label = "From Bone"

    prop_name: bpy.props.StringProperty(name="Property Name")

    def bone_execute(self, context, bone, pose_correction):
        arm = context.active_object

        val = pose_correction.get(self.prop_name)

        pose_correction.set_ref(self.prop_name, val, context.scene.frame_current, context.scene.cursor)

        return {'FINISHED'}

class PC_OT_snap_cursor_to_reference(PC_OP, OPS_, Operator):
    """Snap cursor to the reference location."""
    bl_idname = "pc.snap_cursor_to_reference"
    bl_label = "Snap Cursor"

    prop_name: bpy.props.StringProperty(name="Property Name")

    def bone_execute(self, context, bone, pose_correction):
        arm = context.active_object
        if self.prop_name.lower() == 'location':
            pose_correction.cursor_to_loc(context.scene.cursor)
        elif self.prop_name.lower() == 'transform':
            pose_correction.cursor_to_transform(context.scene.cursor)

        
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

class PC_OT_correct_pose:

    forward: bpy.props.BoolProperty(name='Forward')
    advance: bpy.props.BoolProperty(name='Advance')
    loop: bpy.props.BoolProperty(name='Loop')
    prop_name: bpy.props.StringProperty(name='Prop Name')

    @classmethod
    def do_poll(cls, context):
        first = (DOIF.MODE.IS_POSE(context) and
                DOIF.ACTIVE.POSE_BONE(context) and
                context.scene.frame_current >= context.scene.frame_start and
                context.scene.frame_current <= context.scene.frame_end)

        if not first:
            return False

        pc = context.active_pose_bone.pose_correction

        frame = cls.get_reference_frame(pc)

        return pc.get_poll_valid(context, cls.prop_name)

    def do_apply(self, context, arm, bone, pose_correction, prop_name, changed_bones, length):

        for b in changed_bones:
            path = get_bone_data_path(b, prop_name)

            f = context.scene.frame_current
            for i in range(length):
                arm.keyframe_insert(path, index=i, frame=f)

    def do_execute(self, context):
        arm = context.active_object
        bone = context.active_pose_bone
        pose_correction = bone.pose_correction
        pose_correction.bone_name = bone.name
        scene = context.scene   

        correction_func = self.get_correction_function(pose_correction)
        prop_names = self.get_prop_names()
        lengths = self.get_lengths()

        if self.loop:
            while self.do_poll(context):                            

                changed_bones = correction_func(context, arm, bone)

                for index, prop_name in enumerate(prop_names):
                    length = lengths[index]

                    self.do_apply(context, arm, bone, pose_correction, prop_name, changed_bones, length)

                if self.forward:
                    scene.frame_set(scene.frame_current + 1)
                else:
                    scene.frame_set(scene.frame_current - 1)
        else:            

            changed_bones = correction_func(context, arm, bone)

            for index, prop_name in enumerate(prop_names):
                length = lengths[index]
                self.do_apply(context, arm, bone, pose_correction, prop_name, changed_bones, length)

            if self.advance:
                if self.forward:
                    scene.frame_set(scene.frame_current + 1)
                else:
                    scene.frame_set(scene.frame_current - 1)

        return {'FINISHED'}

class PC_OT_correct_pose_location(PC_OT_correct_pose, OPS_, Operator):
    bl_idname = "pc.correct_pose_location"
    bl_label = "Correct Pose"

    prop_name = 'location'

    @classmethod
    def get_reference_frame(cls, pose_correction):
        return pose_correction.location_reference_frame

    @classmethod
    def get_correction_function(cls, pose_correction):
        return pose_correction.correct_pose_location

    @classmethod
    def get_prop_names(cls):
        return ['location', 'rotation_quaternion', 'scale']

    @classmethod
    def get_lengths(cls):
        return [3, 4, 3]

class PC_OT_correct_pose_rotation(PC_OT_correct_pose, OPS_, Operator):
    bl_idname = "pc.correct_pose_rotation"
    bl_label = "Correct Pose"

    prop_name = 'rotation'

    @classmethod
    def get_reference_frame(cls, pose_correction):
        return -1

    @classmethod
    def get_correction_function(cls, pose_correction):
        return pose_correction.correct_pose_rotation

    @classmethod
    def get_prop_names(cls):
        return ['location', 'rotation_quaternion', 'scale']

    @classmethod
    def get_lengths(cls):
        return [3, 4, 3]

class PC_OT_correct_pose_transform(PC_OT_correct_pose, OPS_, Operator):
    bl_idname = "pc.correct_pose_transform"
    bl_label = "Correct Pose"

    prop_name = 'transform'

    @classmethod
    def get_reference_frame(cls, pose_correction):
        return pose_correction.transform_reference_frame

    @classmethod
    def get_correction_function(cls, pose_correction):
        return pose_correction.correct_pose_transform

    @classmethod
    def get_prop_names(cls):
        return ['location', 'rotation_quaternion', 'scale']

    @classmethod
    def get_lengths(cls):
        return [3, 4, 3]