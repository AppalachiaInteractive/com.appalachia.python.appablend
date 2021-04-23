import bpy
from addon_utils import paths
from appablend.common.core import subtypes
from appablend.common.utils.enums import create_enum_dict

_MODES = {
    "Adjust At Animation Start": "START",
    "Adjust Every Frame": "EVERY",
}
MODE_ENUM = create_enum_dict(_MODES)
_MODE_ENUM_DEF = "START"


class ImportSettings(bpy.types.PropertyGroup):
    import_dir: bpy.props.StringProperty(
        name="Import Directory", subtype=subtypes.ST_StringProperty.Subtypes.DIR_PATH
    )

    import_recursive: bpy.props.BoolProperty(name="Import Recursive")

    maya_mode: bpy.props.EnumProperty(
        name="Mode", items=MODE_ENUM, default=_MODE_ENUM_DEF
    )
    maya_template: bpy.props.StringProperty(
        name="Maya Armature File", subtype=subtypes.ST_StringProperty.Subtypes.FILE_PATH
    )

    maya_import_dir: bpy.props.StringProperty(
        name="Maya Import Directory",
        subtype=subtypes.ST_StringProperty.Subtypes.DIR_PATH,
    )
    maya_import_recursive: bpy.props.BoolProperty(name="Maya Import Recursive")

    maya_rot_bone_name: bpy.props.StringProperty(name="Maya Rotation Bone")
    maya_rot_value: bpy.props.FloatVectorProperty(
        name="Maya Rotation Value",
        subtype=subtypes.ST_FloatVectorProperty.Subtypes.EULER,
    )
    maya_export_dir: bpy.props.StringProperty(
        name="Maya Export Directory",
        subtype=subtypes.ST_StringProperty.Subtypes.DIR_PATH,
    )
