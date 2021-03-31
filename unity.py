import bpy
import math
from mathutils import Vector, Euler, Matrix
import cspy
from cspy import utils, subtypes, icons

def get_active_unity_object(context):
    if context.scene.unity_settings.mode == 'SCENE':
        return context.scene.unity_settings.target_armature
    if context.scene.unity_settings.mode == 'TARGET':
        return context.scene.unity_settings.target_armature

    return context.active_object

def update_clip_index_scene(self, context):
    scene = context.scene
    clip = scene.all_unity_clips[scene.unity_settings.clip_index]
    action = clip.action

    obj = get_active_unity_object(context)

    obj.animation_data.action = action
    context.scene.frame_start = clip.frame_start
    context.scene.frame_end = clip.frame_end

    context.scene.frame_set(clip.frame_start)

    bpy.ops.timeline.view_clip()

_MODES = {
    'Active Mode':'ACTIVE',
    'Target Mode':'TARGET',
    'Scene Mode':'SCENE',
}
_MODE_ENUM =             cspy.utils.create_enum_dict(_MODES)
_MODE_ENUM_DEF           = 'ACTIVE'

class UnitySettings(bpy.types.PropertyGroup):
    mode: bpy.props.EnumProperty(name='Mode', items=_MODE_ENUM, default=_MODE_ENUM_DEF)

    sheet_dir_path: bpy.props.StringProperty(name="Sheet Dir Path", subtype=subtypes.StringProperty.Subtypes.DIR_PATH)
    key_dir_path: bpy.props.StringProperty(name="Key Dir Path", subtype=subtypes.StringProperty.Subtypes.DIR_PATH)

    clip_index: bpy.props.IntProperty(name='Unity Index', default =-1, min=-1, update=update_clip_index_scene)
    target_armature: bpy.props.PointerProperty(name='Target Armature', type=bpy.types.Object)

    draw_sheets: bpy.props.BoolProperty(name='Draw Sheets')
    draw_keyframes: bpy.props.BoolProperty(name='Draw Keyframes')
    draw_clips: bpy.props.BoolProperty(name='Draw Clips')
    draw_metadata: bpy.props.BoolProperty(name='Draw Clip Metadata')
    draw_root_motion: bpy.props.BoolProperty(name='Draw Root Motion')
    draw_frames: bpy.props.BoolProperty(name='Draw Frames')
    draw_pose: bpy.props.BoolProperty(name='Draw Pose')
    draw_operations: bpy.props.BoolProperty(name='Draw Delete')

    icon_unity = cspy.icons.FILE_3D
    icon_sheets = cspy.icons.FILE
    icon_keys = cspy.icons.DECORATE_KEYFRAME
    icon_all_clips = cspy.icons.SEQ_SEQUENCER
    icon_clips = cspy.icons.SEQ_STRIP_DUPLICATE
    icon_clip = cspy.icons.SEQUENCE
    icon_metadata = cspy.icons.MESH_DATA
    icon_root_motion = cspy.icons.CON_FOLLOWPATH
    icon_frames = cspy.icons.CAMERA_DATA
    icon_pose = cspy.icons.ARMATURE_DATA
    icon_operations = cspy.icons.GHOST_DISABLED
    icon_operation = cspy.icons.GHOST_ENABLED


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
        obj = get_active_unity_object(context)

        action = None
        unity_clip = None
        if scene.unity_settings.mode == 'SCENE' and scene.all_unity_clips and len(scene.all_unity_clips) > 0:
            unity_clip = scene.all_unity_clips[scene.unity_settings.clip_index]
            action = unity_clip.action
        else:
            action = obj.animation_data.action
            if action is not None and action.unity_clips and len(action.unity_clips) > 0:
                unity_clip = action.unity_clips[action.unity_metadata.clip_index]

        return action, unity_clip
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
