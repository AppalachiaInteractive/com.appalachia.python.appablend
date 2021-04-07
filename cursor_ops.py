import bpy, cspy
from bpy.types import Operator
from cspy.ops import OPS_, OPS_DIALOG
from cspy.polling import POLL
from cspy.actions import *
import math, mathutils
from mathutils import Matrix, Vector, Euler, Quaternion
from cspy.cursor import *

class CURSOR_OT_Set:
    bl_icon = cspy.icons.CANCEL

    @classmethod
    def do_poll(cls, context):
        return True

    def do_execute(self, context):
        cursor = context.scene.cursor
        matrix = self.exec(context, cursor)

        set_cursor_from_matrix(context, matrix)

        return {'FINISHED'}

class CURSOR_OT_set_world(CURSOR_OT_Set, OPS_, Operator):
    """Sets the cursor to the selected object's matrix"""
    bl_idname = "cursor.set_world"
    bl_label = "World"
    bl_icon = cspy.icons.WORLD
    
    def exec(self, context, cursor):
        return Matrix.Identity(4)

class CURSOR_OT_set_active(CURSOR_OT_Set, OPS_, Operator):
    """Sets the cursor to the selected object's matrix"""
    bl_idname = "cursor.set_active"
    bl_label = "Object"
    bl_icon = cspy.icons.OBJECT_DATA

    @classmethod
    def do_poll(cls, context):
        return context.active_object
    
    def exec(self, context, cursor):
        return context.active_object.matrix_world

class CURSOR_OT_set_active_bone(CURSOR_OT_Set, OPS_, Operator):
    """Sets the cursor to the selected object's matrix"""
    bl_idname = "cursor.set_active_bone"
    bl_label = "Bone"
    bl_icon = cspy.icons.BONE_DATA

    @classmethod
    def do_poll(cls, context):
        return context.active_pose_bone
    
    def exec(self, context, cursor):
        return context.active_pose_bone.matrix




