import bpy, cspy
from bpy.types import Operator
from cspy.ops import OPS_, OPS_DIALOG
from cspy.polling import DOIF
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

class CURSOR_OT_set_target(CURSOR_OT_Set, OPS_, Operator):
    """Sets the cursor to the target's matrix"""
    bl_idname = "cursor.set_target"
    bl_label = "Target"
    bl_icon = cspy.icons.TRACKER

    target_name: bpy.props.StringProperty(name='Target Name')

    @classmethod
    def do_poll(cls, context):
        return True 
    
    def exec(self, context, cursor):
        obj = bpy.data.objects.get(self.target_name)

        return obj.matrix_world

class CURSOR_OT_component:
    def get_matrix(self, context, current_matrix, new_matrix, axis_index):
        loc, rot, _ = current_matrix.decompose()
        nloc, nrot, _ = new_matrix.decompose()

        loc[axis_index] = nloc[axis_index]
        out_matrix = Matrix.Translation(loc) @ rot.to_matrix().to_4x4()
        return out_matrix

class CURSOR_OT_set_x_0(CURSOR_OT_Set, OPS_, Operator):
    """Sets the cursor to the selected object's matrix"""
    bl_idname = "cursor.set_x_0"
    bl_label = "X 0"
    bl_icon = cspy.icons.EVENT_X
    
    def exec(self, context, cursor):
        current = cursor.matrix
        loc, rot, _ = current.decompose()
        loc.x = 0
        new_matrix = Matrix.Translation(loc) @ rot.to_matrix().to_4x4()

        return new_matrix
    
