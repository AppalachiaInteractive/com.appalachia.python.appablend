import cspy
from cspy.unity import *
from cspy.unity_ops import *
from cspy.unity_ul import *
from cspy.timeline_ops import *
from cspy.ui import PT_OPTIONS, PT_, UI
from cspy.polling import POLL
from cspy import subtypes

class UNITY_PANEL:
    bl_label = "Unity"
    bl_icon = UnitySettings.icon_unity

    @classmethod
    def do_poll(cls, context):
        return POLL.active_object_animation_data(context)

    def do_draw(self, context, scene, layout, obj):
        obj = get_active_unity_object(context)
        unity_settings = scene.unity_settings

        col = layout.column(align=True)
        row = col.row(align=True)

        row.prop(unity_settings, 'mode')

        row.prop(unity_settings, 'draw_sheets', toggle=True, text='', icon=unity_settings.icon_sheets)
        row.prop(unity_settings, 'draw_keyframes', toggle=True, text='', icon=unity_settings.icon_keys)
        row.prop(unity_settings, 'draw_clips', toggle=True, text='', icon=unity_settings.icon_clips)

        if unity_settings.mode != 'ACTIVE':
            row = col.row(align=True)
            row.prop(unity_settings, 'target_armature')

class _CLIP_SUBPANEL_REQ():
    @classmethod
    def subpanel_poll(cls, context):
        obj = get_active_unity_object(context)
        return (
                POLL.active_object_animation_data(context) and
                (POLL.unity_mode_SCENE(context) or obj is not None)
            )

    def do_draw(self, context, scene, layout, obj):
        obj = get_active_unity_object(context)
        action, unity_clip = get_unity_action_and_clip(context)

        if action is None or unity_clip is None:
            return

        self.finish_draw(context, scene, layout, obj, action, unity_clip)

class _CLIP_SUBPANEL():
    @classmethod
    def subpanel_poll(cls, context):
        return POLL.active_object_animation_data(context)

    def do_draw(self, context, scene, layout, obj):
        obj = get_active_unity_object(context)
        action, unity_clip = get_unity_action_and_clip(context)

        self.finish_draw(context, scene, layout, obj, action, unity_clip)

class VIEW_3D_PT_UI_Tool_Unity(UNITY_PANEL, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel):
    bl_idname = "VIEW_3D_PT_UI_Tool_Unity"

class DOPESHEET_EDITOR_PT_UI_Tool_Unity(UNITY_PANEL, UI.DOPESHEET_EDITOR.UI, PT_, bpy.types.Panel):
    bl_idname = "DOPESHEET_EDITOR_PT_UI_Tool_Unity"

class _PT_Unity_000_Sheets():
    bl_icon =  UnitySettings.icon_sheets
    bl_label = 'Unity Sheets'

    @classmethod
    def do_poll(cls, context):
        return POLL.active_object_animation_data(context) and context.scene.unity_settings.draw_sheets

    def do_draw(self, context, scene, layout, obj):
        obj = get_active_unity_object(context)
        layout.prop(scene.unity_settings, 'sheet_dir_path')
        row = layout.row(align=True)
        row.operator(UNITY_OT_refresh_clip_data.bl_idname)
        row.operator(UNITY_OT_refresh_clip_data_all.bl_idname)
        row = layout.row(align=True)
        row.operator(UNITY_OT_clear_clip_data.bl_idname)
        row.operator(UNITY_OT_clear_clip_data_all.bl_idname)
        row = layout.row(align=True)
        row.operator(UNITY_OT_sort_clip_data.bl_idname)
        row.operator(UNITY_OT_sort_clip_data_all.bl_idname)

        if obj and obj.animation_data.action:
            row = layout.row(align=True)
            row.prop(obj.animation_data.action, 'unity_clip_template')
            row.operator(UNITY_OT_copy_clips_from_template.bl_idname)

class _PT_Unity_003_Keys():
    bl_icon =  UnitySettings.icon_keys
    bl_label = 'Unity Keyframes'

    @classmethod
    def do_poll(cls, context):
        return POLL.active_object_animation_data(context) and context.scene.unity_settings.draw_keyframes

    def do_draw(self, context, scene, layout, obj):
        obj = get_active_unity_object(context)
        layout.prop(scene.unity_settings, 'key_dir_path')
        row = layout.row(align=True)
        row.operator(UNITY_OT_refresh_key_data.bl_idname)
        row.operator(UNITY_OT_refresh_key_data_all.bl_idname)

class _PT_Unity_Clips_List:
    def do_draw(self, context, scene, layout, obj):
        self.draw_template_list(context, layout)

class _PT_Unity_Clips_Ops:
    bl_icon = UnitySettings.icon_operations
    bl_label = 'Operations'

    @classmethod
    def do_poll(cls, context):
        return POLL.active_unity_object(context)

    def do_draw(self, context, scene, layout, obj):

        action, unity_clip = get_unity_action_and_clip(context)
        col = layout.column(align=True)

        row = col.row(align=True)
        #row.operator(UNITY_OT_refresh_indices.bl_idname)
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
        s = unity_clip.frame_start
        e = unity_clip.frame_end

        row.enabled = ss != s or se != e
        row.alert = row.enabled
        clamp_button = row.operator(UNITY_OT_clamp_to_clip.bl_idname)
        play_button = row.operator(UNITY_OT_clamp_to_clip_and_play.bl_idname)

        row2 = row.split()
        row2.enabled = sf < s or sf < e
        set_button = row2.operator(UNITY_OT_Set_By_Current_Frame.bl_idname)

        if unity_clip and unity_clip.action:
            play_button.action_name = unity_clip.action.name
            play_button.clip_name = unity_clip.name
            clamp_button.action_name = unity_clip.action.name
            clamp_button.clip_name = unity_clip.name
            set_button.action_name = unity_clip.action.name
            set_button.clip_name = unity_clip.name


        row = col.row(align=True)
        row.operator(UNITY_OT_split_by_clip_all.bl_idname)
        row.operator(UNITY_OT_decorate_clips.bl_idname)
        row.operator(UNITY_OT_demarcate_clips.bl_idname)

        row = col.row(align=True)
        row.operator(UNITY_OT_Clamp_Keys.bl_idname)
        row.operator(UNITY_OT_remove_non_clip_keys.bl_idname)
        row.operator(UNITY_OT_bake_all_clips.bl_idname)


class _PT_Unity_005_All_Clips(_PT_Unity_Clips_List):
    bl_icon =  UnitySettings.icon_all_clips
    bl_label = 'All Unity Clips'

    @classmethod
    def do_poll(cls, context):
        return POLL.unity_mode_SCENE(context) and POLL.active_object_animation_data(context) and context.scene.unity_settings.draw_clips

    def draw_template_list(self, context, layout):
        scene = context.scene
        rows = min(max(1, len(scene.all_unity_clips)), 5)
        layout.template_list("UNITY_UL_UnityClips", "", scene, "all_unity_clips", scene.unity_settings, "clip_index", rows=rows)

class _PT_Unity_005_All_Clips_000_Ops(_PT_Unity_Clips_Ops):
    bl_icon =  UnitySettings.icon_operations
    bl_label = 'Operations'

class _PT_Unity_010_Clips(_PT_Unity_Clips_List):
    bl_icon =  UnitySettings.icon_clips
    bl_label = 'Unity Clips'

    @classmethod
    def do_poll(cls, context):
        return (not POLL.unity_mode_SCENE(context)) and POLL.active_object_animation_data(context) and context.scene.unity_settings.draw_clips

    def draw_template_list(self, context, layout):
        obj = get_active_unity_object(context)
        action = obj.animation_data.action
        rows = min(max(1, len(action.unity_clips)), 5)

        layout.template_list("UNITY_UL_UnityClips", "", action, "unity_clips", action.unity_metadata, "clip_index", rows=rows)

class _PT_Unity_010_Clips_000_Ops(_PT_Unity_Clips_Ops):
    bl_icon =  UnitySettings.icon_operations
    bl_label = 'Operations'

class _PT_Unity_020_Clip():
    bl_icon =  UnitySettings.icon_clip
    bl_label = 'Clip'

    @classmethod
    def do_poll(cls, context):
        obj = get_active_unity_object(context)
        anim_data = POLL.active_object_animation_data(context)
        return ( anim_data and (POLL.unity_mode_SCENE(context) or (obj and obj.animation_data and obj.animation_data.action)))

    def do_draw(self, context, scene, layout, obj):
        obj = get_active_unity_object(context)
        action, unity_clip = get_unity_action_and_clip(context)
        if action is None or unity_clip is None:
            return

        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)

        row.label(text=unity_clip.name)

        row.alignment='RIGHT'

        draw_settings = scene.unity_settings

        row.prop(draw_settings, 'draw_metadata',toggle=True, text='', icon=scene.unity_settings.icon_metadata)
        row.prop(draw_settings, 'draw_root_motion',toggle=True, text='', icon=scene.unity_settings.icon_root_motion)
        row.prop(draw_settings, 'draw_frames',toggle=True, text='', icon=scene.unity_settings.icon_frames)
        row.prop(draw_settings, 'draw_pose',toggle=True, text='', icon=scene.unity_settings.icon_pose)
        row.prop(draw_settings, 'draw_operations',toggle=True, text='', icon=scene.unity_settings.icon_operations)

class _PT_Unity_020_Clip_000_Metadata(_CLIP_SUBPANEL_REQ):
    bl_icon =  UnitySettings.icon_metadata
    bl_label = 'Metadata'

    @classmethod
    def do_poll(cls, context):
        return cls.subpanel_poll(context) and context.scene.unity_settings.draw_metadata

    def finish_draw(self, context, scene, layout, obj, action, unity_clip):
        obj = get_active_unity_object(context)
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)

        row_1 = row.split()
        row_1.enabled = False
        row_1.prop(unity_clip, 'action')

        row_2 = row.split()
        row_2.operator(UNITY_OT_sync_actions_with_clips.bl_idname, text='Sync')
        row_2.enabled = (unity_clip.action != unity_clip.id_data)

        row_3 = col.row(align=True)
        row_3.enabled = False
        row_3.prop(unity_clip, 'fbx_name')

        row_4 = col.row(align=True)
        row_4a = row_4.split()
        row_4a.prop(unity_clip, 'name')
        row_4a.enabled = unity_clip.can_edit

        row_4b = row_4.split()
        row_4b.prop(unity_clip, 'can_edit', toggle=True, text='', icon=cspy.icons.UNLOCKED)
        row_4b.enabled = True

class _PT_Unity_020_Clip_010_RootMotion(_CLIP_SUBPANEL_REQ):
    bl_icon =  UnitySettings.icon_root_motion
    bl_label = 'Root Motion'

    @classmethod
    def do_poll(cls, context):
        return cls.subpanel_poll(context) and context.scene.unity_settings.draw_root_motion

    def finish_draw(self, context, scene, layout, obj, action, unity_clip):
        obj = get_active_unity_object(context)
        box = layout.box()
        col = box.column(align=True)

        col.separator()
        row = col.row(align=True)
        row.prop(unity_clip, 'root_motion_rot_bake_into',text='Bake Rot.')
        row.prop(unity_clip, 'root_motion_rot_offset', text='Rot. Offset')
        row = col.row(align=True)
        row.prop(unity_clip, 'root_motion_x_bake_into', text='Bake X')
        row.prop(unity_clip, 'root_motion_x_offset', text='X Offset')
        row = col.row(align=True)
        row.prop(unity_clip, 'root_motion_y_bake_into', text='Bake Y')
        row.prop(unity_clip, 'root_motion_y_offset', text='Y Offset')
        row = col.row(align=True)
        row.prop(unity_clip, 'root_motion_z_bake_into', text='Bake Z')
        row.prop(unity_clip, 'root_motion_z_offset', text='Z Offset')

        row = col.row(align=True)
        row.label(text="Root Offset")
        row.prop(unity_clip, 'root_offset_x', text='')
        row.prop(unity_clip, 'root_offset_y', text='')
        row.prop(unity_clip, 'root_offset_z', text='')

        col.separator()
        row = col.row(align=True)
        row.operator(UNITY_OT_root_motion_settings_to_curves.bl_idname)
        row.operator(UNITY_OT_root_motion_settings_to_curves_all.bl_idname)

class _PT_Unity_020_Clip_020_Frames(_CLIP_SUBPANEL_REQ):
    bl_icon =  UnitySettings.icon_frames
    bl_label = 'Frames'

    @classmethod
    def do_poll(cls, context):
        return cls.subpanel_poll(context) and context.scene.unity_settings.draw_frames

    def finish_draw(self, context, scene, layout, obj, action, unity_clip):
        obj = get_active_unity_object(context)
        box = layout.box()
        col = box.column(align=True)

        row = col.row(align=True)
        row1 = row.split()
        #row1.alignment = 'LEFT'
        row1.prop(unity_clip, 'frame_start', text='Start')
        row1.prop(unity_clip, 'frame_end', text='Stop')
        row2 = row.split()
        row2.separator()
        #row2.alignment = 'RIGHT'
        row2.prop(unity_clip, 'loop_time', text='Loop?')

class _PT_Unity_020_Clip_030_Pose(_CLIP_SUBPANEL_REQ):
    bl_icon =  UnitySettings.icon_pose
    bl_label = 'Pose'

    @classmethod
    def do_poll(cls, context):
        return cls.subpanel_poll(context) and context.scene.unity_settings.draw_pose

    def finish_draw(self, context, scene, layout, obj, action, unity_clip):
        obj = get_active_unity_object(context)
        box = layout.box()

        if obj.pose_library is None:
            return

        row = box.row(align=True)
        row.prop_search(unity_clip, 'pose_start', obj.pose_library, 'pose_markers', text='Start')
        row = row.split()
        row.alignment = 'RIGHT'
        row.prop(unity_clip, 'pose_start_rooted', text='Root?')

        row = box.row(align=True)
        col1 = row.column(align=True)
        start_apply_start = col1.operator(UNITY_OT_apply_pose.bl_idname,text='To Start')

        col2 = row.column(align=True)
        col2.enabled = context.scene.frame_current != context.scene.frame_start
        start_apply_current = col2.operator(UNITY_OT_apply_pose.bl_idname,text='To Current')

        col3 = row.column(align=True)
        col3.enabled = not unity_clip.pose_start.startswith(unity_clip.name)
        start_new_current = col3.operator(UNITY_OT_new_pose.bl_idname,text='From Current')

        start_apply_start.pose_name = unity_clip.pose_start
        start_apply_start.frame = unity_clip.frame_start
        start_apply_start.rooted = unity_clip.pose_start_rooted
        start_apply_current.pose_name = unity_clip.pose_start
        start_apply_current.frame = context.scene.frame_current
        start_apply_current.rooted = unity_clip.pose_start_rooted
        start_new_current.start = True
        start_new_current.frame = context.scene.frame_current

        row = box.row(align=True)
        row.prop_search(unity_clip, 'pose_end', obj.pose_library, 'pose_markers', text='End')
        row = row.split()
        row.alignment = 'RIGHT'
        row.prop(unity_clip, 'pose_end_rooted', text='Root?')

        row = box.row(align=True)
        col1 = row.column(align=True)
        end_apply_end = col1.operator(UNITY_OT_apply_pose.bl_idname,text='To End')

        col2 = row.column(align=True)
        col2.enabled = context.scene.frame_current != context.scene.frame_end
        end_apply_current = col2.operator(UNITY_OT_apply_pose.bl_idname,text='To Current')

        col3 = row.column(align=True)
        col3.enabled = not unity_clip.pose_end.endswith(unity_clip.name)
        end_new_current = col3.operator(UNITY_OT_new_pose.bl_idname,text='From Current')

        end_apply_end.pose_name = unity_clip.pose_end
        end_apply_end.frame = unity_clip.frame_end
        end_apply_end.rooted = unity_clip.pose_end_rooted
        end_apply_current.pose_name = unity_clip.pose_end
        end_apply_current.frame = context.scene.frame_current
        end_apply_current.rooted = unity_clip.pose_end_rooted
        end_new_current.start = False
        end_new_current.frame = context.scene.frame_current

class _PT_Unity_020_Clip_040_Operation(_CLIP_SUBPANEL_REQ):
    bl_icon =  UnitySettings.icon_operation
    bl_label = 'Operation'

    @classmethod
    def do_poll(cls, context):
        return cls.subpanel_poll(context) and context.scene.unity_settings.draw_operations

    def finish_draw(self, context, scene, layout, obj, action, unity_clip):
        obj = get_active_unity_object(context)
        box = layout.box()
        col = box.column(align=True)

        row = col.row(align=True)
        row.operator(UNITY_OT_split_by_clip.bl_idname)
        row.operator(UNITY_OT_decorate_clip.bl_idname)
        row.operator(UNITY_OT_demarcate_clip.bl_idname)
        row = col.row(align=True)
        row.operator(UNITY_OT_bake_clip.bl_idname)

class VIEW_3D_PT_UI_Tool_Unity_000_Sheets(_PT_Unity_000_Sheets, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel):
    bl_parent_id = VIEW_3D_PT_UI_Tool_Unity.bl_idname
    bl_idname = "VIEW_3D_PT_UI_Tool_Unity_000_Sheets"

class VIEW_3D_PT_UI_Tool_Unity_003_Keys(_PT_Unity_003_Keys, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel):
    bl_parent_id = VIEW_3D_PT_UI_Tool_Unity.bl_idname
    bl_idname = "VIEW_3D_PT_UI_Tool_Unity_003_Keys"

class VIEW_3D_PT_UI_Tool_Unity_005_All_Clips(_PT_Unity_005_All_Clips, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel):
    bl_parent_id = VIEW_3D_PT_UI_Tool_Unity.bl_idname
    bl_idname = "VIEW_3D_PT_UI_Tool_Unity_005_All_Clips"

class VIEW_3D_PT_UI_Tool_Unity_005_All_Clips_000_Ops(_PT_Unity_Clips_Ops, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel):
    bl_parent_id = VIEW_3D_PT_UI_Tool_Unity_005_All_Clips.bl_idname
    bl_idname = "VIEW_3D_PT_UI_Tool_Unity_005_All_Clips_000_Ops"

class VIEW_3D_PT_UI_Tool_Unity_010_Clips(_PT_Unity_010_Clips, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel):
    bl_parent_id = VIEW_3D_PT_UI_Tool_Unity.bl_idname
    bl_idname = "VIEW_3D_PT_UI_Tool_Unity_010_Clips"

class VIEW_3D_PT_UI_Tool_Unity_010_Clips_000_Ops(_PT_Unity_Clips_Ops, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel):
    bl_parent_id = VIEW_3D_PT_UI_Tool_Unity_010_Clips.bl_idname
    bl_idname = "VIEW_3D_PT_UI_Tool_Unity_010_Clips_000_Ops"

class VIEW_3D_PT_UI_Tool_Unity_020_Clip(_PT_Unity_020_Clip, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel):
    bl_parent_id = VIEW_3D_PT_UI_Tool_Unity.bl_idname
    bl_idname = "VIEW_3D_PT_UI_Tool_Unity_020_Clip"

class VIEW_3D_PT_UI_Tool_Unity_020_Clip_000_Metadata(_PT_Unity_020_Clip_000_Metadata, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel):
    bl_parent_id = VIEW_3D_PT_UI_Tool_Unity_020_Clip.bl_idname
    bl_idname = "VIEW_3D_PT_UI_Tool_Unity_020_Clip_000_Metadata"

class VIEW_3D_PT_UI_Tool_Unity_020_Clip_010_RootMotion(_PT_Unity_020_Clip_010_RootMotion, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel):
    bl_parent_id = VIEW_3D_PT_UI_Tool_Unity_020_Clip.bl_idname
    bl_idname = "VIEW_3D_PT_UI_Tool_Unity_020_Clip_010_RootMotion"

class VIEW_3D_PT_UI_Tool_Unity_020_Clip_020_Frames(_PT_Unity_020_Clip_020_Frames, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel):
    bl_parent_id = VIEW_3D_PT_UI_Tool_Unity_020_Clip.bl_idname
    bl_idname = "VIEW_3D_PT_UI_Tool_Unity_020_Clip_020_Frames"

class VIEW_3D_PT_UI_Tool_Unity_020_Clip_030_Pose(_PT_Unity_020_Clip_030_Pose, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel):
    bl_parent_id = VIEW_3D_PT_UI_Tool_Unity_020_Clip.bl_idname
    bl_idname = "VIEW_3D_PT_UI_Tool_Unity_020_Clip_030_Pose"

class VIEW_3D_PT_UI_Tool_Unity_020_Clip_040_Operation(_PT_Unity_020_Clip_040_Operation, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel):
    bl_parent_id = VIEW_3D_PT_UI_Tool_Unity_020_Clip.bl_idname
    bl_idname = "VIEW_3D_PT_UI_Tool_Unity_020_Clip_040_Operation"



""" class DOPESHEET_EDITOR_PT_UI_Tool_Unity_000_Sheets(_PT_Unity_000_Sheets, UI.DOPESHEET_EDITOR.UI, PT_, bpy.types.Panel):
    bl_parent_id = DOPESHEET_EDITOR_PT_UI_Tool_Unity.bl_idname
    bl_idname = "DOPESHEET_EDITOR_PT_UI_Tool_Unity_000_Sheets"

class DOPESHEET_EDITOR_PT_UI_Tool_Unity_010_Clips(_PT_Unity_010_Clips,UI.DOPESHEET_EDITOR.UI, PT_, bpy.types.Panel):
    bl_parent_id = DOPESHEET_EDITOR_PT_UI_Tool_Unity.bl_idname
    bl_idname = "DOPESHEET_EDITOR_PT_UI_Tool_Unity_010_Clips" """



def register():
    bpy.types.Scene.unity_settings = bpy.props.PointerProperty(name="Unity Scene Settings", type=UnitySettings)
    bpy.types.Scene.all_unity_clips = bpy.props.CollectionProperty(name='All Unity Clips', type=UnityClipMetadata)
    bpy.types.Scene.unity_clip_filters = bpy.props.PointerProperty(name='Unity Clip Filters', type=Unity_UL_Filters)


    bpy.types.Action.unity_metadata = bpy.props.PointerProperty(name="Unity Metadata", type=UnityActionMetadata)
    bpy.types.Action.unity_clips = bpy.props.CollectionProperty(name="Unity Clips", type=UnityClipMetadata)

    for key in UnityClipMetadata.root_motion_keys:
        if key.endswith('bake_into'):
            prop = bpy.props.IntProperty(name=key, min=0,max=1,default=1)
        else:
            prop = bpy.props.FloatProperty(name=key, default=0.0)

        setattr(bpy.types.Object, key, prop)


def unregister():
    del bpy.types.Scene.unity_settings
    del bpy.types.Scene.all_unity_clips
    del bpy.types.Scene.unity_clip_filters

    del bpy.types.Action.unity_metadata
    del bpy.types.Action.unity_clips

    for key in UnityClipMetadata.root_motion_keys:
        prop = getattr(bpy.types.Object, key, None)
        if prop:
            del prop