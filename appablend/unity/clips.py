from appablend.common.core.subtypes import *


def get_action_mode_clip(context, scene_clip):
    action_clip = scene_clip.action.unity_clips[scene_clip.name]
    return action_clip


def get_scene_mode_clip(context, action_clip):
    scene_clip = context.scene.all_unity_clips[action_clip.name]
    return scene_clip


def sync_with_action_mode(context):
    for scene_clip in context.scene.all_unity_clips:
        action_clip = get_action_mode_clip(context, scene_clip)
        scene_clip.copy_from(action_clip)


def sync_with_scene_mode(context):
    for scene_clip in context.scene.all_unity_clips:
        action_clip = get_action_mode_clip(context, scene_clip)
        action_clip.copy_from(scene_clip)


def sync_with_action_mode_clip(context, scene_clip):
    action_clip = get_action_mode_clip(context, scene_clip)
    scene_clip.copy_from(action_clip)


def sync_with_scene_mode_clip(context, action_clip):
    scene_clip = get_scene_mode_clip(context, action_clip)
    action_clip.copy_from(scene_clip)


def sync_with_clip(context, sync_from, sync_to):
    sync_to.copy_from(sync_from)

