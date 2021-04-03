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
        return POLL.active_unity_object(context)

        
    def do_draw(self, context, scene, layout, obj):
        obj = get_active_unity_object(context)
        unity_settings = scene.unity_settings

        col = layout.column(align=True)
        row = col.row(align=True)

        row.prop(unity_settings, 'mode')

        row.separator()

        if unity_settings.mode != 'ACTIVE':
            row.prop_search(unity_settings, 'target_armature', bpy.data, 'objects', text='', icon=cspy.icons.ARMATURE_DATA)
        
        row.separator()
        row.prop(unity_settings, 'draw_sheets', toggle=True, text='', icon=unity_settings.icon_sheets)
        row.prop(unity_settings, 'draw_keyframes', toggle=True, text='', icon=unity_settings.icon_keys)
        row.prop(unity_settings, 'draw_clips', toggle=True, text='', icon=unity_settings.icon_clips)
        
        obj = get_active_unity_object(context)

        if obj:
            row.separator()
            row.prop(obj.data, "pose_position", expand=True)


class _CLIP_SUBPANEL_REQ():
    @classmethod
    def subpanel_poll(cls, context):
        obj = get_active_unity_object(context)
        return (
                POLL.active_unity_object(context) and 
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
        return POLL.active_unity_object(context)

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
        return POLL.active_unity_object(context) and context.scene.unity_settings.draw_sheets

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
        return POLL.active_unity_object(context) and context.scene.unity_settings.draw_keyframes

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
        return POLL.unity_mode_SCENE(context) and POLL.active_unity_object(context) and context.scene.unity_settings.draw_clips

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
        return (not POLL.unity_mode_SCENE(context)) and POLL.active_unity_object(context) and context.scene.unity_settings.draw_clips

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
        anim_data = POLL.active_unity_object(context)
        return ( anim_data and (POLL.unity_mode_SCENE(context) or (obj and obj.animation_data and obj.animation_data.action)))

    def finish_header(self, context, scene, layout, obj):
        obj = get_active_unity_object(context)
        action, unity_clip = get_unity_action_and_clip(context)
        if action is None or unity_clip is None:
            return

        row = layout.row(align=True)

        row.label(text=unity_clip.name)

        r2 = row.split()

        r2.alignment='RIGHT'

        draw_settings = scene.unity_settings

        r2.prop(draw_settings, 'draw_metadata',toggle=True, text='', icon=scene.unity_settings.icon_metadata)
        r2.prop(draw_settings, 'draw_root_motion',toggle=True, text='', icon=scene.unity_settings.icon_root_motion)
        r2.prop(draw_settings, 'draw_frames',toggle=True, text='', icon=scene.unity_settings.icon_frames)
        r2.prop(draw_settings, 'draw_pose',toggle=True, text='', icon=scene.unity_settings.icon_pose)
        r2.prop(draw_settings, 'draw_operations',toggle=True, text='', icon=scene.unity_settings.icon_operations)

    def do_draw(self, context, scene, layout, obj):
        pass

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

    def draw_root_xyz_component(self, layout, unity_clip, axis):
        l = axis.lower()
        u = axis.upper()
        icon= 'EVENT_{0}'.format(u)
        pre = 'root_motion_{0}_'.format(l)

        layout.prop(unity_clip, '{0}bake_into'.format(pre), icon=icon, text='', toggle=True) 
        
        prop_name = '{0}offset'.format(pre)

        val = getattr(unity_clip, prop_name)

        row = layout.row()

        if val != 0:
            row.alert = True

        row.prop(unity_clip, prop_name, text=u)         

        limits = [('limit_neg', '-'), ('limit_pos', '+')]
        limit_props = [ ( 
            '{0}{1}'.format(pre, limit[0]), 
            '{0}{1}_val'.format(pre, limit[0]), 
            limit[1] 
            ) for limit in limits]

        for limit_prop in limit_props:
            r = layout.row()  
            r.prop(unity_clip, limit_prop[0], text='', toggle=True, icon=cspy.icons.CON_LOCLIMIT)        
            r = r.split()
            r.enabled = getattr(unity_clip, limit_prop[0], False)
            r.alert = getattr(unity_clip, limit_prop[0]) != 0
            r.prop(unity_clip, limit_prop[1], text='Limit {0}'.format(limit_prop[2]))

    def draw_root_node_start(self, layout, armature, unity_clip):
        layout.prop_search(armature, 'original_root_node', bpy.data, 'objects', text='Original Root', icon=cspy.icons.BONE_DATA)
        
        b = layout.box()
        h = b.row(align=True)
        h.alignment='CENTER'
        h.label(text='Root Node Start')

        r = b.row()
        col1 = r.column(align=True)
        col2 = r.column(align=True)
        col3 = r.column(align=True)

        alert = False
        val = unity_clip.root_node_start_location
        if val[0] != 0 or val[1] != 0 or val[2] != 0:
            alert = True
        val = unity_clip.root_node_start_rotation
        if val[0] != 0 or val[1] != 0 or val[2] != 0:
            alert = True

        col1.prop(unity_clip, 'root_node_start_location', text='')       
        col2.prop(unity_clip, 'root_node_start_rotation', text='')
        col3.operator(UNITY_OT_root_motion_rest.bl_idname, icon=cspy.icons.POSE_HLT).operation='start'
        col3.operator(UNITY_OT_root_motion_cursor.bl_idname, icon=cspy.icons.CURSOR).operation='start'
        col3a = col3.split()
        col3a.alert = alert
        col3a.operator(UNITY_OT_root_motion_reset.bl_idname, icon=cspy.icons.CANCEL).operation='start' 

    def draw_root_motion_settings(self, layout, armature, unity_clip):        
        col = layout.column()  
        r0, r1, r2, r3 = col.row(), col.row(), col.row(), col.row()  
        col.separator()      
        r4 = col.row()

        r0.label(text='Bake')
        r0.label(text='Offset')
        r0.label(text='Limit (min)')
        r0.label(text='Limit (max)')

        self.draw_root_xyz_component(r1, unity_clip, 'x')
        self.draw_root_xyz_component(r2, unity_clip, 'y')
        self.draw_root_xyz_component(r3, unity_clip, 'z')

        r4.alert = unity_clip.root_motion_rot_offset != 0.0
        r4.prop(unity_clip, 'root_motion_rot_bake_into',toggle=True,text='',icon=cspy.icons.ORIENTATION_GIMBAL)
       
        r4.prop(unity_clip, 'root_motion_rot_offset', text='Rot. Offset')  
        r4.separator()
        r4.operator(UNITY_OT_root_motion_reset.bl_idname, icon=cspy.icons.CANCEL).operation='settings'

    def draw_bone_start_end(self, layout, armature, unity_clip, bone, phase):
        p1 = '{0}_bone_offset_location_{1}'.format(bone, phase)
        p2 = '{0}_bone_offset_rotation_{1}'.format(bone, phase)
        operation = '{0}_{1}'.format(bone,phase)
        phase = phase.capitalize()        
        alert = False

        def draw_value_row(p, text, alerting):
            r = layout.row(align=True)
            v = getattr(unity_clip, p)   
            r.prop(unity_clip, p, text=text)   

            alerting = alerting or max([1 if c != 0.0 else 0.0 for c in v])

            return alerting

        alert = draw_value_row(p1, 'Loc ({0})'.format(phase), alert)  
        alert = draw_value_row(p2, 'Rot ({0})'.format(phase), alert)        

        row = layout.row(align=True)

        row.operator(UNITY_OT_root_motion_rest.bl_idname, icon=cspy.icons.POSE_HLT).operation = operation
        row.operator(UNITY_OT_root_motion_cursor.bl_idname, icon=cspy.icons.CURSOR).operation = operation
        r2 = row.split()
        r2.alert = alert
        r2.operator(UNITY_OT_root_motion_reset.bl_idname, icon=cspy.icons.CANCEL).operation = operation
        
    def draw_bone_offset(self, layout, armature, unity_clip, bone):       
         
        br = layout.row()

        br.prop_search(armature, 
            '{0}_bone_name'.format(bone), armature, 'bones', text=bone.capitalize(), icon=cspy.icons.BONE_DATA)
        br.prop_search(armature, 
            '{0}_bone_offset'.format(bone), bpy.data, 'objects', text='Offset', icon=cspy.icons.OBJECT_DATA)
            
        offr = layout.row()
        c1 = offr.column()
        c2 = offr.column()

        self.draw_bone_start_end(c1, armature, unity_clip, bone, 'start')
        self.draw_bone_start_end(c2, armature, unity_clip, bone, 'end')
        
    def draw_curve_buttons(self, layout, armature, unity_clip):
        box = layout.box()
        row = box.row(align=True)
        row.operator(UNITY_OT_root_motion_settings_to_curves.bl_idname, icon=cspy.icons.CURVE_DATA)
        row.operator(UNITY_OT_root_motion_settings_to_curves_all.bl_idname, icon=cspy.icons.CURVE_PATH)

  
    def finish_draw(self, context, scene, layout, obj, action, unity_clip):
        obj = get_active_unity_object(context)
        armature = obj.data
        self.draw_curve_buttons(layout, armature, unity_clip)
       
        self.draw_root_node_start(layout, armature, unity_clip)
        
        self.draw_root_motion_settings(layout, armature, unity_clip)

        self.draw_bone_offset(layout.box(), armature, unity_clip, 'root')
        self.draw_bone_offset(layout.box(), armature, unity_clip, 'hip')


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


    bpy.types.Armature.original_root_node = bpy.props.PointerProperty(name='Original Root Node', type=bpy.types.Object)
    bpy.types.Armature.root_bone_name = bpy.props.StringProperty(name='Root Bone Name')
    bpy.types.Armature.root_bone_offset = bpy.props.PointerProperty(name='Root Bone Offset', type=bpy.types.Object)
    bpy.types.Armature.hip_bone_name = bpy.props.StringProperty(name='Hip Bone Name')
    bpy.types.Armature.hip_bone_offset = bpy.props.PointerProperty(name='Hip Bone Offset', type=bpy.types.Object)

    bpy.types.Action.unity_metadata = bpy.props.PointerProperty(name="Unity Metadata", type=UnityActionMetadata)
    bpy.types.Action.unity_clips = bpy.props.CollectionProperty(name="Unity Clips", type=UnityClipMetadata)




def unregister():
    del bpy.types.Scene.unity_settings
    del bpy.types.Scene.all_unity_clips
    del bpy.types.Scene.unity_clip_filters


    del bpy.types.Armature.original_root_node
    del bpy.types.Armature.root_bone_name
    del bpy.types.Armature.root_bone_offset    
    del bpy.types.Armature.hip_bone_name
    del bpy.types.Armature.hip_bone_offset

    del bpy.types.Action.unity_metadata
    del bpy.types.Action.unity_clips
