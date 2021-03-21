import bpy
from bpy.types import Panel
import cspy
from cspy import ops
import math, mathutils
from mathutils import Matrix, Vector

def to_rest_position(armature):
    armature.data.pose_position = 'REST'

def to_pose_position(armature):
    armature.data.pose_position = 'POSE'

class Utils:    
    roots = ['Root','RootMotion','Root Motion']
    
    @classmethod
    def get_root_strings(cls):        
        search = []
        for root in cls.roots:
            u = root.replace(' ', '_')
            h = root.replace(' ', '-')
            ss = [root, root.upper(), root.lower(), u, u.upper(), u.lower(), h, h.upper(), h.lower()]
            for s in ss:
                search.append(s)
        return search

class ArmatureModification(bpy.types.PropertyGroup):
    root_motion_mute_internal: bpy.props.BoolProperty(name='Root Motion Muted Internal')
    root_bone_name: bpy.props.StringProperty(name='Root Motion Bone')
    searched_root_bone: bpy.props.BoolProperty(name='Searched Root Motion Bone')

    def sync_root_motion_mute_poll(self):        
        obj = bpy.context.active_object
        if obj is None:
            return False
        action = obj.animation_data.action
        if action is None:
            return False            
        if self.root_bone_name == '':
            if self.searched_root_bone:
                return False
            ss = Utils.get_root_strings()
            for s in ss:
                if s in obj.data.bones:
                    self.root_bone_name = obj.data.bones[s].name
                    break
            searched_root_bone = True
            if self.root_bone_name == '':
                return False
        else:
            if self.root_bone_name not in obj.data.bones:
                self.root_bone_name = ''
                return False
        return True

    def sync_root_motion_mute(self):
        obj = bpy.context.active_object
        action = obj.animation_data.action

        if not self.sync_root_motion_mute_poll():
            return

        if not self.root_bone_name in action.groups:
            return

        group = action.groups[self.root_bone_name]
        
        for fcurve in group.channels:
            val = self.root_motion_mute_internal
            if fcurve.mute != val: 
                fcurve.mute = val

    def get_root_motion_mute(self):
        self.sync_root_motion_mute()
        return self.root_motion_mute_internal

    def set_root_motion_mute(self, value):
        self.root_motion_mute_internal = value
        self.sync_root_motion_mute()
    
    root_motion_mute: bpy.props.BoolProperty(name='Root Motion Muted', get=get_root_motion_mute,set=set_root_motion_mute)
