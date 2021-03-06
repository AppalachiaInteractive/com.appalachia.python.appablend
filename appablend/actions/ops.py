import bpy
from appablend.actions.core import *
from appablend.common.actions import *
from appablend.common.basetypes.ops import OPS_
from appablend.common.bones import get_bone_data_path, remove_bones
from appablend.common.core.polling import DOIF
from appablend.common.utils import iters
from bpy.types import Operator


class ACT_Single_Action_Op:
    @classmethod
    def do_poll(cls, context):
        return DOIF.ACTIVE.HAS.ACTION(context)

    def do_execute(self, context):
        obj = context.active_object
        if obj and obj.animation_data:
            original_action = obj.animation_data.action

        self.exec(context, context.active_object.animation_data.action)

        if original_action:
            obj.animation_data.action = original_action

        return {"FINISHED"}


class ACT_Multiple_Action_Op:
    @classmethod
    def do_poll(cls, context):
        return DOIF.DATA.ACTIONS(context)

    def do_execute(self, context):
        obj = context.active_object
        if obj and obj.animation_data:
            original_action = obj.animation_data.action

        self.start(context)

        for action in bpy.data.actions:
            self.exec(context, action)

        self.finish(context)

        if original_action:
            obj.animation_data.action = original_action

        return {"FINISHED"}

    def start(self, context):
        pass

    def finish(self, context):
        pass


class ACT_BAKE:
    def exec(self, context, action):
        obj = context.active_object
        scene = context.scene
        selected_bone_names = [bone.name for bone in obj.data.bones if bone.select]

        obj.animation_data.action = action
        deselect_all_frames(action)

        scene.frame_start = action.frame_range[0]
        scene.frame_end = action.frame_range[1]
        scene.frame_current = scene.frame_start

        bpy.ops.nla.bake(
            frame_start=scene.frame_start,
            frame_end=scene.frame_end,
            step=1,
            only_selected=True,
            visual_keying=True,
            clear_constraints=False,
            clear_parents=False,
            use_current_action=True,
            bake_types={"POSE"},
        )

        select_all_frames(action)
        sample_fcurve(action)
        deselect_all_frames(action)
        decorate_curves(action)

    def finish(self, context):
        obj = context.active_object
        for bone in obj.pose.bones:
            if not bone.select:
                continue
            for c in reversed(bone.constraints):
                print("[{1}]: Removed constraint {0}".format(c, bone.name))
                bone.constraints.remove(c)


class ACT_OT_bake_selected_to_action(ACT_BAKE, ACT_Single_Action_Op, OPS_, Operator):
    """Bake selected bones to current action"""

    bl_idname = "nla.bake_selected_to_action"
    bl_label = "Bake Selected To Action"

    @classmethod
    def do_poll(cls, context):
        c = context
        return (
            ACT_Single_Action_Op.do_poll(context)
            and DOIF.ACTIVE.TYPE.IS_ARMATURE(c)
            and DOIF.ACTIVE.HAS.BONES(c)
            and DOIF.ACTIVE.HAS.BONES(context)
        )


class ACT_OT_bake_selected_to_action_all(
    OPS_, ACT_BAKE, ACT_Multiple_Action_Op, Operator
):
    """Bake selected bones to all actions"""

    bl_idname = "act.bake_selected_to_action_all"
    bl_label = "Bake (All)"

    @classmethod
    def do_poll(cls, context):
        return ACT_Multiple_Action_Op.do_poll(context) and DOIF.ACTIVE.HAS.BONES(
            context
        )


class ACT_OT_sample_fcurves(ACT_Single_Action_Op, OPS_, Operator):
    """Sample all fcurve frames"""

    bl_idname = "nla.sample_fcurves"
    bl_label = "Sample FCurves"

    def exec(context, action):
        select_all_frames(action)
        sample_fcurve(action)
        deselect_all_frames(action)
        return {"FINISHED"}


class ACT_OT_sample_fcurves_all(ACT_Multiple_Action_Op, OPS_, Operator):
    """Sample all fcurve frames"""

    bl_idname = "act.sample_fcurves_all"
    bl_label = "Sample (All)"

    def exec(self, context, action):
        select_all_frames(action)
        sample_fcurve(action)
        deselect_all_frames(action)
        return {"FINISHED"}


class ACT_OT_simplify_fcurves(ACT_Single_Action_Op, OPS_, Operator):
    """Simplify all fcruves by removing those which are unnecessary"""

    bl_idname = "act.simplify_fcurves"
    bl_label = "Simplify FCurves"

    def exec(self, context, action):
        simplify_fcurves(action)


class ACT_OT_simplify_fcurves_all(ACT_Multiple_Action_Op, OPS_, Operator):
    """Simplify all action fcurves by removing those which are unnecessary"""

    bl_idname = "act.simplify_fcurves_all"
    bl_label = "Simplify (All)"

    def exec(self, context, action):
        simplify_fcurves(action)


class ACT_OT_decorate_fcurves(ACT_Single_Action_Op, OPS_, Operator):
    """Decorate all fcurves by ensuring metadata and keyframe types are correct"""

    bl_idname = "act.decorate_fcurves"
    bl_label = "Decorate FCurves"

    def exec(self, context, action):
        decorate_curves(action)


class ACT_OT_decorate_fcurves_all(ACT_Multiple_Action_Op, OPS_, Operator):
    """Decorate all action fcurves by ensuring metadata and keyframe types are correct"""

    bl_idname = "act.decorate_fcurves_all"
    bl_label = "Decorate (All)"

    def exec(self, context, action):
        decorate_curves(action)


class ACT_OT_clean_fcurves(ACT_Single_Action_Op, OPS_, Operator):
    """Cleans fcurves with the _NOROT or 'Action Bake' names"""

    bl_idname = "act.clean_fcurves"
    bl_label = "Clean FCurves"

    def exec(self, context, action):
        clean_fcurves(action)
        return {"FINISHED"}


class ACT_OT_clean_fcurves_all(ACT_Multiple_Action_Op, OPS_, Operator):
    """Cleans fcurves with the _NOROT or 'Action Bake' names"""

    bl_idname = "act.clean_fcurves_all"
    bl_label = "Clean (All)"

    def exec(self, context, action):
        clean_fcurves(action)
        return {"FINISHED"}


class ACT_OT_combine_all_actions(OPS_, Operator):
    """Combines all actions and updates relevant strip metadata"""

    bl_idname = "act.combine_all_actions"
    bl_label = "Combine All Actions"

    @classmethod
    def do_poll(cls, context):
        return DOIF.DATA.ACTIONS(context)

    def do_execute(self, context):
        obj = context.active_object

        padding = 10
        round_to_nearest = 10

        master_action_name = "MASTER"
        if master_action_name in bpy.data.actions:
            master_action = bpy.data.actions["MASTER"]

            master_action.unity_metadata.clips_protected = True
            master_action.unity_clips.clear()
            for group in reversed(master_action.groups):
                master_action.groups.remove(group)
            for fcurve in reversed(master_action.fcurves):
                master_action.fcurves.remove(fcurve)
            for marker in reversed(master_action.pose_markers):
                master_action.pose_markers.remove(marker)
        else:
            master_action = bpy.data.actions.new("MASTER")

        master_groups = master_action.groups
        master_curves = master_action.fcurves

        for action in bpy.data.actions:
            if (
                action == master_action
                or action.name.endswith("_Layer")
                or "PoseLib" in action.name
            ):
                continue

            start = master_action.frame_range[1]

            if start != 1:
                start += padding  # 47 + 10 = 57
                overlap = start % round_to_nearest  # 57 %  5 =  2
                offset = round_to_nearest - overlap  #  5 -  2 =  3
                start += offset  # 57 +  3 = 60  - clean frame start

            action_start = action.frame_range[0]

            start -= action_start
            print("{0}: {1}".format(action.name, start))

            for group in action.groups:
                master_group = master_groups.find(group.name)
                if not master_group:
                    master_group = master_groups.new(group.name)

            extreme_frames = set()

            if action.unity_clips:
                for unity_clip in action.unity_clips:
                    new_clip = master_action.unity_clips.add()
                    new_clip.copy_from(unity_clip)

                    new_clip.action = master_action

                    new_clip.frame_start += start
                    new_clip.frame_end += start
                    extreme_frames.add(new_clip.frame_start)
                    extreme_frames.add(new_clip.frame_end)

                    s = master_action.pose_markers.new(new_clip.name)
                    e = master_action.pose_markers.new("{0}.end".format(new_clip.name))
                    s.frame = new_clip.frame_start
                    e.frame = new_clip.frame_end

            for fc in action.fcurves:
                data_path = fc.data_path
                array_index = fc.array_index
                master_curve = master_curves.find(data_path, index=array_index)
                if not master_curve:
                    master_curve = master_curves.new(
                        data_path, index=array_index, action_group=fc.group.name
                    )

                kps = fc.keyframe_points
                kps_count = len(kps)
                for index, key in enumerate(kps):

                    f = start + key.co[0]
                    v = key.co[1]

                    insert_keyframe(
                        master_curve,
                        f,
                        v,
                        needed=False,
                        fast=True,
                        keyframe_type=key.type,
                    )

        for curve in master_action.fcurves:
            curve.update()

        return {"FINISHED"}


class ACT_OT_Action_Euler_To_Quaternion(OPS_, Operator):
    """Converts actions from euler to quaternions."""

    bl_idname = "ops.act_ot_action_euler_to_quaternion"
    bl_label = "Convert Eulers To Quaternions"

    @classmethod
    def do_poll(cls, context):
        acts = len(bpy.data.actions)
        return acts > 0

    def do_execute(self, context):
        def path_check(data_path):
            return data_path == "rotation_euler"

        for action in bpy.data.actions:
            if action.name.startswith(context.active_object.name):
                update_rotations_to_quat(context.active_object, path_check, "")

        return {"FINISHED"}


class ACT_OT_Group_Actions_By_Bone(OPS_, Operator):
    """Groups all action fcurves by the bones they affect."""

    bl_idname = "ops.act_ot_group_actions_by_bone"
    bl_label = "Group Actions By Bone"

    @classmethod
    def do_poll(cls, context):
        arms = len(bpy.data.armatures)
        acts = len(bpy.data.actions)

        return arms > 0 and acts > 0

    def do_execute(self, context):
        group_actions_by_bone()
        self.report({"INFO"}, "Grouped actions by bone!")
        return {"FINISHED"}


class ACT_OT_interpolation_mode(ACT_Single_Action_Op, OPS_, Operator):
    """Changes the interpolation mode for the active action (all keyframes)"""

    bl_idname = "act.interpolation_mode"
    bl_label = "Interpolation Mode"

    interpolation: bpy.props.StringProperty(name="Interpolation")

    def exec(self, context, action):
        change_interpolation(action, self.interpolation)
        return {"FINISHED"}


class ACT_OT_interpolation_mode_all(ACT_Multiple_Action_Op, OPS_, Operator):
    """Changes the interpolation mode for the all actions (all keyframes)"""

    bl_idname = "act.interpolation_mode_all"
    bl_label = "Interpolation Mode (All)"

    interpolation: bpy.props.StringProperty(name="Interpolation")

    def exec(self, context, action):
        change_interpolation(action, self.interpolation)
        return {"FINISHED"}


class ACT_OT_keyframe_type(ACT_Single_Action_Op, OPS_, Operator):
    """Changes the keyframe mode for the active action (all keyframes)"""

    bl_idname = "act.keyframe_type"
    bl_label = "Keyframe Mode"

    keyframe_type: bpy.props.StringProperty(name="Keyframe")

    def exec(self, context, action):
        change_keyframe_type(action, self.keyframe_type)
        return {"FINISHED"}


class ACT_OT_keyframe_type_all(ACT_Multiple_Action_Op, OPS_, Operator):
    """Changes the keyframe mode for the all actions (all keyframes)"""

    bl_idname = "act.keyframe_type_all"
    bl_label = "Keyframe Mode (All)"

    keyframe_type: bpy.props.StringProperty(name="Keyframe")

    def exec(self, context, action):
        change_keyframe_type(action, self.keyframe_type)
        return {"FINISHED"}


class ACT_OT_delete_bone_all(OPS_, ACT_Multiple_Action_Op, Operator):
    """Delete bone and update all actions"""

    bl_idname = "act.delete_bone_all"
    bl_label = "Delete Bone (All)"

    @classmethod
    def do_poll(cls, context):
        return ACT_Multiple_Action_Op.do_poll(context) and DOIF.ACTIVE.HAS.BONES(
            context
        )

    def exec(self, context, action):
        scene = context.scene
        obj = context.active_object
        selected_bone_names = list(
            [bone.name for bone in obj.data.bones if bone.select]
        )

        for bone_name in selected_bone_names:
            path_prefix = get_bone_data_path(bone_name, "")

            for index, fcurve in iters.reverse_enumerate(action.fcurves):
                if fcurve.data_path.startswith(path_prefix):
                    action.fcurves.remove(fcurve)

    def finish(self, context):
        obj = context.active_object
        selected_bone_names = list(
            [bone.name for bone in obj.data.bones if bone.select]
        )

        remove_bones(obj, selected_bone_names)


class ACT_OT_rename_bone_all(OPS_, ACT_Multiple_Action_Op, Operator):
    """Rename bone and update all actions"""

    bl_idname = "act.rename_bone_all"
    bl_label = "Rename Bone (All)"

    old: bpy.props.StringProperty(name="Old Name")
    new: bpy.props.StringProperty(name="New Name")

    @classmethod
    def do_poll(cls, context):
        return ACT_Multiple_Action_Op.do_poll(context) and DOIF.ACTIVE.HAS.BONES(
            context
        )

    def exec(self, context, action):
        scene = context.scene
        obj = context.active_object

        path_old = get_bone_data_path(self.old, "")
        path_new = get_bone_data_path(self.new, "")

        for group in action.groups:
            group.name = group.name.replace(self.old, self.new)

        for index, fcurve in iters.reverse_enumerate(action.fcurves):
            fcurve.data_path = fcurve.data_path.replace(path_old, path_new)

    def finish(self, context):
        obj = context.active_object

        for bone in obj.data.bones:
            if bone.name == self.old:
                bone.name = self.new
                break
