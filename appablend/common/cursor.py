from appablend.common.utils.common import get_rotation_value


def set_cursor_from_matrix(context, matrix):
    cursor = context.scene.cursor

    l, _, _ = matrix.decompose()

    cursor.location = l

    rotation_prop, rotation = get_rotation_value(matrix, cursor.rotation_mode)

    setattr(cursor, rotation_prop, rotation)
