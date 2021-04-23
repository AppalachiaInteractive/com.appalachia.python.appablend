import bpy
from appablend.common.core.enums import icons
from appablend.common.core.subtypes import ST_StringProperty
from appablend.common.models.unity import update_clip_index_scene
from appablend.common.utils.enums import create_enum_dict

_MODES = {
    "Active Mode": "ACTIVE",
    "Target Mode": "TARGET",
    "Scene Mode": "SCENE",
}
_MODE_ENUM = create_enum_dict(_MODES)
_MODE_ENUM_DEF = "ACTIVE"


class UnitySettings(bpy.types.PropertyGroup):
    mode: bpy.props.EnumProperty(name="Mode", items=_MODE_ENUM, default=_MODE_ENUM_DEF)

    sheet_dir_path: bpy.props.StringProperty(
        name="Sheet Dir Path", subtype=ST_StringProperty.Subtypes.DIR_PATH
    )
    key_dir_path: bpy.props.StringProperty(
        name="Key Dir Path", subtype=ST_StringProperty.Subtypes.DIR_PATH
    )

    active_action: bpy.props.PointerProperty(
        type=bpy.types.Action, name="Active Action"
    )
    # active_clip: bpy.props.PointerProperty(type=UnityClipMetadata, name='Active Clip')
    clip_index: bpy.props.IntProperty(
        name="Unity Index", default=-1, min=-1, update=update_clip_index_scene
    )
    target_armature: bpy.props.PointerProperty(
        name="Target Armature", type=bpy.types.Object
    )

    draw_sheets: bpy.props.BoolProperty(name="Draw Sheets")
    draw_keyframes: bpy.props.BoolProperty(name="Draw Keyframes")
    draw_clips: bpy.props.BoolProperty(name="Draw Clips")
    draw_metadata: bpy.props.BoolProperty(name="Draw Clip Metadata")
    draw_root_motion: bpy.props.BoolProperty(name="Draw Root Motion")
    draw_frames: bpy.props.BoolProperty(name="Draw Frames")
    draw_pose: bpy.props.BoolProperty(name="Draw Pose")
    draw_operations: bpy.props.BoolProperty(name="Draw Delete")

    icon_unity = icons.FILE_3D
    icon_sheets = icons.FILE
    icon_keys = icons.DECORATE_KEYFRAME
    icon_all_clips = icons.SEQ_SEQUENCER
    icon_clips = icons.SEQ_STRIP_DUPLICATE
    icon_clip = icons.SEQUENCE
    icon_metadata = icons.MESH_DATA
    icon_root_motion = icons.CON_FOLLOWPATH
    icon_frames = icons.CAMERA_DATA
    icon_pose = icons.ARMATURE_DATA
    icon_operations = icons.GHOST_DISABLED
    icon_operation = icons.GHOST_ENABLED
