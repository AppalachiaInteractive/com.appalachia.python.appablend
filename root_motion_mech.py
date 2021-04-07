import bpy
import cspy
from cspy.armature import *
from cspy.bones import *

class EMPTY:
    @classmethod
    def create(cls, name):
        o = bpy.data.objects.new(name, None)
        return o

    class DISPLAY_TYPE:
        PLAIN_AXES = 'PLAIN_AXES'
        ARROWS = 'ARROWS'
        SINGLE_ARROW = 'SINGLE_ARROW'
        CIRCLE = 'CIRCLE'
        CUBE = 'CUBE'
        SPHERE = 'SPHERE'
        CONE = 'CONE'

class SPACE:
    WORLD = 'WORLD'
    LOCAL = 'LOCAL'

class MIX_MODE:
    OFFSET = 'OFFSET'
    BEFORE = 'BEFORE'
    ADD = 'ADD'
    REPLACE = 'REPLACE'
    AFTER = 'AFTER'

class DRIVER:
    class TYPE:
        AVERAGE = 'AVERAGE'
        SCRIPTED = 'SCRIPTED'

def get_or_create_collection(context, name, parent):    
    c = bpy.data.collections.get(name)
    if not c:
        c = bpy.data.collections.new(name)
    
    if parent and c.name not in parent.children:
        parent.children.link(c)

def get_or_create_empty(context, name, parent, collection, draw_size, draw_type):    
    o = bpy.data.objects.get(name)    
    if not o:
        o = EMPTY.create(name)
        context.scene.objects.link( o )

    o.empty_display_size = draw_size
    o.empty_display_type = draw_type

    if parent:
        parent.children.link(o)
    if collection:
        collection.children.link(o)

    return o

def get_or_create_constraint(obj, name, t):
    if name in obj.constraints:
        con = obj.constraints[name]
    else:
        con = obj.constraints.new(t)
    
    return con
    
def add_copy_location_constraint(obj, name, target, use_offset=False, target_space=SPACE.WORLD, owner_space=SPACE.WORLD, use_x=True,use_y=True,use_z=True,invert_x=False,invert_y=False,invert_z=False):
    t = 'COPY_LOCATION'
    con = get_or_create_constraint(obj, name, t)    
    con.name = name    
    con.target = target
    con.use_offset = use_offset
    con.target_space = target_space
    con.owner_space = owner_space
    con.use_x = use_x
    con.use_y = use_y
    con.use_z = use_z
    con.invert_x = invert_x
    con.invert_y = invert_y
    con.invert_z = invert_z
    return con
    
def add_copy_rotation_constraint(obj, name, target, mix_mode=MIX_MODE.REPLACE, target_space=SPACE.WORLD, owner_space=SPACE.WORLD, use_x=True,use_y=True,use_z=True,invert_x=False,invert_y=False,invert_z=False):
    t = 'COPY_ROTATION'
    con = get_or_create_constraint(obj, name, t)    
    con.name = name    
    con.target = target
    con.mix_mode = mix_mode
    con.target_space = target_space
    con.owner_space = owner_space
    con.use_x = use_x
    con.use_y = use_y
    con.use_z = use_z
    con.invert_x = invert_x
    con.invert_y = invert_y
    con.invert_z = invert_z
    return con
    
def add_copy_transform_constraint(obj, name, target, subtarget, mix_mode=MIX_MODE.REPLACE):
    t = 'COPY_TRANSFORMS'
    con = get_or_create_constraint(obj, name, t)    
    con.name = name    
    con.target = target
    con.subtarget = '' if subtarget is None else subtarget
    con.mix_mode = mix_mode
    return con

def add_child_of_constraint(obj, name, target):
    t = 'CHILD_OF'
    con = get_or_create_constraint(obj, name, t)    
    con.name = name    
    con.target = target
    con.inverse_matrix = con.target.matrix_world.inverted()
    return con

def add_limit_loc_constraint(obj, name):
    t = 'LIMIT_LOC'
    con = get_or_create_constraint(obj, name, t)    
    con.name = name    
    return con


def add_driver(obj, data_path, array_index, driver_type, target, target_data_path, target_v_name, expression):
    if not obj.animation_data:
        obj.animation_data_create()
    
    drivers = obj.animation_data.drivers
    if array_index >= 0:
        d = drivers.find(data_path, index=array_index)
        if not d:
            d = drivers.new(data_path, index=array_index)
    else:
        d = drivers.find(data_path)
        if not d:
            d = drivers.new(data_path)
    
    drv = d.driver
    drv.type = driver_type

    if len(drv.variables) > 0:
        v = drv.variables[0]
    else:
        v = drv.variables.new(target_v_name)
    
    v.name = target_v_name
    v.targets[0].id = target
    v.targets[0].data_path = target_data_path
    
    drv.expression = expression
    return d

    
def create_root_motion_setup(context, armature):
    scene = context.scene
    sc = scene.collection

    to_rest_position(armature)
    settings = armature.data.root_motion_settings
    
    rmc    = get_or_create_collection(context,  'Root Motion',       sc)
    rm_ac  = get_or_create_collection(context,  '1_Root Adjustment', rmc)
    rm_sc  = get_or_create_collection(context,  '2_Settings',        rmc)
    rm_rc  = get_or_create_collection(context,  '3_Root',            rmc)
    rm_pc  = get_or_create_collection(context,  '4_Pelvis',          rmc)

    dt = EMPTY.DISPLAY_TYPE
    new = get_or_create_empty
    c = context
    _00_basis                 = new(c, '_00_basis',                 None, rm_ac, 0.15, dt.PLAIN_AXES)
    _01_current               = new(c, '_01_current',               None, rm_ac, 0.50, dt.PLAIN_AXES)
    _02_tracking              = new(c, '_02_tracking',              None, rm_ac, 0.50, dt.ARROWS)
    _03_offset                = new(c, '_03_offset',                None, rm_ac, 0.22, dt.ARROWS)
    _05_foundation_adjustment = new(c, '_05_foundation_adjustment', None, rm_ac, 0.40, dt.ARROWS)
    _10_start                 = new(c, '_10_start',                 None, rm_ac, 0.81, dt.ARROWS)
    _35_baked_loc             = new(c, '_35_baked_loc',             None, rm_sc, 0.19, dt.PLAIN_AXES)
    _35_baked_rot             = new(c, '_35_baked_rot',             None, rm_sc, 0.20, dt.PLAIN_AXES)
    _50_aggregate_loc         = new(c, '_50_aggregate_loc',         None, rm_sc, 0.27, dt.PLAIN_AXES)
    _51_aggregate             = new(c, '_51_aggregate',             None, rm_sc, 0.41, dt.PLAIN_AXES)
    _97_root_adjustment       = new(c, '_97_root_adjustment',       None, rm_rc, 0.35, dt.ARROWS)
    _98_rootmotion_final      = new(c, '_98_rootmotion_final',      None, rm_rc, 0.35, dt.ARROWS)
    _01_pose                  = new(c, '_01_pose',                  None, rm_pc, 0.20, dt.ARROWS)
    _02_hip_adjustment        = new(c, '_02_hip_adjustment',        None, rm_pc, 0.40, dt.ARROWS)
    _99_hips_final            = new(c, '_99_hips_final',            None, rm_pc, 0.10, dt.ARROWS)
    Hips                      = new(c, 'Hips',                      None, rmc,   0.52, dt.CUBE)
    RootMotion                = new(c, 'RootMotion',                None, rmc,   0.48, dt.ARROWS)
    
    if settings.root_bone_name == '':
        settings.root_bone_name = 'Root'
    if settings.hip_bone_name == '':
        settings.hip_bone_name = 'Hip'
    
    settings.root_node = _02_tracking
    settings.root_bone_offset = _51_aggregate
    settings.hip_bone_offset = _01_pose
    


    objs = [_00_basis,_01_current,_02_tracking,_03_offset,_05_foundation_adjustment,_10_start,_35_baked_loc,_35_baked_rot,_50_aggregate_loc,_51_aggregate,_97_root_adjustment,_98_rootmotion_final,_01_pose,_02_hip_adjustment,_99_hips_final,Hips,RootMotion]

    for obj in objs:
        obj.matrix_world = Matrix.Identity(4)

    _00_basis.matrix_world = get_pose_bone_rest_matrix_world(armature, settings.original_root_bone)
    
    add_copy_transform_constraint(_01_current, 'Copy Transforms', armature, settings.original_root_bone)
    add_copy_transform_constraint(_02_tracking, 'Copy Transforms', _00_basis, None)
    add_child_of_constraint(_02_tracking, 'Child Of', _01_current)

    add_driver(_03_offset, 'location', 0, DRIVER.TYPE.SCRIPTED, armature, 'root_motion_x_offset', 'offset', '-offset')
    add_driver(_03_offset, 'location', 1, DRIVER.TYPE.SCRIPTED, armature, 'root_motion_y_offset', 'offset', '-offset')
    add_driver(_03_offset, 'location', 2, DRIVER.TYPE.SCRIPTED, armature, 'root_motion_z_offset', 'offset', '-offset')

    add_driver(_03_offset, 'rotation_euler', 2, DRIVER.TYPE.SCRIPTED, armature, 'root_motion_rot_offset', 'offset', 'offset * 0.0174533')

    add_driver(_05_foundation_adjustment, 'location', 0, DRIVER.TYPE.AVERAGE, armature, 'root_node_start_location_0', 'v', '')
    add_driver(_05_foundation_adjustment, 'location', 1, DRIVER.TYPE.AVERAGE, armature, 'root_node_start_location_1', 'v', '')
    add_driver(_05_foundation_adjustment, 'location', 2, DRIVER.TYPE.AVERAGE, armature, 'root_node_start_location_2', 'v', '')
    add_driver(_05_foundation_adjustment, 'rotation_euler', 0, DRIVER.TYPE.AVERAGE, armature, 'root_node_start_rotation_0', 'v', '')
    add_driver(_05_foundation_adjustment, 'rotation_euler', 1, DRIVER.TYPE.AVERAGE, armature, 'root_node_start_rotation_1', 'v', '')
    add_driver(_05_foundation_adjustment, 'rotation_euler', 2, DRIVER.TYPE.AVERAGE, armature, 'root_node_start_rotation_2', 'v', '')

    add_copy_transform_constraint(_10_start, 'Copy Transforms', _02_tracking, None)
    add_copy_location_constraint(_10_start, 'Copy Location', _05_foundation_adjustment, use_offset=True)
    add_copy_rotation_constraint(_10_start, 'Copy Rotation', _05_foundation_adjustment, mix_mode=MIX_MODE.AFTER)

    add_copy_location_constraint(_35_baked_loc, '_rm_x_bake_into', _10_start, use_offset=False, use_x=True,  use_y=False, use_z=False)
    add_copy_location_constraint(_35_baked_loc, '_rm_y_bake_into', _10_start, use_offset=False, use_x=False, use_y=True,  use_z=False)
    add_copy_location_constraint(_35_baked_loc, '_rm_z_bake_into', _10_start, use_offset=False, use_x=False, use_y=False, use_z=True)
        
    add_driver(_35_baked_loc, 'constraints["_rm_x_bake_into"].influence', -1, DRIVER.TYPE.SCRIPTED, armature, 'root_motion_x_bake_into', 'v', '1.0-v')
    add_driver(_35_baked_loc, 'constraints["_rm_y_bake_into"].influence', -1, DRIVER.TYPE.SCRIPTED, armature, 'root_motion_y_bake_into', 'v', '1.0-v')
    add_driver(_35_baked_loc, 'constraints["_rm_z_bake_into"].influence', -1, DRIVER.TYPE.SCRIPTED, armature, 'root_motion_z_bake_into', 'v', '1.0-v')
 
    add_copy_rotation_constraint(_35_baked_rot, '_05_rot_bake_into', _10_start, use_x=False, use_y=False)
    add_driver(_35_baked_rot, 'constraints["_05_rot_bake_into"].influence', -1, DRIVER.TYPE.SCRIPTED, armature, 'root_motion_rot_bake_into', 'v', '1.0-v')
    
    add_child_of_constraint(_50_aggregate_loc, 'Child Of', _35_baked_rot)
    add_copy_location_constraint(_50_aggregate_loc, _35_baked_loc.name, _35_baked_loc, use_offset=False)

    add_copy_transform_constraint(_51_aggregate, 'Copy Transforms', _50_aggregate_loc, None)

    offset_objs = [
        (_97_root_adjustment, 'root' ),
        (_02_hip_adjustment, 'hip' )
    ]
    offset_keys = [
        ('location', 'location'),
        ('rotation_euler', 'rotation'),
    ]
    for offset_obj in offset_objs:
        for offset_key in offset_keys:
            target = offset_obj[0]
            bone_name = offset_obj[1]
            data_path = offset_key[0]
            var_token = offset_key[1]

            for i in range(3):
                full_key = '{0}_bone_offset_{1}_{2}'.format(bone_name, var_token, i)
                add_driver(target, data_path, i, DRIVER.TYPE.AVERAGE, armature, full_key, 'v', '1.0-v')
          

    add_copy_transform_constraint(_98_rootmotion_final, 'Copy Transforms', _51_aggregate, None)
    add_child_of_constraint(_98_rootmotion_final, 'Child Of', _97_root_adjustment)
    add_limit_loc_constraint(_98_rootmotion_final, 'Limit Location')

    t = _98_rootmotion_final
    base = 'constraints["Limit Location"]'
    for axis in ['x', 'y', 'z']:
        for mm in ['min', 'max']:
            mm_axis = '{0}_{1}'.format(mm, axis)
            path_a = '{0}.use_{1}'.format(base, mm_axis)
            path_b = '{0}.{1}'.format(base, mm_axis)
            trgt_a = 'root_motion_{0}_limit_{1}'.format(axis, 'neg' if mm == 'min' else 'pos')
            trgt_b = trgt_a + '_val'

            add_driver(t, path_a, -1, DRIVER.TYPE.AVERAGE, obj, trgt_a, 'v', '')
            add_driver(t, path_b, -1, DRIVER.TYPE.AVERAGE, obj, trgt_b, 'v', '')
    
    
    add_copy_transform_constraint(_01_pose, 'Copy Transforms', _01_current, None, mix_mode=MIX_MODE.AFTER)
    
    add_copy_transform_constraint(_99_hips_final, 'Copy Transforms', _01_pose, None)
    add_child_of_constraint(_99_hips_final, 'Child Of', _02_hip_adjustment)

    add_copy_transform_constraint(Hips, 'Copy Transforms', _99_hips_final, None)

    add_copy_transform_constraint(RootMotion, 'Copy Transforms', _98_rootmotion_final, None)
    add_copy_location_constraint(RootMotion, 'Copy Location', _03_offset, use_offset=True)
    add_copy_rotation_constraint(RootMotion, 'Copy Rotation', _03_offset, mix_mode=MIX_MODE.AFTER, invert_z=True)

    if settings.original_root_bone == settings.root_bone_name:
        print("Bone name collision! [{0}]".format(settings.root_bone_name))
        settings.root_bone_name = '{0}_NEW'.format(settings.root_bone_name)

    if settings.original_root_bone == settings.hip_bone_name:
        print("Bone name collision! [{0}]".format(settings.hip_bone_name))
        settings.hip_bone_name = '{0}_NEW'.format(settings.hip_bone_name)

    entered, active, mode = cspy.modes.enter_mode_if(cspy.modes.MODE_EDIT, armature)

    root_edit_bone = cspy.bones.create_or_get_bone(armature, settings.root_bone_name)
    hip_edit_bone = cspy.bones.create_or_get_bone(armature, settings.hip_bone_name)
    original_root_bone = cspy.bones.create_or_get_bone(armature, settings.original_root_bone)
    
    try:
        hip_edit_bone.parent = root_edit_bone
    except AttributeError:
        pass
    
    cspy.bones.set_local_head_tail(armature, settings.root_bone_name, Vector([0,0,0]), Vector([0,0.5,0]), 0)
    cspy.bones.copy_local_head_tail(armature, settings.hip_bone_name,  settings.original_root_bone)
    
    for child in original_root_bone.children:
        cspy.bones.set_bone_parenting(armature, child.name, settings.hip_bone_name, False)

    cspy.modes.exit_mode_if(entered, active, mode)

    entered, active, mode = cspy.modes.enter_mode_if(cspy.modes.MODE_POSE, armature)

    root_bone = armature.pose.bones[settings.root_bone_name]
    c = root_bone.constraints.get('Copy Transforms')
    if not c:
        c = root_bone.constraints.new('COPY_TRANSFORMS')
    c.name = 'Copy Transforms'
    c.target = RootMotion

    hip_bone = armature.pose.bones[settings.hip_bone_name]

    c = hip_bone.constraints.get('Copy Transforms')
    if not c:
        c = hip_bone.constraints.new('COPY_TRANSFORMS')
    c.name = 'Copy Transforms'
    c.target = Hips

    cspy.modes.exit_mode_if(entered, active, mode)

    to_pose_position(armature)