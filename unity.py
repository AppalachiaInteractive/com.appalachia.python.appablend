import bpy
import math
from mathutils import Vector, Euler, Matrix
import cspy
from cspy import utils


class UnityClipDrawSettings(bpy.types.PropertyGroup):
    draw_metadata: bpy.props.BoolProperty(name='Draw Clip Metadata')
    draw_root_motion: bpy.props.BoolProperty(name='Draw Root Motion')
    draw_frames: bpy.props.BoolProperty(name='Draw Frames')
    draw_pose: bpy.props.BoolProperty(name='Draw Pose')
    draw_delete: bpy.props.BoolProperty(name='Draw Delete')

class UnityClipMetadata(bpy.types.PropertyGroup):
    action: bpy.props.PointerProperty(name='Action', type=bpy.types.Action)
    fbx_name: bpy.props.StringProperty(name='FBX Name')
    name: bpy.props.StringProperty(name='Clip Name')
    frame_start: bpy.props.IntProperty(name='Frame Start')
    frame_end: bpy.props.IntProperty(name='Frame End')
    pose_start: bpy.props.StringProperty(name='Pose Start')
    pose_end: bpy.props.StringProperty(name='Pose End')
    pose_start_rooted: bpy.props.BoolProperty(name='Pose Start Rooted')
    pose_end_rooted: bpy.props.BoolProperty(name='Pose End Rooted')
    loop_time: bpy.props.BoolProperty(name='Loop Time')
    rot_bake_into: bpy.props.BoolProperty(name='Root Rotation - Bake Into Pose')
    rot_keep_orig: bpy.props.BoolProperty(name='Root Rotation -  Keep Original')
    rot_offset: bpy.props.FloatProperty(name='Root Rotation -  Offset')
    y_bake_into: bpy.props.BoolProperty(name='Root Position Y - Bake Into Pose')
    y_keep_orig: bpy.props.BoolProperty(name='Root Position Y -  Keep Original')
    y_offset: bpy.props.FloatProperty(name='Root Position Y -  Offset')
    xz_bake_into: bpy.props.BoolProperty(name='Root Position XZ - Bake Into Pose')
    xz_keep_orig: bpy.props.BoolProperty(name='Root Position XZ - Keep Original')

    def copy_from(self, other):
        self.action = other.action
        self.fbx_name = other.fbx_name
        self.name = other.name
        self.frame_start = other.frame_start
        self.frame_end = other.frame_end
        self.pose_start = other.pose_start
        self.pose_end = other.pose_end
        self.loop_time = other.loop_time
        self.rot_bake_into = other.rot_bake_into
        self.rot_keep_orig = other.rot_keep_orig
        self.rot_offset = other.rot_offset
        self.y_bake_into = other.y_bake_into
        self.y_keep_orig = other.y_keep_orig
        self.y_offset = other.y_offset
        self.xz_bake_into = other.xz_bake_into
        self.xz_keep_orig = other.xz_keep_orig

    @classmethod
    def parse_row(cls, row, key_offset):
        obj_name = row['obj_name']
        obj_name = obj_name.replace('Avatar','')
        clip_name = row['clip_name']
        frame_start = int(row['start_frame']) + key_offset
        frame_end = int(row['stop_frame']) + key_offset
        loop_time = True if row['loop_time'] == 'True' else False
        rot_bake_into = True if row['rot_bake_into'] == 'True' else False
        rot_keep_orig = True if row['rot_keep_orig'] == 'True' else False
        rot_offset = float(row['rot_offset'])
        y_bake_into = True if row['y_bake_into'] == 'True' else False
        y_keep_orig = True if row['y_keep_orig'] == 'True' else False
        y_offset = float(row['y_offset'])
        xz_bake_into = True if row['xz_bake_into'] == 'True' else False
        xz_keep_orig = True if row['xz_keep_orig'] == 'True' else False

        return obj_name,clip_name,frame_start,frame_end,loop_time,rot_bake_into,rot_keep_orig,rot_offset,y_bake_into,y_keep_orig ,y_offset,xz_bake_into,xz_keep_orig

    @classmethod
    def process_row(cls, row, key_offset, action):
        obj_name,clip_name,frame_start,frame_end,loop_time,rot_bake_into,rot_keep_orig,rot_offset,y_bake_into,y_keep_orig ,y_offset,xz_bake_into,xz_keep_orig = UnityClipMetadata.parse_row(row, key_offset)

        if action is None:
            if obj_name not in bpy.data.actions:   
                print('Could not find action for [{0}]'.format(obj_name))
                return None
            else:
                action = bpy.data.actions[obj_name]
        else:
            if obj_name != action.name:
                return None

        metadata = action.unity_clips.get(clip_name)

        if not metadata:
            metadata = action.unity_clips.add()

        metadata.action = action
        metadata.fbx_name = obj_name
        metadata.name = clip_name
        metadata.frame_start = frame_start
        metadata.frame_end = frame_end
        metadata.pose_start = 'Default'
        metadata.pose_end = 'Default'
        metadata.loop_time = loop_time
        metadata.rot_bake_into = rot_bake_into
        metadata.rot_keep_orig = rot_keep_orig
        metadata.rot_offset = rot_offset
        metadata.y_bake_into = y_bake_into
        metadata.y_keep_orig = y_keep_orig
        metadata.y_offset = y_offset
        metadata.xz_bake_into = xz_bake_into
        metadata.xz_keep_orig = xz_keep_orig
        return metadata

    @classmethod
    def parse_files(cls, context, dir_path, key_offset, action=None):
        filepaths = cspy.files.get_files_in_dir(dir_path, '','','.txt')

        headers, rows = cspy.files.parse_csvs(filepaths)

        metadatas = []

        if action:
            action.unity_clips.clear()

        for row in rows:
            metadata = UnityClipMetadata.process_row(row, key_offset, action)

            if metadata:
                metadatas.append(metadata)

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

def apply_pose_to_frame(context, armature, pose_name, frame):
    pose_index = armature.pose_library.pose_markers.find(pose_name)

    if pose_index == -1:
        return
    context.scene.frame_current = frame
    bpy.ops.poselib.apply_pose(pose_index=pose_index)
