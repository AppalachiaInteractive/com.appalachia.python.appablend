import bpy
import math
from mathutils import Vector, Euler, Matrix
import cspy
from cspy import utils

def copy_from_existing(obj1, obj2, prop_names, delete):
    for prop_name in prop_names:
        if hasattr(obj2, prop_name):
            value = getattr(obj2, prop_name)
            setattr(obj1, prop_name, value)
            if delete:
                try:
                    delattr(obj2, prop_name)
                except AttributeError:
                    pass


class ArmatureRootMotionSettings(bpy.types.PropertyGroup):    
    original_root_bone = bpy.props.StringProperty(name='Original Root Bone')
    root_node = bpy.props.PointerProperty(name='Root Node', type=bpy.types.Object)
    root_bone_name = bpy.props.StringProperty(name='Root Bone Name', default='Root')
    root_bone_offset = bpy.props.PointerProperty(name='Root Bone Offset', type=bpy.types.Object)
    hip_bone_name = bpy.props.StringProperty(name='Hip Bone Name', default='Hips')
    hip_bone_offset = bpy.props.PointerProperty(name='Hip Bone Offset', type=bpy.types.Object)

    def copy_from_armature(self, obj):       
        prop_names = set(['original_root_bone','root_node','root_bone_name','root_bone_offset','hip_bone_name','hip_bone_offset'])        
        copy_from_existing(self, obj, prop_names, False)

class RootMotionMetadata(bpy.types.PropertyGroup):
    pose_start: bpy.props.StringProperty(name='Pose Start')
    pose_end: bpy.props.StringProperty(name='Pose End')
    pose_start_rooted: bpy.props.BoolProperty(name='Pose Start Rooted')
    pose_end_rooted: bpy.props.BoolProperty(name='Pose End Rooted')
    loop_time: bpy.props.BoolProperty(name='Loop Time')

    root_node_start_location: bpy.props.FloatVectorProperty(name='Root Node Start Location', subtype=cspy.subtypes.FloatVectorProperty.Subtypes.TRANSLATION, size=3)
    root_node_start_rotation: bpy.props.FloatVectorProperty(name='Root Node Start Rotation', subtype=cspy.subtypes.FloatVectorProperty.Subtypes.EULER, size=3, default=[0,0,0])
 
    root_motion_rot_bake_into: bpy.props.BoolProperty(name='Root Rotation - Bake Into Pose')
    root_motion_x_bake_into: bpy.props.BoolProperty(name='Root Position X - Bake Into Pose')
    root_motion_y_bake_into: bpy.props.BoolProperty(name='Root Position Y - Bake Into Pose')
    root_motion_z_bake_into: bpy.props.BoolProperty(name='Root Position Z - Bake Into Pose')

    root_motion_x_limit_neg: bpy.props.BoolProperty(name='X Limit Neg.')
    root_motion_x_limit_neg_val: bpy.props.FloatProperty(name='X Limit Neg. Val', unit=cspy.subtypes.FloatProperty.Units.LENGTH)
    root_motion_x_limit_pos: bpy.props.BoolProperty(name='X Limit Pos.')
    root_motion_x_limit_pos_val: bpy.props.FloatProperty(name='X Limit Pos. Val', unit=cspy.subtypes.FloatProperty.Units.LENGTH)
    root_motion_y_limit_neg: bpy.props.BoolProperty(name='Y Limit Neg.')
    root_motion_y_limit_neg_val: bpy.props.FloatProperty(name='Y Limit Neg. Val', unit=cspy.subtypes.FloatProperty.Units.LENGTH)
    root_motion_y_limit_pos: bpy.props.BoolProperty(name='Y Limit Pos.')
    root_motion_y_limit_pos_val: bpy.props.FloatProperty(name='Y Limit Pos. Val', unit=cspy.subtypes.FloatProperty.Units.LENGTH)
    root_motion_z_limit_neg: bpy.props.BoolProperty(name='Z Limit Neg.')
    root_motion_z_limit_neg_val: bpy.props.FloatProperty(name='Z Limit Neg. Val', unit=cspy.subtypes.FloatProperty.Units.LENGTH)
    root_motion_z_limit_pos: bpy.props.BoolProperty(name='Z Limit Pos.')
    root_motion_z_limit_pos_val: bpy.props.FloatProperty(name='Z Limit Pos. Val', unit=cspy.subtypes.FloatProperty.Units.LENGTH)

    root_motion_rot_offset: bpy.props.FloatProperty(name='Root Rotation -  Offset')
    root_motion_x_offset: bpy.props.FloatProperty(name='Root Offset X')
    root_motion_y_offset: bpy.props.FloatProperty(name='Root Offset Y')
    root_motion_z_offset: bpy.props.FloatProperty(name='Root Offset Z')
    
    root_bone_offset_location_start: bpy.props.FloatVectorProperty(name='Root Bone Offset Location Start', subtype=cspy.subtypes.FloatVectorProperty.Subtypes.TRANSLATION, size=3)
    root_bone_offset_rotation_start: bpy.props.FloatVectorProperty(name='Root Bone Offset Rotation Start', subtype=cspy.subtypes.FloatVectorProperty.Subtypes.EULER, size=3,default=[0,0,0])
    root_bone_offset_location_end: bpy.props.FloatVectorProperty(name='Root Bone Offset Location End', subtype=cspy.subtypes.FloatVectorProperty.Subtypes.TRANSLATION, size=3)
    root_bone_offset_rotation_end: bpy.props.FloatVectorProperty(name='Root Bone Offset Rotation End', subtype=cspy.subtypes.FloatVectorProperty.Subtypes.EULER, size=3,default=[0,0,0])

    hip_bone_offset_location_start: bpy.props.FloatVectorProperty(name='Hip Bone Offset Location Start', subtype=cspy.subtypes.FloatVectorProperty.Subtypes.TRANSLATION, size=3)
    hip_bone_offset_rotation_start: bpy.props.FloatVectorProperty(name='Hip Bone Offset Rotation Start', subtype=cspy.subtypes.FloatVectorProperty.Subtypes.EULER, size=3,default=[0,0,0])
    hip_bone_offset_location_end: bpy.props.FloatVectorProperty(name='Hip Bone Offset Location End', subtype=cspy.subtypes.FloatVectorProperty.Subtypes.TRANSLATION, size=3)
    hip_bone_offset_rotation_end: bpy.props.FloatVectorProperty(name='Hip Bone Offset Rotation End', subtype=cspy.subtypes.FloatVectorProperty.Subtypes.EULER, size=3,default=[0,0,0])

    root_motion_keys = [
        'root_node_start_location',
        'root_node_start_rotation',
        'root_motion_rot_bake_into',
        'root_motion_x_bake_into',
        'root_motion_y_bake_into',
        'root_motion_z_bake_into',
        'root_motion_rot_offset',
        'root_motion_x_offset',
        'root_motion_y_offset',
        'root_motion_z_offset',

        'root_bone_offset_location_start',
        'root_bone_offset_rotation_start',
        'root_bone_offset_location_end',
        'root_bone_offset_rotation_end',
        'hip_bone_offset_location_start',
        'hip_bone_offset_rotation_start',
        'hip_bone_offset_location_end',
        'hip_bone_offset_rotation_end',

        'root_motion_x_limit_neg',
        'root_motion_x_limit_neg_val',
        'root_motion_x_limit_pos',
        'root_motion_x_limit_pos_val',
        'root_motion_y_limit_neg',
        'root_motion_y_limit_neg_val',
        'root_motion_y_limit_pos',
        'root_motion_y_limit_pos_val',
        'root_motion_z_limit_neg',
        'root_motion_z_limit_neg_val',
        'root_motion_z_limit_pos',
        'root_motion_z_limit_pos_val',
    ]

    def copy_from(self, other):
        cspy.utils.copy_from_to(other, self)
    
    def copy_from_clip(self, obj):        
        prop_names = set(['pose_start','pose_end','pose_start_rooted','pose_end_rooted','loop_time','root_node_start_location','root_node_start_rotation','root_motion_rot_bake_into','root_motion_x_bake_into','root_motion_y_bake_into','root_motion_z_bake_into','root_motion_x_limit_neg','root_motion_x_limit_neg_val','root_motion_x_limit_pos','root_motion_x_limit_pos_val','root_motion_y_limit_neg','root_motion_y_limit_neg_val','root_motion_y_limit_pos','root_motion_y_limit_pos_val','root_motion_z_limit_neg','root_motion_z_limit_neg_val','root_motion_z_limit_pos','root_motion_z_limit_pos_val','root_motion_rot_offset','root_motion_x_offset','root_motion_y_offset','root_motion_z_offset','root_bone_offset_location_start','root_bone_offset_rotation_start','root_bone_offset_location_end','root_bone_offset_rotation_end','hip_bone_offset_location_start','hip_bone_offset_rotation_start','hip_bone_offset_location_end','hip_bone_offset_rotation_end'])
        for key in self.root_motion_keys:
            prop_names.add(key)
        
        copy_from_existing(self, obj, prop_names, False)

