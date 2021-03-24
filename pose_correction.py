import bpy
import cspy
import math, mathutils
from mathutils import Matrix, Vector, Euler, Quaternion
from cspy.bones import *
from cspy import subtypes

CORRECTION_TYPE = [ 'LOCK', 'NEGATE' ]

CORRECTION_TYPE_ENUM =  cspy.utils.create_enum(CORRECTION_TYPE)
CORRECTION_TYPE_ENUM_DEF = 'LOCK'

class PoseCorrection(bpy.types.PropertyGroup):
    bone_name: bpy.props.StringProperty(name='Bone')

    location_correction_type: bpy.props.EnumProperty(name='Location Correction Type', items=CORRECTION_TYPE_ENUM, default=CORRECTION_TYPE_ENUM_DEF)

    reference_location: bpy.props.FloatVectorProperty(name='Reference Point', subtype=subtypes.FloatVectorProperty.Subtypes.TRANSLATION)
    location_handle_bone_name: bpy.props.StringProperty(name='Correction Bone')
    influence_location: bpy.props.FloatProperty(name='Influence', default=1.0,min=0.0,max=1.0)
    reference_location_frame: bpy.props.IntProperty(name="Frame")    
    
    location_negate_bone_name: bpy.props.StringProperty(name='Negate Bone')

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
        if self.location_correction_type == 'LOCK':
            return self.influence_location * (self.reference_location - self.get_location())
        else:
            bl = self.get_location()
            nl = self.get_location_by_bone(self.location_negate_bone_name)

            return self.influence_location * (nl - bl)

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

    def get_poll_alert(self, arm, bone):
        disconnected_bone_names = get_disconnected_bone_names(arm)
        parent_bone_names = get_parent_bone_names(bone)
        child_bone_names = get_child_bone_names_recursive(bone)

        if self.location_correction_type == 'LOCK':
            hb = self.location_handle_bone_name
            return (hb != '' and (hb not in disconnected_bone_names or hb not in parent_bone_names))
        else:
            nb = self.location_negate_bone_name
            return (nb != '' and (nb not in disconnected_bone_names and nb in child_bone_names))

        return False
        
    def get_poll_valid(self, context):
        if self.location_correction_type == 'LOCK':
            return context.scene.frame_current != self.reference_location_frame
        else:
            return self.location_negate_bone_name != ''

    def correct_pose_location(self, context, armature, pose_bone):
        self.bone_name = pose_bone.name

        obj_correction = self.get_location_correction()
        obj_correction_matrix = Matrix.Translation(obj_correction)
        neg_obj_correction_matrix = Matrix.Translation(-obj_correction)

        if self.location_correction_type == 'LOCK':
            other_bone_name = self.location_handle_bone_name
        else:
            other_bone_name = self.location_negate_bone_name

        if other_bone_name == '' or not other_bone_name in armature.pose.bones:
            return []

        other_bone = armature.pose.bones[other_bone_name]        
        
        pose_bone_world_matrix = armature.matrix_world @ obj_correction_matrix @ pose_bone.matrix
        neg_pose_bone_world_matrix = armature.matrix_world @ neg_obj_correction_matrix @ pose_bone.matrix
        
        other_bone_world_matrix = armature.matrix_world @ obj_correction_matrix @ other_bone.matrix
        neg_other_bone_world_matrix = armature.matrix_world @ neg_obj_correction_matrix @ other_bone.matrix
        
        if self.location_correction_type == 'LOCK':
            other_bone.matrix = other_bone_world_matrix
            return [other_bone.name]
        else:
            pose_bone.matrix = pose_bone_world_matrix
            other_bone.matrix = neg_other_bone_world_matrix
            return [pose_bone.name, other_bone.name]
