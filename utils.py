import bpy
import sys
import os, traceback

traceback_template = '''[EXCP] [%(note)s] File "%(filename)s", line %(lineno)s, in %(name)s %(type)s: %(message)s\n'''

def print_exception(note):
    exc_type, exc_value, exc_traceback = sys.exc_info() # most recent (if any) by default

    traceback_details = {
                         'note'    : note,
                         'filename': exc_traceback.tb_frame.f_code.co_filename,
                         'lineno'  : exc_traceback.tb_lineno,
                         'name'    : exc_traceback.tb_frame.f_code.co_name,
                         'type'    : exc_type.__name__,
                         'message' : str(exc_value), # or see traceback._some_str()
                        }

    del(exc_type, exc_value, exc_traceback) 

    print('-'*20)
    print(traceback.format_exc()) 
    print(traceback_template % traceback_details) 
    print()

def copy_from_to(f, t):
    try:
        from_props = set(dir(f))
        to_props = set(dir(t))

        common_props = [prop for prop in from_props.intersection(to_props) if (
            not prop.startswith('_') and            
            not prop.startswith("bl_") and
            not prop.startswith("rna_") and
            not prop in set(['int','float','bool','int_array','float_array','bool_array']) and
            not callable(getattr(f, prop))
        )]

        for prop in common_props:
            val = getattr(f, prop)

            copy = getattr(val, 'copy_from', None)

            if copy and callable(copy):
                val_to = getattr(t, prop)
                copy_to = getattr(val_to, 'copy_from', None)

                copy_to(val)

            else:
                setattr(t, prop, val)
    except Exception as e:
        namef = getattr(f, 'name', str(f))
        namet = getattr(t, 'name', str(t))

        print('copy_from_to: [{0}] to [{1}]: {2}'.format(namef, namet, e))
        raise

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

    enums = []
    for description in enum_items:
        key = enum_items[description]
        item = (key, description, description)
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