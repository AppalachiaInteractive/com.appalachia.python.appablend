import bpy
import cspy
from cspy.imports import *
from cspy.ops import *

class IMPORTS_OT_import_directory(OPS_, Operator):
    """Imports the files in a directory"""
    bl_idname = "imports.import_directory"
    bl_label = "Import Directory"

    @classmethod
    def do_poll(cls, context):
        return len(bpy.data.actions) > 0 and context.scene.unity_settings.sheet_dir_path != ''

    def do_execute(self, context):
        obj = get_active_unity_object(context)
        scene = context.scene
        key_offset = 1

        path = bpy.path.abspath(scene.unity_settings.sheet_dir_path)

        for action in bpy.data.actions:
            action.unity_metadata.clip_index = 0

        UnityClipMetadata.parse_clip_files(context, path, key_offset)

        return {'FINISHED'}
