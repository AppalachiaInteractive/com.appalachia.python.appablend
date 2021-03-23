import bpy, cspy
from bpy.types import Operator
from cspy.ops import OPS_, OPS_DIALOG
from cspy.polling import POLL
from cspy.ui import PT_OPTIONS, PT_, UI
from cspy.animation_retargeting import *

class AR_OPS_:
    @classmethod
    def get_cache_data(cls, context):
        obj = context.active_object
        anim_ret = obj.anim_ret
        anim_ret_bone_cache = obj.anim_ret_bone_cache
        anim_ret_constraints_cache = obj.anim_ret_constraints_cache
        return obj, anim_ret, anim_ret_bone_cache, anim_ret_constraints_cache

    @classmethod
    def poll_update(cls, context):
        if context.active_object.anim_ret.is_frozen:
            return False
        obj, ar, arbc, arcc = cls.get_cache_data(context)
        return obj and ar and arbc and arcc and (len(arbc) > 0 or len(arcc) > 0)

    @classmethod
    def poll_debug(cls, context):
        if context.active_object.anim_ret.is_frozen:
            return False
        obj, ar, arbc, arcc = cls.get_cache_data(context)
        return obj and ar and ((arbc and len(arbc) > 0) or (arcc and len(arcc) > 0))

    @classmethod
    def poll_clear(cls, context):
        if context.active_object.anim_ret.is_frozen:
            return False
        obj, ar, arbc, arcc = cls.get_cache_data(context)
        return obj and ar and ((arbc and len(arbc) > 0) or (arcc and len(arcc) > 0))

    @classmethod
    def poll_restore(cls, context):
        if context.active_object.anim_ret.is_frozen:
            return False
        obj, ar, arbc, arcc = cls.get_cache_data(context)
        return obj and ar and arbc and arcc and (len(arbc) > 0 or len(arcc) > 0)

    @classmethod
    def debug_cache(cls, context):
        obj, ar, arbc, arcc = cls.get_cache_data(context)
        for bone in arbc:
            print('{0} >> {1}'.format(bone.bone_name, bone.source_bone_name))
        for constraint in arcc:
            print('{0} >> {1}'.format(constraint.bone_name, constraint.constraint_type))

    @classmethod
    def clear_cache(cls, context):
        obj, ar, arbc, arcc = cls.get_cache_data(context)
        arbc.clear()
        arcc.clear()

    @classmethod
    def cache_bone(cls, context, bone_name):
        obj, ar, arbc, arcc = cls.get_cache_data(context)
        pbone = obj.pose.bones[bone_name]
        anim_ret_bone = pbone.anim_ret_bone

        if anim_ret_bone.source_bone_name == '':
            return

        anim_ret_bone.target_bone_name = bone_name
        new_bone = arbc.add()
        new_bone.cache_from(anim_ret_bone)

        for anim_ret_constraint in pbone.anim_ret_constraints:
            anim_ret_constraint.target_bone_name = bone_name
            new_constraint = arcc.add()
            new_constraint.cache_from(anim_ret_constraint)

    @classmethod
    def refresh_cache(cls, context):
        cls.clear_cache(context)

        obj, ar, arbc, arcc = cls.get_cache_data(context)

        for bone in obj.data.bones:
            cls.cache_bone(context, bone.name)

    @classmethod
    def restore_bone(cls, context, cached_bone):
        obj, ar, arbc, arcc = cls.get_cache_data(context)
        pbone = obj.pose.bones[cached_bone.bone_name]

        anim_ret_bone = pbone.anim_ret_bone
        anim_ret_bone.restore_from(cached_bone)

    @classmethod
    def restore_constraint(cls, context, cached_constraint):
        obj, ar, arbc, arcc = cls.get_cache_data(context)
        pbone = obj.pose.bones[cached_constraint.bone_name]

        new_constraint = pbone.anim_ret_constraints.add()
        new_constraint.restore_from(cached_constraint)

    @classmethod
    def get_cache_status(cls, context):
        obj, ar, arbc, arcc = cls.get_cache_data(context)
        bone_count = len(arbc)
        constraint_count = len(arcc)
        return 'Cache contains {0} bones and {1} constraints.'.format(bone_count, constraint_count)

    @classmethod
    def refresh_constraints(cls, context):
        frame = bpy.context.scene.frame_current
        bpy.context.scene.frame_set(0)

        bone = get_active_pose_bone(context)
        if bone is None:
            bone = context.active_object.pose.bones[context.active_bone.name]

        anim_ret_bone = bone.anim_ret_bone
        anim_ret_bone.bone_name = bone.name

        context.active_object.anim_ret.active_mirror_bone=False
        context.active_object.anim_ret.active_mirror_constraint=False
        anim_ret_bone.check_bone(context)

        bpy.context.scene.frame_set(frame)

    @classmethod
    def synchronize_bones(cls, context):
        frame = bpy.context.scene.frame_current
        bpy.context.scene.frame_set(0)

        obj = context.active_object
        anim_ret = obj.anim_ret
        source_armature = anim_ret.source

        bones = obj.data.bones
        bone_names = []
        for bone in bones:
            bone_names.append(bone.name)

        for bone_name in bone_names:
            pbone = obj.pose.bones[bone_name]
            anim_ret_bone = pbone.anim_ret_bone
            anim_ret_bone.bone_name = bone_name

            use_offset_bone = False
            for constraint in pbone.anim_ret_constraints:
                use_offset_bone = use_offset_bone or constraint.use_offset_bone
                constraint.bone_name = bone_name

            source_armature = anim_ret.source
            ObjectAnimRet.update_offset_bones(obj, bone_name, source_armature, anim_ret_bone.source_bone_name, use_offset_bone)

        bpy.context.scene.frame_set(frame)

    @classmethod
    def refresh_bones(cls, context):
        frame = bpy.context.scene.frame_current
        bpy.context.scene.frame_set(0)

        obj = context.active_object
        anim_ret = obj.anim_ret
        source_armature = anim_ret.source

        bones = obj.data.bones
        bone_names = []
        for bone in bones:
            bone_names.append(bone.name)

        for bone_name in bone_names:
            bone = obj.data.bones[bone_name]
            pbone = obj.pose.bones[bone_name]
            anim_ret_bone = pbone.anim_ret_bone
            anim_ret_bone.bone_name = pbone.name

            anim_ret.active_mirror_bone=False
            anim_ret.active_mirror_constraint=False
            anim_ret_bone.check_bone(context)

        bpy.context.scene.frame_set(frame)

class AR_OPS_Create_New_Constraint(AR_OPS_):

    @classmethod
    def do_poll(cls, context):
        return POLL.ANIM_RET_IS_NOT_FROZEN(context)

    def do_execute(self, context):
        obj = context.active_object
        if not obj:
            return {'FINISHED'}
        anim_ret = obj.anim_ret
        if anim_ret and anim_ret.is_frozen:
            return {'FINISHED'}

        bone = get_active_pose_bone(context)
        if bone is None:
            bone_name = anim_ret.get_active_bone_name(context)
            bone = obj.pose.bones[bone_name]
        if bone is None:
            return {'FINISHED'}

        anim_ret_bone = bone.anim_ret_bone
        anim_ret_constraints = bone.anim_ret_constraints

        new_anim_ret_constraint = anim_ret_constraints.add()
        new_anim_ret_constraint.initialize(context, self.constraint_type, bone)

        self.initialize(context, new_anim_ret_constraint)

        self.report({'INFO'}, '{0} constraint added to bone {1}.'.format(self.constraint_type, bone.name))

        return {'FINISHED'}

    def initialize(self, context, new_anim_ret_constraint):
        pass

class AR_Create_New_Constraint_COPY_LOCATION(AR_OPS_Create_New_Constraint, Operator):
    bl_idname = "ops.ar_create_new_constraint_copy_location"
    bl_label = "Create a new Copy Location bone constraint"
    constraint_type = Constants.COPY_LOCATION

class AR_Create_New_Constraint_COPY_ROTATION(AR_OPS_Create_New_Constraint, Operator):
    bl_idname = "ops.ar_create_new_constraint_copy_rotation"
    bl_label = "Create a new COPY_ROTATION bone constraint"
    constraint_type = Constants.COPY_ROTATION

class AR_Create_New_Constraint_COPY_SCALE(AR_OPS_Create_New_Constraint, Operator):
    bl_idname = "ops.ar_create_new_constraint_copy_scale"
    bl_label = "Create a new COPY_SCALE bone constraint"
    constraint_type = Constants.COPY_SCALE

class AR_Create_New_Constraint_LIMIT_DISTANCE(AR_OPS_Create_New_Constraint, Operator):
    bl_idname = "ops.ar_create_new_constraint_limit_distance"
    bl_label = "Create a new LIMIT_DISTANCE bone constraint"
    constraint_type = Constants.LIMIT_DISTANCE

class AR_Create_New_Constraint_LIMIT_LOCATION(AR_OPS_Create_New_Constraint, Operator):
    bl_idname = "ops.ar_create_new_constraint_limit_location"
    bl_label = "Create a new LIMIT_LOCATION bone constraint"
    constraint_type = Constants.LIMIT_LOCATION

class AR_Create_New_Constraint_LIMIT_ROTATION(AR_OPS_Create_New_Constraint, Operator):
    bl_idname = "ops.ar_create_new_constraint_limit_rotation"
    bl_label = "Create a new LIMIT_ROTATION bone constraint"
    constraint_type = Constants.LIMIT_ROTATION

class AR_Create_New_Constraint_LIMIT_SCALE(AR_OPS_Create_New_Constraint, Operator):
    bl_idname = "ops.ar_create_new_constraint_limit_scale"
    bl_label = "Create a new LIMIT_SCALE bone constraint"
    constraint_type = Constants.LIMIT_SCALE

class AR_Create_New_Constraint_TRANSFORM(AR_OPS_Create_New_Constraint, Operator):
    bl_idname = "ops.ar_create_new_constraint_transform"
    bl_label = "Create a new TRANSFORM bone constraint"
    constraint_type = Constants.TRANSFORM

    def initialize(self, context, new_anim_ret_constraint):
        constraint = get_active_pose_bone(context).constraints[new_anim_ret_constraint.name]
        constraint.target_space = 'WORLD'
        constraint.owner_space = 'WORLD'
        constraint.use_motion_extrapolate = True
        constraint.from_max_x = math.radians(1.0)
        constraint.from_max_x_rot = math.radians(1.0)
        constraint.from_max_x_scale = math.radians(1.0)
        constraint.from_max_y = math.radians(1.0)
        constraint.from_max_y_rot = math.radians(1.0)
        constraint.from_max_y_scale = math.radians(1.0)
        constraint.from_max_z = math.radians(1.0)
        constraint.from_max_z_rot = math.radians(1.0)
        constraint.from_max_z_scale = math.radians(1.0)
        constraint.from_min_x = 0
        constraint.from_min_x_rot = 0
        constraint.from_min_x_scale = 0
        constraint.from_min_y = 0
        constraint.from_min_y_rot = 0
        constraint.from_min_y_scale = 0
        constraint.from_min_z = 0
        constraint.from_min_z_rot = 0
        constraint.from_min_z_scale = 0
        constraint.to_max_x = math.radians(1.0)
        constraint.to_max_x_rot = math.radians(1.0)
        constraint.to_max_x_scale = math.radians(1.0)
        constraint.to_max_y = math.radians(1.0)
        constraint.to_max_y_rot = math.radians(1.0)
        constraint.to_max_y_scale = math.radians(1.0)
        constraint.to_max_z = math.radians(1.0)
        constraint.to_max_z_rot = math.radians(1.0)
        constraint.to_max_z_scale = math.radians(1.0)
        constraint.to_min_x = 0
        constraint.to_min_x_rot = 0
        constraint.to_min_x_scale = 0
        constraint.to_min_y = 0
        constraint.to_min_y_rot = 0
        constraint.to_min_y_scale = 0
        constraint.to_min_z = 0
        constraint.to_min_z_rot = 0
        constraint.to_min_z_scale = 0
        constraint.map_from = 'ROTATION'
        constraint.map_to = 'ROTATION'
        constraint.mix_mode_rot = 'REPLACE'

class AR_Create_New_Constraint_DAMPED_TRACK(AR_OPS_Create_New_Constraint, Operator):
    bl_idname = "ops.ar_create_new_constraint_damped_track"
    bl_label = "Create a new DAMPED_TRACK bone constraint"
    constraint_type = Constants.DAMPED_TRACK

class AR_Create_New_Constraint_IK(AR_OPS_Create_New_Constraint, Operator):
    bl_idname = "ops.ar_create_new_constraint_ik"
    bl_label = "Create a new IK bone constraint"
    constraint_type = Constants.IK

class AR_Create_New_Constraint_STRETCH_TO(AR_OPS_Create_New_Constraint, Operator):
    bl_idname = "ops.ar_create_new_constraint_stretch_to"
    bl_label = "Create a new STRETCH_TO bone constraint"
    constraint_type = Constants.STRETCH_TO

class AR_Create_New_Constraint_CHILD_OF(AR_OPS_Create_New_Constraint, Operator):
    bl_idname = "ops.ar_create_new_constraint_child_of"
    bl_label = "Create a new CHILD_OF bone constraint"
    constraint_type = Constants.CHILD_OF

class AR_Create_New_Constraint_PIVOT(AR_OPS_Create_New_Constraint, Operator):
    bl_idname = "ops.ar_create_new_constraint_pivot"
    bl_label = "Create a new PIVOT bone constraint"
    constraint_type = Constants.PIVOT

class AR_Create_New_Constraint_SHRINKWRAP(AR_OPS_Create_New_Constraint, Operator):
    bl_idname = "ops.ar_create_new_constraint_shrinkwrap"
    bl_label = "Create a new SHRINKWRAP bone constraint"
    constraint_type = Constants.SHRINKWRAP

class AR_Refresh_Constraints(OPS_, AR_OPS_, Operator):
    bl_idname = 'ops.ar_refresh_constraints'
    bl_label = 'Refresh the bones constraints'

    @classmethod
    def do_poll(cls, context):
        if context.active_object.anim_ret.is_frozen:
            return False
        return True

    def do_execute(self, context):
        cls = AR_OPS_
        cls.refresh_constraints(context)
        self.report({'INFO'}, '[{0}] constraints refreshed.'.format(get_active_pose_bone(context).name))
        return {'FINISHED'}

class AR_Synchronize_Bones(OPS_, AR_OPS_, Operator):
    bl_idname = 'ops.ar_synchronize_bones'
    bl_label = 'Synchronize the bones constraint names.'

    @classmethod
    def do_poll(cls, context):
        if context.active_object.anim_ret.is_frozen:
            return False
        return context.active_object is not None and context.active_object.type == 'ARMATURE'

    def do_execute(self, context):
        cls = AR_OPS_
        cls.synchronize_bones(context)
        self.report({'INFO'}, 'Bones synchronized.')
        return {'FINISHED'}

class AR_Refresh_Bones(OPS_, AR_OPS_, Operator):
    bl_idname = 'ops.ar_refresh_bones'
    bl_label = 'Refresh all bone data.'

    @classmethod
    def do_poll(cls, context):
        if context.active_object.anim_ret.is_frozen:
            return False
        return context.active_object is not None and context.active_object.type == 'ARMATURE'

    def do_execute(self, context):
        cls = AR_OPS_
        cls.refresh_bones(context)
        self.report({'INFO'}, 'Bones refreshed.')
        return {'FINISHED'}

class AR_Update_Cache(OPS_, AR_OPS_, Operator):
    """Updates the cache with the current bone and constraint data."""
    bl_idname = 'ops.ar_update_cache'
    bl_label = 'Update'

    @classmethod
    def do_poll(cls, context):
        return cls.poll_update

    def do_execute(self, context):
        cls = AR_OPS_
        cls.refresh_cache(context)
        self.report({'INFO'}, cls.get_cache_status(context))
        return {'FINISHED'}

class AR_Clear_Cache(OPS_, AR_OPS_, Operator):
    """Clears the cache back to its original state."""
    bl_idname = 'ops.ar_clear_cache'
    bl_label = 'Clear'

    @classmethod
    def do_poll(cls, context):
        return cls.poll_clear

    def do_execute(self, context):
        cls = AR_OPS_
        cls.clear_cache(context)
        self.report({'INFO'}, cls.get_cache_status(context))
        return {'FINISHED'}

class AR_Debug_Cache(OPS_, AR_OPS_, Operator):
    """Shows debug data for a cache."""
    bl_idname = 'ops.ar_debug_cache'
    bl_label = 'Debug'

    @classmethod
    def do_poll(cls, context):
        return cls.poll_debug

    def do_execute(self, context):
        cls = AR_OPS_
        cls.debug_cache(context)

        self.report({'INFO'}, cls.get_cache_status(context))
        return {'FINISHED'}

class AR_Restore_Cache(OPS_, AR_OPS_, Operator):
    """Restores the cache by applying its bones and constraints to this armature."""
    bl_idname = 'ops.ar_restore_cache'
    bl_label = 'Restore'

    @classmethod
    def do_poll(cls, context):
        return cls.poll_debug

    def do_execute(self, context):
        cls = AR_OPS_

        obj, ar, arbc, arcc = cls.get_cache_data(context)

        for bone in arbc:
            cls.restore_bone(context, bone)

        for constraint in arcc:
            cls.restore_constraint(context, constraint)

        cls.refresh_bones(context)
        self.report({'INFO'}, cls.get_cache_status(context))
        return {'FINISHED'}
