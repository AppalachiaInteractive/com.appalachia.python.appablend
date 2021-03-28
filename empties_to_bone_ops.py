import bpy, cspy
from bpy.types import Operator
from cspy import empties_to_bone
from cspy.ops import OPS_, OPS_DIALOG
from cspy.polling import POLL
from cspy.empties_to_bone import *

class EB_OPS_():
    @classmethod
    def poll_duplicate(cls, context):
        obj = context.active_object
        scn = context.scene

        return obj and obj.type == "EMPTY" and scn.eb_target_armature

    @classmethod
    def poll_create(cls, context):
        obj = context.active_object
        scn = context.scene

        return obj and obj.type == "EMPTY" and not scn.eb_target_armature

    @classmethod
    def poll_deconstruct(cls, context):
        obj = context.active_object
        scn = context.scene

        return obj and obj.type == "ARMATURE" and obj.animation_data and obj.animation_data.action

    @classmethod
    def poll_bake(cls, context):
        obj = context.active_object

        return obj and obj.type == "ARMATURE"

    def execute_duplicate(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False
        try:
            if not context.scene.eb_source_object:
                context.scene.eb_source_object = context.active_object

            cspy.empties_to_bone._duplicate_armature()
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        finally:
            context.preferences.edit.use_global_undo = use_global_undo
        return {'FINISHED'}

    def execute_create(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False
        try:
            if not context.scene.eb_source_object:
                context.scene.eb_source_object = context.active_object

            cspy.empties_to_bone._create_armature()
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        finally:
            context.preferences.edit.use_global_undo = use_global_undo
        return {'FINISHED'}

    def execute_deconstruct(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False
        try:
            if not context.scene.eb_source_object:
                context.scene.eb_source_object = context.active_object

            cspy.empties_to_bone._deconstruct_armature()
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        finally:
            context.preferences.edit.use_global_undo = use_global_undo
        return {'FINISHED'}

    def draw_bake(self, context):
        layout = self.layout
        layout.prop(self, 'bake_type', expand=True)
        row = layout.column().row()
        if self.bake_type == "STATIC":
            row.enabled = False
        row.prop(self, "frame_start", text="Frame Start")
        row.prop(self, "frame_end", text="Frame End")
        layout.separator()
        layout.prop(self, "clear_empties", text="Delete Empties")
        layout.prop(self, "clear_armature", text="Delete Armature")

    def invoke_bake(self, context, event, act=None):
        scn = context.scene
        if not act:
            if scn.eb_current_empty_action != "":
                act = bpy.data.actions.get(scn.eb_current_empty_action)

        if act:
            self.frame_start = act.frame_range[0]
            self.frame_end = act.frame_range[1]

        # Open dialog
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute_bake(self, context):
        if not context.scene.eb_source_object:
            scn.eb_source_object = context.active_object

        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False
        empties_list = []
        try:
            if self.bake_type == "STATIC":
                self.frame_start = context.scene.frame_current
                self.frame_end = context.scene.frame_current

            # Bake
            bake_anim(self, frame_start=self.frame_start, frame_end=self.frame_end, only_selected=False, bake_bones=True, bake_object=False, clear_constraints=True)

            # remove NOROT bones
            bpy.ops.object.mode_set(mode='EDIT')
            for ebone in bpy.context.active_object.data.edit_bones:
                if "_NOROT" in ebone.name:
                    empties_list.append(ebone.name.replace("_NOROT", ""))
                    delete_edit_bone(ebone)
            bpy.ops.object.mode_set(mode='OBJECT')

            # clear empties
            if self.clear_empties:
                for emp_name in empties_list:
                    emp = bpy.data.objects.get(emp_name)
                    if not emp:
                        continue
                    if emp.animation_data and emp.animation_data.action:
                        emp.animation_data.action.use_fake_user = False
                        bpy.data.actions.remove(emp.animation_data.action)
                    bpy.data.objects.remove(emp, do_unlink=True)

                tricky_bones = ["Root", "CG", "root", "ROOT"]
                for tricky_bone in tricky_bones:
                    root = bpy.data.objects.get(tricky_bone)
                    if root:
                        if root.animation_data and root.animation_data.action:
                            root.animation_data.action.use_fake_user = False
                            bpy.data.actions.remove(root.animation_data.action)
                        cspy.hierarchy.delete_hierarchy(root)

            if self.clear_armature:
                ar = bpy.context.active_object
                bpy.data.objects.remove(ar, do_unlink=True)

            cspy.data.purge_unused()
            if bpy.context.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        #except Exception as inst:
        #    print(inst)
        finally:
            context.preferences.edit.use_global_undo = use_global_undo
        return {'FINISHED'}

class EB_OPS_BAKE():
    bake_type: bpy.props.EnumProperty(items=(('ANIM', 'Anim', 'Bake animation'), ('STATIC', 'Static', 'Bake single pose')), description='Finalize the armature conversion by baking the current pose or animation')
    frame_start: bpy.props.IntProperty(default=0, description="First frame to bake from")
    frame_end: bpy.props.IntProperty(default=10, description="Last frame to bake to")
    clear_empties: bpy.props.BoolProperty(default=True, description="Delete the empties chain")
    clear_armature: bpy.props.BoolProperty(default=True, description="Delete the armature")

class EB_OT_duplicate_armature(OPS_, EB_OPS_, Operator):
    """Copy the base pose of the specified armature, and set the selected empties to bones"""
    bl_idname = "eb.duplicate_armature"
    bl_label = "duplicate_armature"

    @classmethod
    def do_poll(cls, context):
        return cls.poll_duplicate(context)

    def do_execute(self, context):
        return self.execute_duplicate(context)

class EB_OT_create_armature(OPS_, EB_OPS_, Operator):
    """Convert the selected empties to bones"""
    bl_idname = "eb.create_armature"
    bl_label = "create_armature"

    @classmethod
    def do_poll(cls, context):
        return cls.poll_create(context)

    def do_execute(self, context):
        return self.execute_create(context)

class BE_OT_deconstruct_armature(OPS_, EB_OPS_, Operator):
    """Convert the selected bones to empties"""
    bl_idname = "be.deconstruct_armature"
    bl_label = "deconstruct_armature"

    @classmethod
    def do_poll(cls, context):
        return cls.poll_deconstruct(context);

    def do_execute(self, context):
        return self.execute_deconstruct(context)

class EB_OT_bake_anim(EB_OPS_BAKE, EB_OPS_, OPS_DIALOG, Operator):
    """Bake bones animation"""
    bl_idname = "eb.bake_anim"
    bl_label = "Complete Armature"

    @classmethod
    def do_poll(cls, context):
        return cls.poll_bake(context)

    def invoke(self, context, event):
        return self.invoke_bake(context, event)

    def do_draw(self, context, scene, layout, obj):
        self.draw_bake(context)

    def do_execute(self, context):
        return self.execute_bake(context)

class EB_OT_deconstruct_duplicate_bake(EB_OPS_BAKE, EB_OPS_, OPS_DIALOG, Operator):
    """Deconstruct the armature, create empties, duplicate armature, bake"""
    bl_idname = "eb.deconstruct_duplicate_bake"
    bl_label = "Deconstruct Duplicate Bake"

    @classmethod
    def do_poll(cls, context):
        return cls.poll_deconstruct(context)

    def invoke(self, context, event):
        return self.invoke_bake(context, event, context.active_object.animation_data.action)

    def do_draw(self, context, scene, layout, obj):
        self.draw_bake(context)

    def do_execute(self, context):
        self.execute_deconstruct(context)
        self.execute_duplicate(context)
        return self.execute_bake(context)

class EB_OT_create_bake(EB_OPS_BAKE, EB_OPS_, OPS_DIALOG, Operator):
    """Create the armature and bake the animations"""
    bl_idname = "eb.create_bake"
    bl_label = "Create Bake"

    @classmethod
    def do_poll(cls, context):
        return cls.poll_create(context)

    def invoke(self, context, event):
        return self.invoke_bake(context, event)

    def do_draw(self, context, scene, layout, obj):
        self.draw_bake(context)

    def do_execute(self, context):
        self.execute_create(context)
        return self.execute_bake(context)

class EB_OT_duplicate_bake(EB_OPS_BAKE, EB_OPS_, OPS_DIALOG, Operator):
    """Duplicate the armature and bake the animations"""
    bl_idname = "eb.duplicate_bake"
    bl_label = "Duplicate Bake"

    @classmethod
    def do_poll(cls, context):
        return cls.poll_duplicate(context) and cls.poll_bake(context)

    def invoke(self, context, event):
        return self.invoke_bake(context, event)

    def do_draw(self, context, scene, layout, obj):
        self.draw_bake(context)

    def do_execute(self, context):
        self.execute_duplicate(context)
        return self.execute_bake(context)

class EB_OT_process_batch(EB_OPS_BAKE, EB_OPS_, OPS_, Operator):
    """Batch processing"""
    bl_idname = 'eb.eb_ot_process_batch'
    bl_label = "Batch Processing"

    @classmethod
    def do_poll(cls, context):
        scene = context.scene
        return ((scene.eb_target_type == 'FILE' and scene.eb_target_file != '') or
            (scene.eb_target_type == 'DIR' and scene.eb_target_dir != ''))

    def do_execute(self, context):
        scene = context.scene
        original_active_object = context.active_object
        scene.eb_target_action = None
        scene.eb_target_action_name = ''
        self.bake_type = 'ANIM'
        self.clear_empties = True
        self.clear_armature = True

        files = []

        if scene.eb_target_type == 'FILE':
            abs_path = cspy.files.abspath(scene.eb_target_file)
            files.append(abs_path)
        else:
            abs_path = cspy.files.abspath(scene.eb_target_dir)
            f = cspy.files.get_files_in_dir(abs_path, endswith='.fbx', case_sensitive=False)
            files.extend(f)

        for f in files:
            filename = cspy.files.filename(f)
            print(filename)

            scene.eb_target_action_name = filename

            cspy.imports.import_fbx(filepath=f, automatic_bone_orientation=True)

            for obj in bpy.context.selected_objects:
                if obj.name == 'Root':
                    bpy.data.objects.remove(obj)
                    continue
                if obj and not obj.parent:
                    scene.eb_source_object = obj

            obj = scene.eb_source_object

            self.frame_start = obj.animation_data.action.frame_range[0]
            self.frame_end = obj.animation_data.action.frame_range[1]

            if obj.type == 'ARMATURE':
                self.execute_deconstruct(context)

            self.execute_duplicate(context)
            self.execute_bake(context)

        cspy.utils.set_object_active(original_active_object)
        #original_active_object.animation_data.action = bpy.data.actions[0]
        return self.finished()
 