import bpy
import cspy
import math, mathutils
from cspy import utils, modes
from cspy.modes import *

from mathutils import Matrix, Vector

def get_bone_data_path(bone_name, prop):
    path = 'pose.bones["{0}"].{1}'.format(bone_name, prop)
    return path

def get_edit_bones(obj):
    if hasattr(obj, 'data'):
        return obj.data.edit_bones
    else:
        return obj.edit_bones

def set_bone_parenting(obj, bone_name, parent_name, use_connect):
    entered, active, mode = enter_mode_if(MODE_EDIT, obj)
    
    edit_bones = get_edit_bones(obj)
    bone = edit_bones[bone_name]
    if parent_name in edit_bones:
        bone.parent = edit_bones[parent_name]

    bone.use_connect = use_connect

    exit_mode_if(entered, active, mode)

def is_bone_in_layer(obj, bone_name, index):
    if not bone_name in obj.data.bones:
        return False

    bone = obj.data.bones[bone_name]
    return bone.layers[index]

def set_bone_layer(obj, bone_name, index, value):
    if not bone_name in obj.data.bones:
        return

    obj.data.bones[bone_name].layers[index] = value

def remove_bones_startwith(obj, prefix):
    entered, active, mode = enter_mode_if(MODE_EDIT, obj)

    edit_bones = get_edit_bones(obj)

    removing = []

    for edit_bone in edit_bones:
        if edit_bone.name.startswith(prefix):
            removing.append(edit_bone)

    for edit_bone in remove:
        edit_bones.remove(edit_bone)

    exit_mode_if(entered, active, mode)

def remove_bones(obj, bone_names):
    entered, active, mode = enter_mode_if(MODE_EDIT, obj)

    edit_bones = get_edit_bones(obj)

    for bone_name in bone_names:
        if not bone_name in edit_bones:
            continue
        bone = edit_bones[bone_name]
        edit_bones.remove(bone)

    exit_mode_if(entered, active, mode)

def remove_bone(obj, bone_name):
    if not bone_name in obj.data.bones:
        return      

    entered, active, mode = enter_mode_if(MODE_EDIT, obj)

    edit_bones = get_edit_bones(obj)
    bone = edit_bones[bone_name]
    edit_bones.remove(bone)

    exit_mode_if(entered, active, mode)

def get_pose_bone(obj, bone_name):
    if bone_name in obj.data.bones:
        return obj.pose.bones[bone_name]

    return None

def get_bone_and_pose_bone(obj, bone_name):
    if bone_name in obj.data.bones:
        return obj.data.bones[bone_name], obj.pose.bones[bone_name]

    return None, None

def create_or_get_bone(obj, bone_name):
    if bone_name in obj.data.bones:
        return obj.data.bones[bone_name]

    entered, active, mode = enter_mode_if(MODE_EDIT, obj)    

    edit_bones = get_edit_bones(obj)
    ebone = edit_bones.new(bone_name)
    ebone.tail = Vector([0.0, 0.0, 1.0])

    exit_mode_if(entered, active, mode)

    if 'EDIT' not in bpy.context.mode:
        return obj.data.bones[bone_name]

    return ebone

def shift_bones(obj, matrix):
    entered, active, mode = enter_mode_if(MODE_EDIT, obj)

    edit_bones = get_edit_bones(obj)

    for bone in edit_bones:
        if not bone.use_connect:
            bone.head = matrix @ bone.head

        bone.tail = matrix @ bone.tail

    exit_mode_if(entered, active, mode)

def set_local_head_tail(obj, bone_name, head, tail, roll=0):
    entered, active, mode = enter_mode_if(MODE_EDIT, obj)

    edit_bones = get_edit_bones(obj)
    bone = edit_bones[bone_name]

    bone.head = head
    bone.tail = tail
    bone.roll = roll

    exit_mode_if(entered, active, mode)
    
def copy_local_head_tail(obj, bone_name, copy_bone_name):
    entered, active, mode = enter_mode_if(MODE_EDIT, obj)

    edit_bones = get_edit_bones(obj)
    bone = edit_bones[bone_name]
    copy_bone = edit_bones[copy_bone_name]

    bone.head = copy_bone.head
    bone.tail = copy_bone.tail
    bone.roll = copy_bone.roll

    exit_mode_if(entered, active, mode)

def set_local_tail(obj, bone_name, tail):
    entered, active, mode = enter_mode_if(MODE_EDIT, obj)

    edit_bones = get_edit_bones(obj)
    bone = edit_bones[bone_name]

    bone.tail = tail

    exit_mode_if(entered, active, mode)

def set_edit_bone_matrix_by_object(obj, bone_name, target_object, bone_length = 1.0):
    entered, active, mode = enter_mode_if(MODE_EDIT, obj)

    set_edit_bone_matrix(obj, bone_name, target_object.matrix_local, bone_length)

    exit_mode_if(entered, active, mode)

def set_edit_bone_matrix(obj, bone_name, matrix, bone_length = 1.0):
    entered, active, mode = enter_mode_if(MODE_EDIT, obj)

    edit_bones = get_edit_bones(obj)
    bone = edit_bones[bone_name]
    bone.matrix = matrix
    bone.length = bone_length

    exit_mode_if(entered, active, mode)

def get_pose_bone_rest_matrix_object(obj, bone_name):    
    entered, active, mode = enter_mode_if(MODE_POSE, obj)   

    bone = obj.data.bones[bone_name]
    
    bone_matrix_obj = bone.matrix_local

    exit_mode_if(entered, active, mode)

    return bone_matrix_obj.copy()

def get_pose_bone_matrix_object(obj, bone_name):    
    entered, active, mode = enter_mode_if(MODE_POSE, obj)

    bone = obj.pose.bones[bone_name]
    
    bone_matrix_obj = bone.matrix

    exit_mode_if(entered, active, mode)

    return bone_matrix_obj.copy()

def get_pose_bone_rest_matrix_world(obj, bone_name):    
    entered, active, mode = enter_mode_if(MODE_POSE, obj)

    bone = obj.data.bones[bone_name]
    
    obj_matrix_world = obj.matrix_world
    bone_matrix_obj = bone.matrix_local

    bone_world_matrix = bone_matrix_obj @ obj_matrix_world

    exit_mode_if(entered, active, mode)

    return bone_world_matrix

def get_pose_bone_matrix_world(obj, bone_name):    
    entered, active, mode = enter_mode_if(MODE_POSE, obj)

    bone = obj.pose.bones[bone_name]
    
    obj_matrix_world = obj.matrix_world
    bone_matrix_obj = bone.matrix

    bone_world_matrix = bone_matrix_obj @ obj_matrix_world

    exit_mode_if(entered, active, mode)

    return bone_world_matrix

def set_pose_bone_matrix_object(obj, bone_name, matrix):
    entered, active, mode = enter_mode_if(MODE_POSE, obj)

    bone = obj.pose.bones[bone_name]
    bone.matrix = matrix.copy()

    exit_mode_if(entered, active, mode)

def set_pose_bone_matrix_world(obj, bone_name, matrix):
    entered, active, mode = enter_mode_if(MODE_POSE, obj)

    bone = obj.pose.bones[bone_name]
    bone.matrix = obj.matrix_world.inverted() @ matrix

    exit_mode_if(entered, active, mode)

def reset_pose_bone_location(obj, bone_name):
    entered, active, mode = enter_mode_if(MODE_POSE, obj)

    bone = obj.pose.bones[bone_name]

    rest_matrix = get_pose_bone_rest_matrix_object(obj, bone_name)
    current_matrix = bone.matrix
    
    rl,_,_ = rest_matrix.decompose()
    cl,cr,cs = current_matrix.decompose()

    ml = Matrix.Translation(rl)
    mr = cr.to_matrix().to_4x4()
    msc = Matrix.Diagonal(cs).to_4x4()

    ms = ml @ mr @ msc
    
    bone.matrix = ms

    exit_mode_if(entered, active, mode)

def reset_pose_bone_rotation(obj, bone_name):
    entered, active, mode = enter_mode_if(MODE_POSE, obj)

    bone = obj.pose.bones[bone_name]

    rest_matrix = get_pose_bone_rest_matrix_object(obj, bone_name)
    current_matrix = bone.matrix
    
    _,rr,_ = rest_matrix.decompose()
    cl,cr,cs = current_matrix.decompose()

    ml = Matrix.Translation(cl)
    mr = rr.to_matrix().to_4x4()
    msc = Matrix.Diagonal(cs).to_4x4()

    ms = ml @ mr @ msc
    
    bone.matrix = ms

    exit_mode_if(entered, active, mode)

def reset_pose_bone_transform(obj, bone_name):
    entered, active, mode = enter_mode_if(MODE_POSE, obj)

    bone = obj.pose.bones[bone_name]

    bone.matrix = get_pose_bone_rest_matrix_object(obj, bone_name)    

    exit_mode_if(entered, active, mode)

def set_edit_bone_matrix_world(obj, bone_name, matrix):
    entered, active, mode = enter_mode_if(MODE_EDIT, obj)

    edit_bones = get_edit_bones(obj)
    bone = edit_bones[bone_name]
    bone.matrix = matrix @ obj.matrix_world.inverted()

    exit_mode_if(entered, active, mode)

def set_world_tail(obj, bone_name, tail):
    entered, active, mode = enter_mode_if(MODE_EDIT, obj)

    edit_bones = get_edit_bones(obj)
    bone = edit_bones[bone_name]
    matrix = obj.matrix_world

    bone.tail = matrix.inverted() @ tail

    exit_mode_if(entered, active, mode)

def set_world_head_tail(obj, bone_name, head, tail):
    entered, active, mode = enter_mode_if(MODE_EDIT, obj)

    edit_bones = get_edit_bones(obj)
    bone = edit_bones[bone_name]
    matrix = obj.matrix_world

    bone.head = matrix.inverted() @ head
    bone.tail = matrix.inverted() @ tail
    bone.roll = 0

    exit_mode_if(entered, active, mode)

def set_world_head_tail_xaxis(obj, bone_name, head, tail, x_axis):
    entered, active, mode = enter_mode_if(MODE_EDIT, obj)

    edit_bones = get_edit_bones(obj)
    bone = edit_bones[bone_name]
    matrix = obj.matrix_world

    bone.head = matrix.inverted() @ head
    bone.tail = matrix.inverted() @ tail
    cspy.bones.align_bone_x_axis(bone, x_axis)

    exit_mode_if(entered, active, mode)

def get_world_head_tail(obj, bone_name):
    entered, active, mode = enter_mode_if(MODE_EDIT, obj)

    edit_bones = get_edit_bones(obj)
    bone = edit_bones[bone_name]

    matrix = obj.matrix_world
    head = matrix @ bone.head
    tail = matrix @ bone.tail
    x_axis = matrix @ bone.x_axis

    exit_mode_if(entered, active, mode)

    return matrix, head, tail, x_axis

def are_bones_same_values(obj, bone, obj2, bone2):

    h = obj.matrix_world @ bone.bone.matrix_local @ bone.bone.head
    t = obj.matrix_world @ bone.bone.matrix_local @ bone.bone.tail
    x = bone.x_axis
    y = bone.y_axis
    z = bone.z_axis

    h2 = obj2.matrix_world @ bone2.bone.matrix_local @ bone.head
    t2 = obj2.matrix_world @ bone2.bone.matrix_local @ bone2.bone.tail
    x2 = bone2.x_axis
    y2 = bone2.y_axis
    z2 = bone2.z_axis

    #print(h, t, x)
    #print(h2, t2, x2)

    return (h == h2 and t == t2 and x == x2 and y == y2 and z == z2)

def get_edit_bone_data_dict(obj):
    entered, active, mode = enter_mode_if(MODE_EDIT, obj)

    edit_bones = get_edit_bones(obj)
    edit_bone_dict = {}

    for bone in edit_bones:
        edit_bone_dict[bone.name] = (bone.head.copy(), bone.tail.copy(), bone.roll, bone.use_connect)

    exit_mode_if(entered, active, mode)

    return edit_bone_dict

def get_edit_bone_matrices(obj):
    entered, active, mode = enter_mode_if(MODE_EDIT, obj)

    bone_matrices = {}

    for bone in obj.data.edit_bones:
        bone_matrices[bone.name] = bone.matrix.copy()

    exit_mode_if(entered, active, mode)

    return bone_matrices

def get_pose_bone_matrices(obj):

    entered, active, mode = enter_mode_if(MODE_POSE, obj)

    bone_matrices = {}

    for bone in obj.pose.bones:
        bone_matrices[bone.name] = bone.matrix.copy()

    exit_mode_if(entered, active, mode)

    return bone_matrices

def align_bone_x_axis(edit_bone, new_x_axis):
    """ new_x_axis is a 3D Vector the edit_bone's x-axis will point towards.
    """
    new_x_axis = new_x_axis.cross(edit_bone.y_axis)
    new_x_axis.normalize()
    dot = max(-1.0, min(1.0, edit_bone.z_axis.dot(new_x_axis)))
    angle = math.acos(dot)
    edit_bone.roll += angle
    dot1 = edit_bone.z_axis.dot(new_x_axis)
    edit_bone.roll -= angle * 2.0
    dot2 = edit_bone.z_axis.dot(new_x_axis)
    if dot1 > dot2:
        edit_bone.roll += angle * 2.0

def get_disconnected_bone_names(armature):
    disconnected_bone_names = set()
    for b in armature.data.bones:
        if not b.use_connect:
            disconnected_bone_names.add(b.name)

    return disconnected_bone_names

def get_parent_bone_names(bone):
    parent_bone_names = set()
    parent_bone = bone
    while parent_bone is not None:
        parent_bone_names.add(parent_bone.name)
        parent_bone = parent_bone.parent

    return parent_bone_names

def get_child_bone_names_recursive(bone):
    bone_names = set()

    for child in bone.children:
        bone_names.add(child.name)

        cr = get_child_bone_names_recursive(child)
        bone_names.union(cr)

    return bone_names

