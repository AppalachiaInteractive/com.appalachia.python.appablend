import bpy

MODE_EDIT = ['EDIT_ARMATURE', 'EDIT']
MODE_POSE = ['POSE', 'POSE']
MODE_OBJECT = ['OBJECT', 'OBJECT']

def enter_mode_simple(new_mode):
    return enter_mode(bpy.context.active_object, new_mode, False)

def enter_mode(new_active_object, new_mode, unselect_current=True):

    if bpy.context.active_object == new_active_object and bpy.context.mode == new_mode:
        return new_active_object, new_mode

    print('Entering {0} ({1})'.format(new_mode, new_active_object.name))
    previous_active_object = bpy.context.view_layer.objects.active
    previous_active_object_mode = bpy.context.mode if not previous_active_object else previous_active_object.mode

    new_active_object_mode = new_mode
    
    if new_active_object:
        new_active_object_mode = new_active_object.mode

    if previous_active_object and previous_active_object != new_active_object and unselect_current:
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        previous_active_object.select_set(False)

    new_active_object.select_set(True)

    if new_active_object:
        new_active_object_mode = new_active_object.mode

    if previous_active_object != new_active_object:
        bpy.context.view_layer.objects.active = new_active_object

    if new_active_object_mode != new_mode:
        #print(new_active_object_mode, new_mode)
        bpy.ops.object.mode_set(mode=new_mode, toggle=False)

    return previous_active_object, previous_active_object_mode


def exit_mode(new_active_object, new_mode, unselect_current=True):
    previous_active_object = bpy.context.view_layer.objects.active
    previous_active_object_mode = previous_active_object.mode

    print('Exiting {0} ({1}). Returning to {2} ({3})'.format(previous_active_object_mode, 'NONE' if not previous_active_object else previous_active_object.name, new_mode, 'NONE' if not new_active_object else new_active_object.name))

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

def enter_mode_if(MODE, obj):    
    entered = False
    check = bpy.context.mode != MODE[0]
    active = None
    mode = ''

    if check:
        entered = True
        active, mode = enter_mode(obj, MODE[1])
    return entered, active, mode

def exit_mode_if(entered, active, mode):   
    if entered and bpy.context.mode != mode:
        exit_mode(active, mode)
