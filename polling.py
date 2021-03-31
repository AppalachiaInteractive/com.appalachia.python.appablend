import bpy
import cspy
from cspy import unity

class CONTEXT_MODES:
    EDIT_MESH = 'EDIT_MESH'
    EDIT_CURVE = 'EDIT_CURVE'
    EDIT_SURFACE = 'EDIT_SURFACE'
    EDIT_TEXT = 'EDIT_TEXT'
    EDIT_ARMATURE = 'EDIT_ARMATURE'
    EDIT_METABALL = 'EDIT_METABALL'
    EDIT_LATTICE = 'EDIT_LATTICE'
    POSE = 'POSE'
    SCULPT = 'SCULPT'
    PAINT_WEIGHT = 'PAINT_WEIGHT'
    PAINT_VERTEX = 'PAINT_VERTEX'
    PAINT_TEXTURE = 'PAINT_TEXTURE'
    PARTICLE = 'PARTICLE'
    OBJECT = 'OBJECT'
    PAINT_GPENCIL = 'PAINT_GPENCIL'
    EDIT_GPENCIL = 'EDIT_GPENCIL'
    SCULPT_GPENCIL = 'SCULPT_GPENCIL'
    WEIGHT_GPENCIL = 'WEIGHT_GPENCIL'
    VERTEX_GPENCIL = 'VERTEX_GPENCIL'

class OBJECT_TYPES:
    MESH = 'MESH'
    CURVE = 'CURVE'
    SURFACE = 'SURFACE'
    META = 'META'
    FONT = 'FONT'
    HAIR = 'HAIR'
    POINTCLOUD = 'POINTCLOUD'
    VOLUME = 'VOLUME'
    GPENCIL = 'GPENCIL'
    ARMATURE = 'ARMATURE'
    LATTICE = 'LATTICE'
    EMPTY = 'EMPTY'
    LIGHT = 'LIGHT'
    LIGHT_PROBE = 'LIGHT_PROBE'
    CAMERA = 'CAMERA'
    SPEAKER = 'SPEAKER'

class POLL:
    @classmethod
    def active_object(cls, context):
        return context.active_object is not None
    @classmethod

    def active_unity_object(cls, context):
        return cspy.unity.get_active_unity_object(context)

    @classmethod
    def active_object_type(cls, context, data_type):
        return POLL.active_object(context) and context.active_object.type == data_type

    @classmethod
    def active_object_data(cls, context):
        return POLL.active_object(context) and context.active_object.data is not None

    @classmethod
    def active_object_animation_data(cls, context):
        return POLL.active_object(context) and  context.active_object.animation_data is not None

    @classmethod
    def active_object_action(cls, context):
        return POLL.active_object_animation_data(context) and context.active_object.animation_data.action is not None

    @classmethod
    def active_object_unity_clips(cls, context):
        return POLL.active_object_action(context) and context.active_object.animation_data.action.unity_clips #and len(context.active_object.animation_data.action.unity_clips) > 0

    @classmethod
    def active_object_unity_clips_none(cls, context):
        return POLL.active_object_action(context) and context.active_object.animation_data.action.unity_clips and len(context.active_object.animation_data.action.unity_clips) == 0

    @classmethod
    def active_object_unity_clips_one(cls, context):
        return POLL.active_object_action(context) and context.active_object.animation_data.action.unity_clips and len(context.active_object.animation_data.action.unity_clips) == 1

    @classmethod
    def active_object_unity_clips_some(cls, context):
        return POLL.active_object_action(context) and context.active_object.animation_data.action.unity_clips and len(context.active_object.animation_data.action.unity_clips) > 0

    @classmethod
    def active_object_unity_clips_multiple(cls, context):
        return POLL.active_object_unity_clips(context) and len(context.active_object.animation_data.action.unity_clips) > 1

    @classmethod
    def active_object_unity_clips_split(cls, context):
        return POLL.active_object_unity_clips_one(context) and context.active_object.animation_data.action.unity_clips[0].source_action is not None

    @classmethod
    def active_ARMATURE(cls, context):
        return POLL.active_object_type(context, OBJECT_TYPES.ARMATURE)

    @classmethod
    def active_ARMATURE_AND_BONES(cls, context):
        return POLL.active_object_type(context, OBJECT_TYPES.ARMATURE) and len(context.active_object.data.bones) > 0

    @classmethod
    def active_ARMATURE_AND_BONES_AND_ANIMRET_SOURCE(cls, context):
        return (
            POLL.active_ARMATURE(context) and
            len(context.active_object.data.bones) > 0 and
            context.active_object.anim_ret.source != '' and
            context.active_pose_bone
        )

    @classmethod
    def active_ARMATURE_action(cls, context):
        return POLL.active_ARMATURE(context) and POLL.active_object_action(context)

    @classmethod
    def active_CURVE(cls, context):
        return POLL.active_object_type(context, OBJECT_TYPES.CURVE)

    @classmethod
    def active_MESH(cls, context):
        return POLL.active_object_type(context, OBJECT_TYPES.MESH)

    @classmethod
    def active_EMPTY(cls, context):
        return POLL.active_object_type(context, OBJECT_TYPES.EMPTY)

    @classmethod
    def mode(cls, context, mode):
        return context.mode == mode
    @classmethod
    def mode_EDIT_MESH(cls, context):
        return POLL.mode(context, CONTEXT_MODES.EDIT_MESH)

    @classmethod
    def mode_EDIT_CURVE(cls, context):
        return POLL.mode(context, CONTEXT_MODES.EDIT_CURVE)

    @classmethod
    def mode_EDIT_SURFACE(cls, context):
        return POLL.mode(context, CONTEXT_MODES.EDIT_SURFACE)

    @classmethod
    def mode_EDIT_TEXT(cls, context):
        return POLL.mode(context, CONTEXT_MODES.EDIT_TEXT)

    @classmethod
    def mode_EDIT_ARMATURE(cls, context):
        return POLL.mode(context, CONTEXT_MODES.EDIT_ARMATURE)

    @classmethod
    def mode_EDIT_METABALL(cls, context):
        return POLL.mode(context, CONTEXT_MODES.EDIT_METABALL)

    @classmethod
    def mode_EDIT_LATTICE(cls, context):
        return POLL.mode(context, CONTEXT_MODES.EDIT_LATTICE)

    @classmethod
    def mode_POSE(cls, context):
        return POLL.mode(context, CONTEXT_MODES.POSE)

    @classmethod
    def mode_SCULPT(cls, context):
        return POLL.mode(context, CONTEXT_MODES.SCULPT)

    @classmethod
    def mode_PAINT_WEIGHT(cls, context):
        return POLL.mode(context, CONTEXT_MODES.PAINT_WEIGHT)

    @classmethod
    def mode_PAINT_VERTEX(cls, context):
        return POLL.mode(context, CONTEXT_MODES.PAINT_VERTEX)

    @classmethod
    def mode_PAINT_TEXTURE(cls, context):
        return POLL.mode(context, CONTEXT_MODES.PAINT_TEXTURE)

    @classmethod
    def mode_PARTICLE(cls, context):
        return POLL.mode(context, CONTEXT_MODES.PARTICLE)

    @classmethod
    def mode_OBJECT(cls, context):
        return POLL.mode(context, CONTEXT_MODES.OBJECT)

    @classmethod
    def mode_PAINT_GPENCIL(cls, context):
        return POLL.mode(context, CONTEXT_MODES.PAINT_GPENCIL)

    @classmethod
    def mode_EDIT_GPENCIL(cls, context):
        return POLL.mode(context, CONTEXT_MODES.EDIT_GPENCIL)

    @classmethod
    def mode_SCULPT_GPENCIL(cls, context):
        return POLL.mode(context, CONTEXT_MODES.SCULPT_GPENCIL)

    @classmethod
    def mode_WEIGHT_GPENCIL(cls, context):
        return POLL.mode(context, CONTEXT_MODES.WEIGHT_GPENCIL)

    @classmethod
    def mode_VERTEX_GPENCIL(cls, context):
        return POLL.mode(context, CONTEXT_MODES.VERTEX_GPENCIL)

    @classmethod
    def ANIM_RET_IS_NOT_FROZEN(cls, context):
        return not context.active_object.anim_ret.is_frozen

    @classmethod
    def active_pose_bone(cls, context):
        return context.active_pose_bone

    @classmethod
    def data_actions(cls, context):
        return len(bpy.data.actions) > 0

    @classmethod
    def data_armatures(cls, context):
        return len(bpy.data.armatures) > 0

    @classmethod
    def unity_mode(cls, context, mode):
        return context.scene.unity_settings.mode == mode

    @classmethod
    def unity_mode_SCENE(cls, context):
        return  POLL.unity_mode(context, 'SCENE')

    @classmethod
    def unity_mode_TARGET(cls, context):
        return POLL.active_unity_object(context) and POLL.unity_mode(context, 'TARGET')

    @classmethod
    def unity_mode_ACTIVE(cls, context):
        return POLL.active_unity_object(context) and POLL.unity_mode(context, 'ACTIVE')
