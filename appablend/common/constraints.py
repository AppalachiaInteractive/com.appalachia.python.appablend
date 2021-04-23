from appablend.common.core.enums import constraints, icons

icons = {
    constraints.COPY_LOCATION: icons.CON_LOCLIKE,
    constraints.COPY_ROTATION: icons.CON_ROTLIKE,
    constraints.COPY_SCALE: icons.CON_SIZELIKE,
    constraints.LIMIT_DISTANCE: icons.CON_DISTLIMIT,
    constraints.LIMIT_LOCATION: icons.CON_LOCLIMIT,
    constraints.LIMIT_ROTATION: icons.CON_ROTLIMIT,
    constraints.LIMIT_SCALE: icons.CON_SIZELIMIT,
    constraints.TRANSFORM: icons.CON_TRANSFORM,
    constraints.DAMPED_TRACK: icons.CON_TRACKTO,
    constraints.IK: icons.CON_KINEMATIC,
    constraints.STRETCH_TO: icons.CON_STRETCHTO,
    constraints.CHILD_OF: icons.CON_CHILDOF,
    constraints.PIVOT: icons.CON_PIVOT,
    constraints.SHRINKWRAP: icons.CON_SHRINKWRAP,
}

ops = {
    constraints.COPY_LOCATION: "ops.ar_create_new_constraint_copy_location",
    constraints.COPY_ROTATION: "ops.ar_create_new_constraint_copy_rotation",
    constraints.COPY_SCALE: "ops.ar_create_new_constraint_copy_scale",
    constraints.LIMIT_DISTANCE: "ops.ar_create_new_constraint_limit_distance",
    constraints.LIMIT_LOCATION: "ops.ar_create_new_constraint_limit_location",
    constraints.LIMIT_ROTATION: "ops.ar_create_new_constraint_limit_rotation",
    constraints.LIMIT_SCALE: "ops.ar_create_new_constraint_limit_scale",
    constraints.TRANSFORM: "ops.ar_create_new_constraint_transform",
    constraints.DAMPED_TRACK: "ops.ar_create_new_constraint_damped_track",
    constraints.IK: "ops.ar_create_new_constraint_ik",
    constraints.STRETCH_TO: "ops.ar_create_new_constraint_stretch_to",
    constraints.CHILD_OF: "ops.ar_create_new_constraint_child_of",
    constraints.PIVOT: "ops.ar_create_new_constraint_pivot",
    constraints.SHRINKWRAP: "ops.ar_create_new_constraint_shrinkwrap",
}
