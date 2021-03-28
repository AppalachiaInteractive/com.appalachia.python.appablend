import bpy

def is_playing(context):
    return context.screen.is_animation_playing

def stop_timeline(context):
    if is_playing(context):
        bpy.ops.screen.animation_play()

def play_timeline(context):
    if not is_playing(context):
        bpy.ops.screen.animation_play()

def rew_timeline(context):
    context.scene.frame_current = context.scene.frame_start

def ff_timeline(context):
    context.scene.frame_current = context.scene.frame_end

def clamp_timeline_start_to_current(context):
    context.scene.frame_start = context.scene.frame_current

def clamp_timeline_end_to_current(context):
    context.scene.frame_end = context.scene.frame_current

def clamp_timeline_to_range(context, frame_start, frame_end, play=False):
    context.scene.frame_current = frame_start
    context.scene.frame_start = frame_start
    context.scene.frame_end = frame_end
    if play:
        play_timeline(context)

def clamp_to_action(context, play=False):
    action = context.active_object.animation_data.action
    clamp_timeline_to_range(context, action.frame_range[0], action.frame_range[1], play)

def clamp_to_unity_clip(context, clip, play=False):
    clamp_timeline_to_range(context, clip.frame_start, clip.frame_end, play)

def clamp_to_strip(context, play=False):
    strips = get_selected_strips()

    start = 10000
    end = 0
    for strip in strips:
        if strip.select:
            start = min(start, strip.frame_start)
            end = max(end, strip.frame_end)
            
    clamp_timeline_to_range(context, start, end, play)

def clamp_to_strips(context, play=False):
    strips = get_selected_strips()

    start = 10000
    end = 0
    for strip in strips:
        start = min(start, strip.frame_start)
        end = max(end, strip.frame_end)

    action = context.active_object.animation_data.action
    clamp_timeline_to_range(context, start, end, play)

def get_notable_frames(action):
    frame_max = 1 + int(action.frame_range[1])
    frame_keys = [0] * frame_max

    for fcurve in action.fcurves:
        for index, keyframe in enumerate(fcurve.keyframe_points):
            f = int(keyframe.co[0])
            v = keyframe.co[1]
            if keyframe.type == 'EXTREME':
                c = frame_keys[f]
                frame_keys[f] = c + 1

    max_keys_per_frame = max(frame_keys)
    min_keys_per_frame = min(frame_keys)
    avg_keys_per_frame = sum(frame_keys) / len(frame_keys)

    notable_frames = []

    for i in range(frame_max):
        frame_key_count = frame_keys[i]

        limit = max_keys_per_frame * .2
        if frame_key_count > 5:
            notable_frames.append(i)

    return notable_frames

def get_next_notable_frame(context, action, from_frame):
    notable_frames = get_notable_frames(action)
    for frame in notable_frames:
        if frame <= from_frame:
            continue
        else:
            return frame
    return 0

def get_previous_notable_frame(context, action, from_frame):
    latest = 0
    notable_frames = get_notable_frames(action)
    for frame in notable_frames:
        if frame < from_frame:
            latest = frame
        else:
            return latest
    return 0

def get_previous_notable_frame_from_start(context, action):
    return get_previous_notable_frame(context, action, context.scene.frame_start)

def get_previous_notable_frame_from_end(context, action):
    return get_previous_notable_frame(context, action, context.scene.frame_end)

def get_next_notable_frame_from_start(context, action):
    return get_next_notable_frame(context, action, context.scene.frame_start)

def get_next_notable_frame_from_end(context, action):
    return get_next_notable_frame(context, action, context.scene.frame_end)