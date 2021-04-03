import bpy, cspy
from bpy.types import Operator
from cspy.ops import OPS_, OPS_DIALOG
from cspy.polling import POLL
from cspy.drivers import *

class DRV_OT_None(OPS_, Operator):
    """Integrates the empties above an armature into its bone chain."""
    bl_idname = 'drv.none'
    bl_label = 'Integrate Empties'

    @classmethod
    def do_poll(cls, context):        
        return True

    def do_execute(self, context):
        pass