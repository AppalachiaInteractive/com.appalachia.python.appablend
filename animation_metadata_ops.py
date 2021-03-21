import bpy, cspy
from bpy.types import Operator
from cspy.ops import OPS_OPTIONS, OPS_, OPS_MODAL
from cspy.polling import POLL
from cspy.animation_metadata import *

class AS_Split_Action_Via_Sheet(Operator, OPS_):
    """Split the current action using the provided sheet"""
    bl_idname = "ops.aa_split_action_via_sheet"
    bl_label = "Split Via Sheet"
    bl_icon = Constants.ICON_SHEET
    bl_options = {'UNDO'}

    @classmethod
    def do_poll(cls, context):
        obj = context.active_object

        if (obj is None or obj.animation_split is None or obj.animation_split_clips is None 
            or len(obj.animation_split_clips) == 0 or obj.animation_split.sheet_path == ''
            or obj.animation_split.action == ''):
            return False
        return True

    def do_execute(self, context):        
        
        obj = context.active_object
        animation_split = obj.animation_split

        animation_split.get_animation_sets(context)

        master_action = bpy.data.actions[animation_split.action]

        for clip in obj.animation_split_clips:
            clip.split_action(master_action)
        
        self.report({'INFO'}, 'Split {0} actions from animation sheet.'.format(len(obj.animation_split_clips)))       
        return {'FINISHED'}
