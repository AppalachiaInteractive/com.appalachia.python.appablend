import bpy
from bpy.props import (BoolProperty, EnumProperty, FloatProperty, FloatVectorProperty, IntProperty, StringProperty)
from mathutils import Matrix, Vector
from rna_prop_ui import PropertyPanel
import math
import cspy

def get_active_pose_bone(context):
    bone = context.active_pose_bone
    if bone:
        return bone

    obj = context.active_object
    if not obj:
        return None

    bone = context.active_bone

    if bone:
        return obj.pose.bones[bone.name]

    parentless_bones = [bone for bone in obj.data.bones if (not bone.parent or bone.parent == '')]

    if parentless_bones:
        return parentless_bones[0]

    return None

class Constants:
    ICON_ON = 'RADIOBUT_ON'
    ICON_OFF = 'RADIOBUT_OFF'
    ICON_HIDE_OFF = 'HIDE_OFF'
    ICON_HIDE_ON = 'HIDE_ON'
    ICON_USE_MIRROR = 'MOD_MIRROR'
    ICON_USE_OFFSET_BONE = 'SEQ_STRIP_DUPLICATE'
    ICON_REFRESH = 'FILE_REFRESH'

    ICON_FREEZE = 'FREEZE'
    ICON_SYNC = 'UV_SYNC_SELECT'
    ICON_COPY_LOCATION = 'CON_LOCLIKE'
    ICON_COPY_ROTATION  = 'CON_ROTLIKE'
    ICON_COPY_SCALE  = 'CON_SIZELIKE'
    ICON_LIMIT_DISTANCE  = 'CON_DISTLIMIT'
    ICON_LIMIT_LOCATION  = 'CON_LOCLIMIT'
    ICON_LIMIT_ROTATION  = 'CON_ROTLIMIT'
    ICON_LIMIT_SCALE  = 'CON_SIZELIMIT'
    ICON_TRANSFORM = 'CON_TRANSFORM'
    ICON_DAMPED_TRACK = 'CON_TRACKTO'
    ICON_IK = 'CON_KINEMATIC'
    ICON_STRETCH_TO = 'CON_STRETCHTO'
    ICON_CHILD_OF = 'CON_CHILDOF'
    ICON_PIVOT = 'CON_PIVOT'
    ICON_SHRINKWRAP = 'CON_SHRINKWRAP'


    COPY_LOCATION = 'COPY_LOCATION'
    COPY_ROTATION  = 'COPY_ROTATION'
    COPY_SCALE  = 'COPY_SCALE'
    LIMIT_DISTANCE  = 'LIMIT_DISTANCE'
    LIMIT_LOCATION  = 'LIMIT_LOCATION'
    LIMIT_ROTATION  = 'LIMIT_ROTATION'
    LIMIT_SCALE  = 'LIMIT_SCALE'
    TRANSFORM = 'TRANSFORM'
    DAMPED_TRACK = 'DAMPED_TRACK'
    IK = 'IK'
    STRETCH_TO = 'STRETCH_TO'
    CHILD_OF = 'CHILD_OF'
    PIVOT = 'PIVOT'
    SHRINKWRAP = 'SHRINKWRAP'

    CONSTRAINTS = [
        COPY_LOCATION,
        COPY_ROTATION,
        COPY_SCALE ,
        LIMIT_DISTANCE,
        LIMIT_LOCATION,
        LIMIT_ROTATION,
        LIMIT_SCALE ,
        TRANSFORM,
        DAMPED_TRACK,
        IK,
        STRETCH_TO,
        CHILD_OF,
        PIVOT,
        SHRINKWRAP,
    ]

    CONSTRAINT_ICONS = {
            COPY_LOCATION:ICON_COPY_LOCATION,
            COPY_ROTATION:ICON_COPY_ROTATION,
            COPY_SCALE :ICON_COPY_SCALE ,
            LIMIT_DISTANCE:ICON_LIMIT_DISTANCE,
            LIMIT_LOCATION:ICON_LIMIT_LOCATION,
            LIMIT_ROTATION:ICON_LIMIT_ROTATION,
            LIMIT_SCALE :ICON_LIMIT_SCALE ,
            TRANSFORM:ICON_TRANSFORM,
            DAMPED_TRACK:ICON_DAMPED_TRACK,
            IK:ICON_IK,
            STRETCH_TO:ICON_STRETCH_TO,
            CHILD_OF:ICON_CHILD_OF,
            PIVOT:ICON_PIVOT,
            SHRINKWRAP:ICON_SHRINKWRAP,
        }

    CONSTRAINT_OPS = {
            COPY_LOCATION:'ops.ar_create_new_constraint_copy_location',
            COPY_ROTATION:'ops.ar_create_new_constraint_copy_rotation',
            COPY_SCALE :'ops.ar_create_new_constraint_copy_scale',
            LIMIT_DISTANCE:'ops.ar_create_new_constraint_limit_distance',
            LIMIT_LOCATION:'ops.ar_create_new_constraint_limit_location',
            LIMIT_ROTATION:'ops.ar_create_new_constraint_limit_rotation',
            LIMIT_SCALE :'ops.ar_create_new_constraint_limit_scale',
            TRANSFORM:'ops.ar_create_new_constraint_transform',
            DAMPED_TRACK:'ops.ar_create_new_constraint_damped_track',
            IK:'ops.ar_create_new_constraint_ik',
            STRETCH_TO:'ops.ar_create_new_constraint_stretch_to',
            CHILD_OF:'ops.ar_create_new_constraint_child_of',
            PIVOT:'ops.ar_create_new_constraint_pivot',
            SHRINKWRAP:'ops.ar_create_new_constraint_shrinkwrap',
    }

class ObjectAnimRet(bpy.types.PropertyGroup):
    prefix = 'AR_'
    @classmethod
    def _add_source(cls, _context, target_armature, do_check):
        if _context.active_object.anim_ret.is_frozen:
            return

        if do_check:
            for bone in target_armature.pose.bones:
                bone.anim_ret_bone.disabled = False

                for constraint in bone.anim_ret_constraints:
                    constraint.disabled = False


    @classmethod
    def _remove_source(cls, _context, old_source_armature, do_check):
        if _context.active_object.anim_ret.is_frozen:
            return

        cspy.bones.remove_bones_startwith(old_source_armature, ObjectAnimRet.prefix)

        target_armature = _context.active_object

        if do_check:
            for bone in target_armature.pose.bones:
                bone.anim_ret_bone.disabled = True

                for cd in bone.anim_ret_constraints:
                    constraint.disabled = True

    def _on_update_source(self, _context):
        if _context.active_object.anim_ret.is_frozen:
            return

        if self.source == self.old_source:
            return
        if not self.source and self.old_source:
            ObjectAnimRet._remove_source(_context, self.old_source, True)
        elif self.source and not self.old_source:
            ObjectAnimRet._add_source(_context, self.source, True)
        else:
            ObjectAnimRet._remove_source(_context, self.old_source, False)
            ObjectAnimRet._add_source(_context, self.source, True)

        self.old_source = self.source

    def _get_active_index(self):
        target_bones = bpy.context.active_object.data.bones
        anim_ret = bpy.context.active_object.anim_ret
        active_bone_name = anim_ret.get_active_bone_name(bpy.context)

        if active_bone_name == '' or active_bone_name not in target_bones:
            return -1
        new_index = target_bones.find(active_bone_name)

        if new_index != self.active_index_internal and new_index != -1:
            self.active_index_internal = new_index

        return self.active_index_internal

    def _set_active_index(self, value):

        self.active_index_internal = value
        if value == -1:
            return
        target_bones = bpy.context.active_object.data.bones
        bone = target_bones[self.active_index_internal]
        bpy.context.active_object.data.bones.active = bone
        bone.select = True

    active_index_internal:bpy.props.IntProperty(name='Active Index Internal')
    active_index: bpy.props.IntProperty(name='Active Index', get=_get_active_index, set=_set_active_index)
    old_source: bpy.props.PointerProperty(type=bpy.types.Object, name='Old Source Object')
    source: bpy.props.PointerProperty(type=bpy.types.Object, name='Source Object', update=_on_update_source)
    is_frozen: bpy.props.BoolProperty(name='Is Frozen',default=False)
    draw_gizmos: bpy.props.BoolProperty(name='Gizmos',default=True)
    show_def: bpy.props.BoolProperty(name='DEF',default=True)
    show_mch: bpy.props.BoolProperty(name='MCH',default=True)
    show_org: bpy.props.BoolProperty(name='ORG',default=True)
    show_fk: bpy.props.BoolProperty(name='FK', default=True)
    show_ik: bpy.props.BoolProperty(name='IK',default=True)
    filter_layers: bpy.props.BoolProperty(name='LAYER',default=True)
    active_mirror_bone: bpy.props.BoolProperty(name='Active Mirror (Bone)',default=False)
    active_mirror_constraint: bpy.props.BoolProperty(name='Active Mirror (Constraint)',default=False)

    @classmethod
    def get_offset_bone_name(cls, target_bone_name, source_bone_name):
        offset_bone_name = '{0}{1}__{2}'.format(ObjectAnimRet.prefix, target_bone_name, source_bone_name)
        return offset_bone_name

    @classmethod
    def update_offset_bones(cls, target_armature, target_bone_name, source_armature, source_bone_name, use_offset_bone):
        if bpy.context.active_object.anim_ret.is_frozen:
            return
        offset_bone_name = ObjectAnimRet.get_offset_bone_name(target_bone_name, source_bone_name)

        must_add=False
        must_update=False
        must_remove=False

        if not use_offset_bone:
            if offset_bone_name in source_armature.pose.bones:
                cspy.bones.remove_bone(source_armature, offset_bone_name)
            return

        offset_bone = cspy.bones.create_or_get_bone(source_armature, offset_bone_name)

        cspy.bones.set_bone_layer(source_armature, offset_bone_name, 0, False)
        cspy.bones.set_bone_layer(source_armature, offset_bone_name, 31, True)

        offset_pbone = source_armature.pose.bones[offset_bone_name]
        offset_pbone_parent_name = '' if offset_pbone.parent is None else offset_pbone.parent.name
        target_bone = target_armature.data.bones[target_bone_name]
        target_pbone = target_armature.pose.bones[target_bone_name]

        if offset_pbone.parent is None or offset_pbone_parent_name != source_bone_name:
            print('updating offset bone {0} - wrong parent: [{1}] vs [{2}]'.format(offset_bone_name, offset_pbone_parent_name, source_bone_name))
            cspy.bones.set_bone_parenting(source_armature, offset_bone_name, source_bone_name, False)
            offset_bone, offset_pbone = cspy.bones.get_bone_and_pose_bone(source_armature, offset_bone_name)
            target_bone, target_pbone = cspy.bones.get_bone_and_pose_bone(target_armature, target_bone_name)

        if not cspy.bones.are_bones_same_values(target_armature, target_pbone, source_armature, offset_pbone):
            print('updating offset bone {0} - wrong transformation'.format(offset_bone_name))

            matrix, head, tail, x_axis = cspy.bones.get_world_head_tail(target_armature, target_bone_name)
            cspy.bones.set_world_head_tail_xaxis(source_armature, offset_bone_name, head, tail, x_axis)

    def get_active_bone_name(self, _context):
        bone = get_active_pose_bone(_context)

        if bone is not None:
            return bone.name
        if _context.active_object is not None:
            if _context.active_object.type == 'ARMATURE':
                return _context.active_object.data.bones[self.active_index_internal].name

        return ''

class AnimRetBoneBase:

    def on_update_source_bone_name(self, _context):
        pass

    def on_update_disabled(self, _context):
        pass

    def on_update_hide_off(self, _context):
        pass

    def on_update_influence(self, _context):
        pass

    def _update_source_bone_name(self, _context):
        self.on_update_source_bone_name(_context)

    def _update_disabled(self, _context):
        self.on_update_disabled(_context)

    def _update_hide_off(self, _context):
        self.on_update_hide_off(_context)

    def _update_influence(self, _context):
        self.on_update_influence(_context)

    bone_name: bpy.props.StringProperty(name='Target Bone')
    source_bone_name: bpy.props.StringProperty(name='Source Bone', update=_update_source_bone_name)
    disabled: bpy.props.BoolProperty(name='Disabled', default=False, update=_update_disabled)
    cached: bpy.props.BoolProperty(name='Cached', default=False)
    hide_off: bpy.props.BoolProperty(name='Hide Off', default=True, update=_update_hide_off)
    influence: bpy.props.FloatProperty(name='Influence', default=1.0, min=0.0,max=1.0,update=_update_influence)

    def set_if_different_explicit(self, attr, val):
        if getattr(self, attr) != val:
            setattr(self, attr, val)

    def set_if_different(self, other, attr):
        other_val = getattr(other, attr)
        if getattr(self, attr) != other_val:
            setattr(self, attr, other_val)

    @classmethod
    def constraint_name_matches(cls, constraint):
        if constraint is None:
            return False
        if constraint.name.startswith(ObjectAnimRet.prefix):
            return True
        return False

    @classmethod
    def get_anim_ret(cls, _context, bone_name):
        obj = _context.active_object
        anim_ret = obj.anim_ret
        if anim_ret.is_frozen:
            return obj, anim_ret, None, None, None, None, None
        if bone_name not in obj.data.bones:
            return obj, anim_ret, None, None, None, None, None
        target_bone = obj.data.bones[bone_name]
        target_pbone = obj.pose.bones[bone_name]
        anim_ret_bone = target_pbone.anim_ret_bone
        pbone_constraints = target_pbone.constraints
        anim_ret_constraints = target_pbone.anim_ret_constraints

        return obj, anim_ret, target_bone, target_pbone, anim_ret_bone, pbone_constraints, anim_ret_constraints

class ConstraintAnimRet(AnimRetBoneBase, bpy.types.PropertyGroup):

    _flipped_mirrored_fields = [ 'source_bone_name']
    _mirrored_fields = ['name', 'index', 'constraint_type', 'use_constraint', 'use_offset_bone', 'disabled', 'hide_off', 'influence']

    def on_update_source_bone_name(self, _context):
        self.check_constraint(_context)

    def on_update_disabled(self, _context):
        self.check_constraint(_context)

    def on_update_hide_off(self, _context):
        self.check_constraint(_context)

    def on_update_influence(self, _context):
        self.check_constraint(_context)

    def _update_use_constraint(self, _context):
        self.check_constraint(_context)

    def _update_use_offset_bone(self, _context):
        self.check_constraint(_context)

    name : bpy.props.StringProperty(name="Constraint Name")
    index : bpy.props.IntProperty(name="Constraint Index")
    constraint_type: bpy.props.StringProperty(name='Constraint Type')
    icon: bpy.props.StringProperty(name='Constraint Icon')
    use_constraint: bpy.props.BoolProperty(name='Use Constraint', update=_update_use_constraint)
    use_offset_bone: bpy.props.BoolProperty(name='Use Offset Bone', update=_update_use_offset_bone, default=True)

    def get_source_bone_name(self, anim_ret_bone):
        if self.source_bone_name != '':
            return self.source_bone_name
        return anim_ret_bone.source_bone_name

    def get_subtarget(self, anim_ret_bone):
        target_bone_name = self.bone_name
        source_bone_name = self.get_source_bone_name(anim_ret_bone)

        if self.use_offset_bone:
            result = ObjectAnimRet.get_offset_bone_name(target_bone_name, source_bone_name)
        else:
            result = source_bone_name

        print('subtarget: {0} >> {1} >> {2}'.format(target_bone_name, source_bone_name, result))

        return result

    def get_hide_off(self, anim_ret_bone):
        if anim_ret_bone.disabled or self.disabled:
            return False
        if anim_ret_bone.hide_off:
            return self.hide_off
        return anim_ret_bone.hide_off

    def get_influence(self, anim_ret_bone):
        return self.influence * anim_ret_bone.influence

    def get_name(self, _context):
        name =  '{0}{1}_{2}'.format(ObjectAnimRet.prefix, self.constraint_type, self.index)

        if self.name != name:
            self.name = name
        return self.name

    def get_constraint(self, _context):
        name = self.get_name(_context)
        _, _, _, _, _, pbone_constraints, _ = AnimRetBoneBase.get_anim_ret(_context, self.bone_name)

        if name in pbone_constraints:
            return pbone_constraints[name]

        return None

    def mirror_constraint_data(self, _context, mirroring):
        for field in ConstraintAnimRet._mirrored_fields:
            self.set_if_different(mirroring, field)

        for field in ConstraintAnimRet._flipped_mirrored_fields:
            val = getattr(mirroring, field)
            flipped = cspy.naming.flip_side_name(val)
            self.set_if_different_explicit(field, flipped)

    def check_constraint_internal(self, _context):
        if _context.active_object.anim_ret.is_frozen:
            return
        obj, anim_ret, target_bone, target_pbone, anim_ret_bone, pbone_constraints, anim_ret_constraints = AnimRetBoneBase.get_anim_ret(_context, self.bone_name)

        print('{0}: check_constraint_internal'.format(self.bone_name))

        constraint = self.get_constraint(_context)

        # check removal
        if not self.use_constraint:
            if constraint is not None:
                pbone_constraints.remove(constraint)
            ix = anim_ret_constraints.find(self.name)
            anim_ret_constraints.remove(ix)
            return

        target_bone_name = target_pbone.name
        source_bone_name = self.get_source_bone_name(anim_ret_bone)

        if source_bone_name is None or source_bone_name == '':
            if constraint is not None:
                pbone_constraints.remove(constraint)
            return

        source_armature = anim_ret.source

        ObjectAnimRet.update_offset_bones(obj, target_bone_name, source_armature, source_bone_name, self.use_offset_bone)

        obj, anim_ret, target_bone, target_pbone, anim_ret_bone, pbone_constraints, anim_ret_constraints = AnimRetBoneBase.get_anim_ret(_context, self.bone_name)

        name = self.get_name(_context)

        constraint = self.get_constraint(_context)

        if constraint is None:
            constraint = pbone_constraints.new(self.constraint_type)

        constraint.name = name
        constraint.mute = not self.get_hide_off(anim_ret_bone)
        constraint.influence = self.get_influence(anim_ret_bone)
        constraint.target = source_armature
        constraint.subtarget = self.get_subtarget(anim_ret_bone)


    def check_mirrored_constraint(self, _context):
        if _context.active_object.anim_ret.is_frozen:
            return
        _, anim_ret, _, _, _, _, _ = AnimRetBoneBase.get_anim_ret(_context, self.bone_name)

        print('{0}: check_mirrored_constraint'.format(self.bone_name))

        anim_ret.active_mirror_constraint = True

        mirror_bone_name = cspy.naming.flip_side_name(self.bone_name)

        _, _, _, mirror_pbone, _, _, mirror_bone_anim_ret_constraints = AnimRetBoneBase.get_anim_ret(_context, mirror_bone_name)

        if mirror_pbone is None:
            anim_ret.active_mirror_constraint = False
            return

        found=False
        for cd in mirror_bone_anim_ret_constraints:
            if cd.name == self.name:
                found=True
                cd.mirror_constraint_data(_context, self)
                cd.check_constraint_internal(_context)
                break

        if not found:
            cd = mirror_bone_anim_ret_constraints.add()
            cd.initialize(_context, self.constraint_type, mirror_pbone)
            cd.mirror_constraint_data(_context, self)
            cd.check_constraint_internal(_context)

        anim_ret.active_mirror_constraint = False


    def check_constraint(self, _context):
        if _context.active_object.anim_ret.is_frozen:
            return
        if self.cached or self.disabled:
            return
        _, anim_ret, _, _, anim_ret_bone, _, _ = AnimRetBoneBase.get_anim_ret(_context, self.bone_name)

        if anim_ret.active_mirror_constraint:
            return

        print('{0}: check_constraint'.format(self.bone_name))

        self.check_constraint_internal(_context)
        if anim_ret_bone.use_mirror:
            self.check_mirrored_constraint(_context)


    def initialize(self, _context, constraint_type, bone):
        if _context.active_object.anim_ret.is_frozen:
            return

        print('{0}: initialize'.format(bone.name))
        self.constraint_type = constraint_type
        self.bone_name = bone.name

        anim_ret_bone = bone.anim_ret_bone
        anim_ret_constraints = bone.anim_ret_constraints

        index = 0
        for con in anim_ret_constraints:
            if con.index > index:
                index = con.index + 1

        self.index = index
        self.use_constraint = True
        self.check_constraint(_context)

    def copy_from(self, other):
        self.name = other.name
        self.index = other.index
        self.constraint_type = other.constraint_type
        self.icon = other.icon
        self.use_constraint = other.use_constraint
        self.use_offset_bone = other.use_offset_bone
        self.bone_name = other.bone_name
        self.source_bone_name = other.source_bone_name
        self.disabled = other.disabled
        self.hide_off = other.hide_off
        self.influence = other.influence

    def cache_from(self, other):
        self.cached = True
        self.copy_from(other)

    def restore_from(self, other):
        self.cached = True
        self.copy_from(other)
        self.cached = False

class BoneAnimRet(AnimRetBoneBase, bpy.types.PropertyGroup):

    _flipped_mirrored_fields = [ 'source_bone_name']
    _mirrored_fields = ['use_mirror', 'disabled', 'hide_off', 'influence']

    def on_update_source_bone_name(self, _context):
        self.check_bone(_context)

    def on_update_disabled(self, _context):
        self.check_bone(_context)

    def on_update_hide_off(self, _context):
        self.check_bone(_context)

    def on_update_influence(self, _context):
        self.check_bone(_context)

    def on_update_use_mirror(self, _context):
        self.check_bone(_context)

    use_mirror: bpy.props.BoolProperty(
        name='Use Mirror',
        description='Mirror retargeting constraints to appropriate bones.',
        update=on_update_use_mirror, default=True
    )

    def mirror_bone_data(self, _context, mirroring):
        if _context.active_object.anim_ret.is_frozen:
            return
        for field in BoneAnimRet._mirrored_fields:
            self.set_if_different(mirroring, field)

        for field in BoneAnimRet._flipped_mirrored_fields:
            val = getattr(mirroring, field)
            flipped = cspy.naming.flip_side_name(val)
            self.set_if_different_explicit(field, flipped)


    def check_bone_internal(self, _context):
        if _context.active_object.anim_ret.is_frozen:
            return
        _, anim_ret, _, _, _, _, anim_ret_constraints = AnimRetBoneBase.get_anim_ret(_context, self.bone_name)

        print('{0}: check_bone_internal'.format(self.bone_name))

        if anim_ret_constraints is None:
            return

        for con in anim_ret_constraints:
            if con.bone_name == '':
                con.bone_name = self.bone_name

            con.check_constraint(_context)


    def check_mirrored_bone(self, _context):
        if _context.active_object.anim_ret.is_frozen:
            return
        _, anim_ret, _, _, _, _, _ = AnimRetBoneBase.get_anim_ret(_context, self.bone_name)
        print('{0}: check_mirrored_bone'.format(self.bone_name))

        anim_ret.active_mirror_bone = True

        mirror_bone_name = cspy.naming.flip_side_name(self.bone_name)

        _, _, _, _, anim_ret_bone, _, _ = AnimRetBoneBase.get_anim_ret(_context, mirror_bone_name)

        if anim_ret_bone is None:
            return

        anim_ret_bone.bone_name = mirror_bone_name
        anim_ret_bone.mirror_bone_data(_context, self)
        anim_ret_bone.check_bone_internal(_context)

        anim_ret.active_mirror_bone = False


    def check_bone(self, _context):
        if _context.active_object.anim_ret.is_frozen:
            return
        if self.cached or self.disabled:
            return

        _, anim_ret, _, _, _, _, anim_ret_constraints = AnimRetBoneBase.get_anim_ret(_context, self.bone_name)

        if anim_ret.active_mirror_bone:
            return

        print('{0}: check_bone'.format(self.bone_name))


        self.check_bone_internal(_context)
        if self.use_mirror:
            self.check_mirrored_bone(_context)


    def copy_from(self, other):
        self.use_mirror = other.use_mirror
        self.source_bone_name = other.source_bone_name
        self.disabled = other.disabled
        self.hide_off = other.hide_off
        self.influence = other.influence

    def cache_from(self, other):
        self.cached = True
        self.copy_from(other)

    def restore_from(self, other):
        self.cached = True
        self.copy_from(other)
        self.cached = False
