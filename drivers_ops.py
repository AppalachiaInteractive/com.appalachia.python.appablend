import bpy, cspy
from bpy.types import Operator
from cspy.ops import OPS_, OPS_DIALOG
from cspy.polling import POLL
from cspy.drivers import *
from cspy.utils import *

class DRV_OT_update_dependencies(OPS_, Operator):
    """Integrates the empties above an armature into its bone chain."""
    bl_idname = 'drv.update_dependencies'
    bl_label = 'Update Dependencies'
    bl_icon = cspy.icons.FILE_REFRESH

    @classmethod
    def do_poll(cls, context):        
        return True

    def do_execute(self, context):
        for action in bpy.data.actions:
            for fcurve in action.fcurves:
                fcurve.data_path = fcurve.data_path
                fcurve.is_valid = True
        
        for collection in get_collections():
            for item in collection:
                if hasattr(item, 'animation_data') and item.animation_data:
                    for driver in item.animation_data.drivers:
                        driver.data_path = driver.data_path
                        driver.is_valid = True
