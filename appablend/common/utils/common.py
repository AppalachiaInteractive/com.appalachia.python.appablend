import sys
import traceback

import bpy

traceback_template = """[EXCP] [%(note)s] File "%(filename)s", line %(lineno)s, in %(name)s %(type)s: %(message)s\n"""


def print_exception(note):
    (
        exc_type,
        exc_value,
        exc_traceback,
    ) = sys.exc_info()  # most recent (if any) by default

    traceback_details = {
        "note": note,
        "filename": exc_traceback.tb_frame.f_code.co_filename,
        "lineno": exc_traceback.tb_lineno,
        "name": exc_traceback.tb_frame.f_code.co_name,
        "type": exc_type.__name__,
        "message": str(exc_value),  # or see traceback._some_str()
    }

    del (exc_type, exc_value, exc_traceback)

    print("-" * 20)
    print(traceback.format_exc())
    print(traceback_template % traceback_details)
    print()


def enumerate_reversed(L):
    for index in reversed(range(len(L))):
        yield index, L[index]


def select_by_name(name):
    obj = bpy.data.objects.get(name)
    if obj is not None:
        obj.select_set(True)


def select_by_names(names):
    for name in names:
        select_by_name(name)


def deselect_all():
    for obj in bpy.data.objects:
        if obj.select_get():
            obj.select_set(False)


def set_object_active(obj, unselect_previous=True):
    old = bpy.context.view_layer.objects.active
    bpy.context.view_layer.objects.active = obj
    obj.select_set(state=True)
    if unselect_previous and old and old != obj:
        old.select_set(state=False)
    return old


def get_rna_and_path(data_path):

    parts = split_path(data_path)
    path = parts[len(parts) - 1].strip(".")
    rna = data_path.replace(path, "").strip(".")

    return rna, path


def split_path(data_path):
    """
    Split a data_path into parts
    """
    if not data_path:
        return []

    # extract names from data_path
    names = data_path.split('"')[1::2]

    data_path_no_names = "".join(data_path.split('"')[0::2])

    # segment into chunks
    # ID props will be segmented by replacing ][ with ].[
    data_chunks = data_path_no_names.replace("][", "].[").split(".")

    # probably regex should be used here and things put into dictionary
    # so it's clear what chunk is what
    # depends of use case, the main idea is to extract names, segment, then put back

    # put names back into chunks where [] are
    for id, chunk in enumerate(data_chunks):
        # print('{0}: {1}'.format(id, chunk))

        if chunk.find("[]") > 0 or chunk == "[]":
            recovered_name = names.pop(0)

            # print('{0}: putting name {1} back into chunk'.format(id, recovered_name))
            data_chunks[id] = chunk.replace("[]", '["' + recovered_name + '"]')

    return data_chunks


# Right click functions and operators
def dump(obj, text):
    print("-" * 40, text, "-" * 40)
    for attr in dir(obj):
        if hasattr(obj, attr):
            print("obj.%s = %s" % (attr, getattr(obj, attr)))


def get_rotation_value(matrix, mode):
    _, r, _ = matrix.decompose()

    if mode == "QUATERNION":
        prop = "rotation_quaternion"
        value = r
    elif mode == "AXIS_ANGLE":
        prop = "rotation_axis_angle"
        r.to_axis_angle()
    elif mode == "XYZ":
        prop = "rotation_euler"
        value = r.to_euler("XYZ")
    elif mode == "XZY":
        prop = "rotation_euler"
        value = r.to_euler("XZY")
    elif mode == "YXZ":
        prop = "rotation_euler"
        value = r.to_euler("YXZ")
    elif mode == "YZX":
        prop = "rotation_euler"
        value = r.to_euler("YZX")
    elif mode == "ZXY":
        prop = "rotation_euler"
        value = r.to_euler("ZXY")
    elif mode == "ZYX":
        prop = "rotation_euler"
        value = r.to_euler("ZYX")

    return prop, value
