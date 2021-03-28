import bpy
import math
from mathutils import Vector, Euler, Matrix
import cspy
from cspy import utils

def update_clip_index(self, context):    
    action = context.active_object.animation_data.action
    if self.id_data != action:
        return
    clip = action.unity_clips[action.unity_metadata.clip_index]

    context.scene.frame_start = clip.frame_start
    context.scene.frame_end = clip.frame_end
    context.scene.frame_set(clip.frame_start)    
    bpy.ops.timeline.view_clip()

class UnityActionMetadata(bpy.types.PropertyGroup):  
    clips_protected: bpy.props.BoolProperty(name='Clip Data Protected')
    clips_hidden: bpy.props.BoolProperty(name='Clips Hidden')
    master_action: bpy.props.BoolProperty(name='Master Action')
    unity_clip_template: bpy.props.PointerProperty(name="Unity Clip Template", type=bpy.types.Action)
    clip_index: bpy.props.IntProperty(name='Unity Index', default =-1, min=-1, update=update_clip_index)
    split_from: bpy.props.PointerProperty(name='Action', type=bpy.types.Action)

class UnityRootMotionSettings(bpy.types.PropertyGroup):    
    rot_bake_into: bpy.props.BoolProperty(name='Root Rotation - Bake Into Pose')
    x_bake_into: bpy.props.BoolProperty(name='Root Position X - Bake Into Pose')
    y_bake_into: bpy.props.BoolProperty(name='Root Position Y - Bake Into Pose')
    z_bake_into: bpy.props.BoolProperty(name='Root Position Z - Bake Into Pose')

    rot_offset: bpy.props.FloatProperty(name='Root Rotation -  Offset')
    x_offset: bpy.props.FloatProperty(name='Root Position X -  Offset')
    y_offset: bpy.props.FloatProperty(name='Root Position Y -  Offset')
    z_offset: bpy.props.FloatProperty(name='Root Position Z -  Offset')

    keys = [
        'rot_bake_into',
        'x_bake_into',
        'y_bake_into',
        'z_bake_into',
        'rot_offset',
        'x_offset',
        'y_offset',
        'z_offset'
    ]

    def copy_from(self, other):
        cspy.utils.copy_from_to(other, self)

class UnityClipMetadata(bpy.types.PropertyGroup):
    can_edit: bpy.props.BoolProperty(name='Can Edit')
    fbx_name: bpy.props.StringProperty(name='FBX Name')
    name: bpy.props.StringProperty(name='Clip Name')
    action: bpy.props.PointerProperty(name='Action', type=bpy.types.Action)
    frame_start: bpy.props.IntProperty(name='Frame Start')
    frame_end: bpy.props.IntProperty(name='Frame End')
    source_action: bpy.props.PointerProperty(name='Source Action', type=bpy.types.Action)
    source_frame_start: bpy.props.IntProperty(name='Source Frame Start')
    source_frame_end: bpy.props.IntProperty(name='Source Frame End')
    source_frame_shift: bpy.props.IntProperty(name='Source Frame Shift')
    pose_start: bpy.props.StringProperty(name='Pose Start')
    pose_end: bpy.props.StringProperty(name='Pose End')
    pose_start_rooted: bpy.props.BoolProperty(name='Pose Start Rooted')
    pose_end_rooted: bpy.props.BoolProperty(name='Pose End Rooted')
    loop_time: bpy.props.BoolProperty(name='Loop Time')
    root_motion: bpy.props.PointerProperty(name='Root Motion', type=UnityRootMotionSettings)

    def copy_from(self, other):
        cspy.utils.copy_from_to(other, self)

    @classmethod
    def parse_clip_row(cls, row, key_offset):
        obj_name = row['obj_name']
        obj_name = obj_name.replace('Avatar','')
        clip_name = row['clip_name']
        frame_start = int(row['start_frame']) + key_offset
        frame_end = int(row['stop_frame']) + key_offset
        loop_time = True if row['loop_time'] == 'True' else False        
        rot_bake_into = True if row['rot_bake_into'] == 'True' else False
        rot_offset = float(row['rot_offset'])
        y_bake_into = True if row['y_bake_into'] == 'True' else False
        y_offset = float(row['y_offset'])
        xz_bake_into = True if row['xz_bake_into'] == 'True' else False

        return obj_name,clip_name,frame_start,frame_end,loop_time,rot_bake_into,rot_offset,y_bake_into ,y_offset,xz_bake_into

    @classmethod
    def process_clip_row(cls, row, key_offset, action):
        obj_name,clip_name,frame_start,frame_end,loop_time,rot_bake_into,rot_offset,y_bake_into ,y_offset,xz_bake_into = UnityClipMetadata.parse_clip_row(row, key_offset)
            
        potential_action_names = [obj_name, clip_name, '{0}_{1}'.format(obj_name, clip_name)]

        matching_metadatas = []

        if action is not None:
            found = False
            for potential_name in potential_action_names:
                if action.name == potential_name:
                    found = True
            
            if not found:
                return None

            metadata = action.unity_clips.get(clip_name)

            if not metadata:
                metadata = action.unity_clips.get(action.name)

            if not metadata:
                metadata = action.unity_clips.add()

            matching_metadatas.append(metadata)
        else:
            for potential_name in potential_action_names:
                if not action.name in bpy.data.actions:
                    continue
                
                action = bpy.data.actions[potential_name]

                metadata = action.unity_clips.get(clip_name)

                if not metadata:
                    metadata = action.unity_clips.get(action.name)

                if not metadata:
                    metadata = action.unity_clips.add()

                matching_metadatas.append(metadata)

        for metadata in matching_metadatas:                
            metadata.action = action
            metadata.fbx_name = obj_name
            metadata.name = clip_name
            metadata.frame_start = frame_start
            metadata.frame_end = frame_end
            metadata.pose_start = 'Default'
            metadata.pose_end = 'Default'
            metadata.loop_time = loop_time

            metadata.root_motion.rot_bake_into = rot_bake_into
            metadata.root_motion.x_bake_into = xz_bake_into
            metadata.root_motion.y_bake_into = y_bake_into
            metadata.root_motion.z_bake_into = xz_bake_into

            metadata.root_motion.rot_offset = rot_offset
            metadata.root_motion.x_offset = 0
            metadata.root_motion.y_offset = y_offset
            metadata.root_motion.z_offset = 0

        return matching_metadatas

    @classmethod
    def parse_clip_files(cls, context, dir_path, key_offset, action=None):
        filepaths = [path for path in cspy.files.get_files_in_dir(dir_path, '','','.txt') if not '.keys.' in path]

        headers, rows = cspy.files.parse_csvs(filepaths)

        metadatas = []

        if action:
            action.unity_clips.clear()

        for row in rows:
            metadatas = UnityClipMetadata.process_clip_row(row, key_offset, action)

            if metadatas:
                metadatas.extend(metadatas)

        return metadatas

    def decorate(self, action):

        start_marker_name = self.name
        stop_marker_name = '{0}.end'.format(start_marker_name)

        start_marker = action.pose_markers.get(start_marker_name)
        stop_marker = action.pose_markers.get(stop_marker_name)

        if not start_marker:
            start_marker = action.pose_markers.new(start_marker_name)
        if not stop_marker:
            stop_marker = action.pose_markers.new(start_marker_name)

        start_marker.frame = self.frame_start
        stop_marker.frame = self.frame_end

        for fc in action.fcurves:
            self.demarcate(fc)

    def demarcate(self, fcurve):
        s = self.frame_start
        e = self.frame_end

        sv = fcurve.evaluate(s)
        ev = fcurve.evaluate(e)
        cspy.actions.insert_keyframe_extreme(fcurve, s, sv, needed=False, fast=True)
        cspy.actions.insert_keyframe_extreme(fcurve, e, ev, needed=False, fast=True)

    @classmethod
    def handle_split(cls, master_action, new_action, old_clip_name, new_clip_name, frame_shift):
        for clip in master_action.unity_clips:
            if clip.name != old_clip_name:
                continue
            
            new_clip = new_action.unity_clips.add()
            new_clip.copy_from(clip)

            new_clip.action = new_action
            new_clip.name = new_clip_name

            new_clip.source_action = master_action
            new_clip.source_frame_start = new_clip.frame_start
            new_clip.source_frame_end = new_clip.frame_end
            new_clip.source_frame_shift = frame_shift

            new_clip.action = new_action
            new_clip.frame_start -= frame_shift
            new_clip.frame_end -= frame_shift
            break
        
        new_action.unity_metadata.split_from = master_action
        master_action.unity_metadata.clips_protected = True
        return new_clip

    def full_frame_range(self):
        self.frame_start = self.action.frame_range[0]
        self.frame_end = self.action.frame_range[1]
    
    def refresh_keys(self):
        cspy.actions.copy_from_action_range(self.source_action, self.action, self.source_frame_start, self.source_frame_end, self.source_frame_shift)
