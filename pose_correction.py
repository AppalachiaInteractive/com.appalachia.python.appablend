import bpy
import cspy
import math, mathutils
from mathutils import Matrix, Vector, Euler, Quaternion
from cspy.bones import *
from cspy import subtypes

CORRECTION_TYPE = [ 'LOCK', 'NEGATE' ]

CORRECTION_TYPE_ENUM =  cspy.utils.create_enum(CORRECTION_TYPE)
CORRECTION_TYPE_ENUM_DEF = 'LOCK'

NEGATE_TYPE = [ 'EXACT', 'OFFSET', 'OBJECT', 'CANCEL' ]

NEGATE_TYPE_ENUM =  cspy.utils.create_enum(NEGATE_TYPE)
NEGATE_TYPE_ENUM_DEF = 'EXACT'

class PoseCorrection(bpy.types.PropertyGroup):
    bone_name: bpy.props.StringProperty(name='Bone')

    location_correction_type: bpy.props.EnumProperty(name='Location Correction Type', items=CORRECTION_TYPE_ENUM, default=CORRECTION_TYPE_ENUM_DEF)

    reference_location: bpy.props.FloatVectorProperty(name='Reference Point', subtype=subtypes.FloatVectorProperty.Subtypes.TRANSLATION)
    location_handle_bone_name: bpy.props.StringProperty(name='Correction Bone')
    influence_location: bpy.props.FloatProperty(name='Influence', default=1.0,min=0.0,max=1.0)
    reference_location_frame: bpy.props.IntProperty(name="Frame")

    location_negate_bone_name: bpy.props.StringProperty(name='Negate Bone')
    location_negate_type: bpy.props.EnumProperty(name='Type', items=NEGATE_TYPE_ENUM, default=NEGATE_TYPE_ENUM_DEF)
    negate_co_offset: bpy.props.FloatVectorProperty(name='Negation Offset', subtype=subtypes.FloatVectorProperty.Subtypes.TRANSLATION)
    negate_co_object: bpy.props.FloatVectorProperty(name='Negation Point', subtype=subtypes.FloatVectorProperty.Subtypes.TRANSLATION)
    negate_cancel_x: bpy.props.BoolProperty(name='Cancel X')
    negate_cancel_y: bpy.props.BoolProperty(name='Cancel Y')
    negate_cancel_z: bpy.props.BoolProperty(name='Cancel Z')


    def decompose_bones(self, name):
        arm =  self.id_data
        bone = arm.pose.bones[name]
        loc, rot, sca = bone.matrix.decompose()
        return loc, rot, sca

    def get_location_by_bone(self, name):
        loc, rot, sca = self.decompose_bones(name)
        return loc

    def get_location(self):
        return self.get_location_by_bone(self.bone_name)

    def get_location_correction(self):
        if self.location_correction_type == 'LOCK':
            return self.influence_location * (self.reference_location - self.get_location())
        elif self.location_correction_type == 'NEGATE':
            bl = self.get_location()

            if self.location_negate_type == 'EXACT':
                nl = self.get_location_by_bone(self.location_negate_bone_name)
            elif self.location_negate_type == 'OFFSET':
                nl = self.get_location_by_bone(self.location_negate_bone_name) + self.negate_co_offset
            elif self.location_negate_type == 'OBJECT':
                nl = self.negate_co_object
            elif self.location_negate_type == 'CANCEL':
                nl = self.get_location_by_bone(self.location_negate_bone_name)
                nl[0] = 0 if self.negate_cancel_x else nl[0]
                nl[1] = 0 if self.negate_cancel_x else nl[1]
                nl[2] = 0 if self.negate_cancel_x else nl[2]

            return self.influence_location * (nl - bl)

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
