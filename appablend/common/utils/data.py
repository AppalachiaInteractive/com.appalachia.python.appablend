import bpy


def purge_unused():
    x = {"FINISHED"}
    while "FINISHED" in x:
        x = bpy.ops.outliner.orphans_purge()


def get_collections():

    import collections

    colls = dir(bpy.data)
    for coll in colls:
        if callable(coll):
            continue
        if coll.startswith("_") or coll.startswith("is_") or coll.startswith("bl_"):
            continue

        collection_eval_string = "bpy.data.{0}".format(coll)
        collection = eval(collection_eval_string)

        if not hasattr(collection, "__iter__"):
            continue

        yield collection
