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

    TK_MASK   = '[MASK]'
    TK_ENV_S  = '[ENVIRONMENT-START]'
    TK_ENV_E  = '[ENVIRONMENT-END]'
    TK_STATE_S  = '[STATE-START]'
    TK_STATE_E  = '[STATE-END]'
    TK_SUBS_S = '[SUBSTATE-START]'
    TK_SUBS_E = '[SUBSTATE-END]'
    TK_DIR    = '[DIRECTION]'
    TK_ORI_E  = '[ORIENTATION-END]'
    TK_RMIP   = '[ROOT MOTION/IN PLACE]'
    TK_VARI   = '[VARIATION #]'
    TK_DFFL   = '[DEFAULT/FLIPPED]'
    TK_STGE   = '[STAGE]'
    TK_FLEN   = '[FRAME LENGTH]'

    _TKC_ENV      = _TK_SEP_SUB.join( [TK_ENV_S, TK_ENV_E] )
    _TKC_STATE      = _TK_SEP_SUB.join( [TK_STATE_S, TK_SUBS_S, TK_STATE_E, TK_SUBS_E] )
    _TKC_VARIATION     = 'v{0}'.format(_TK_SEP_SUB.join( [TK_VARI, TK_DFFL] ))
    _TKC_FRAME_LENGTH  = 'F{0}'.format(TK_FLEN)

    _TEMPLATE_KEYS = [
        TK_MASK,
        _TKC_ENV,
        _TKC_STATE,
        TK_DIR, 
        TK_ORI_E,
        TK_RMIP,
        _TKC_VARIATION,
        TK_STGE, 
        _TKC_FRAME_LENGTH
    ]

    TEMPLATE= _TK_SEP_TOP.join(_TEMPLATE_KEYS)
    
class Constants:
    ICON_PANEL = 'IMGDISPLAY'
    ICON_SHEET = "FILE_BLANK"

class AnimationMetadataBase():
    environment_start: bpy.props.EnumProperty(name='Environment', items=ENVIRONMENTS_ENUM, default=ENVIRONMENTS_ENUM_DEF)
    changes_environment: bpy.props.BoolProperty(name='Changes?', default=False)
    environment_end: bpy.props.EnumProperty(name='End', items=ENVIRONMENTS_ENUM, default=ENVIRONMENTS_ENUM_DEF)

    state_start: bpy.props.EnumProperty(name='State', items=STATES_ENUM, default=STATES_ENUM_DEF)
    changes_state: bpy.props.BoolProperty(name='Changes?', default=False)    
    state_end: bpy.props.EnumProperty(name='End', items=STATES_ENUM, default=STATES_ENUM_DEF)

    changes_substate: bpy.props.BoolProperty(name='Changes?', default=False)
    IDLE_substate_start: bpy.props.EnumProperty(name='Substate', items=IDLE_SUBSTATES_ENUM, default=IDLE_SUBSTATES_ENUM_DEF)    
    IDLE_substate_end: bpy.props.EnumProperty(name='End', items=IDLE_SUBSTATES_ENUM, default=IDLE_SUBSTATES_ENUM_DEF)

    SITT_substate_start: bpy.props.EnumProperty(name='Substate', items=SITT_SUBSTATES_ENUM, default=SITT_SUBSTATES_ENUM_DEF)
    SITT_substate_end: bpy.props.EnumProperty(name='End', items=SITT_SUBSTATES_ENUM, default=SITT_SUBSTATES_ENUM_DEF)

    LYNG_substate_start: bpy.props.EnumProperty(name='Substate', items=LYNG_SUBSTATES_ENUM, default=LYNG_SUBSTATES_ENUM_DEF)
    LYNG_substate_end: bpy.props.EnumProperty(name='End', items=LYNG_SUBSTATES_ENUM, default=LYNG_SUBSTATES_ENUM_DEF)

    MOVE_substate_start: bpy.props.EnumProperty(name='Substate', items=MOVE_SUBSTATES_ENUM, default=MOVE_SUBSTATES_ENUM_DEF)
    MOVE_substate_end: bpy.props.EnumProperty(name='End', items=MOVE_SUBSTATES_ENUM, default=MOVE_SUBSTATES_ENUM_DEF)

    ACTV_substate_start: bpy.props.EnumProperty(name='Substate', items=ACTV_SUBSTATES_ENUM, default=ACTV_SUBSTATES_ENUM_DEF)
    ACTV_substate_end: bpy.props.EnumProperty(name='End', items=ACTV_SUBSTATES_ENUM, default=ACTV_SUBSTATES_ENUM_DEF)

    CMBT_substate_start: bpy.props.EnumProperty(name='Substate', items=CMBT_SUBSTATES_ENUM, default=CMBT_SUBSTATES_ENUM_DEF)
    CMBT_substate_end: bpy.props.EnumProperty(name='End', items=CMBT_SUBSTATES_ENUM, default=CMBT_SUBSTATES_ENUM_DEF)

    ATCK_substate_start: bpy.props.EnumProperty(name='Substate', items=ATCK_SUBSTATES_ENUM, default=ATCK_SUBSTATES_ENUM_DEF)
    ATCK_substate_end: bpy.props.EnumProperty(name='End', items=ATCK_SUBSTATES_ENUM, default=ATCK_SUBSTATES_ENUM_DEF)

    VOCL_substate_start: bpy.props.EnumProperty(name='Substate', items=VOCL_SUBSTATES_ENUM, default=VOCL_SUBSTATES_ENUM_DEF)
    VOCL_substate_end: bpy.props.EnumProperty(name='End', items=VOCL_SUBSTATES_ENUM, default=VOCL_SUBSTATES_ENUM_DEF)

    SENS_substate_start: bpy.props.EnumProperty(name='Substate', items=SENS_SUBSTATES_ENUM, default=SENS_SUBSTATES_ENUM_DEF)
    SENS_substate_end: bpy.props.EnumProperty(name='End', items=SENS_SUBSTATES_ENUM, default=SENS_SUBSTATES_ENUM_DEF)

    EMOT_substate_start: bpy.props.EnumProperty(name='Substate', items=EMOT_SUBSTATES_ENUM, default=EMOT_SUBSTATES_ENUM_DEF)
    EMOT_substate_end: bpy.props.EnumProperty(name='End', items=EMOT_SUBSTATES_ENUM, default=EMOT_SUBSTATES_ENUM_DEF)

    stage: bpy.props.EnumProperty(name='Stage', items=STAGES_ENUM, default=STAGES_ENUM_DEF)

    oriented: bpy.props.BoolProperty(name='Is Oriented?', default=False)
    orientation_end: bpy.props.FloatProperty(name='Orientation', default=0.0, min=-math.pi*2,max=math.pi*2, subtype=subtypes.FloatProperty.Subtypes.ANGLE, unit=subtypes.FloatProperty.Units.ROTATION)

    masked: bpy.props.BoolProperty(name='Is Masked?', default=False)
    mask: bpy.props.EnumProperty(name='Mask', items=MASKS_ENUM, default=MASKS_ENUM_DEF)

    directional: bpy.props.BoolProperty(name='Is Directional?', default=False)
    direction: bpy.props.EnumProperty(name='Direction', items=DIRECTIONS_ENUM, default=DIRECTIONS_ENUM_DEF)
    
    variation: bpy.props.IntProperty(name='Variation', default=1)

    motion: bpy.props.BoolProperty(name='Root Motion', default=False)
    mirrored: bpy.props.BoolProperty(name='Mirrored', default=False)

    def _get_substate_key(self, val):
        return '{0}_'.format(val)

    def _get_substate_keys(self):
        start = self._get_substate_key(self.state_start)
        end = self._get_substate_key(self.state_end if self.changes_state else self.state_start)

        sk = '{0}substate_start'.format(start)
        ek = '{0}substate_end'.format(end)

        return sk, ek

    def _get_environment(self):
        return self.environment_start, self.environment_end if self.changes_environment else ''

    def _get_state(self):
        return self.state_start, self.state_end if self.changes_state else ''

    def _get_substate(self):
        sk, ek = self._get_substate_keys()

        s = getattr(self, sk)
        e = getattr(self, ek)

        return s, e if self.changes_substate else ''

    def get_action_name(self):
        action_name = NameTemplate.TEMPLATE

        action = self.id_data
        length = action.frame_range[1] - action.frame_range[0]

        env_start, env_end = self._get_environment()
        state_start, state_end = self._get_state()
        substate_start, substate_end = self._get_substate()

        action_name = action_name.replace(NameTemplate.TK_MASK   , self.mask if self.masked else 'FULL')        

        action_name = action_name.replace(NameTemplate.TK_ENV_S  , env_start)
        action_name = action_name.replace(NameTemplate.TK_ENV_E  , env_end)

        action_name = action_name.replace(NameTemplate.TK_STATE_S  , state_start)
        action_name = action_name.replace(NameTemplate.TK_STATE_E  , state_end)

        action_name = action_name.replace(NameTemplate.TK_SUBS_S , substate_start)
        action_name = action_name.replace(NameTemplate.TK_SUBS_E , substate_end)
        
        action_name = action_name.replace(NameTemplate.TK_DIR    , self.direction if self.directional else '')
        
        o = str(int(math.degrees(self.orientation_end)))
        action_name = action_name.replace(NameTemplate.TK_ORI_E  , o if self.oriented else '')

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

    def draw_start_change_end(self, context, col, key_start, key_change='', key_end='', icon=cspy.icons.CANCEL):
        key_change = key_start if key_change == '' else key_change
        key_end = key_start if key_end == '' else key_end

        start_prop_name = key_start if '_start' in key_start else '{0}_start'.format(key_start)
        changes_prop_name = 'changes_{0}'.format(key_change)
        end_prop_name = key_end if '_end' in key_end else '{0}_end'.format(key_end)
        changes = getattr(self, changes_prop_name)

        row1 = col.row(align=True)
        row1.prop(self, start_prop_name)        

        row1b = row1.split()
        row1b.prop(self, changes_prop_name, toggle=True, text='', icon=icon)      
        row1c = row1.split()   
        row1c.enabled = changes      
        row1c.prop(self, end_prop_name, text='') 

    def draw_enabled(self, context, layout, value_key, change_key, icon):
        row = self.get_row(layout)
        row.prop(self, change_key, toggle=True, text='', icon=icon)
        rowb = row.split()
        rowb.enabled = getattr(self, change_key)
        rowb.prop(self, value_key)
    
    def draw(self, context, layout):
        action = self.id_data
        new_name = self.get_action_name()
        substate_start_key, substate_end_key = self._get_substate_keys()

        box = layout.box()

        col = box.column(align=True)
        col.label(text=action.name)
        col.label(text=new_name)

        box = layout.box()        
        col = box.column(align=True)

        self.draw_enabled(context, col, 'mask', 'masked', cspy.icons.MOD_MASK)

        self.draw_start_change_end(context, col, 'environment', icon=cspy.icons.WORLD_DATA)
        self.draw_start_change_end(context, col, 'state', icon=cspy.icons.OUTLINER_OB_ARMATURE)
        self.draw_start_change_end(context, col, substate_start_key, 'substate', substate_end_key, icon=cspy.icons.MOD_ARMATURE)
        
        self.draw_enabled(context, col, 'direction', 'directional', cspy.icons.ORIENTATION_CURSOR)
        self.draw_enabled(context, col, 'orientation_end', 'oriented', cspy.icons.ORIENTATION_GIMBAL)

        row = self.get_row(col)        
        row.prop(self, 'variation', icon=cspy.icons.SEQUENCE)
        row.prop(self, 'stage')

        row = self.get_row(col)
        row.prop(self, 'motion', toggle=True, icon=cspy.icons.ORIENTATION_GLOBAL)
        row.prop(self, 'mirrored', toggle=True, icon=cspy.icons.MOD_MIRROR)
        

class AnimationMetadata(AnimationMetadataBase, bpy.types.PropertyGroup):
    def print(self):
        print(self.get_action_name())

    def from_animation_clip_metadata(self, acm):
        self.state = acm.state
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
