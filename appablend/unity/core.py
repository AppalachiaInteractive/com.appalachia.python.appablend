import bpy
from appablend.common.timeline import clamp_timeline_to_range


def clamp_to_unity_clip(context, clip, play=False):
    clamp_timeline_to_range(context, clip.frame_start, clip.frame_end, play)

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

    if scene.unity_settings.mode == "SCENE":
        return scene.all_unity_clips
    else:
        action = obj.animation_data.action
        return action.unity_clips


def get_filtered_clips(context):
    scene = context.scene
    scene_mode = scene.unity_settings.mode == "SCENE"
    filters = scene.unity_clip_filters

    all_clips = get_all_clips(context)
    filtered_clips = [
        clip for clip in all_clips if not filters.should_filter(context, clip)
    ]

    return filtered_clips
