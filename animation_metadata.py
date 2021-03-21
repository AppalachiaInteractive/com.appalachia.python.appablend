import bpy
from bpy.types import Header, Menu, Panel
from bpy.props import *
import cspy
C = bpy.context
D = bpy.data

class Constants:
    ICON_PANEL = 'IMGDISPLAY'
    ICON_SHEET = "FILE_BLANK"

class Utils:
    @classmethod
    def get_casing_set(cls, v):        
        vals = []
        vals.append(v)
        vals.append(v.lower())
        vals.append(v.upper())
        vals.append(v.title())
        return vals

    @classmethod
    def get_full_key_set(cls, d, need_empty_prefix):    
        fullkeys = []
        for key in d.keys():        
            value = d[key]        
            keys = cls.get_casing_set(key)
            
            for xkey in keys:
                if need_empty_prefix:
                    fullkeys.append([key, xkey, value]) 
                for pfx in cspy.animals.Constants.PREFIXES:
                    fullkey = '{0}{1}'.format(pfx, xkey)
                    fullkeys.append([key, fullkey, value])
        return fullkeys
        
    @classmethod
    def replacement_collection(cls, clip_name, d, need_empty_prefix, format_string):    
        c= clip_name.strip()
        hits = set()
        
        for okey, key, value in cls.get_full_key_set(d, need_empty_prefix):
            c = c.strip()
            if okey in hits:
                continue
            if key in c:
                hits.add(okey)
                c = c.replace(key, '').strip()
                c = format_string.format(c, value)
                c = c.strip()
        
        c = c.strip()
        return c

    @classmethod
    def strip_many(cls, string, chars):
        
        hit = True

        while(hit):
            hit = False
            for char in chars:
                new = string.strip(char)
                if new != string:
                    hit = True
                    string = new
        
        return string

class AnimationSplit(bpy.types.PropertyGroup):
    sheet_path : bpy.props.StringProperty(name='Sheet Path', description="Choose the file path of the sheet.", 
        maxlen=1024, subtype='FILE_PATH')
    sheet_frame_offset : bpy.props.IntProperty(name='Sheet Offset', description="Offset to apply to sheet values.", default=1)
    action : bpy.props.StringProperty(name='Input Action', description="The action to split.")
    col_1_width : bpy.props.IntProperty(name='Col 1 Width', description="The width of the frame start column", default=4)  
    sep_1_width : bpy.props.IntProperty(name='Separator 1 Width', description="The width of the frame column separator", default=1)  
    col_2_width : bpy.props.IntProperty(name='Col 2 Width', description="The width of the frame end column", default=4)  
    sep_2_width : bpy.props.IntProperty(name='Separator 2 Width', description="The width of the clip name column separator", default=1)  

    def get_animation_sets(self, context):

        obj = context.active_object
        filepath_full = bpy.path.abspath(self.sheet_path)
        with open(filepath_full) as f:
            anim_sheet = f.readlines()
        
        animation_split_clips = obj.animation_split_clips
        animation_split_clips.clear()

        for anim_sheet_line in anim_sheet:
            if len(anim_sheet_line) < 9:
                continue
            
            animation_clip = animation_split_clips.add()
            animation_clip.parse_sheet_line(anim_sheet_line, self.col_1_width, self.sep_1_width, self.col_2_width, self.sep_2_width, self.sheet_frame_offset)
            animation_clip.print()


    def draw(self, layout, context):
                        
        row = layout.row()
        row.prop(self, 'sheet_path')

        row = layout.row()        
        row.prop_search(self, 'action', bpy.data, 'actions')    
        row.prop(self, 'sheet_frame_offset') 

        if self.action != '':
            row = layout.row()
            action = bpy.data.actions[self.action]
            curves = len(action.fcurves)
            keys = len(action.fcurves[0].keyframe_points)
            row.label(text='{0} curves, {1} keys'.format(curves, keys))

        layout.separator()

        row = layout.row()
        row.prop(self, 'col_1_width')
        row.prop(self, 'sep_1_width')
        row = layout.row()
        row.prop(self, 'col_2_width')
        row.prop(self, 'sep_2_width')

class ActionMetadataBase():   
    length: bpy.props.IntProperty(name='Length')
    action: bpy.props.StringProperty(name='Action')

    state: bpy.props.EnumProperty(name='State', items=cspy.animals.Constants.STATES_ENUM, default=cspy.animals.Constants.STATES_ENUM_DEF)
    substate_start: bpy.props.EnumProperty(name='Substate Start', items=cspy.animals.Constants.SUBSTATES_ENUM, default=cspy.animals.Constants.SUBSTATES_ENUM_DEF)
    substate_end: bpy.props.EnumProperty(name='Substate End', items=cspy.animals.Constants.SUBSTATES_ENUM, default=cspy.animals.Constants.SUBSTATES_ENUM_DEF)

    environment_start: bpy.props.EnumProperty(name='Environment Start', items=cspy.animals.Constants.ENVIRONMENTS_ENUM, default=cspy.animals.Constants.ENVIRONMENTS_ENUM_DEF)
    environment_end: bpy.props.EnumProperty(name='Environment End', items=cspy.animals.Constants.ENVIRONMENTS_ENUM, default=cspy.animals.Constants.ENVIRONMENTS_ENUM_DEF)
    
    orientation_start: bpy.props.IntProperty(name='Orientation Start', default=0)
    orientation_end: bpy.props.IntProperty(name='Orientation End', default=0)

    stage: bpy.props.EnumProperty(name='Stage', items=cspy.animals.Constants.STAGES_ENUM, default=cspy.animals.Constants.STAGES_ENUM_DEF)
    direction: bpy.props.EnumProperty(name='Direction', items=cspy.animals.Constants.DIRECTIONS_ENUM, default=cspy.animals.Constants.DIRECTIONS_ENUM_DEF)
    
    variation: bpy.props.IntProperty(name='Variation', default=1)
    motion: bpy.props.BoolProperty(name='Root Motion', default=False)
    mirrored: bpy.props.BoolProperty(name='Mirrored', default=False)

    def get_action_name(self):
        if self.state == 'MOVE':       
            orientation = '{0:03d}-{1:03d}'.format(self.orientation_start, self.orientation_end)
            movement = '{1}_{0}'.format(orientation, 'RM' if self.motion else 'IP')
            
            envstate = '{0}-{1}-{2}-{3}'.format(
                    self.environment_start,
                    self.substate_start, 
                    self.substate_end,
                    self.environment_end
                )

            basis = '{0}_{1}_{2}_{3}_v{4}'.format(
                self.state, 
                envstate, 
                self.direction, 
                movement,
                self.variation)

            append = '{0}_{1}_F{2}'.format(                
                'FL' if self.mirrored else 'DF',
                self.stage,
                self.length
                )

            action = '{0}-{1}'.format(basis, append)
            
            return action
            
        basis = '{0}-{1}-{2}_{3}'.format(self.state, self.substate_start, self.direction, 'v{0}'.format(self.variation))
        return '{0}_{1}_{2}_F{3}'.format(
            basis,
            'FL' if self.mirrored else 'DF',
            self.stage,
            self.length)

class ActionMetadata(ActionMetadataBase, bpy.types.PropertyGroup):  
    def print(self):
        print(self.get_action_name())
    
    def from_animation_clip_metadata(self, acm):
        self.length = acm.length
        self.action = acm.action
        self.state = acm.state
        self.substate_start = acm.substate_start
        self.substate_end = acm.substate_end
        self.environment_start = acm.environment_start
        self.environment_end = acm.environment_end
        self.orientation_start = acm.orientation_start
        self.orientation_end = acm.orientation_end
        self.stage = acm.stage
        self.direction = acm.direction
        self.variation = acm.variation
        self.motion = acm.motion
        self.mirrored = acm.mirrored


class AnimationClipMetadata(ActionMetadataBase, bpy.types.PropertyGroup):
    
    clip_name: bpy.props.StringProperty(name='Name')   
    clean_name: bpy.props.StringProperty(name='Clean Name')    
    start: bpy.props.IntProperty(name='Start')
    end: bpy.props.IntProperty(name='End')

    def parse_sheet_line(self, anim_sheet_line, col_1_width=4, sep_width=1, col_2_width=4,sep_2_width=1,offset=1):
        clean = Utils.strip_many(anim_sheet_line, cspy.animals.Constants.LINE_STRIP_CHARS)

        col_1_start = 0
        col_1_end = col_1_start + col_1_width
        col_2_start = col_1_end + sep_width
        col_2_end = col_2_start + col_2_width
        clip_start = col_2_end + sep_2_width
        
        self.start = offset+int(clean[col_1_start:col_1_end].strip())
        self.end = offset+int(clean[col_2_start:col_2_end].strip())
        self.clip_name = clean[clip_start:].strip()
        self.length = self.end - self.start
        
        self.clean_name = self.clip_name

        for key in cspy.animals.Constants.TYPOS.keys():
            value = cspy.animals.Constants.TYPOS[key]
            self.clean_name = self.clean_name.replace(key, value).replace(key.lower(), value).replace(key.upper(), value)  
        
        self.clean_name = Utils.replacement_collection(self.clean_name, cspy.animals.Constants.DIRECTIONS, False, '{0} {1}')
        self.clean_name = Utils.replacement_collection(self.clean_name, cspy.animals.Constants.STAGES, True, '{0} {1}')

        for val in cspy.animals.Constants.ENVIRONMENTS.values():
            if val in self.clean_name:
                self.environment_start = val
                self.environment_end = val
                self.clean_name = self.clean_name.replace(val, '')

        for val in cspy.animals.Constants.STATES.values():
            if val in self.clean_name:
                self.state = val
                self.clean_name = self.clean_name.replace(val, '')

        
        for val in cspy.animals.Constants.SUBSTATES.values():
            if val in self.clean_name:
                self.substate_start = val
                self.clean_name = self.clean_name.replace(val, '')

        self.substate_end = self.substate_start

        for val in cspy.animals.Constants.STAGES.values():
            if val in self.clean_name:
                self.stage = val
                self.clean_name = self.clean_name.replace(val, '')

        for val in cspy.animals.Constants.DIRECTIONS.values():
            if val in self.clean_name:
                self.direction = val
                self.clean_name = self.clean_name.replace(val, '')

        for key in cspy.animals.Constants.VARIATIONS.keys():
            if key in self.clean_name:
                val = cspy.animals.Constants.VARIATIONS[key]
                self.variation = val
                self.clean_name = self.clean_name.replace(key, '')

        for key in cspy.animals.Constants.ORIENTATIONS.keys():
            if key in self.clean_name:
                val = cspy.animals.Constants.ORIENTATIONS[key]
                self.orientation_start = val[0]
                self.orientation_end = val[1]
                self.clean_name = self.clean_name.replace(key, '')

        for key in cspy.animals.Constants.CHAR_REPLACEMENTS.keys():
            if key in self.clean_name:
                val = cspy.animals.Constants.CHAR_REPLACEMENTS[key]
                self.clean_name = self.clean_name.replace(key, val)

        self.clean_name = Utils.strip_many(self.clean_name, ['_','-','[',']',' ','|'])
            
    def split_action(self, master_action):
        
        new_action = cspy.actions.split_action(
            master_action,
            self.get_action_name(),
            self.start,
            self.end
            )
        new_action.action_metadata.from_animation_clip_metadata(self)

    def print(self):
        print('{0} - {1} : {2}  |  {3}  |  {4}'.format(
            self.start, self.end, 
            self.get_action_name(),
            self.clip_name,
            self.clean_name
        ))
        
    
