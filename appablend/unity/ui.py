from appablend.common.basetypes.ui import PT_, UI
from appablend.common.core.enums import icons
from appablend.common.models.unity import UnityActionMetadata, get_unity_target
from appablend.unity.ops import *
from appablend.unity.scene import UnitySettings
from appablend.unity.ul import Unity_UL_Filters


class UNITY_PANEL:
    bl_label = "Unity"
    bl_icon = UnitySettings.icon_unity

    @classmethod
    def do_poll(cls, context):
        return True  # DOIF.UNITY.TARGET.SET(context)

    def do_draw(self, context, scene, layout, obj):
        obj = get_unity_target(context)
        unity_settings = scene.unity_settings

        col = layout.column(align=True)
        row = col.row(align=True)

        row.prop(unity_settings, "mode")

        row.separator()

        if unity_settings.mode != "ACTIVE":
            row.prop_search(
                unity_settings,
                "target_armature",
                bpy.data,
                "objects",
                text="",
                icon=icons.ARMATURE_DATA,
            )

        row.separator()
        row.prop(
            unity_settings,
            "draw_sheets",
            toggle=True,
            text="",
            icon=unity_settings.icon_sheets,
        )
        row.prop(
            unity_settings,
            "draw_keyframes",
            toggle=True,
            text="",
            icon=unity_settings.icon_keys,
        )
        row.prop(
            unity_settings,
            "draw_clips",
            toggle=True,
            text="",
            icon=unity_settings.icon_clips,
        )

        obj = get_unity_target(context)

        if obj:
            row.separator()
            row.prop(obj.data, "pose_position", expand=True)


class CLIP_SUBPANEL_REQ:
    @classmethod
    def subpanel_poll(cls, context):
        obj = get_unity_target(context)
        return DOIF.UNITY.TARGET.SET(context) and (
            DOIF.UNITY.MODE.SCENE(context) or obj is not None
        )

    def do_draw(self, context, scene, layout, obj):
        obj = get_unity_target(context)
        action, clip, clip_index = get_unity_action_and_clip(context)

        if action is None or clip is None:
            return

        self.finish_draw(context, scene, layout, obj, action, clip)


class CLIP_SUBPANEL:
    @classmethod
    def subpanel_poll(cls, context):
        return DOIF.UNITY.TARGET.SET(context)

    def do_draw(self, context, scene, layout, obj):
        obj = get_unity_target(context)
        action, clip, clip_index = get_unity_action_and_clip(context)

        self.finish_draw(context, scene, layout, obj, action, clip)


class VIEW_3D_PT_UI_Tool_Unity(UNITY_PANEL, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel):
    bl_idname = "VIEW_3D_PT_UI_Tool_Unity"


class DOPESHEET_EDITOR_PT_UI_Tool_Unity(
    UNITY_PANEL, UI.DOPESHEET_EDITOR.UI, PT_, bpy.types.Panel
):
    bl_idname = "DOPESHEET_EDITOR_PT_UI_Tool_Unity"


class _PT_Unity_000_Sheets:
    bl_icon = UnitySettings.icon_sheets
    bl_label = "Unity Sheets"

    @classmethod
    def do_poll(cls, context):
        return (
            DOIF.UNITY.TARGET.SET(context) and context.scene.unity_settings.draw_sheets
        )

    def do_draw(self, context, scene, layout, obj):
        obj = get_unity_target(context)
        layout.prop(scene.unity_settings, "sheet_dir_path")
        row = layout.row(align=True)
        row.operator(UNITY_OT_refresh_clip_data.bl_idname)
        row.operator(UNITY_OT_refresh_clip_data_all.bl_idname)
        row = layout.row(align=True)
        row.operator(UNITY_OT_clear_clip_data.bl_idname)
        row.operator(UNITY_OT_clear_clip_data_all.bl_idname)
        row = layout.row(align=True)
        row.operator(UNITY_OT_sort_clip_data.bl_idname)
        row.operator(UNITY_OT_sort_clip_data_all.bl_idname)

        if obj and obj.animation_data and obj.animation_data.action:
            row = layout.row(align=True)
            a = obj.animation_data.action
            row.prop(a.unity_metadata, "clip_template")
            row.operator(UNITY_OT_copy_clips_from_template.bl_idname)


class _PT_Unity_003_Keys:
    bl_icon = UnitySettings.icon_keys
    bl_label = "Unity Keyframes"

    @classmethod
    def do_poll(cls, context):
        return (
            DOIF.UNITY.TARGET.SET(context)
            and context.scene.unity_settings.draw_keyframes
        )

    def do_draw(self, context, scene, layout, obj):
        obj = get_unity_target(context)
        layout.prop(scene.unity_settings, "key_dir_path")
        row = layout.row(align=True)
        row.operator(UNITY_OT_refresh_key_data.bl_idname)
        row.operator(UNITY_OT_refresh_key_data_all.bl_idname)


class _PT_Unity_Clips_List:
    def do_draw(self, context, scene, layout, obj):
        self.draw_template_list(context, layout)


class _PT_Unity_Clips_Ops:
    bl_icon = UnitySettings.icon_operations
    bl_label = "Operations"

    @classmethod
    def do_poll(cls, context):
        return DOIF.UNITY.TARGET.SET(context)

    def do_draw(self, context, scene, layout, obj):

        action, clip, clip_index = get_unity_action_and_clip(context)

        if action is None or clip is None:
            return

        col = layout.column(align=True)

        row = col.row(align=True)
        # row.operator(UNITY_OT_refresh_indices.bl_idname)
        row.operator(UNITY_OT_new_clip.bl_idname)
        row1 = row.split()
        row1.operator(UNITY_OT_split_clip.bl_idname)
        row1 = row.split()
        row1.alert = True
        row1.operator(UNITY_OT_delete_clip.bl_idname)

        row = col.row(align=True)
        sf = context.scene.frame_current
        ss = context.scene.frame_start
        se = context.scene.frame_end
        s = clip.frame_start
        e = clip.frame_end

        row.enabled = ss != s or se != e
        row.alert = row.enabled
        clamp_button = row.operator(UNITY_OT_clamp_to_clip.bl_idname)
        play_button = row.operator(UNITY_OT_clamp_to_clip_and_play.bl_idname)

        row2 = row.split()
        row2.enabled = sf < s or sf < e
        set_button = row2.operator(UNITY_OT_Set_By_Current_Frame.bl_idname)

        if clip and clip.action:
            play_button.action_name = clip.action.name
            play_button.clip_name = clip.name
            clamp_button.action_name = clip.action.name
            clamp_button.clip_name = clip.name
            set_button.action_name = clip.action.name
            set_button.clip_name = clip.name

        row = col.row(align=True)
        row.operator(UNITY_OT_split_by_clip_all.bl_idname)
        row.operator(UNITY_OT_decorate_clips.bl_idname)
        row.operator(UNITY_OT_demarcate_clips.bl_idname)

        row = col.row(align=True)
        row.operator(UNITY_OT_Clamp_Keys.bl_idname)
        row.operator(UNITY_OT_remove_non_clip_keys.bl_idname)
        row.operator(UNITY_OT_bake_all_clips.bl_idname)


class _PT_Unity_005_All_Clips(_PT_Unity_Clips_List):
    bl_icon = UnitySettings.icon_all_clips
    bl_label = "All Unity Clips"

    @classmethod
    def do_poll(cls, context):
        return (
            DOIF.UNITY.MODE.SCENE(context)
            and DOIF.UNITY.TARGET.SET(context)
            and context.scene.unity_settings.draw_clips
        )

    def draw_template_list(self, context, layout):
        scene = context.scene
        rows = min(max(1, len(scene.all_unity_clips)), 5)
        layout.template_list(
            "UNITY_UL_UnityClips",
            "",
            scene,
            "all_unity_clips",
            scene.unity_settings,
            "clip_index",
            rows=rows,
        )


class _PT_Unity_005_All_Clips_000_Ops(_PT_Unity_Clips_Ops):
    bl_icon = UnitySettings.icon_operations
    bl_label = "Operations"


class _PT_Unity_010_Clips(_PT_Unity_Clips_List):
    bl_icon = UnitySettings.icon_clips
    bl_label = "Unity Clips"

    @classmethod
    def do_poll(cls, context):
        return (
            (not DOIF.UNITY.MODE.SCENE(context))
            and DOIF.UNITY.TARGET.SET(context)
            and context.scene.unity_settings.draw_clips
        )

    def draw_template_list(self, context, layout):
        obj = get_unity_target(context)
        action = obj.animation_data.action
        rows = min(max(1, len(action.unity_clips)), 5)

        layout.template_list(
            "UNITY_UL_UnityClips",
            "",
            action,
            "clips",
            action.unity_metadata,
            "clip_index",
            rows=rows,
        )


class _PT_Unity_010_Clips_000_Ops(_PT_Unity_Clips_Ops):
    bl_icon = UnitySettings.icon_operations
    bl_label = "Operations"


class _PT_Unity_020_Clip:
    bl_icon = UnitySettings.icon_clip
    bl_label = "Clip"

    @classmethod
    def do_poll(cls, context):
        obj = get_unity_target(context)
        anim_data = DOIF.UNITY.TARGET.SET(context)
        return anim_data and (
            DOIF.UNITY.MODE.SCENE(context)
            or (obj and obj.animation_data and obj.animation_data.action)
        )

    def finish_header(self, context, scene, layout, obj):
        obj = get_unity_target(context)
        action, clip, clip_index = get_unity_action_and_clip(context)
        if action is None or clip is None:
            return

        row = layout.row(align=True)

        row.label(text=clip.name)

        r2 = row.split()

        r2.alignment = "RIGHT"

        draw_settings = scene.unity_settings

        r2.prop(
            draw_settings,
            "draw_metadata",
            toggle=True,
            text="",
            icon=scene.unity_settings.icon_metadata,
        )
        r2.prop(
            draw_settings,
            "draw_root_motion",
            toggle=True,
            text="",
            icon=scene.unity_settings.icon_root_motion,
        )
        r2.prop(
            draw_settings,
            "draw_frames",
            toggle=True,
            text="",
            icon=scene.unity_settings.icon_frames,
        )
        r2.prop(
            draw_settings,
            "draw_pose",
            toggle=True,
            text="",
            icon=scene.unity_settings.icon_pose,
        )
        r2.prop(
            draw_settings,
            "draw_operations",
            toggle=True,
            text="",
            icon=scene.unity_settings.icon_operations,
        )

    def do_draw(self, context, scene, layout, obj):
        pass


class _PT_Unity_020_Clip_000_Metadata(CLIP_SUBPANEL_REQ):
    bl_icon = UnitySettings.icon_metadata
    bl_label = "Metadata"

    @classmethod
    def do_poll(cls, context):
        return cls.subpanel_poll(context) and context.scene.unity_settings.draw_metadata

    def finish_draw(self, context, scene, layout, obj, action, clip):
        obj = get_unity_target(context)
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)

        row_1 = row.split()
        row_1.enabled = False
        row_1.prop(clip, "action")

        row_2 = row.split()
        row_2.operator(UNITY_OT_sync_actions_with_clips.bl_idname, text="Sync")
        row_2.enabled = clip.action != clip.id_data

        row_3 = col.row(align=True)
        row_3.enabled = False
        row_3.prop(clip, "fbx_name")

        row_4 = col.row(align=True)
        row_4a = row_4.split()
        row_4a.prop(clip, "name")
        row_4a.enabled = clip.can_edit

        row_4b = row_4.split()
        row_4b.prop(clip, "can_edit", toggle=True, text="", icon=icons.UNLOCKED)
        row_4b.enabled = True


class _PT_Unity_020_Clip_020_Frames(CLIP_SUBPANEL_REQ):
    bl_icon = UnitySettings.icon_frames
    bl_label = "Frames"

    @classmethod
    def do_poll(cls, context):
        return cls.subpanel_poll(context) and context.scene.unity_settings.draw_frames

    def finish_draw(self, context, scene, layout, obj, action, clip):
        obj = get_unity_target(context)
        box = layout.box()
        col = box.column(align=True)

        row = col.row(align=True)
        row1 = row.split()
        # row1.alignment = 'LEFT'
        row1.prop(clip, "frame_start", text="Start")
        row1.prop(clip, "frame_end", text="Stop")
        row2 = row.split()
        row2.separator()
        # row2.alignment = 'RIGHT'
        row2.prop(clip, "loop_time", text="Loop?")


class _PT_Unity_020_Clip_040_Operation(CLIP_SUBPANEL_REQ):
    bl_icon = UnitySettings.icon_operation
    bl_label = "Operation"

    @classmethod
    def do_poll(cls, context):
        return (
            cls.subpanel_poll(context) and context.scene.unity_settings.draw_operations
        )

    def finish_draw(self, context, scene, layout, obj, action, clip):
        obj = get_unity_target(context)
        box = layout.box()
        col = box.column(align=True)

        row = col.row(align=True)
        row.operator(UNITY_OT_split_by_clip.bl_idname)
        row.operator(UNITY_OT_decorate_clip.bl_idname)
        row.operator(UNITY_OT_demarcate_clip.bl_idname)
        row = col.row(align=True)
        row.operator(UNITY_OT_bake_clip.bl_idname)


class VIEW_3D_PT_UI_Tool_Unity_000_Sheets(
    _PT_Unity_000_Sheets, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel
):
    bl_parent_id = VIEW_3D_PT_UI_Tool_Unity.bl_idname
    bl_idname = "VIEW_3D_PT_UI_Tool_Unity_000_Sheets"


class VIEW_3D_PT_UI_Tool_Unity_003_Keys(
    _PT_Unity_003_Keys, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel
):
    bl_parent_id = VIEW_3D_PT_UI_Tool_Unity.bl_idname
    bl_idname = "VIEW_3D_PT_UI_Tool_Unity_003_Keys"


class VIEW_3D_PT_UI_Tool_Unity_005_All_Clips(
    _PT_Unity_005_All_Clips, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel
):
    bl_parent_id = VIEW_3D_PT_UI_Tool_Unity.bl_idname
    bl_idname = "VIEW_3D_PT_UI_Tool_Unity_005_All_Clips"


class VIEW_3D_PT_UI_Tool_Unity_005_All_Clips_000_Ops(
    _PT_Unity_Clips_Ops, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel
):
    bl_parent_id = VIEW_3D_PT_UI_Tool_Unity_005_All_Clips.bl_idname
    bl_idname = "VIEW_3D_PT_UI_Tool_Unity_005_All_Clips_000_Ops"


class VIEW_3D_PT_UI_Tool_Unity_010_Clips(
    _PT_Unity_010_Clips, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel
):
    bl_parent_id = VIEW_3D_PT_UI_Tool_Unity.bl_idname
    bl_idname = "VIEW_3D_PT_UI_Tool_Unity_010_Clips"


class VIEW_3D_PT_UI_Tool_Unity_010_Clips_000_Ops(
    _PT_Unity_Clips_Ops, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel
):
    bl_parent_id = VIEW_3D_PT_UI_Tool_Unity_010_Clips.bl_idname
    bl_idname = "VIEW_3D_PT_UI_Tool_Unity_010_Clips_000_Ops"


class VIEW_3D_PT_UI_Tool_Unity_020_Clip(
    _PT_Unity_020_Clip, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel
):
    bl_parent_id = VIEW_3D_PT_UI_Tool_Unity.bl_idname
    bl_idname = "VIEW_3D_PT_UI_Tool_Unity_020_Clip"


class VIEW_3D_PT_UI_Tool_Unity_020_Clip_000_Metadata(
    _PT_Unity_020_Clip_000_Metadata, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel
):
    bl_parent_id = VIEW_3D_PT_UI_Tool_Unity_020_Clip.bl_idname
    bl_idname = "VIEW_3D_PT_UI_Tool_Unity_020_Clip_000_Metadata"


class VIEW_3D_PT_UI_Tool_Unity_020_Clip_020_Frames(
    _PT_Unity_020_Clip_020_Frames, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel
):
    bl_parent_id = VIEW_3D_PT_UI_Tool_Unity_020_Clip.bl_idname
    bl_idname = "VIEW_3D_PT_UI_Tool_Unity_020_Clip_020_Frames"


class VIEW_3D_PT_UI_Tool_Unity_020_Clip_040_Operation(
    _PT_Unity_020_Clip_040_Operation, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel
):
    bl_parent_id = VIEW_3D_PT_UI_Tool_Unity_020_Clip.bl_idname
    bl_idname = "VIEW_3D_PT_UI_Tool_Unity_020_Clip_040_Operation"


""" class DOPESHEET_EDITOR_PT_UI_Tool_Unity_000_Sheets(_PT_Unity_000_Sheets, UI.DOPESHEET_EDITOR.UI, PT_, bpy.types.Panel):
    bl_parent_id = DOPESHEET_EDITOR_PT_UI_Tool_Unity.bl_idname
    bl_idname = "DOPESHEET_EDITOR_PT_UI_Tool_Unity_000_Sheets"

class DOPESHEET_EDITOR_PT_UI_Tool_Unity_010_Clips(_PT_Unity_010_Clips,UI.DOPESHEET_EDITOR.UI, PT_, bpy.types.Panel):
    bl_parent_id = DOPESHEET_EDITOR_PT_UI_Tool_Unity.bl_idname
    bl_idname = "DOPESHEET_EDITOR_PT_UI_Tool_Unity_010_Clips" """


def register():
    bpy.types.Scene.unity_settings = bpy.props.PointerProperty(
        name="Unity Scene Settings", type=UnitySettings
    )
    bpy.types.Scene.all_unity_clips = bpy.props.CollectionProperty(
        name="All Unity Clips", type=UnityClipMetadata
    )
    bpy.types.Scene.unity_clip_filters = bpy.props.PointerProperty(
        name="Unity Clip Filters", type=Unity_UL_Filters
    )

    bpy.types.Action.unity_metadata = bpy.props.PointerProperty(
        name="Unity Metadata", type=UnityActionMetadata
    )
    bpy.types.Action.unity_clips = bpy.props.CollectionProperty(
        name="Unity Clips", type=UnityClipMetadata
    )


def unregister():
    del bpy.types.Scene.unity_settings
    del bpy.types.Scene.all_unity_clips
    del bpy.types.Scene.unity_clip_filters

    del bpy.types.Action.unity_metadata
    del bpy.types.Action.unity_clips
