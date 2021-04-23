import bpy
from bpy.props import *

C = bpy.context
D = bpy.data
number_tokens = []
side_pairs = [
    ("l", "r"),
    ("L", "R"),
    ("Left", "Right"),
    ("left", "right"),
    ("LEFT", "RIGHT"),
]
seperators = {".", " ", "-", "_"}

tokens_start = []
tokens_mid = []
tokens_mid2 = []
tokens_end = []

format_start = "{0}{1}"
format_mid = "{1}{0}."
format_mid2 = "{1}{0}{1}"
format_end = "{1}{0}"


def initialize():

    if len(number_tokens) == 0:
        for x in range(0, 10):
            for y in range(0, 10):
                for z in range(0, 10):
                    number_token = ".{0}{1}{2}".format(x, y, z)
                    number_tokens.append(number_token)


def replace_unnecessary_numbers(object):

    initialize()

    for number_token in number_tokens:
        if number_token not in object.name:
            continue

        test_name = object.name.replace(number_token, "")

        if test_name in bpy.data.objects:
            continue
        else:
            # print('{0} >>> {1}'.format(object.name, test_name))
            object.name = test_name
            break


def replace_characters_str(str, old, new):
    return str.replace(old, new)


def replace_characters(object, old, new):
    object.name = object.name.replace(old, new)


def replace_characters_id(object, old, new):
    object.id = object.id.replace(old, new)


def replace_characters_path(object, old, new):
    object.path = object.path.replace(old, new)


def traverse_collections_and_replace(collection, old, new):
    for coll in collection.children:
        traverse_collections_and_replace(coll, old, new)

    replace_characters(collection, old, new)
    replace_unnecessary_numbers(collection)


### prefix characters in a path
def prefix_path(r, prefix_value):
    if not hasattr(r, "path"):
        return
    if not r.path.startswith(prefix_value):
        r.path = "{0}{1}".format(prefix_value, r.path)


### prefix characters in a name
def prefix_name(r, prefix_value):
    if not hasattr(r, "name"):
        return
    if not r.name.startswith(prefix_value):
        r.name = "{0}{1}".format(prefix_value, r.name)


### replaces characters in a path
def replace_in_path(r, replace_old, replace_new):
    if not hasattr(r, "path"):
        return
    r.path = r.path.replace(replace_old, replace_new)


### replaces characters in a name
def replace_in_name(r, replace_old, replace_new):
    if not hasattr(r, "name"):
        return
    r.name = r.name.replace(replace_old, replace_new)


### syncs particle system settings names up with their objects:
def sync_particle_settings_names(o):
    if o is None:
        return
    if o.particle_systems is None:
        return
    if len(o.particle_systems) != 1:
        return
    ps = o.particle_systems[0]
    if ps.settings is None:
        return
    if ps.settings.users > 1:
        return
    ps.settings.name = o.name


### syncs mesh names up with their objects:
def sync_mesh_names(o):
    if o is None:
        return
    if o.data is None:
        return
    if o.type != "MESH":
        return
    if o.data.users > 1:
        return
    o.data.name = o.name


### syncs armature names up with their objects:
def sync_armature_names(o):
    if o is None:
        return
    if o.data is None:
        return
    if o.type != "ARMATURE":
        return
    if o.data.users > 1:
        return
    o.data.name = o.name


### syncs data names up with their objects:
def sync_names(o):
    ### syncs data names up with their objects:
    if o is None:
        return

    sync_particle_settings_names(o)
    sync_mesh_names(o)
    sync_armature_names(o)


def flip_side_name(from_name):
    t = len(seperators) * len(side_pairs)

    if (
        len(tokens_start) != t
        or len(tokens_mid) != t
        or len(tokens_mid2) != t
        or len(tokens_end) != t
    ):
        tokens_start.clear()
        tokens_mid.clear()
        tokens_mid2.clear()
        tokens_end.clear()
        for sep in seperators:
            for pair in side_pairs:
                tokens_start.append(
                    (
                        format_start.format(pair[0], sep),
                        format_start.format(pair[1], sep),
                    )
                )
                tokens_mid.append(
                    (format_mid.format(pair[0], sep), format_mid.format(pair[1], sep))
                )
                tokens_mid2.append(
                    (format_mid2.format(pair[0], sep), format_mid2.format(pair[1], sep))
                )
                tokens_end.append(
                    (format_end.format(pair[0], sep), format_end.format(pair[1], sep))
                )

    for token in tokens_start:
        if from_name.startswith(token[0]):
            return from_name.replace(token[0], token[1])
        if from_name.startswith(token[1]):
            return from_name.replace(token[1], token[0])
    for token in tokens_mid:
        if token[0] in from_name:
            return from_name.replace(token[0], token[1])
        if token[1] in from_name:
            return from_name.replace(token[1], token[0])
    for token in tokens_mid2:
        if token[0] in from_name:
            return from_name.replace(token[0], token[1])
        if token[1] in from_name:
            return from_name.replace(token[1], token[0])
    for token in tokens_end:
        if from_name.endswith(token[0]):
            return from_name.replace(token[0], token[1])
        if from_name.endswith(token[1]):
            return from_name.replace(token[1], token[0])

    return from_name


def get_logging_name(obj):
    try:

        if obj is None:
            return "NoneType"
        if hasattr(obj, "__name__"):
            return obj.__name__
        t = type(obj)
        if hasattr(t, "__name__"):
            return t.__name__
    except:
        return "ERROR EVALUATING TYPE"

    return "UNKNOWN"
