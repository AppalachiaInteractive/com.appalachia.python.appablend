import bpy
from appablend.common.basetypes.ui import PT_, UI
from appablend.common.core.enums import icons
from appablend.common.core.subtypes import ST_StringProperty
from appablend.empties_to_bones.core import *
from appablend.empties_to_bones.ops import (BE_OT_deconstruct_armature,
                                            EB_OT_bake_anim,
                                            EB_OT_create_armature,
                                            EB_OT_create_bake,
                                            EB_OT_deconstruct_duplicate_bake,
                                            EB_OT_duplicate_armature,
                                            EB_OT_duplicate_bake,
                                            EB_OT_process_batch)


class EB_PT_menu(bpy.types.Panel, PT_, UI.VIEW_3D.UI.Tool):
    bl_label = "Empties to Bones"
    bl_idname = "EB_PT_menu"
    bl_icon = icons.EMPTY_ARROWS

    @classmethod
    def do_poll(cls, context):
        return True

    def do_draw(self, context, scene, layout, obj):
        arm = scene.eb_target_armature

        box = layout.box()
        col = box.column(align=True)
        col.label(text="Armature Options:")
        row = col.row()
        row.prop(scene, "eb_target_armature")
        row = col.row()
        row.enabled = arm is None
        row.prop(scene, "eb_bone_scale", text="Bone Scale")
        col.separator()
        row = col.row(align=True)
        row.prop(scene, "eb_auto_bones_orientation", text="Auto Orient")
        enabled = row.enabled
        rc = row.split(align=True)
        rc.enabled = scene.eb_auto_bones_orientation
        rc.prop(scene, "eb_auto_target_axis", text="X")
        row.enabled = enabled
        col.separator()
        row = col.row(align=True)
        row.prop(scene, "eb_invert_x", text="Invert X")
        row.prop(scene, "eb_invert_y", text="Invert Y")
        row.prop(scene, "eb_invert_z", text="Invert Z")
        if scene.eb_auto_bones_orientation:
            row.enabled = False

        box = layout.box()
        col = box.column(align=True)
        col.label(text="Target Options:")
        col.prop(
            scene, "eb_target_type"
        )  # TARGETS = ['ACTION', 'ACTION NAME', 'FILE', 'DIR']
        if scene.eb_target_type == "ACTION NAME":
            col.prop(scene, "eb_source_object")
            col.prop(scene, "eb_target_action_name")
        elif scene.eb_target_type == "ACTION":
            col.prop(scene, "eb_source_object")
            col.prop(scene, "eb_target_action")
        elif scene.eb_target_type == "FILE":
            col.prop(scene, "eb_target_file")
        elif scene.eb_target_type == "DIR":
            col.prop(scene, "eb_target_dir")

        box = layout.box()
        col = box.column(align=True)
        row = col.row()
        if scene.eb_target_type != "DIR" and scene.eb_target_type != "FILE":
            row.operator(BE_OT_deconstruct_armature.bl_idname, text="Deconstruct")
            row.operator(EB_OT_create_armature.bl_idname, text="Create")
            row = col.row()
            row.operator(EB_OT_duplicate_armature.bl_idname, text="Duplicate")
            row.operator(EB_OT_bake_anim.bl_idname, text="Bake")
            col.separator()
            col.operator(
                EB_OT_deconstruct_duplicate_bake.bl_idname,
                text="Deconstruct + Duplicate + Bake",
            )
            col.operator(EB_OT_create_bake.bl_idname, text="Create + Bake")
            col.operator(EB_OT_duplicate_bake.bl_idname, text="Duplicate + Bake")
        else:
            row.operator(EB_OT_process_batch.bl_idname, text="Process Batch")


def register():
    bpy.types.Scene.eb_auto_bones_orientation = bpy.props.BoolProperty(
        name="Automatic Bones Orientation", default=True
    )
    bpy.types.Scene.eb_auto_target_axis = bpy.props.EnumProperty(
        name="Target Axis",
        items=(
            ("X", "X", "X"),
            ("Y", "Y", "Y"),
            ("Z", "Z", "Z"),
            ("-X", "-X", "-X"),
            ("-Y", "-Y", "-Y"),
            ("-Z", "-Z", "-Z"),
        ),
        default="Z",
        description="The empty's target axis that the bone's X axis will match",
    )
    bpy.types.Scene.eb_invert_x = bpy.props.BoolProperty(
        name="Invert X Rot", default=False
    )
    bpy.types.Scene.eb_invert_y = bpy.props.BoolProperty(
        name="Invert Y Rot", default=False
    )
    bpy.types.Scene.eb_invert_z = bpy.props.BoolProperty(
        name="Invert Z Rot", default=False
    )
    bpy.types.Scene.eb_current_empty_action = bpy.props.StringProperty(
        default="", name="Empty Action"
    )
    bpy.types.Scene.eb_bone_scale = bpy.props.FloatProperty(
        default=1.0, name="Bone Scale"
    )
    bpy.types.Scene.eb_source_object = bpy.props.PointerProperty(
        type=bpy.types.Object, name="Source Object"
    )
    bpy.types.Scene.eb_target_armature = bpy.props.PointerProperty(
        type=bpy.types.Object, name="Target Armature"
    )
    bpy.types.Scene.eb_target_type = bpy.props.EnumProperty(
        name="Target Type", items=TARGET_ENUM, default=TARGET_ENUM_DEF
    )
    bpy.types.Scene.eb_target_action = bpy.props.PointerProperty(
        type=bpy.types.Action, name="Target Action"
    )
    bpy.types.Scene.eb_target_action_name = bpy.props.StringProperty(
        default="", name="Target Action Name"
    )
    bpy.types.Scene.eb_target_file = bpy.props.StringProperty(
        default="",
        name="Target Action Name",
        subtype=ST_StringProperty.Subtypes.FILE_PATH,
    )
    bpy.types.Scene.eb_target_dir = bpy.props.StringProperty(
        name="Sheet Dir Path", subtype=ST_StringProperty.Subtypes.DIR_PATH
    )


def unregister():
    del bpy.types.Scene.eb_auto_bones_orientation
    del bpy.types.Scene.eb_auto_target_axis
    del bpy.types.Scene.eb_invert_x
    del bpy.types.Scene.eb_invert_y
    del bpy.types.Scene.eb_invert_z
    del bpy.types.Scene.eb_current_empty_action
    del bpy.types.Scene.eb_bone_scale
    del bpy.types.Scene.eb_source_object
    del bpy.types.Scene.eb_target_armature
    del bpy.types.Scene.eb_target_type
    del bpy.types.Scene.eb_target_action
    del bpy.types.Scene.eb_target_action_name
    del bpy.types.Scene.eb_target_file
    del bpy.types.Scene.eb_target_dir
