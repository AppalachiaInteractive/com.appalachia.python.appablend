import bpy, cspy
from bpy.types import Operator
from cspy import utils, modes
import time
import inspect
import sys, os


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

class OPS_(Operator):
    bl_options = OPS_OPTIONS.UNDO_REGISTER
    bl_label = 'Label'
    bl_idname = 'ops.base_op'

    @classmethod
    def poll(cls, context):
        try:
            result = cls.do_poll(context)
            if callable(result):
                print('[EXCP] {0}:  [do_poll]  Must correct call [{1}]'.format(cspy.utils.get_logging_name(cls), result))
                return False
            return result
        except Exception as inst:
            utils.print_exception(inst, 'do_poll')
            return False

    @classmethod
    def do_poll(cls, context):
        return True

    def finished(self):
        return {'FINISHED'}

    def cancelled(self):
        return {'CANCELLED'}

    def quit(self, context, active, mode):
        modes.exit_mode(active, mode)
        return {'FINISHED'}

    def execute(self, context):
        returning = self.finished()

        try:
            use_global_undo = context.preferences.edit.use_global_undo
            context.preferences.edit.use_global_undo = False
            start = time.perf_counter()
            returning = self.do_execute(context)
            end = time.perf_counter()

            print('[PERF] {0}:  [do_execute]  {1}s'.format(cspy.utils.get_logging_name(self), end - start))

            if returning is None:
                returning = self.finished()
        except Exception:
            utils.print_exception('do_execute')
            returning = self.cancelled()
        finally:
            context.preferences.edit.use_global_undo = use_global_undo

        return returning


class OPS_DIALOG(OPS_):

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


class OPS_MODAL(OPS_):
    def __init__(self):
        pass

    def __del__(self):
        pass

    def running_modal(self):
        return {'RUNNING_MODAL'}

    def execute(self, context):
        return self.finished()

    def modal(self, context, event):
        try:
            if self.do_cancel(context, event):
                return self.cancelled()
        except Exception:
            utils.print_exception('do_cancel')
            return self.cancelled()

        try:
            if self.do_continue(context, event):
                try:
                    self.do_iteration(context, event)
                except Exception:
                    utils.print_exception('do_iteration')
                    return self.cancelled()

                return self.running_modal()
        except Exception:
            utils.print_exception('do_continue')
            return self.cancelled()

        try:
            self.do_end(context, event)
        except Exception:
            utils.print_exception('do_end')
            return self.cancelled()

        return self.finished()

    def invoke(self, context, event):
        self.do_start(context, event)
        context.window_manager.modal_handler_add(self)
        return self.running_modal()

    def do_cancel(self, context, event):
        c = False
        return c

    def do_continue(self, context, event):
        return False

    def do_iteration(self, context, event):
        pass

    def do_start(self, context, event):
        pass

    def do_end(self, context, event):
        pass
    
    
    
    