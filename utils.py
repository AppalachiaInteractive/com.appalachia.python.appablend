import bpy

def get_logging_name(obj):
    try:

        if obj is None:
            return 'NoneType'
        if hasattr(obj, '__name__'):
            return obj.__name__
        t = type(obj)
        if hasattr(t,'__name__'):
            return t.__name__
    except:
        return 'ERROR EVALUATING TYPE'

    return 'UNKNOWN'

def create_enum(enum_items):
        keys = set()
        for enum_item_key in enum_items:
            keys.add(enum_item_key)

        enums = []
        for key in keys:
            item = (key, key.capitalize(), key.capitalize())
            enums.append(item)

        return enums

def create_enum_dict(enum_items):
        keys = set()
        for enum_item_key in enum_items:
            key = enum_items[enum_item_key]
            keys.add(key)

        enums = []
        for key in keys:
            item = (key, '', '')
            enums.append(item)

        return enums

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

def enter_mode(new_active_object, new_mode, unselect_current=True):
    print('Entering mode {0} with active object {1}'.format(new_mode, new_active_object.name))
    previous_active_object = bpy.context.view_layer.objects.active
    previous_active_object_mode = previous_active_object.mode

    new_active_object_mode = new_active_object.mode

    if previous_active_object is not None and previous_active_object != new_active_object and unselect_current:
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        previous_active_object.select_set(False)

    new_active_object.select_set(True)

    new_active_object_mode = new_active_object.mode

    if previous_active_object != new_active_object:
        bpy.context.view_layer.objects.active = new_active_object

    if new_active_object_mode != new_mode:
        print(new_active_object_mode, new_mode)
        bpy.ops.object.mode_set(mode=new_mode, toggle=False)

    return previous_active_object, previous_active_object_mode


def exit_mode(new_active_object, new_mode, unselect_current=True):
    previous_active_object = bpy.context.view_layer.objects.active
    previous_active_object_mode = previous_active_object.mode

    print('Exiting mode {0} with active object {1}'.format(previous_active_object_mode, previous_active_object.name))
    print('Returning to mode {0} with active object {1}'.format(new_mode, new_active_object.name))

    new_active_object_mode = new_active_object.mode

    if previous_active_object is not None and previous_active_object != new_active_object and unselect_current:
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        previous_active_object.select_set(False)

    new_active_object.select_set(True)

    if previous_active_object != new_active_object:
        bpy.context.view_layer.objects.active = new_active_object

    if new_active_object_mode != new_mode:
        bpy.ops.object.mode_set(mode=new_mode, toggle=False)

    return previous_active_object, previous_active_object_mode

def get_rna_and_path(data_path):

    parts = split_path(data_path)
    path = parts[len(parts)-1].strip('.')
    rna = data_path.replace(path, '').strip('.')

    return rna, path

def split_path(data_path):
    '''
    Split a data_path into parts
    '''
    if not data_path:
        return []

    # extract names from data_path
    names = data_path.split('"')[1::2]

    data_path_no_names = ''.join(data_path.split('"')[0::2])

    # segment into chunks
    # ID props will be segmented by replacing ][ with ].[
    data_chunks = data_path_no_names.replace('][', '].[').split('.')

    # probably regex should be used here and things put into dictionary
    # so it's clear what chunk is what
    # depends of use case, the main idea is to extract names, segment, then put back

    # put names back into chunks where [] are
    for id, chunk in enumerate(data_chunks):
        # print('{0}: {1}'.format(id, chunk))

        if chunk.find('[]') > 0 or chunk == '[]':
            recovered_name = names.pop(0)

            # print('{0}: putting name {1} back into chunk'.format(id, recovered_name))
            data_chunks[id] = chunk.replace('[]', '["' + recovered_name + '"]')

    return data_chunks


# Right click functions and operators
def dump(obj, text):
    print('-'*40, text, '-'*40)
    for attr in dir(obj):
        if hasattr( obj, attr ):
            print( "obj.%s = %s" % (attr, getattr(obj, attr)))