import bpy
from bpy.types import Header, Menu, Panel
from bpy.props import *
import cspy
from cspy import subtypes, utils, animation_metadata_enums
from cspy.animation_metadata_enums import *
import math

class NameTemplate:
    _TK_SEP_TOP = '_'
    _TK_SEP_SUB = '-'

    TK_ACTOR   = '[ACTOR]'
    TK_MASK    = '[MASK]'
    TK_ENV_S   = '[ENVIRONMENT-START]'
    TK_CAT_S   = '[CATEGORY-START]'
    TK_POSE_S  = '[POSE-START]'
    TK_SUBS    = '[SUBSTATE]'
    TK_DIR     = '[DIRECTION]'
    TK_RMIP    = '[ROOT MOTION/IN PLACE]'
    TK_ORI_E   = '[ORIENTATION-END]'
    TK_ENV_E   = '[ENVIRONMENT-END]'
    TK_CAT_E   = '[CATEGORY-END]'
    TK_POSE_E  = '[POSE-END]'
    TK_VARI    = '[VARIATION #]'
    TK_DFFL    = '[DEFAULT/FLIPPED]'
    TK_STGE    = '[STAGE]'
    TK_FLEN    = '[FRAME LENGTH]'

    _TKC_VARIATION     = 'v{0}'.format(_TK_SEP_SUB.join( [TK_VARI, TK_DFFL] ))
    _TKC_FRAME_LENGTH  = 'F{0}'.format(TK_FLEN)

    _TEMPLATE_KEYS = [
        TK_ACTOR,
        TK_MASK,
        TK_ENV_S,
        TK_CAT_S,
        TK_POSE_S,
        TK_SUBS,
        TK_DIR,
        TK_RMIP,
        TK_ORI_E,
        TK_ENV_E,
        TK_CAT_E,
        TK_POSE_E,
        _TKC_VARIATION,
        TK_STGE,
        _TKC_FRAME_LENGTH
    ]

    TEMPLATE= _TK_SEP_TOP.join(_TEMPLATE_KEYS)

class Constants:
    ICON_PANEL = 'IMGDISPLAY'
    ICON_SHEET = "FILE_BLANK"

class AnimationMetadataBase():

    envs = AM_ENVS()

    def _get_actors_enum(self, context):
        return self.envs.actors_enum.ENUM

    def _get_env_start_enum(self, context):
        return self.envs.env_enum.ENUM

    def _get_env_end_enum(self, context):
        return self.envs.env_enum.ENUM

    def _get_category_start_enum(self, context):
        e = self.environment_start
        if e == '':
            return []
        return self.envs.envs[e].category_enum.ENUM

    def _get_category_end_enum(self, context):
        e = self.environment_end if self.changes_environment else self.environment_start
        if e == '':
            return []
        return self.envs.envs[e].category_enum.ENUM

    def _get_mask_enum(self, context):
        e = self.environment_start
        c = self.category_start
        if e == '' or c == '':
            return []
        return self.envs.envs[e].categories[c].mask_enum.ENUM

    def _get_stage_enum(self, context):
        e = self.environment_start
        c = self.category_start
        if e == '' or c == '':
            return []
        return self.envs.envs[e].categories[c].stage_enum.ENUM

    def _get_pose_start_enum(self, context):
        e = self.environment_start
        c = self.category_start
        if e == '' or c == '':
            return []
        return self.envs.envs[e].categories[c].pose_enum.ENUM

    def _get_pose_end_enum(self, context):
        e = self.environment_end if self.changes_environment else self.environment_start
        c = self.category_end if self.changes_category else self.category_start
        if e == '' or c == '':
            return []
        return self.envs.envs[e].categories[c].pose_enum.ENUM

    def _get_substate_enum(self, context):
        e = self.environment_start
        c = self.category_start
        p = self.pose_start
        if e == '' or c == '' or p == '':
            return []
        return self.envs.envs[e].categories[c].poses[p].substate_enum.ENUM

    def _get_direction_enum(self, context):
        e = self.environment_start
        c = self.category_start
        p = self.pose_start
        if e == '' or c == '' or p == '':
            return []
        return self.envs.envs[e].categories[c].poses[p].direction_enum.ENUM

    actor: bpy.props.EnumProperty(name='Actor', items=_get_actors_enum, default=0)

    environment_start: bpy.props.EnumProperty(name='Environment', items=_get_env_start_enum, default=0)
    changes_environment: bpy.props.BoolProperty(name='Changes?', default=False)
    environment_end: bpy.props.EnumProperty(name='End', items=_get_env_end_enum, default=0)

    category_start: bpy.props.EnumProperty(name='Category', items=_get_category_start_enum, default=0)
    changes_category: bpy.props.BoolProperty(name='Changes?', default=False)
    category_end: bpy.props.EnumProperty(name='End', items=_get_category_end_enum, default=0)

    mask: bpy.props.EnumProperty(name='Mask', items=_get_mask_enum, default=0)

    stage: bpy.props.EnumProperty(name='Stage', items=_get_stage_enum, default=0)

    pose_start: bpy.props.EnumProperty(name='Pose', items=_get_pose_start_enum, default=0)
    changes_pose: bpy.props.BoolProperty(name='Changes?', default=False)
    pose_end: bpy.props.EnumProperty(name='End', items=_get_pose_end_enum, default=0)

    substate: bpy.props.EnumProperty(name='Substate', items=_get_substate_enum, default=0)

    orientation_end: bpy.props.FloatProperty(name='Orientation', default=0.0, min=-math.pi*2,max=math.pi*2, subtype=subtypes.FloatProperty.Subtypes.ANGLE, unit=subtypes.FloatProperty.Units.ROTATION)

    direction: bpy.props.EnumProperty(name='Direction', items=_get_direction_enum, default=0)

    variation: bpy.props.IntProperty(name='Variation', default=1)

    motion: bpy.props.BoolProperty(name='Root Motion', default=False)
    mirrored: bpy.props.BoolProperty(name='Mirrored', default=False)

    def _get_environment(self):
        return self.environment_start, self.environment_end if self.changes_environment else ''

    def _get_pose(self):
        return self.pose_start, self.pose_end if self.changes_pose else ''

    def _get_category(self):
        return self.category_start, self.category_end if self.changes_category else ''

    def _get_substate(self):
        return self.substate

    def get_action_name(self):
        action_name = NameTemplate.TEMPLATE

        action = self.id_data
        length = action.frame_range[1] - action.frame_range[0]

        env_start, env_end = self._get_environment()
        cat_start, cat_end = self._get_category()
        pose_start, pose_end = self._get_pose()
        substate = self._get_substate()

        action_name = action_name.replace(NameTemplate.TK_ACTOR  , self.actor)

        action_name = action_name.replace(NameTemplate.TK_CAT_S    , cat_start)
        action_name = action_name.replace(NameTemplate.TK_CAT_E    , cat_end)

        action_name = action_name.replace(NameTemplate.TK_MASK   , self.mask)

        action_name = action_name.replace(NameTemplate.TK_ENV_S  , env_start)
        action_name = action_name.replace(NameTemplate.TK_ENV_E  , env_end)

        action_name = action_name.replace(NameTemplate.TK_POSE_S  , pose_start)
        action_name = action_name.replace(NameTemplate.TK_POSE_E  , pose_end)

        action_name = action_name.replace(NameTemplate.TK_SUBS    , substate)

        action_name = action_name.replace(NameTemplate.TK_DIR    , self.direction)

        o = str(int(math.degrees(self.orientation_end)))
        action_name = action_name.replace(NameTemplate.TK_ORI_E  , o)

        action_name = action_name.replace(NameTemplate.TK_RMIP   , 'RM' if self.motion else 'IP')
        action_name = action_name.replace(NameTemplate.TK_VARI   , str(self.variation))
        action_name = action_name.replace(NameTemplate.TK_DFFL   , 'FL' if self.mirrored else 'DF')
        action_name = action_name.replace(NameTemplate.TK_STGE   , self.stage)
        action_name = action_name.replace(NameTemplate.TK_FLEN   , str(int(length)))

        return action_name

    def get_row(self, col):
        col.separator()
        row = col.row(align=True)
        return row

    def draw_basic(self, context, col, prop, icon=cspy.icons.CANCEL):
        row1 = col.row(align=True)
        row1.prop(self, prop, icon=icon)

    def draw_toggle(self, context, col, prop, icon=cspy.icons.CANCEL):
        row1 = col.row(align=True)
        row1.prop(self, prop, icon=icon,toggle=True)

    def draw_start_change_end(self, context, col, key_start, key_change='', key_end='', icon=cspy.icons.CANCEL):
        key_change = key_start if key_change == '' else key_change
        key_end = key_start if key_end == '' else key_end

        start_prop_name = key_start if '_start' in key_start else '{0}_start'.format(key_start)
        changes_prop_name = 'changes_{0}'.format(key_change)
        end_prop_name = key_end if '_end' in key_end else '{0}_end'.format(key_end)
        changes = getattr(self, changes_prop_name)

        row1 = col.row(align=True)
        row1.prop(self, start_prop_name, icon=icon)

        row1b = row1.split()
        row1b.prop(self, changes_prop_name, toggle=True, text='', icon=cspy.icons.CHECKBOX_HLT if changes else cspy.icons.CHECKBOX_DEHLT)
        row1c = row1.split()
        row1c.enabled = changes
        row1c.prop(self, end_prop_name, text='')

    def draw_enabled(self, context, layout, value_key, change_key, icon):
        row = self.get_row(layout)
        row.prop(self, change_key, toggle=True, text='', icon=icon)
        rowb = row.split()
        rowb.enabled = getattr(self, change_key)
        rowb.prop(self, value_key)

    def draw(self, context, layout, check_op):
        action = self.id_data
        new_name = self.get_action_name()
        substate = self._get_substate()

        box = layout.box()

        col = box.column(align=True)
        col.label(text=action.name)
        col.label(text=new_name)

        box = layout.box()
        col = box.column(align=True)

        row = col.row(align=True)
        self.draw_basic(context, row, 'actor', cspy.icons.MONKEY)
        self.draw_basic(context, row, 'mask', cspy.icons.MOD_MASK)

        self.draw_start_change_end(context, col, 'environment', icon=cspy.icons.WORLD_DATA)
        self.draw_start_change_end(context, col, 'category', icon=cspy.icons.OUTLINER_OB_GROUP_INSTANCE)
        self.draw_start_change_end(context, col, 'pose', icon=cspy.icons.OUTLINER_OB_ARMATURE)
        self.draw_basic(context, col, 'substate', icon=cspy.icons.MOD_ARMATURE)

        row = col.row(align=True)
        self.draw_basic(context, row, 'direction', cspy.icons.ORIENTATION_CURSOR)
        self.draw_basic(context, row, 'orientation_end', cspy.icons.ORIENTATION_GIMBAL)

        row = self.get_row(col)
        self.draw_basic(context, row, 'variation', icon=cspy.icons.SEQUENCE)
        self.draw_basic(context, row, 'stage', cspy.icons.FILE_REFRESH)

        row = self.get_row(col)
        self.draw_toggle(context, row, 'motion', icon=cspy.icons.ORIENTATION_GLOBAL)
        self.draw_toggle(context, row, 'mirrored', icon=cspy.icons.MOD_MIRROR)

        col.separator()
        col.operator(check_op, icon=cspy.icons.VIEWZOOM)


class AnimationMetadata(AnimationMetadataBase, bpy.types.PropertyGroup):
    def print(self):
        print(self.get_action_name())

    def from_animation_clip_metadata(self, acm):
        self.pose = acm.state
        self.substate_start = acm.substate_start
        self.substate_end = acm.substate_end
        self.environment_start = acm.environment_start
        self.environment_end = acm.environment_end
        self.orientation_end = acm.orientation_end
        self.stage = acm.stage
        self.direction = acm.direction
        self.variation = acm.variation
        self.motion = acm.motion
        self.mirrored = acm.mirrored
