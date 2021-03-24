import cspy
from cspy.unity import *
from cspy.unity_ops import *
from cspy.unity_ul import *
from cspy.ui import PT_OPTIONS, PT_, UI
from cspy.polling import POLL
from cspy import subtypes


class UNITY_PANEL:
    bl_label = "Unity"
    bl_icon = cspy.icons.FILE_3D

    @classmethod
    def do_poll(cls, context):
        return POLL.active_object_animation_data(context)

class VIEW_3D_PT_UI_Tool_Unity(UNITY_PANEL, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel):
    bl_idname = "VIEW_3D_PT_UI_Tool_Unity"

    def do_draw(self, context, scene, layout, obj):
        pass

class DOPESHEET_EDITOR_PT_UI_Tool_Unity(UNITY_PANEL, UI.DOPESHEET_EDITOR.UI, PT_, bpy.types.Panel):
    bl_idname = "DOPESHEET_EDITOR_PT_UI_Tool_Unity"

    def do_draw(self, context, scene, layout, obj):
        pass

class UNITY_SUBPANEL():
    @classmethod
    def do_poll(cls, context):
        return True

class _PT_Unity_00_Sheets(UNITY_SUBPANEL):
    bl_icon = cspy.icons.FILE
    bl_label = 'Unity Sheets'

    def do_draw(self, context, scene, layout, obj):    
        layout.prop(scene, 'unity_sheet_dir_path')
        row = layout.row(align=True)
        row.operator(UNITY_OT_refresh_clip_data.bl_idname)
        row.operator(UNITY_OT_refresh_clip_data_all.bl_idname)
        row = layout.row(align=True)
        row.operator(UNITY_OT_clear_clip_data.bl_idname)
        row.operator(UNITY_OT_clear_clip_data_all.bl_idname)
        row = layout.row(align=True)
        row.operator(UNITY_OT_sort_clip_data.bl_idname)
        row.operator(UNITY_OT_sort_clip_data_all.bl_idname)
        row = layout.row(align=True)
        row.operator(UNITY_OT_demarcate_clips.bl_idname)
        row.operator(UNITY_OT_update_master_clip_metadata.bl_idname)
        row = layout.row(align=True)
        row.operator(UNITY_OT_remove_non_clip_keys.bl_idname)
        row = layout.row(align=True)
        row.prop(context.active_object.animation_data.action, 'unity_clip_template')
        row.operator(UNITY_OT_copy_clips_from_template.bl_idname)

class _PT_Unity_01_Clips(UNITY_SUBPANEL):
    bl_icon = cspy.icons.SEQ_SEQUENCER
    bl_label = 'Unity Clips'

    def do_draw(self, context, scene, layout, obj):
        action = obj.animation_data.action

        layout.template_list("UNITY_UL_UnityClips", "", action, "unity_clips", action, "unity_index", rows=2,maxrows=4)
    
_icon_metadata = cspy.icons.MESH_DATA
_icon_root_motion = cspy.icons.CON_FOLLOWPATH
_icon_frames = cspy.icons.CAMERA_DATA
_icon_pose = cspy.icons.ARMATURE_DATA
_icon_delete = cspy.icons.GHOST_DISABLED

class _PT_Unity_02_Clip(UNITY_SUBPANEL):
    bl_icon = cspy.icons.SEQUENCE
    bl_label = 'Clip'

    def do_draw(self, context, scene, layout, obj):
        action = obj.animation_data.action
        unity_clip = action.unity_clips[action.unity_index]     
        
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)

        row.label(text=unity_clip.name)   

        row.alignment='RIGHT'

        draw_settings = scene.unity_clip_draw_settings

        row.prop(draw_settings, 'draw_metadata',toggle=True, text='', icon=_icon_metadata)
        row.prop(draw_settings, 'draw_root_motion',toggle=True, text='', icon=_icon_root_motion)
        row.prop(draw_settings, 'draw_frames',toggle=True, text='', icon=_icon_frames)
        row.prop(draw_settings, 'draw_pose',toggle=True, text='', icon=_icon_pose)
        row.prop(draw_settings, 'draw_delete',toggle=True, text='', icon=_icon_delete)

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
        
        if context.scene.unity_clip_draw_settings.draw_delete:
            row = col.row(align=True)
            row.alert = True
            row.operator(UNITY_OT_delete_clip.bl_idname)


class _CLIP_SUBPANEL(UNITY_SUBPANEL):
    def do_draw(self, context, scene, layout, obj):
        action = obj.animation_data.action
        unity_clip = action.unity_clips[action.unity_index]

        self.finish_draw(context, scene, layout, obj, action, unity_clip)


class _PT_Unity_02_Clip_00_Metadata(_CLIP_SUBPANEL):
    bl_icon = _icon_metadata
    bl_label = 'Metadata'

    @classmethod
    def do_poll(cls, context):
        return context.scene.unity_clip_draw_settings.draw_metadata

    def finish_draw(self, context, scene, layout, obj, action, unity_clip):
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        row_1 = row.split()
        row_1.enabled = False
        row_1.prop(unity_clip, 'action')
        row_2 = row.split()
        row_2.operator(UNITY_OT_sync_actions_with_clips.bl_idname, text='Sync')
        row_2.enabled = (unity_clip.action != unity_clip.id_data)
        col = box.column(align=True)
        col.prop(unity_clip, 'fbx_name')
        col.prop(unity_clip, 'name')
        col.enabled = False
            

class _PT_Unity_02_Clip_01_RootMotion(_CLIP_SUBPANEL):
    bl_icon = _icon_root_motion
    bl_label = 'Root Motion'

    @classmethod
    def do_poll(cls, context):
        return context.scene.unity_clip_draw_settings.draw_root_motion

    def finish_draw(self, context, scene, layout, obj, action, unity_clip):
        box = layout.box()
        col = box.column(align=True)

        col.separator()
        row = col.row(align=True)
        row.prop(unity_clip, 'rot_bake_into',text='Bake Rot.')
        row.prop(unity_clip, 'y_bake_into', text='Bake Y')
        row.prop(unity_clip, 'xz_bake_into', text='Bake XZ')

        col.separator()
        row = col.row(align=True)
        row.prop(unity_clip, 'rot_offset', text='Rot. Offset')
        row.prop(unity_clip, 'y_offset', text='Y Offset')


class _PT_Unity_02_Clip_02_Frames(_CLIP_SUBPANEL):
    bl_icon = _icon_frames
    bl_label = 'Frames'

    @classmethod
    def do_poll(cls, context):
        return context.scene.unity_clip_draw_settings.draw_frames

    def finish_draw(self, context, scene, layout, obj, action, unity_clip):
        box = layout.box()
        col = box.column(align=True)
        
        row = col.row(align=True)
        row.prop(unity_clip, 'frame_start', text='Start')
        row.prop(unity_clip, 'frame_end', text='Stop')
        row.prop(unity_clip, 'loop_time', text='Loop?')

class _PT_Unity_02_Clip_03_Pose(_CLIP_SUBPANEL):
    bl_icon = _icon_pose
    bl_label = 'Pose'

    @classmethod
    def do_poll(cls, context):
        return context.scene.unity_clip_draw_settings.draw_pose

    def finish_draw(self, context, scene, layout, obj, action, unity_clip):
        box = layout.box()    
        
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
             


class VIEW_3D_PT_UI_Tool_Unity_00_Sheets(_PT_Unity_00_Sheets, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel):
    bl_parent_id = VIEW_3D_PT_UI_Tool_Unity.bl_idname
    bl_idname = "VIEW_3D_PT_UI_Tool_Unity_00_Sheets"

class VIEW_3D_PT_UI_Tool_Unity_01_Clips(_PT_Unity_01_Clips, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel):
    bl_parent_id = VIEW_3D_PT_UI_Tool_Unity.bl_idname
    bl_idname = "VIEW_3D_PT_UI_Tool_Unity_01_Clips"

class VIEW_3D_PT_UI_Tool_Unity_02_Clip(_PT_Unity_02_Clip, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel):
    bl_parent_id = VIEW_3D_PT_UI_Tool_Unity.bl_idname
    bl_idname = "VIEW_3D_PT_UI_Tool_Unity_02_Clip"

class VIEW_3D_PT_UI_Tool_Unity_02_Clip_00_Metadata(_PT_Unity_02_Clip_00_Metadata, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel):
    bl_parent_id = VIEW_3D_PT_UI_Tool_Unity_02_Clip.bl_idname
    bl_idname = "VIEW_3D_PT_UI_Tool_Unity_02_Clip_00_Metadata"

class VIEW_3D_PT_UI_Tool_Unity_02_Clip_01_RootMotion(_PT_Unity_02_Clip_01_RootMotion, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel):
    bl_parent_id = VIEW_3D_PT_UI_Tool_Unity_02_Clip.bl_idname
    bl_idname = "VIEW_3D_PT_UI_Tool_Unity_02_Clip_01_RootMotion"

class VIEW_3D_PT_UI_Tool_Unity_02_Clip_02_Frames(_PT_Unity_02_Clip_02_Frames, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel):
    bl_parent_id = VIEW_3D_PT_UI_Tool_Unity_02_Clip.bl_idname
    bl_idname = "VIEW_3D_PT_UI_Tool_Unity_02_Clip_02_Frames"

class VIEW_3D_PT_UI_Tool_Unity_02_Clip_03_Pose(_PT_Unity_02_Clip_03_Pose, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel):
    bl_parent_id = VIEW_3D_PT_UI_Tool_Unity_02_Clip.bl_idname
    bl_idname = "VIEW_3D_PT_UI_Tool_Unity_02_Clip_03_Pose"


""" class DOPESHEET_EDITOR_PT_UI_Tool_Unity_00_Sheets(_PT_Unity_00_Sheets, UI.DOPESHEET_EDITOR.UI, PT_, bpy.types.Panel):
    bl_parent_id = DOPESHEET_EDITOR_PT_UI_Tool_Unity.bl_idname
    bl_idname = "DOPESHEET_EDITOR_PT_UI_Tool_Unity_00_Sheets"

class DOPESHEET_EDITOR_PT_UI_Tool_Unity_01_Clips(_PT_Unity_01_Clips,UI.DOPESHEET_EDITOR.UI, PT_, bpy.types.Panel):
    bl_parent_id = DOPESHEET_EDITOR_PT_UI_Tool_Unity.bl_idname
    bl_idname = "DOPESHEET_EDITOR_PT_UI_Tool_Unity_01_Clips" """


def _update_unity_index(self, context):
    action = context.active_object.animation_data.action
    clip = action.unity_clips[action.unity_index]

    context.scene.frame_start = clip.frame_start
    context.scene.frame_end = clip.frame_end
    context.scene.frame_current = clip.frame_start


def register():
    bpy.types.Scene.unity_sheet_dir_path = bpy.props.StringProperty(name="Sheet Dir Path", subtype=subtypes.StringProperty.Subtypes.DIR_PATH)
    bpy.types.Scene.unity_clip_draw_settings = bpy.props.PointerProperty(name="Unity Clip Draw Settings", type=UnityClipDrawSettings)
    
    bpy.types.Action.unity_clip_template = bpy.props.PointerProperty(name="Unity Clip Template", type=bpy.types.Action)
    bpy.types.Action.unity_clips = bpy.props.CollectionProperty(name="Unity Clips", type=UnityClipMetadata)
    bpy.types.Action.unity_index = bpy.props.IntProperty(name='Unity Index', default = 0, min=0, update=_update_unity_index)
    bpy.types.Action.unity_clips_protected = bpy.props.BoolProperty(name='Unity Clips Protected', default=False)
    bpy.types.Object.rot_bake_into = bpy.props.IntProperty(name="rot_bake_into", min=0,max=1,default=1)
    bpy.types.Object.rot_offset = bpy.props.FloatProperty(name="rot_offset", default=0.0)
    bpy.types.Object.y_bake_into = bpy.props.IntProperty(name="y_bake_into", min=0,max=1,default=1)
    bpy.types.Object.y_offset = bpy.props.FloatProperty(name="y_offset", default=0.0)
    bpy.types.Object.xz_bake_into = bpy.props.IntProperty(name="xz_bake_into", min=0,max=1,default=1)

def unregister():
    del bpy.types.Scene.unity_sheet_dir_path
    del bpy.types.Scene.unity_clip_draw_settings
    del bpy.types.Action.unity_clip_template
    del bpy.types.Action.unity_clips
    del bpy.types.Action.unity_index
    del bpy.types.Action.unity_clips_protected
    del bpy.types.Object.rot_bake_into
    del bpy.types.Object.rot_offset
    del bpy.types.Object.y_bake_into
    del bpy.types.Object.y_offset
    del bpy.types.Object.xz_bake_into