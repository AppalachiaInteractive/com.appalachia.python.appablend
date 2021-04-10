import bpy
import math
from mathutils import Vector, Euler, Matrix
import cspy
from cspy import utils, subtypes, icons

def get_unity_target(context):
    obj = None
    if context.scene.unity_settings.mode == 'SCENE':
        obj = context.scene.unity_settings.target_armature
    elif context.scene.unity_settings.mode == 'TARGET':
        obj = context.scene.unity_settings.target_armature
    else:
        obj = context.active_object

    if obj is None:
        return None
    if obj.animation_data is None:
        obj.animation_data_create()

    return obj

def apply_clip_by_index(context, clip_index):
    if clip_index < 0:
        return
    scene = context.scene
    clip = scene.all_unity_clips[clip_index]
    action = clip.action

    scene.unity_settings.active_action = action

    obj = get_unity_target(context)

    obj.animation_data.action = action
    context.scene.frame_start = clip.frame_start
    context.scene.frame_end = clip.frame_end

    context.scene.frame_set(clip.frame_start)

def update_clip_index_scene(self, context):
    scene = context.scene
    apply_clip_by_index(context, scene.unity_settings.clip_index)
    
    bpy.ops.timeline.view_clip()


def apply_pose_to_frame(context, armature, pose_name, frame):
    pose_index = armature.pose_library.pose_markers.find(pose_name)

    if pose_index == -1:
        return
    context.scene.frame_current = frame
    bpy.ops.poselib.apply_pose(pose_index=pose_index)

def get_clip_frame_range_analysis(action):
    start_ends = []
    starts = set()
    ends = set()
    minf = 10000
    maxf = 0

    for clip in action.unity_clips:
        start = clip.frame_start
        end = clip.frame_end

        start_ends.append((start, end))
        starts.add(start)
        ends.add(end)

        minf = min(start, minf)
        maxf = max(end, maxf)

    return start_ends, starts, ends, minf, maxf

def get_all_clips(context):
    scene = context.scene
    obj = context.active_object

    if scene.unity_settings.mode == 'SCENE':
        return scene.all_unity_clips
    else:
        action = obj.animation_data.action
        return action.unity_clips

def get_unity_action_and_clip(context):
    try:
        scene = context.scene
        settings = scene.unity_settings

        obj = get_unity_target(context)

        action = None
        clip = None
        index = 0

        if not obj  or not obj.animation_data or not obj.animation_data.action:
            return action, clip, index

        if scene.unity_settings.mode == 'SCENE' and scene.all_unity_clips and len(scene.all_unity_clips) > 0:
            clip = scene.all_unity_clips[scene.unity_settings.clip_index]
            action = clip.action
            index = settings.clip_index
        else:
            action = settings.active_action
            if action is not None and action.unity_clips and len(action.unity_clips) > 0:
                clip = action.unity_clips[action.unity_metadata.clip_index]
                index = action.unity_metadata.clip_index

        return action, clip, index
    except Exception as inst:
        print('get_unity_action_and_clip: {0}'.format(inst))
        raise

def get_filtered_clips(context):
    scene = context.scene
    scene_mode = scene.unity_settings.mode == 'SCENE'
    filters = scene.unity_clip_filters

    all_clips = get_all_clips(context)
    filtered_clips = [clip for clip in all_clips if not filters.should_filter(context, clip)]

    return filtered_clips
