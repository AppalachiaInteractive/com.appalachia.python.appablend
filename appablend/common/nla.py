from typing import List, Tuple

import bpy
from bpy.types import Action, NlaStrip, NlaTrack


def get_selected_strips() -> List[NlaStrip]:
    try:
        selected_strips = []

        for obj in bpy.context.selectable_objects:
            if obj and obj.animation_data and obj.animation_data.nla_tracks:
                strip: NlaStrip
                for strip in obj.animation_data.nla_tracks.active.strips:
                    if strip.select:
                        selected_strips.append(strip)
    except AttributeError:
        selected_strips = []
    return selected_strips


def get_nla_track(obj) -> NlaTrack:
    if not obj or not obj.animation_data or not obj.animation_data.nla_tracks:
        return None
    tracks = obj.animation_data.nla_tracks

    if len(tracks) == 0:
        return tracks.new()

    for track in tracks:
        if track.select:
            return track

    return tracks[0]


def add_bind_pose_for_strip_population(context, track, padding=5) -> Tuple[int, Action]:
    start = 1
    firsts = [action for action in bpy.data.actions if "bind" in action.name.lower()]
    first = None
    if firsts:
        first = firsts[0]
        track.strips.new(first.name, start, first)
        start += first.frame_range[1] + padding

    return start, first


def clear_nla_track(track) -> None:
    for strip in reversed(track.strips):
        track.strips.remove(strip)


def clear_nla_tracks(obj) -> None:
    for track in obj.animation_data.nla_tracks:
        clear_nla_track(track)
