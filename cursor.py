import bpy
import cspy
import mathutils, math
from mathutils import Vector, Matrix, Quaternion, Euler
from cspy import iters, unity, unity_clips
from cspy.bones import *
from cspy.unity_clips import *
from cspy.utils import *

def set_cursor_from_matrix(context, matrix):
    cursor = context.scene.cursor

    l,_,_ = matrix.decompose()

    cursor.location = l

    rotation_prop, rotation = get_rotation_value(matrix, cursor.rotation_mode)

    setattr(cursor, rotation_prop, rotation)