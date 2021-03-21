import bpy, cspy
from bpy.types import Operator

class OPS_OPTION:    
    '''Register, Display in the info window and support the redo toolbar panel.'''
    REGISTER = 'REGISTER'

    '''Undo, Push an undo event (needed for operator redo).'''
    UNDO = 'UNDO'

    '''Grouped Undo, Push a single undo event for repeated instances of this operator.'''
    UNDO_GROUPED = 'UNDO_GROUPED'

    '''Blocking, Block anything else from using the cursor.'''
    BLOCKING = 'BLOCKING'

    '''Macro, Use to check if an operator is a macro.'''
    MACRO = 'MACRO'

    '''Grab Pointer, Use so the operator grabs the mouse focus, enables wrapping when continuous grab is enabled.'''
    GRAB_CURSOR = 'GRAB_CURSOR'

    '''Grab Pointer X, Grab, only warping the X axis.'''
    GRAB_CURSOR_X = 'GRAB_CURSOR_X'

    '''Grab Pointer Y, Grab, only warping the Y axis.'''
    GRAB_CURSOR_Y = 'GRAB_CURSOR_Y'

    '''Preset, Display a preset button with the operators settings.'''
    PRESET = 'PRESET'

    '''Internal, Removes the operator from search results.'''
    INTERNAL = 'INTERNAL'

class OPS_OPTIONS:
    UNDO = { OPS_OPTION.UNDO }
    UNDO_REGISTER = { OPS_OPTION.UNDO, OPS_OPTION.REGISTER }

class OPS_():
    bl_options = OPS_OPTIONS.UNDO_REGISTER
    bl_label = 'Label'
    bl_idname = 'ops.base_op'
    
    @classmethod
    def poll(cls, context):
        try:
            return cls.do_poll(context)
        except Exception as inst:
            print('{0}:  [do_poll]  {1}'.format(cspy.utils.get_logging_name(cls), inst))
            return False
    
    @classmethod
    def do_poll(cls, context):
        return True

    def finished(self):
        return {'FINISHED'}

    def cancelled(self):
        return {'CANCELLED'}

    def quit(self, context, active, mode):        
        cspy.utils.exit_mode(active, mode)
        return {'FINISHED'}
            
    def execute(self, context):
        returning = self.finished()

        try:
            use_global_undo = context.preferences.edit.use_global_undo
            context.preferences.edit.use_global_undo = False
            returning = self.do_execute(context)

            if returning is None:
                returning = self.finished()
        except Exception as inst:
            print('{0}:  [do_execute]  {1}'.format(cspy.utils.get_logging_name(self), inst))
            returning = self.cancelled()
        finally:
            context.preferences.edit.use_global_undo = use_global_undo

        return returning
    

class OPS_MODAL(OPS_):

    def do_draw(self, context, scene, layout, obj):        
        layout = self.layout        
        
        d = dir(self.properties)
        for attr in d:
            if attr == 'rna_type' or attr.startswith('bl_') or attr.startswith('_'):
                continue
            layout.prop(self, attr)

    def invoke(self, context, event):        
        scn = context.scene
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

