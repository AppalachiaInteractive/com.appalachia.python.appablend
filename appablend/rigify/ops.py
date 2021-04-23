import re

import bpy
from appablend.common.basetypes.ops import OPS_
from bpy.types import Operator


class RTU_OT_convert_human(OPS_, Operator):
    bl_idname = "rtu.convert_human"
    bl_label = "Prepare rig for unity"

    @classmethod
    def do_poll(cls, context):
        return True

    def do_execute(self, context):
        obj = context.object

        bpy.ops.object.mode_set(mode="OBJECT")

        removal_bone_names = [
            "DEF-pelvis.L",
            "DEF-breast.R",
            "DEF-pelvis.L",
            "DEF-pelvis.R",
        ]

        parent_changes = [
            ("DEF-shoulder.L", "DEF-spine.003"),
            ("DEF-shoulder.R", "DEF-spine.003"),
            ("DEF-upper_arm.L", "DEF-shoulder.L"),
            ("DEF-upper_arm.R", "DEF-shoulder.R"),
            ("DEF-thigh.L", "DEF-spine"),
            ("DEF-thigh.R", "DEF-spine"),
        ]

        twist_bones = [
            ("DEF-upper_arm.L", "DEF-upper_arm.L.001"),
            ("DEF-upper_arm.R", "DEF-upper_arm.R.001"),
            ("DEF-forearm.L", "DEF-forearm.L.001"),
            ("DEF-forearm.R", "DEF-forearm.R.001"),
            ("DEF-thigh.L", "DEF-thigh.L.001"),
            ("DEF-thigh.R", "DEF-thigh.R.001"),
            ("DEF-shin.L", "DEF-shin.L.001"),
            ("DEF-shin.R", "DEF-shin.R.001"),
        ]

        name_adjustments = [
            ("DEF-spine.006", "DEF-head"),
            ("DEF-spine.005", "DEF-neck"),
        ]

        for removal_bone_name in removal_bone_names:
            if removal_bone_name in obj.data.bones:
                obj.data.bones[removal_bone_name].use_deform = False

        bpy.ops.object.mode_set(mode="EDIT")

        bones = obj.data.edit_bones

        for bone_name, new_parent_name in parent_changes:
            bones[bone_name].parent = bones[new_parent_name]

        for parent_bone_name, twist_bone_name in twist_bones:
            parent_bone = bones[parent_bone_name]
            twist_bone = bones[twist_bone_name]

            parent_bone.tail = twist_bone.tail

            for child_bone in twist_bone.children:
                child_bone.parent = parent_bone

            bones.remove(twist_bone)

        for removal_bone_name in removal_bone_names:
            if removal_bone_name in bones:
                bones.remove(bones[removal_bone_name])
            if removal_bone_name in obj.vertex_groups:
                obj.vertex_groups.remove(obj.vertex_groups[removal_bone_name])

        bpy.ops.object.mode_set(mode="OBJECT")

        for old_name, new_name in name_adjustments:
            pb = obj.pose.bones.get(old_name)

            if pb:
                pb.name = new_name

        self.report({"INFO"}, "Unity ready rig!")

        return {"FINISHED"}
