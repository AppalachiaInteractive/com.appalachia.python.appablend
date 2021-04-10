import bpy

def unselect_hierarchy(obj):

    if obj.children is not None and len(obj.children) > 0:
        for child in obj.children:
            select_hierarchy(child)

    obj.select_set(state=False)

def select_hierarchy(obj):

    if obj.children is not None and len(obj.children) > 0:
        for child in obj.children:
            select_hierarchy(child)

    obj.select_set(state=True)

def delete_hierarchy(obj, include_actions=True):
    if not obj:
        return
    if obj.children and len(obj.children) > 0:
        for child in obj.children:
            delete_hierarchy(child)

    anim_data = obj.animation_data
    if anim_data and anim_data.action:
        anim_data.action.use_fake_user = False
        bpy.data.actions.remove(anim_data.action)
    bpy.data.objects.remove(obj, do_unlink=True)

def remove_child_relations(context, parent, clear_type='CLEAR_KEEP_TRANSFORM'):
    child_objects = []
    selections = []
    active_object = context.view_layer.objects.active

    for obj in context.selected_objects:
        selections.append(obj)
        obj.select_set(state=False)

    for child in parent.children:
        child_objects.append(child)
        child.select_set(state=True)
        context.view_layer.objects.active = child
        bpy.ops.object.parent_clear(type=clear_type)
        child.select_set(state=False)

    for obj in selections:
        obj.select_set(state=True)

    context.view_layer.objects.active = active_object

    return child_objects

def get_collection_hierarchy(collection):
    c = bpy.data.collections.get(collection)

    return c.all_objects
