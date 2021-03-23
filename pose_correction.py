import bpy
import cspy
import math, mathutils
from mathutils import Matrix, Vector, Euler, Quaternion
from cspy.bones import *
from cspy import subtypes

class PoseCorrection(bpy.types.PropertyGroup):
    bone_name: bpy.props.StringProperty(name='Bone')

    reference_location: bpy.props.FloatVectorProperty(name='Reference Point', subtype=subtypes.FloatVectorProperty.Subtypes.TRANSLATION)
    location_handle_bone_name: bpy.props.StringProperty(name='Correction Bone')
    influence_location: bpy.props.FloatProperty(name='Influence', default=1.0,min=0.0,max=1.0)
    reference_location_frame: bpy.props.IntProperty(name="Frame")

    reference_rotation: bpy.props.FloatVectorProperty(name='Reference Rotation', size=4, subtype=subtypes.FloatVectorProperty.Subtypes.QUATERNION)
    influence_rotation: bpy.props.FloatProperty(name='Influence', default=1.0,min=0.0,max=1.0)
    reference_rotation_frame: bpy.props.IntProperty(name="Frame")

    reference_scale: bpy.props.FloatVectorProperty(name='Reference Scale', size=3, subtype=subtypes.FloatVectorProperty.Subtypes.XYZ)
    influence_scale: bpy.props.FloatProperty(name='Influence', default=1.0,min=0.0,max=1.0)
    reference_scale_frame: bpy.props.IntProperty(name="Frame")

    def decompose_bones(self, name):
        arm =  self.id_data
        bone = arm.pose.bones[name]
        loc, rot, sca = bone.matrix.decompose()
        return loc, rot, sca

    def get_location_by_bone(self, name):
        loc, rot, sca = self.decompose_bones(name)
        return loc

    def get_rotation_by_bone(self, name):
        loc, rot, sca = self.decompose_bones(name)
        return rot

    def get_scale_by_bone(self, name):
        loc, rot, sca = self.decompose_bones(name)
        return sca

    def get_location(self):
        return self.get_location_by_bone(self.bone_name)

    def get_location_correction(self):
        return self.influence_location * (self.get_location() - self.reference_location)

    def get_rotation(self):
        return self.get_rotation_by_bone(self.bone_name)

    def get_rotation_correction(self):
        reference = Quaternion(self.reference_rotation)
        current = self.get_rotation()

        diff = current.rotation_difference(reference)

        correction = Quaternion().slerp(diff, self.influence_rotation)
        return correction

    def get_scale(self):
        return self.get_scale_by_bone(self.bone_name)

    def get_scale_correction(self):
        return self.influence_scale * (self.get_scale() - self.reference_scale)

def pose_correction_location_handle_invalid(arm, bone, pose_correction):
    pose = arm.pose
    disconnected_bones = {}
    for b in arm.data.bones:
        if not b.use_connect:
            disconnected_bones[b.name] = pose.bones[b.name]

    parent_bones = set()
    parent_bone = bone
    while parent_bone is not None:
        parent_bones.add(parent_bone.name)
        parent_bone = parent_bone.parent

    hb = pose_correction.location_handle_bone_name
    if (hb != '' and
        (hb not in disconnected_bones or hb not in parent_bones)
        ):
        return True
    return False

def correct_pose_location(context, armature, pose_bone):
    pose_correction = pose_bone.pose_correction
    pose_correction.bone_name = pose_bone.name

    hn = pose_correction.location_handle_bone_name

    if hn == '' or not hn in armature.pose.bones:
        return False

    control_bone = armature.pose.bones[hn]

    object_correction = pose_correction.get_location_correction()
    oc_matrix = Matrix.Translation(-object_correction)

    world_bone_matrix = armature.matrix_world @ oc_matrix @ control_bone.matrix

    control_bone.matrix = world_bone_matrix

    return True

def correct_pose_rotation(context, armature, pose_bone):
    pose_correction = pose_bone.pose_correction
    pose_correction.bone_name = pose_bone.name

    object_correction = pose_correction.get_rotation_correction()
    oc_matrix = object_correction.normalized().to_matrix().to_4x4()

    world_bone_matrix = armature.matrix_world @ oc_matrix @ pose_bone.matrix

    pose_bone.matrix = world_bone_matrix

    return True

def correct_pose_scale(context, armature, pose_bone):
    pose_correction = pose_bone.pose_correction
    pose_correction.bone_name = pose_bone.name

    object_correction = pose_correction.get_scale_correction()
    oc_matrix = Matrix.Scale(-object_correction, size=4)

    world_bone_matrix = armature.matrix_world @ oc_matrix @ pose_bone.matrix

    pose_bone.matrix = world_bone_matrix

    return True