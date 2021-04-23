import bpy
import mathutils
from appablend.common.bones import (get_child_bone_names_recursive,
                                    get_disconnected_bone_names,
                                    get_parent_bone_names,
                                    get_pose_bone_matrix_world,
                                    reset_pose_bone_location,
                                    reset_pose_bone_rotation,
                                    reset_pose_bone_transform,
                                    set_pose_bone_matrix_world)
from appablend.common.core.modes import enter_mode, enter_mode_simple
from appablend.common.core.subtypes import ST_FloatVectorProperty
from appablend.common.utils.enums import create_enum
from mathutils import Matrix

LOCATION_CORRECTION_TYPE = ["LOCK", "NEGATE", "CLEAR"]
LOCATION_CORRECTION_TYPE_ENUM = create_enum(LOCATION_CORRECTION_TYPE)

LOCATION_NEGATE_TYPE = ["EXACT", "OFFSET", "OBJECT", "CANCEL"]
LOCATION_NEGATE_TYPE_ENUM = create_enum(LOCATION_NEGATE_TYPE)

ROTATION_CORRECTION_TYPE = ["CLEAR"]
ROTATION_CORRECTION_TYPE_ENUM = create_enum(ROTATION_CORRECTION_TYPE)

TRANSFORM_CORRECTION_TYPE = ["LOCK", "NEGATE", "CLEAR"]
TRANSFORM_CORRECTION_TYPE_ENUM = create_enum(TRANSFORM_CORRECTION_TYPE)

TRANSFORM_NEGATE_TYPE = [
    "EXACT",
]
TRANSFORM_NEGATE_TYPE_ENUM = create_enum(TRANSFORM_NEGATE_TYPE)


class PoseCorrection(bpy.types.PropertyGroup):
    bone_name: bpy.props.StringProperty(name="Bone")

    location_correction_type: bpy.props.EnumProperty(
        name="Location Correction Type", items=LOCATION_CORRECTION_TYPE_ENUM, default=0
    )
    location_reference: bpy.props.FloatVectorProperty(
        name="Reference Point", subtype=ST_FloatVectorProperty.Subtypes.TRANSLATION
    )
    location_influence: bpy.props.FloatProperty(
        name="Influence", default=1.0, min=0.0, max=1.0
    )
    location_reference_frame: bpy.props.IntProperty(name="Frame")

    location_has_lock_bone: bpy.props.BoolProperty(name="Has Lock Bone?")
    location_lock_bone_name: bpy.props.StringProperty(name="Correction Bone")

    location_negate_bone_name: bpy.props.StringProperty(name="Negate Bone")
    location_negate_type: bpy.props.EnumProperty(
        name="Type", items=LOCATION_NEGATE_TYPE_ENUM, default=0
    )
    location_negate_co_offset: bpy.props.FloatVectorProperty(
        name="Negation Offset", subtype=ST_FloatVectorProperty.Subtypes.TRANSLATION
    )
    location_negate_co_object: bpy.props.FloatVectorProperty(
        name="Negation Point", subtype=ST_FloatVectorProperty.Subtypes.TRANSLATION
    )
    location_negate_cancel_x: bpy.props.BoolProperty(name="Cancel X")
    location_negate_cancel_y: bpy.props.BoolProperty(name="Cancel Y")
    location_negate_cancel_z: bpy.props.BoolProperty(name="Cancel Z")

    rotation_correction_type: bpy.props.EnumProperty(
        name="Rotation Correction Type", items=ROTATION_CORRECTION_TYPE_ENUM, default=0
    )
    rotation_influence: bpy.props.FloatProperty(
        name="Influence", default=1.0, min=0.0, max=1.0
    )

    transform_correction_type: bpy.props.EnumProperty(
        name="Transform Correction Type",
        items=TRANSFORM_CORRECTION_TYPE_ENUM,
        default=0,
    )
    transform_reference: bpy.props.FloatVectorProperty(
        name="Reference Point", subtype=ST_FloatVectorProperty.Subtypes.MATRIX, size=16
    )
    transform_influence: bpy.props.FloatProperty(
        name="Influence", default=1.0, min=0.0, max=1.0
    )
    transform_reference_frame: bpy.props.IntProperty(name="Frame")

    transform_has_lock_bone: bpy.props.BoolProperty(name="Has Lock Bone?")
    transform_lock_bone_name: bpy.props.StringProperty(name="Correction Bone")

    transform_negate_bone_name: bpy.props.StringProperty(name="Negate Bone")
    transform_negate_type: bpy.props.EnumProperty(
        name="Type", items=TRANSFORM_NEGATE_TYPE_ENUM, default=0
    )

    def flatten(self, mat):
        dim = len(mat)
        return [mat[j][i] for i in range(dim) for j in range(dim)]

    def get_bone_matrix(self, name):
        arm = self.id_data
        bone = arm.pose.bones[name]
        return bone.matrix

    def decompose_bones(self, name):
        bone_matrix = self.get_bone_matrix(name)
        loc, rot, sca = bone_matrix.decompose()
        return loc, rot, sca

    def get_location_by_bone(self, name):
        loc, rot, sca = self.decompose_bones(name)
        return loc

    def get_rotation_by_bone(self, name):
        loc, rot, sca = self.decompose_bones(name)
        return rot

    def get_scale_by_bone(self, name):
        loc, rot, sca = self.decompose_bones(name)
        return sca

    def get_transform_by_bone(self, name):
        return self.get_bone_matrix(name)

    def get_location(self):
        return self.get_location_by_bone(self.bone_name)

    def get_rotation(self):
        return self.get_rotation_by_bone(self.bone_name)

    def get_scale(self):
        return self.get_scale_by_bone(self.bone_name)

    def get_transform(self):
        return self.get_transform_by_bone(self.bone_name)

    def get(self, prop_name):
        if prop_name.lower() == "location":
            return self.get_location_by_bone(self.bone_name)
        if prop_name.lower() == "rotation":
            return self.get_rotation_by_bone(self.bone_name)
        if prop_name.lower() == "scale":
            return self.get_scale_by_bone(self.bone_name)
        if prop_name.lower() == "transform":
            return self.get_transform_by_bone(self.bone_name)

        return None

    def cursor_to_loc(self, cursor):
        arm = self.id_data
        cursor.location = arm.matrix_world @ self.location_reference

    def cursor_to_transform(self, cursor):
        arm = self.id_data
        tl, _, _ = self.transform_reference.decompose()
        cursor.location = arm.matrix_world @ tl

    def set_ref(self, prop_name, val, frame, cursor):
        arm = self.id_data

        if prop_name.lower() == "location":
            self.location_reference = val
            self.location_reference_frame = frame
            self.cursor_to_loc(cursor)
        if prop_name.lower() == "rotation":
            self.rotation_reference = val
            self.rotation_reference_frame = frame
        if prop_name.lower() == "scale":
            self.scale_reference = val
            self.scale_reference_frame = frame
        if prop_name.lower() == "transform":
            self.transform_reference = self.flatten(val)
            self.transform_reference_frame = frame
            self.cursor_to_transform(cursor)

    def get_poll_alert(self, arm, bone, prop_name):
        disconnected_bone_names = get_disconnected_bone_names(arm)
        parent_bone_names = get_parent_bone_names(bone)
        child_bone_names = get_child_bone_names_recursive(bone)

        correction_type = getattr(self, "{0}_correction_type".format(prop_name), "")
        reference_frame = getattr(self, "{0}_reference_frame".format(prop_name), "")
        negate_bone_name = getattr(self, "{0}_negate_bone_name".format(prop_name), "")
        lock_bone_name = getattr(self, "{0}_lock_bone_name".format(prop_name), "")

        if correction_type == "LOCK":
            hb = lock_bone_name
            return hb != "" and (
                hb not in disconnected_bone_names or hb not in parent_bone_names
            )
        elif correction_type == "CLEAR":
            return False
        else:
            nb = negate_bone_name
            return nb != "" and (
                nb not in disconnected_bone_names and nb in child_bone_names
            )

        return False

    def get_poll_valid(self, context, prop_name):
        correction_type = getattr(self, "{0}_correction_type".format(prop_name), "")
        reference_frame = getattr(self, "{0}_reference_frame".format(prop_name), "")
        negate_bone_name = getattr(self, "{0}_negate_bone_name".format(prop_name), "")

        if correction_type == "LOCK":
            return context.scene.frame_current != reference_frame
        elif correction_type == "CLEAR":
            return True
        else:
            return negate_bone_name != ""

    def get_location_correction(self):
        current = self.get_location()
        orig = self.location_reference
        diff = orig - current
        inf = self.location_influence

        if self.location_correction_type == "LOCK":
            return diff  # - current.lerp(orig, inf)
        elif self.location_correction_type == "NEGATE":
            nl = self.get_location_by_bone(self.location_negate_bone_name)
            return current - current.lerp(nl, inf)

    def get_transform_correction(self):
        current = self.get_transform()
        orig = self.transform_reference
        inf = self.transform_influence

        cl, cr, cs = current.decompose()

        if self.transform_correction_type == "NEGATE":
            orig = self.get_transform_by_bone(self.transform_negate_bone_name)

        gl, gr, gs = orig.decompose()

        l = cl.lerp(gl, inf)
        r = cr.slerp(gr, inf)
        s = cs.lerp(gs, inf)

        dl = l - cl
        dr = r - cr
        ds = s - cs

        ml = Matrix.Translation(dl)
        rl = r.to_matrix().to_4x4()

        return ml @ rl

    def correct_pose_clear(self, context, armature, pose_bone, prop_name):
        affected = []
        affected.append(self.bone_name)

        selected_bones = [b.name for b in armature.data.bones if b.select]

        empties = []

        def get_empty_name(bone_name):
            return "_EE_{0}".format(bone_name)

        enter_mode_simple("OBJECT")

        for child_bone in pose_bone.children:
            bpy.ops.object.empty_add()
            e = context.active_object
            e.name = get_empty_name(child_bone.name)
            empties.append(e)

        enter_mode(armature, "POSE")

        for index, child_bone in enumerate(pose_bone.children):
            affected.append(child_bone.name)
            e = empties[index]
            e.matrix_world = get_pose_bone_matrix_world(armature, child_bone.name)

        if prop_name == "location":
            reset_pose_bone_location(armature, pose_bone.name)
        elif prop_name == "rotation":
            reset_pose_bone_rotation(armature, pose_bone.name)
        else:
            reset_pose_bone_transform(armature, pose_bone.name)

        enter_mode(armature, "OBJECT")
        enter_mode(armature, "POSE")

        for index, child_bone in enumerate(pose_bone.children):
            empty = empties[index]
            set_pose_bone_matrix_world(armature, child_bone.name, empty.matrix_world)

            bpy.data.objects.remove(empty)

        for bone_name in selected_bones:
            armature.data.bones[bone_name].select = True

        return affected

    def correct_pose_location(self, context, armature, pose_bone):
        self.bone_name = pose_bone.name

        if self.location_correction_type == "CLEAR":
            return self.correct_pose_clear(context, armature, pose_bone, "location")

        obj_correction = self.get_location_correction()
        obj_correction_matrix = Matrix.Translation(obj_correction)
        neg_obj_correction_matrix = Matrix.Translation(-obj_correction)

        if self.location_correction_type == "LOCK":
            other_bone_name = (
                self.location_lock_bone_name
                if self.location_has_lock_bone
                else self.bone_name
            )
        else:
            other_bone_name = self.location_negate_bone_name

        if other_bone_name == "" or not other_bone_name in armature.pose.bones:
            return []

        other_bone = armature.pose.bones[other_bone_name]

        pose_bone_world_matrix = (
            armature.matrix_world @ obj_correction_matrix @ pose_bone.matrix
        )
        neg_pose_bone_world_matrix = (
            armature.matrix_world @ neg_obj_correction_matrix @ pose_bone.matrix
        )

        other_bone_world_matrix = (
            armature.matrix_world @ obj_correction_matrix @ other_bone.matrix
        )
        neg_other_bone_world_matrix = (
            armature.matrix_world @ neg_obj_correction_matrix @ other_bone.matrix
        )

        if self.location_correction_type == "LOCK":
            other_bone.matrix = other_bone_world_matrix
            return [other_bone.name]
        else:
            pose_bone.matrix = pose_bone_world_matrix
            other_bone.matrix = neg_other_bone_world_matrix
            return [pose_bone.name, other_bone.name]

    def correct_pose_rotation(self, context, armature, pose_bone):
        self.bone_name = pose_bone.name

        if self.rotation_correction_type == "CLEAR":
            return self.correct_pose_clear(context, armature, pose_bone, "rotation")

        return []

    def correct_pose_transform(self, context, armature, pose_bone):
        armature = bpy.data.objects[armature.name]
        selected_bones = [bone.name for bone in armature.data.bones if bone.select]
        self.bone_name = pose_bone.name

        if self.transform_correction_type == "CLEAR":
            return self.correct_pose_clear(context, armature, pose_bone, "transform")

        obj_correction_matrix = self.get_transform_correction()

        t, r, s = obj_correction_matrix.decompose()

        mat_loc = mathutils.Matrix.Translation(-t)
        mat_rot = r.inverted().to_matrix().to_4x4()
        mat_out = mat_loc @ mat_rot  # @ mat_sca

        neg_obj_correction_matrix = mat_out

        if self.transform_correction_type == "LOCK":
            other_bone_name = (
                self.transform_lock_bone_name
                if self.transform_has_lock_bone
                else self.bone_name
            )
        else:
            other_bone_name = self.transform_negate_bone_name

        if other_bone_name == "" or not other_bone_name in armature.pose.bones:
            return []

        other_bone = armature.pose.bones[other_bone_name]

        pose_bone_world_matrix = (
            armature.matrix_world @ obj_correction_matrix @ pose_bone.matrix
        )
        neg_pose_bone_world_matrix = (
            armature.matrix_world @ neg_obj_correction_matrix @ pose_bone.matrix
        )

        other_bone_world_matrix = (
            armature.matrix_world @ obj_correction_matrix @ other_bone.matrix
        )
        neg_other_bone_world_matrix = (
            armature.matrix_world @ neg_obj_correction_matrix @ other_bone.matrix
        )

        if self.transform_correction_type == "LOCK":
            other_bone.matrix = other_bone_world_matrix
            return [other_bone.name]
        else:
            pose_bone.matrix = pose_bone_world_matrix
            other_bone.matrix = neg_other_bone_world_matrix
            return [pose_bone.name, other_bone.name]
