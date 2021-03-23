import bpy, cspy
from bpy.types import Operator
from cspy.ops import OPS_, OPS_DIALOG
from cspy.polling import POLL
from cspy.armature import *

class AM_Integrate_Empties(OPS_, Operator):
    """Integrates the empties above an armature into its bone chain."""
    bl_idname = 'ops.am_integrate_empties'
    bl_label = 'Integrate Empties'

    @classmethod
    def do_poll(cls, context):
        obj = context.active_object
        if obj is None:
            return False
        if obj.type != 'ARMATURE':
            return False
        if obj.parent is None:
            return False
        if obj.parent.type != 'EMPTY':
            return False
        return True

    def do_execute(self, context):
        cls = OPS_
        armature = context.active_object
        armature_name = armature.name

        cspy.actions.group_actions_by_bone()
        bpy.ops.view3d.snap_cursor_to_selected()

        armature = bpy.data.objects[armature_name]
        to_rest_position(armature)

        tobj = armature

        parents = []
        parent_names = []

        while tobj.parent is not None:
            tobj.animation_data.action = None
            parents.append(tobj.parent)
            parent_names.append(tobj.parent.name)
            tobj = tobj.parent

        def path_check(data_path):
            return data_path == 'rotation_euler'

        for parent_name in parent_names:
            pobj = bpy.data.objects[parent_name]
            if pobj.rotation_mode != 'QUATERNION':
                cspy.actions.update_rotations_to_quat(pobj, path_check, '')

        if armature.rotation_mode != 'QUATERNION':
            cspy.actions.update_rotations_to_quat(armature, path_check, '')

        bpy.ops.object.rotation_clear(clear_delta=False)

        active, mode = cspy.utils.enter_mode(armature, 'POSE')
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.transforms_clear()

        armature_matrix_world = armature.matrix_world.copy()
        armature_matrix_local = armature.matrix_local.copy()

        last = parents[len(parents) - 1]
        last_scale_max = max(last.scale)
        parents.remove(last)
        parent_names.remove(last.name)

        child_objects = cspy.hierarchy.remove_child_relations(context, armature)

        parentless_bone_names = []

        for bone in armature.data.bones:
            if bone.parent is None:
                parentless_bone_names.append(bone.name)

        matrices_world = {}

        for bone in armature.data.bones:
            matrices_world[bone.name] = armature_matrix_world @ bone.matrix_local

        cspy.utils.enter_mode(armature, cspy.bones.EDIT_MODE_SET)

        arma_bone_name = armature.name
        arma_bone = cspy.bones.create_or_get_bone(armature, arma_bone_name)
        arma_bone.tail /= last_scale_max

        matrices_world[arma_bone_name] = armature_matrix_world

        for parentless_bone_name in parentless_bone_names:
            cspy.bones.set_bone_parenting(armature, parentless_bone_name, arma_bone_name, False)
        added_bone_names = []

        for parent_name in parent_names:
            b = cspy.bones.create_or_get_bone(armature, parent_name)
            b.tail /= last_scale_max
            added_bone_names.append(b.name)

        if len(added_bone_names) > 0:
            child_name = arma_bone_name
            parent_name = added_bone_names[0]

            cspy.bones.set_bone_parenting(armature, child_name, parent_name, False)

            for added_bone_name in added_bone_names:
                child_name = parent_name
                parent_name = added_bone_name
                if child_name != parent_name:
                    cspy.bones.set_bone_parenting(armature, child_name, parent_name, False)

                added_matrix_obj = bpy.data.objects[added_bone_name]
                matrices_world[added_bone_name] = added_matrix_obj.matrix_world.copy()

        context.view_layer.objects.active = armature

        for bone_name in matrices_world.keys():
            matrix = matrices_world[bone_name]
            cspy.bones.set_edit_bone_matrix_world(armature, bone_name, matrix)

        cspy.bones.shift_bones(armature, armature_matrix_local)

        armature.parent = None
        armature.matrix_world = last.matrix_world.copy()

        cspy.utils.enter_mode(armature, 'POSE')
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.transforms_clear()

        cspy.utils.exit_mode(active, mode)
        to_pose_position(armature)

        new_armature_name = last.name

        bpy.data.objects.remove(last)

        for parent_name in parent_names:
            p = bpy.data.objects[parent_name]
            bpy.data.objects.remove(p)

        old_armature_name = armature.name
        armature.name = new_armature_name

        for child_obj in child_objects:
            matrix = child_obj.matrix_world.copy()
            child_obj.parent = armature
            child_obj.matrix_world = matrix

        cspy.actions.integrate_empties_action_into_bones(parent_names, arma_bone_name)

        for parent_name in parent_names:
            for action in [action for action in bpy.data.actions if action.name.startswith(parent_name)]:
                bpy.data.actions.remove(action)

        for action in [action for action in bpy.data.actions if action.name.startswith(new_armature_name)]:
            bpy.data.actions.remove(action)

        for action in [action for action in bpy.data.actions if action.name.startswith(old_armature_name)]:
            action.name = action.name.replace(old_armature_name, new_armature_name)

        cspy.fcurves.shift_fcurve_channels(new_armature_name, arma_bone_name, armature_matrix_local.inverted())

        cspy.actions.group_actions_by_bone()

        armature.rotation_mode = 'XYZ'

        message = 'Added {0} bones to armature to account for empties, which were removed.'.format(len(added_bone_names))
        self.report({'INFO'}, message)
        return {'FINISHED'}
  