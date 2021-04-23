import bpy
from appablend.common.basetypes.ops import OPS_
from appablend.common.core.enums import icons
from appablend.common.cursor import set_cursor_from_matrix
from bpy.types import Operator
from mathutils import Matrix


class CURSOR_OT_Set:
    bl_icon = icons.CANCEL

    @classmethod
    def do_poll(cls, context):
        return True

    def do_execute(self, context):
        cursor = context.scene.cursor
        matrix = self.exec(context, cursor)

        set_cursor_from_matrix(context, matrix)

        return {"FINISHED"}


class CURSOR_OT_set_world(CURSOR_OT_Set, OPS_, Operator):
    """Sets the cursor to the selected object's matrix"""

    bl_idname = "cursor.set_world"
    bl_label = "World"
    bl_icon = icons.WORLD

    def exec(self, context, cursor):
        return Matrix.Identity(4)


class CURSOR_OT_set_active(CURSOR_OT_Set, OPS_, Operator):
    """Sets the cursor to the selected object's matrix"""

    bl_idname = "cursor.set_active"
    bl_label = "Object"
    bl_icon = icons.OBJECT_DATA

    @classmethod
    def do_poll(cls, context):
        return context.active_object

    def exec(self, context, cursor):
        return context.active_object.matrix_world


class CURSOR_OT_set_active_bone(CURSOR_OT_Set, OPS_, Operator):
    """Sets the cursor to the selected object's matrix"""

    bl_idname = "cursor.set_active_bone"
    bl_label = "Bone"
    bl_icon = icons.BONE_DATA

    @classmethod
    def do_poll(cls, context):
        return context.active_pose_bone

    def exec(self, context, cursor):
        return context.active_pose_bone.matrix


class CURSOR_OT_set_target(CURSOR_OT_Set, OPS_, Operator):
    """Sets the cursor to the target's matrix"""

    bl_idname = "cursor.set_target"
    bl_label = "Target"
    bl_icon = icons.TRACKER

    target_name: bpy.props.StringProperty(name="Target Name")

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
    bl_icon = icons.EVENT_X

    def exec(self, context, cursor):
        current = cursor.matrix
        loc, rot, _ = current.decompose()
        loc.x = 0
        new_matrix = Matrix.Translation(loc) @ rot.to_matrix().to_4x4()

        return new_matrix
