import bpy
from appablend.common import bones
from appablend.common.armature import to_pose_position, to_rest_position
from appablend.common.bones import get_pose_bone_rest_matrix_world
from appablend.common.core import modes
from appablend.common.utils import hierarchy
from mathutils import Matrix, Vector


class EMPTY:
    @classmethod
    def create(cls, name):
        o = bpy.data.objects.new(name, None)
        return o

    class DISPLAY_TYPE:
        PLAIN_AXES = "PLAIN_AXES"
        ARROWS = "ARROWS"
        SINGLE_ARROW = "SINGLE_ARROW"
        CIRCLE = "CIRCLE"
        CUBE = "CUBE"
        SPHERE = "SPHERE"
        CONE = "CONE"


class SPACE:
    WORLD = "WORLD"
    LOCAL = "LOCAL"


class MIX_MODE:
    OFFSET = "OFFSET"
    BEFORE = "BEFORE"
    ADD = "ADD"
    REPLACE = "REPLACE"
    AFTER = "AFTER"


class DRIVER:
    class TYPE:
        AVERAGE = "AVERAGE"
        SCRIPTED = "SCRIPTED"


def get_or_create_collection(context, name, parent):
    c = bpy.data.collections.get(name)
    if not c:
        c = bpy.data.collections.new(name)

    if parent and c.name not in parent.children:
        parent.children.link(c)

    return c


def get_or_create_empty(context, name, parent, collection, draw_size, draw_type):
    o = bpy.data.objects.get(name)
    if not o:
        o = EMPTY.create(name)

    o.empty_display_size = draw_size
    o.empty_display_type = draw_type

    if parent:
        parent.children.link(o)
    if collection and not o.name in collection.objects:
        collection.objects.link(o)
    else:
        context.scene.collection.objects.link(o)

    return o


def get_or_create_constraint(obj, name, t):
    if name in obj.constraints:
        con = obj.constraints[name]
    else:
        con = obj.constraints.new(t)

    return con


def add_copy_location_constraint(
    obj,
    name,
    target,
    use_offset=False,
    target_space=SPACE.WORLD,
    owner_space=SPACE.WORLD,
    use_x=True,
    use_y=True,
    use_z=True,
    invert_x=False,
    invert_y=False,
    invert_z=False,
):
    t = "COPY_LOCATION"
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


def add_copy_rotation_constraint(
    obj,
    name,
    target,
    mix_mode=MIX_MODE.REPLACE,
    target_space=SPACE.WORLD,
    owner_space=SPACE.WORLD,
    use_x=True,
    use_y=True,
    use_z=True,
    invert_x=False,
    invert_y=False,
    invert_z=False,
):
    t = "COPY_ROTATION"
    con = get_or_create_constraint(obj, name, t)
    con.name = name
    con.target = target
    con.mix_mode = mix_mode
    con.target_space = target_space
    con.owner_space = owner_space
    con.use_x = use_x
    con.use_y = use_y
    con.use_z = use_z
    con.euler_order = "YXZ"
    con.invert_x = invert_x
    con.invert_y = invert_y
    con.invert_z = invert_z
    return con


def add_copy_transform_constraint(
    obj, name, target, subtarget, mix_mode=MIX_MODE.REPLACE
):
    t = "COPY_TRANSFORMS"
    con = get_or_create_constraint(obj, name, t)
    con.name = name
    con.target = target
    con.subtarget = "" if subtarget is None else subtarget
    con.mix_mode = mix_mode
    return con


def add_child_of_constraint(obj, name, target):
    t = "CHILD_OF"
    con = get_or_create_constraint(obj, name, t)
    con.name = name
    con.target = target
    con.inverse_matrix = con.target.matrix_world.inverted()
    return con


def refresh_child_of_matrices(armature):
    collection = "Root Motion"

    all_objects = reversed(hierarchy.get_collection_hierarchy(collection))

    for obj in all_objects:
        for constraint in obj.constraints:
            if constraint.type == "CHILD_OF":
                constraint.inverse_matrix = constraint.target.matrix_world.inverted()


def add_limit_loc_constraint(obj, name):
    t = "LIMIT_LOCATION"
    con = get_or_create_constraint(obj, name, t)
    con.name = name
    return con


def add_driver(
    obj,
    data_path,
    array_index,
    driver_type,
    target,
    target_data_path,
    target_v_name,
    expression,
):
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
        v = drv.variables.new()

    v.name = target_v_name
    v.targets[0].id = target
    v.targets[0].data_path = target_data_path

    drv.expression = expression
    return d


def create_root_motion_setup(context, armature):
    scene = context.scene
    sc = scene.collection

    orig_entered, orig_active, orig_mode = modes.enter_mode_if(
        modes.MODE_OBJECT, armature
    )

    to_rest_position(armature)
    settings = armature.data.root_motion_settings

    rmc = get_or_create_collection(context, "Root Motion", sc)
    rm_ac = get_or_create_collection(context, "1_Root Adjustment", rmc)
    rm_sc = get_or_create_collection(context, "2_Settings", rmc)
    rm_rc = get_or_create_collection(context, "3_Root", rmc)
    rm_pc = get_or_create_collection(context, "4_Pelvis", rmc)

    dt = EMPTY.DISPLAY_TYPE
    new = get_or_create_empty
    c = context
    _00_basis = new(c, "_00_basis", None, rm_ac, 0.10, dt.PLAIN_AXES)
    _01_current = new(c, "_01_current", None, rm_ac, 0.11, dt.PLAIN_AXES)
    _02_tracking = new(c, "_02_tracking", None, rm_ac, 0.13, dt.ARROWS)
    _03_offset = new(c, "_03_offset", None, rm_ac, 0.15, dt.ARROWS)
    _05_common_adjustment = new(
        c, "_05_common_adjustment", None, rm_ac, 0.18, dt.ARROWS
    )
    _10_start = new(c, "_10_start", None, rm_ac, 0.21, dt.ARROWS)
    _21_baked_rot = new(c, "_21_baked_rot", None, rm_sc, 0.25, dt.ARROWS)
    _22_baked_loc = new(c, "_22_baked_loc", None, rm_sc, 0.29, dt.ARROWS)
    _28_aggregate_loc = new(c, "_28_aggregate_loc", None, rm_sc, 0.34, dt.ARROWS)
    _29_aggregate = new(c, "_29_aggregate", None, rm_sc, 0.39, dt.ARROWS)
    _80_root_adjustment_rot = new(
        c, "_80_root_adjustment_rot", None, rm_rc, 0.45, dt.ARROWS
    )
    _81_root_adjustment_loc = new(
        c, "_81_root_adjustment_loc", None, rm_rc, 0.51, dt.ARROWS
    )
    _89_rootmotion_final = new(c, "_89_rootmotion_final", None, rm_rc, 0.57, dt.ARROWS)
    _01_pose = new(c, "_01_pose", None, rm_pc, 0.20, dt.SPHERE)
    _82_hip_adjustment_rot = new(
        c, "_82_hip_adjustment_rot", None, rm_pc, 0.40, dt.SPHERE
    )
    _83_hip_adjustment_loc = new(
        c, "_83_hip_adjustment_loc", None, rm_pc, 0.45, dt.SPHERE
    )
    _99_hips_final = new(c, "_99_hips_final", None, rm_pc, 0.10, dt.SPHERE)
    Hips = new(c, "Hips", None, rmc, 0.25, dt.CUBE)
    RootMotion = new(c, "RootMotion", None, rmc, 1.00, dt.ARROWS)

    if settings.root_bone_name == "":
        settings.root_bone_name = "Root"
    if settings.hip_bone_name == "":
        settings.hip_bone_name = "Hips"

    settings.root_node = _02_tracking
    settings.root_bone_offset = _89_rootmotion_final
    settings.hip_bone_offset = _99_hips_final
    settings.root_final = RootMotion

    objs = [
        _00_basis,
        _01_current,
        _02_tracking,
        _03_offset,
        _05_common_adjustment,
        _10_start,
        _22_baked_loc,
        _21_baked_rot,
        _28_aggregate_loc,
        _29_aggregate,
        _80_root_adjustment_rot,
        _81_root_adjustment_loc,
        _89_rootmotion_final,
        _01_pose,
        _82_hip_adjustment_rot,
        _83_hip_adjustment_loc,
        _99_hips_final,
        Hips,
        RootMotion,
    ]

    for obj in objs:
        obj.matrix_world = Matrix.Identity(4)

    _00_basis.matrix_world = get_pose_bone_rest_matrix_world(
        armature, settings.original_root_bone
    )

    add_copy_transform_constraint(
        _01_current, "Copy Transforms", armature, settings.original_root_bone
    )
    add_copy_transform_constraint(_02_tracking, "Copy Transforms", _00_basis, None)
    add_child_of_constraint(_02_tracking, "Child Of", _01_current)

    add_driver(
        _03_offset,
        "location",
        0,
        DRIVER.TYPE.SCRIPTED,
        armature,
        "root_motion_x_offset",
        "offset",
        "-offset",
    )
    add_driver(
        _03_offset,
        "location",
        1,
        DRIVER.TYPE.SCRIPTED,
        armature,
        "root_motion_y_offset",
        "offset",
        "-offset",
    )
    add_driver(
        _03_offset,
        "location",
        2,
        DRIVER.TYPE.SCRIPTED,
        armature,
        "root_motion_z_offset",
        "offset",
        "-offset",
    )

    add_driver(
        _03_offset,
        "rotation_euler",
        2,
        DRIVER.TYPE.SCRIPTED,
        armature,
        "root_motion_rot_offset",
        "offset",
        "offset * 0.0174533",
    )

    add_driver(
        _05_common_adjustment,
        "location",
        0,
        DRIVER.TYPE.AVERAGE,
        armature,
        "root_node_start_location_0",
        "v",
        "",
    )
    add_driver(
        _05_common_adjustment,
        "location",
        1,
        DRIVER.TYPE.AVERAGE,
        armature,
        "root_node_start_location_1",
        "v",
        "",
    )
    add_driver(
        _05_common_adjustment,
        "location",
        2,
        DRIVER.TYPE.AVERAGE,
        armature,
        "root_node_start_location_2",
        "v",
        "",
    )
    add_driver(
        _05_common_adjustment,
        "rotation_euler",
        0,
        DRIVER.TYPE.AVERAGE,
        armature,
        "root_node_start_rotation_0",
        "v",
        "",
    )
    add_driver(
        _05_common_adjustment,
        "rotation_euler",
        1,
        DRIVER.TYPE.AVERAGE,
        armature,
        "root_node_start_rotation_1",
        "v",
        "",
    )
    add_driver(
        _05_common_adjustment,
        "rotation_euler",
        2,
        DRIVER.TYPE.AVERAGE,
        armature,
        "root_node_start_rotation_2",
        "v",
        "",
    )

    add_copy_transform_constraint(_10_start, "Copy Transforms", _02_tracking, None)
    add_copy_location_constraint(
        _10_start, "Copy Location", _05_common_adjustment, use_offset=True
    )
    add_copy_rotation_constraint(
        _10_start, "Copy Rotation", _05_common_adjustment, mix_mode=MIX_MODE.AFTER
    )

    add_copy_location_constraint(
        _22_baked_loc,
        "_rm_x_bake_into",
        _10_start,
        use_offset=False,
        use_x=True,
        use_y=False,
        use_z=False,
    )
    add_copy_location_constraint(
        _22_baked_loc,
        "_rm_y_bake_into",
        _10_start,
        use_offset=False,
        use_x=False,
        use_y=True,
        use_z=False,
    )
    add_copy_location_constraint(
        _22_baked_loc,
        "_rm_z_bake_into",
        _10_start,
        use_offset=False,
        use_x=False,
        use_y=False,
        use_z=True,
    )

    add_driver(
        _22_baked_loc,
        'constraints["_rm_x_bake_into"].influence',
        -1,
        DRIVER.TYPE.SCRIPTED,
        armature,
        "root_motion_x_bake_into",
        "v",
        "1.0-v",
    )
    add_driver(
        _22_baked_loc,
        'constraints["_rm_y_bake_into"].influence',
        -1,
        DRIVER.TYPE.SCRIPTED,
        armature,
        "root_motion_y_bake_into",
        "v",
        "1.0-v",
    )
    add_driver(
        _22_baked_loc,
        'constraints["_rm_z_bake_into"].influence',
        -1,
        DRIVER.TYPE.SCRIPTED,
        armature,
        "root_motion_z_bake_into",
        "v",
        "1.0-v",
    )

    add_copy_rotation_constraint(
        _21_baked_rot, "_05_rot_bake_into", _10_start, use_x=False, use_y=False
    )
    add_driver(
        _21_baked_rot,
        'constraints["_05_rot_bake_into"].influence',
        -1,
        DRIVER.TYPE.SCRIPTED,
        armature,
        "root_motion_rot_bake_into",
        "v",
        "1.0-v",
    )

    add_child_of_constraint(_28_aggregate_loc, "Child Of", _21_baked_rot)
    add_copy_location_constraint(
        _28_aggregate_loc, _22_baked_loc.name, _22_baked_loc, use_offset=False
    )

    add_copy_transform_constraint(
        _29_aggregate, "Copy Transforms", _28_aggregate_loc, None
    )

    offset_params = [
        (_80_root_adjustment_rot, "root", "rotation_euler", "rotation", None),
        (
            _81_root_adjustment_loc,
            "root",
            "location",
            "location",
            _80_root_adjustment_rot,
        ),
        (_82_hip_adjustment_rot, "hip", "rotation_euler", "rotation", None),
        (_83_hip_adjustment_loc, "hip", "location", "location", _82_hip_adjustment_rot),
    ]

    for offset_param in offset_params:
        target = offset_param[0]
        bone_name = offset_param[1]
        data_path = offset_param[2]
        var_token = offset_param[3]
        childof = offset_param[4]

        for i in range(3):
            full_key = "{0}_bone_offset_{1}_{2}".format(bone_name, var_token, i)
            add_driver(
                target,
                data_path,
                i,
                DRIVER.TYPE.AVERAGE,
                armature,
                full_key,
                "v",
                "1.0-v",
            )

        if childof:
            add_child_of_constraint(target, "Child Of", childof)

    add_copy_transform_constraint(
        _89_rootmotion_final, "Copy Transforms", _29_aggregate, None
    )
    add_child_of_constraint(_89_rootmotion_final, "Child Of", _81_root_adjustment_loc)
    add_limit_loc_constraint(_89_rootmotion_final, "Limit Location")

    t = _89_rootmotion_final
    base = 'constraints["Limit Location"]'
    for axis in ["x", "y", "z"]:
        for mm in ["min", "max"]:
            mm_axis = "{0}_{1}".format(mm, axis)
            path_a = "{0}.use_{1}".format(base, mm_axis)
            path_b = "{0}.{1}".format(base, mm_axis)
            trgt_a = "root_motion_{0}_limit_{1}".format(
                axis, "neg" if mm == "min" else "pos"
            )
            trgt_b = trgt_a + "_val"

            add_driver(t, path_a, -1, DRIVER.TYPE.AVERAGE, armature, trgt_a, "v", "")
            add_driver(t, path_b, -1, DRIVER.TYPE.AVERAGE, armature, trgt_b, "v", "")

    add_copy_transform_constraint(
        _01_pose, "Copy Transforms", _01_current, None, mix_mode=MIX_MODE.AFTER
    )

    add_copy_transform_constraint(_99_hips_final, "Copy Transforms", _01_pose, None)
    add_child_of_constraint(_99_hips_final, "Child Of", _83_hip_adjustment_loc)

    add_copy_transform_constraint(Hips, "Copy Transforms", _99_hips_final, None)

    add_copy_transform_constraint(
        RootMotion, "Copy Transforms", _89_rootmotion_final, None
    )
    add_copy_location_constraint(
        RootMotion, "Copy Location", _03_offset, use_offset=True
    )
    add_copy_rotation_constraint(
        RootMotion, "Copy Rotation", _03_offset, mix_mode=MIX_MODE.AFTER, invert_z=True
    )

    if settings.original_root_bone == settings.root_bone_name:
        print("Bone name collision! [{0}]".format(settings.root_bone_name))
        settings.root_bone_name = "{0}_NEW".format(settings.root_bone_name)

    if settings.original_root_bone == settings.hip_bone_name:
        print("Bone name collision! [{0}]".format(settings.hip_bone_name))
        settings.hip_bone_name = "{0}_NEW".format(settings.hip_bone_name)

    entered, active, mode = modes.enter_mode_if(modes.MODE_EDIT, armature)

    root_edit_bone = bones.create_or_get_bone(armature, settings.root_bone_name)
    hip_edit_bone = bones.create_or_get_bone(armature, settings.hip_bone_name)
    original_root_bone = bones.create_or_get_bone(armature, settings.original_root_bone)

    try:
        hip_edit_bone.parent = root_edit_bone
    except AttributeError:
        pass

    bones.set_local_head_tail(
        armature, settings.root_bone_name, Vector([0, 0, 0]), Vector([0, 0.5, 0]), 0
    )
    bones.copy_local_head_tail(
        armature, settings.hip_bone_name, settings.original_root_bone
    )

    for child in original_root_bone.children:
        bones.set_bone_parenting(armature, child.name, settings.hip_bone_name, False)

    modes.exit_mode_if(entered, active, mode)

    entered, active, mode = modes.enter_mode_if(modes.MODE_POSE, armature)

    root_bone = armature.pose.bones[settings.root_bone_name]
    c = root_bone.constraints.get("Copy Transforms")
    if not c:
        c = root_bone.constraints.new("COPY_TRANSFORMS")
    c.name = "Copy Transforms"
    c.target = RootMotion

    hip_bone = armature.pose.bones[settings.hip_bone_name]

    c = hip_bone.constraints.get("Copy Transforms")
    if not c:
        c = hip_bone.constraints.new("COPY_TRANSFORMS")
    c.name = "Copy Transforms"
    c.target = Hips

    modes.exit_mode_if(entered, active, mode)

    to_pose_position(armature)

    for mesh in [obj for obj in bpy.data.objects if obj.type == "MESH"]:
        for vg in mesh.vertex_groups:
            if vg.name == settings.original_root_bone:
                vg.name = settings.hip_bone_name

    to_rest_position(armature)
    refresh_child_of_matrices(armature)
    refresh_child_of_matrices(armature)
    refresh_child_of_matrices(armature)
    to_pose_position(armature)

    rm_ac.hide_viewport = True
    rm_sc.hide_viewport = True
    rm_rc.hide_viewport = True
    rm_pc.hide_viewport = True
