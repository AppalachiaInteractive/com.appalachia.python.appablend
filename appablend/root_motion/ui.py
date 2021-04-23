import bpy
from appablend.common.basetypes.ui import PT_, UI
from appablend.common.core.enums import icons
from appablend.common.models.root_motion import ArmatureRootMotionSettings
from appablend.cursor.ops import (CURSOR_OT_set_active, CURSOR_OT_set_target,
                                  CURSOR_OT_set_world)
from appablend.drivers.ops import DRV_OT_update_dependencies
from appablend.root_motion.ops import *
from appablend.unity.scene import UnitySettings
from appablend.unity.ui import (CLIP_SUBPANEL_REQ,
                                VIEW_3D_PT_UI_Tool_Unity_020_Clip)


class _PT_RM_020_Clip_010_RootMotion(CLIP_SUBPANEL_REQ):
    bl_icon = UnitySettings.icon_root_motion
    bl_label = "Root Motion"

    @classmethod
    def do_poll(cls, context):
        return (
            cls.subpanel_poll(context) and context.scene.unity_settings.draw_root_motion
        )

    def draw_curve_buttons(self, layout, armature, root_motion):
        box = layout.box()
        row = box.row(align=True)
        row.operator(RM_OT_settings_to_curves.bl_idname, icon=icons.CURVE_DATA)
        row.operator(RM_OT_settings_to_curves.bl_idname, icon=icons.CURVE_PATH)
        row.separator()
        row.operator(DRV_OT_update_dependencies.bl_idname)
        row.separator()
        rows = row.split()
        rows.alignment = "RIGHT"
        rows.operator(
            RM_OT_refresh_settings.bl_idname, icon=icons.FILE_REFRESH, text=""
        )
        rows.operator(
            RM_OT_create_root_motion_setup.bl_idname, icon=icons.MOD_BUILD, text=""
        )
        rows.operator(
            RM_OT_reset_offsets_all.bl_idname,
            icon=RM_OT_reset_offsets_all.bl_icon,
            text="",
        )
        o = rows.operator(
            RM_OT_set_offset_all.bl_idname, icon=icons.ARMATURE_DATA, text=""
        )
        o.target, o.operation, o.phase = "origin", "set_to_rest", "start"
        rows.operator(
            RM_OT_push_location_offsets_all.bl_idname, icon=icons.CON_LOCLIKE, text=""
        )
        rows.operator(
            RM_OT_push_rotation_offsets_all.bl_idname,
            icon=icons.ORIENTATION_GIMBAL,
            text="",
        )
        rows.operator(
            RM_OT_refresh_childof_constraints.bl_idname,
            icon=RM_OT_refresh_childof_constraints.bl_icon,
            text="",
        )

    def draw_root_node_start(self, layout, armature, root_motion):
        rms = armature.root_motion_settings

        b = layout.box()
        h = b.row(align=True)
        h.prop_search(
            rms,
            "original_root_bone",
            armature,
            "bones",
            text="Original Root",
            icon=icons.BONE_DATA,
        )
        h2 = h.split()
        h2.enabled = False
        h2.prop(rms, "root_node")
        h3 = h.split()
        h3.enabled = rms.root_final is None
        h3.prop(rms, "root_final")

        r = b.row()
        col1 = r.column(align=True)
        col2 = r.column(align=True)
        col3 = r.column(align=True)

        alert = False
        val = root_motion.root_node_start_location
        if val[0] != 0 or val[1] != 0 or val[2] != 0:
            alert = True
        val = root_motion.root_node_start_rotation
        if val[0] != 0 or val[1] != 0 or val[2] != 0:
            alert = True

        col1.prop(root_motion, "root_node_start_location", text="")
        col2.prop(root_motion, "root_node_start_rotation", text="")
        col3r = col3.row()
        RM_OT_set_offset.rest_operator(col3r, RM.TARGET.ORIGIN, RM.PHASE.START)

        col3r = col3.row(align=True)
        col3r.operator(
            CURSOR_OT_set_world.bl_idname, icon=CURSOR_OT_set_world.bl_icon, text=""
        )
        col3r.operator(
            CURSOR_OT_set_active.bl_idname, icon=CURSOR_OT_set_active.bl_icon, text=""
        )
        col3r2 = col3r.split()
        s = col3r2.operator(
            CURSOR_OT_set_target.bl_idname, icon=CURSOR_OT_set_target.bl_icon, text=""
        )
        col3r2.enabled = rms.root_node is not None
        if col3r2.enabled:
            s.target_name = rms.root_node.name

        RM_OT_set_offset.cursor_set_operator(col3r, RM.TARGET.ORIGIN, RM.PHASE.START)
        RM_OT_set_offset.cursor_start_operator(col3r, RM.TARGET.ORIGIN, RM.PHASE.START)

        col3a = col3.split()
        col3a.alert = alert
        RM_OT_set_offset.reset_operator(col3a, RM.TARGET.ORIGIN, RM.PHASE.START)

    def draw_root_motion_settings(self, layout, armature, root_motion):
        col = layout.column()
        r0, r1, r2, r3 = (
            col.row(align=True),
            col.row(align=True),
            col.row(align=True),
            col.row(align=True),
        )
        col.separator()
        r4 = col.row(align=True)

        r0.label(text="Bake")
        r0.label(text="Offset")
        r0.label(text="Limit (min)")
        r0.label(text="Limit (max)")

        self.draw_root_xyz_component(r1, root_motion, "x")
        self.draw_root_xyz_component(r2, root_motion, "y")
        self.draw_root_xyz_component(r3, root_motion, "z")

        r4a, r4b = r4.row(align=True), r4.row(align=True)

        r4a.alert = root_motion.root_motion_rot_offset != 0.0
        r4a.prop(
            root_motion,
            "root_motion_rot_bake_into",
            toggle=True,
            text="",
            icon=icons.ORIENTATION_GIMBAL,
        )

        r4a.prop(root_motion, "root_motion_rot_offset", text="Rot. Offset")
        r4a.separator()
        RM_OT_set_offset.reset_operator(r4a, RM.TARGET.SETTINGS, RM.PHASE.START)
        r4a.separator()
        r4b.operator(
            RM_OT_push_location_offsets.bl_idname,
            icon=RM_OT_push_location_offsets.bl_icon,
        )
        r4b.operator(
            RM_OT_push_rotation_offsets.bl_idname,
            icon=RM_OT_push_rotation_offsets.bl_icon,
        )

    def draw_root_xyz_component(self, layout, root_motion, axis):
        l = axis.lower()
        u = axis.upper()
        icon = "EVENT_{0}".format(u)
        pre = "root_motion_{0}_".format(l)
        layout.prop(
            root_motion, "{0}bake_into".format(pre), icon=icon, text="", toggle=True
        )

        prop_name = "{0}offset".format(pre)

        val = getattr(root_motion, prop_name)

        row = layout.row()

        if val != 0:
            row.alert = True

        row.prop(root_motion, prop_name, text=u)

        limits = [("limit_neg", "-"), ("limit_pos", "+")]
        limit_props = [
            (
                "{0}{1}".format(pre, limit[0]),
                "{0}{1}_val".format(pre, limit[0]),
                limit[1],
            )
            for limit in limits
        ]

        for limit_prop in limit_props:
            r = layout.row()
            r.prop(
                root_motion,
                limit_prop[0],
                text="",
                toggle=True,
                icon=icons.CON_LOCLIMIT,
            )
            r = r.split()
            r.enabled = getattr(root_motion, limit_prop[0], False)
            r.alert = getattr(root_motion, limit_prop[0]) != 0
            r.prop(root_motion, limit_prop[1], text="Limit {0}".format(limit_prop[2]))

    def draw_bone_offset(self, layout, armature, root_motion, bone):

        br = layout.row()
        brs = br.row()
        # brs.enabled = False
        brs.prop_search(
            armature.root_motion_settings,
            "{0}_bone_name".format(bone),
            armature,
            "bones",
            text=bone.capitalize(),
            icon=icons.BONE_DATA,
        )
        brs.prop_search(
            armature.root_motion_settings,
            "{0}_bone_offset".format(bone),
            bpy.data,
            "objects",
            text="Offset",
            icon=icons.OBJECT_DATA,
        )

        sr = br.row(align=True)
        sr.enabled = True
        p0 = "{0}_bone_offset_blend".format(bone) + "_{0}"
        sr.prop(root_motion, p0.format("low"), slider=True)
        sr.prop(root_motion, p0.format("mid"), slider=True)
        sr.prop(root_motion, p0.format("high"), slider=True)

        offr = layout.row()
        c1 = offr.column()
        c2 = offr.column()

        alerting1 = self.draw_bone_start_end(c1, armature, root_motion, bone, "start")
        alerting2 = self.draw_bone_start_end(c2, armature, root_motion, bone, "end")
        alerting = alerting1 or alerting2
        sr.enabled = alerting

    def draw_cursor_options(self, layout, armature, root_motion):
        row = layout.row(align=True)

        row.operator(
            CURSOR_OT_set_world.bl_idname, icon=CURSOR_OT_set_world.bl_icon, text=""
        )
        row.operator(
            CURSOR_OT_set_active.bl_idname, icon=CURSOR_OT_set_active.bl_icon, text=""
        )

    def draw_bone_start_end(self, layout, armature, root_motion, bone, phase):
        p0 = "{0}_bone_offset".format(bone)
        p1 = "{0}_bone_offset_location_{1}".format(bone, phase)
        p2 = "{0}_bone_offset_rotation_{1}".format(bone, phase)

        rms = armature.root_motion_settings

        operation = "{0}_{1}".format(bone, phase)

        phase = phase.capitalize()
        alert = False

        def draw_value_row(p, text, alerting):
            r = layout.row(align=True)
            v = getattr(root_motion, p)
            r.prop(root_motion, p, text=text)

            alerting = alerting or max([1 if c != 0.0 else 0.0 for c in v])

            return alerting

        alert = draw_value_row(p1, "Loc ({0})".format(phase), alert)
        alert = draw_value_row(p2, "Rot ({0})".format(phase), alert)

        row = layout.row(align=True)

        RM_OT_set_offset.rest_operator(row, bone.capitalize(), phase)
        row.separator()

        row.operator(
            CURSOR_OT_set_world.bl_idname, icon=CURSOR_OT_set_world.bl_icon, text=""
        )
        row.operator(
            CURSOR_OT_set_active.bl_idname, icon=CURSOR_OT_set_active.bl_icon, text=""
        )

        r2 = row.split()
        s = r2.operator(
            CURSOR_OT_set_target.bl_idname, icon=CURSOR_OT_set_target.bl_icon, text=""
        )
        r2.enabled = getattr(rms, p0) is not None
        if r2.enabled:
            s.target_name = getattr(rms, p0).name

        RM_OT_set_offset.cursor_set_operator(row, bone.capitalize(), phase)
        RM_OT_set_offset.cursor_start_operator(row, bone.capitalize(), phase)

        row.separator()
        r2 = row.split()
        r2.alert = alert
        RM_OT_set_offset.reset_operator(r2, bone.capitalize(), phase)

        return alert

    def finish_draw(self, context, scene, layout, obj, action, unity_clip):
        obj = get_unity_target(context)
        armature = obj.data
        root_motion = unity_clip.root_motion
        self.draw_curve_buttons(layout, armature, root_motion)

        self.draw_root_node_start(layout, armature, root_motion)

        self.draw_root_motion_settings(layout, armature, root_motion)

        self.draw_bone_offset(layout.box(), armature, root_motion, "root")
        self.draw_bone_offset(layout.box(), armature, root_motion, "hip")


class _PT_RM_020_Clip_030_Pose(CLIP_SUBPANEL_REQ):
    bl_icon = UnitySettings.icon_pose
    bl_label = "Pose"

    @classmethod
    def do_poll(cls, context):
        return cls.subpanel_poll(context) and context.scene.unity_settings.draw_pose

    def finish_draw(self, context, scene, layout, obj, action, unity_clip):
        obj = get_unity_target(context)
        box = layout.box()

        if obj.pose_library is None:
            return

        row = box.row(align=True)
        row.prop_search(
            unity_clip, "pose_start", obj.pose_library, "pose_markers", text="Start"
        )
        row = row.split()
        row.alignment = "RIGHT"
        row.prop(unity_clip, "pose_start_rooted", text="Root?")

        row = box.row(align=True)
        col1 = row.column(align=True)
        start_apply_start = col1.operator(RM_OT_apply_pose.bl_idname, text="To Start")

        col2 = row.column(align=True)
        col2.enabled = context.scene.frame_current != context.scene.frame_start
        start_apply_current = col2.operator(
            RM_OT_apply_pose.bl_idname, text="To Current"
        )

        col3 = row.column(align=True)
        col3.enabled = not unity_clip.pose_start.startswith(unity_clip.name)
        start_new_current = col3.operator(RM_OT_new_pose.bl_idname, text="From Current")

        start_apply_start.pose_name = unity_clip.pose_start
        start_apply_start.frame = unity_clip.frame_start
        start_apply_start.rooted = unity_clip.pose_start_rooted
        start_apply_current.pose_name = unity_clip.pose_start
        start_apply_current.frame = context.scene.frame_current
        start_apply_current.rooted = unity_clip.pose_start_rooted
        start_new_current.start = True
        start_new_current.frame = context.scene.frame_current

        row = box.row(align=True)
        row.prop_search(
            unity_clip, "pose_end", obj.pose_library, "pose_markers", text="End"
        )
        row = row.split()
        row.alignment = "RIGHT"
        row.prop(unity_clip, "pose_end_rooted", text="Root?")

        row = box.row(align=True)
        col1 = row.column(align=True)
        end_apply_end = col1.operator(RM_OT_apply_pose.bl_idname, text="To End")

        col2 = row.column(align=True)
        col2.enabled = context.scene.frame_current != context.scene.frame_end
        end_apply_current = col2.operator(RM_OT_apply_pose.bl_idname, text="To Current")

        col3 = row.column(align=True)
        col3.enabled = not unity_clip.pose_end.endswith(unity_clip.name)
        end_new_current = col3.operator(RM_OT_new_pose.bl_idname, text="From Current")

        end_apply_end.pose_name = unity_clip.pose_end
        end_apply_end.frame = unity_clip.frame_end
        end_apply_end.rooted = unity_clip.pose_end_rooted
        end_apply_current.pose_name = unity_clip.pose_end
        end_apply_current.frame = context.scene.frame_current
        end_apply_current.rooted = unity_clip.pose_end_rooted
        end_new_current.start = False
        end_new_current.frame = context.scene.frame_current


class VIEW_3D_PT_UI_Tool_RM_020_Clip_010_RootMotion(
    _PT_RM_020_Clip_010_RootMotion, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel
):
    bl_parent_id = VIEW_3D_PT_UI_Tool_Unity_020_Clip.bl_idname
    bl_idname = "VIEW_3D_PT_UI_Tool_RM_020_Clip_010_RootMotion"


class VIEW_3D_PT_UI_Tool_RM_020_Clip_030_Pose(
    _PT_RM_020_Clip_030_Pose, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel
):
    bl_parent_id = VIEW_3D_PT_UI_Tool_Unity_020_Clip.bl_idname
    bl_idname = "VIEW_3D_PT_UI_Tool_RM_020_Clip_030_Pose"


def register():
    bpy.types.Armature.root_motion_settings = bpy.props.PointerProperty(
        name="Root Motion Settings", type=ArmatureRootMotionSettings
    )


def unregister():
    del bpy.types.Armature.root_motion_settings
