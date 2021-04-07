import cspy
from cspy.ui import PT_OPTIONS, PT_, UI
from cspy.polling import POLL
from cspy import subtypes, root_motion
from cspy.root_motion import *
from cspy.root_motion_ops import *
from cspy.unity import *
from cspy.unity_ui import *
from cspy.cursor_ops import *

class _PT_RM_020_Clip_010_RootMotion(CLIP_SUBPANEL_REQ):
    bl_icon =  UnitySettings.icon_root_motion
    bl_label = 'Root Motion'

    @classmethod
    def do_poll(cls, context):
        return cls.subpanel_poll(context) and context.scene.unity_settings.draw_root_motion

    def draw_curve_buttons(self, layout, armature, root_motion):
        box = layout.box()
        row = box.row(align=True)
        row.operator(RM_OT_root_motion_settings_to_curves.bl_idname, icon=cspy.icons.CURVE_DATA)
        row.operator(RM_OT_root_motion_settings_to_curves_all.bl_idname, icon=cspy.icons.CURVE_PATH)
        row.separator()
        rows = row.split()
        rows.alignment='RIGHT'
        rows.operator(RM_OT_refresh_settings.bl_idname, icon=cspy.icons.FILE_REFRESH, text='')
        rows.operator(RM_OT_create_root_motion_setup.bl_idname, icon=cspy.icons.MOD_BUILD, text='')        
        rows.operator(RM_OT_root_motion_rest_all.bl_idname, icon=cspy.icons.ARMATURE_DATA, text='')
        rows.operator(RM_OT_root_motion_push_location_offsets_all.bl_idname, icon=cspy.icons.CON_LOCLIKE, text='')
        rows.operator(RM_OT_root_motion_push_rotation_offsets_all.bl_idname, icon=cspy.icons.ORIENTATION_GIMBAL, text='')

    def draw_root_node_start(self, layout, armature, root_motion):
        b = layout.box()
        h = b.row(align=True)
        h.prop_search(armature.root_motion_settings, 'original_root_bone', armature, 'bones', text='Original Root', icon=cspy.icons.BONE_DATA)
        h2 = h.split()
        h2.enabled = False
        h2.prop(armature.root_motion_settings, 'root_node')
        
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

        col1.prop(root_motion, 'root_node_start_location', text='')       
        col2.prop(root_motion, 'root_node_start_rotation', text='')
        col3r = col3.row()
        col3r.operator(RM_OT_root_motion_rest.bl_idname, icon=cspy.icons.POSE_HLT).operation='start'
        
        col3r = col3.row(align=True)        
        col3r.operator(CURSOR_OT_set_world.bl_idname,  icon=CURSOR_OT_set_world.bl_icon, text='')
        col3r.operator(CURSOR_OT_set_active.bl_idname, icon=CURSOR_OT_set_active.bl_icon, text='')       
        col3r.operator(CURSOR_OT_set_active_bone.bl_idname, icon=CURSOR_OT_set_active_bone.bl_icon, text='')    
        col3r.operator(RM_OT_root_motion_cursor.bl_idname, icon=cspy.icons.CURSOR).operation='start'
        
        col3a = col3.split()
        col3a.alert = alert
        col3a.operator(RM_OT_root_motion_reset.bl_idname, icon=cspy.icons.CANCEL).operation='start' 

    def draw_root_motion_settings(self, layout, armature, root_motion):        
        col = layout.column()  
        r0, r1, r2, r3 = col.row(), col.row(), col.row(), col.row()  
        col.separator()      
        r4 = col.row()

        r0.label(text='Bake')
        r0.label(text='Offset')
        r0.label(text='Limit (min)')
        r0.label(text='Limit (max)')

        self.draw_root_xyz_component(r1, root_motion, 'x')
        self.draw_root_xyz_component(r2, root_motion, 'y')
        self.draw_root_xyz_component(r3, root_motion, 'z')

        r4.alert = root_motion.root_motion_rot_offset != 0.0
        r4.prop(root_motion, 'root_motion_rot_bake_into',toggle=True,text='',icon=cspy.icons.ORIENTATION_GIMBAL)
       
        r4.prop(root_motion, 'root_motion_rot_offset', text='Rot. Offset')  
        r4.separator()
        r4.operator(RM_OT_root_motion_reset.bl_idname, icon=cspy.icons.CANCEL).operation='settings'

    def draw_root_xyz_component(self, layout, root_motion, axis):
        l = axis.lower()
        u = axis.upper()
        icon= 'EVENT_{0}'.format(u)
        pre = 'root_motion_{0}_'.format(l)

        layout.prop(root_motion, '{0}bake_into'.format(pre), icon=icon, text='', toggle=True) 
        
        prop_name = '{0}offset'.format(pre)

        val = getattr(root_motion, prop_name)

        row = layout.row()

        if val != 0:
            row.alert = True

        row.prop(root_motion, prop_name, text=u)         

        limits = [('limit_neg', '-'), ('limit_pos', '+')]
        limit_props = [ ( 
            '{0}{1}'.format(pre, limit[0]), 
            '{0}{1}_val'.format(pre, limit[0]), 
            limit[1] 
            ) for limit in limits]

        for limit_prop in limit_props:
            r = layout.row()  
            r.prop(root_motion, limit_prop[0], text='', toggle=True, icon=cspy.icons.CON_LOCLIMIT)        
            r = r.split()
            r.enabled = getattr(root_motion, limit_prop[0], False)
            r.alert = getattr(root_motion, limit_prop[0]) != 0
            r.prop(root_motion, limit_prop[1], text='Limit {0}'.format(limit_prop[2]))
  
    def draw_bone_offset(self, layout, armature, root_motion, bone):       
         
        br = layout.row()
        br.enabled = False
        br.prop_search(armature.root_motion_settings, 
            '{0}_bone_name'.format(bone), armature, 'bones', text=bone.capitalize(), icon=cspy.icons.BONE_DATA)
        br.prop_search(armature.root_motion_settings, 
            '{0}_bone_offset'.format(bone), bpy.data, 'objects', text='Offset', icon=cspy.icons.OBJECT_DATA)
            
        offr = layout.row()
        c1 = offr.column()
        c2 = offr.column()

        self.draw_bone_start_end(c1, armature, root_motion, bone, 'start')
        self.draw_bone_start_end(c2, armature, root_motion, bone, 'end')
      
    def draw_bone_start_end(self, layout, armature, root_motion, bone, phase):
        p1 = '{0}_bone_offset_location_{1}'.format(bone, phase)
        p2 = '{0}_bone_offset_rotation_{1}'.format(bone, phase)
        operation = '{0}_{1}'.format(bone,phase)
        phase = phase.capitalize()        
        alert = False

        def draw_value_row(p, text, alerting):
            r = layout.row(align=True)
            v = getattr(root_motion, p)   
            r.prop(root_motion, p, text=text)   

            alerting = alerting or max([1 if c != 0.0 else 0.0 for c in v])

            return alerting

        alert = draw_value_row(p1, 'Loc ({0})'.format(phase), alert)  
        alert = draw_value_row(p2, 'Rot ({0})'.format(phase), alert)        

        row = layout.row(align=True)

        row.operator(RM_OT_root_motion_rest.bl_idname, icon=cspy.icons.POSE_HLT).operation = operation
        row.separator()
        
        row.operator(CURSOR_OT_set_world.bl_idname,  icon=CURSOR_OT_set_world.bl_icon, text='')
        row.operator(CURSOR_OT_set_active.bl_idname, icon=CURSOR_OT_set_active.bl_icon, text='')       
        row.operator(CURSOR_OT_set_active_bone.bl_idname, icon=CURSOR_OT_set_active_bone.bl_icon, text='')    
        row.operator(RM_OT_root_motion_cursor.bl_idname, icon=cspy.icons.CURSOR).operation = operation
        
        row.separator()
        r2 = row.split()
        r2.alert = alert
        r2.operator(RM_OT_root_motion_reset.bl_idname, icon=cspy.icons.CANCEL).operation = operation
        
  
    def finish_draw(self, context, scene, layout, obj, action, unity_clip):
        obj = get_active_unity_object(context)
        armature = obj.data
        root_motion = unity_clip.root_motion
        self.draw_curve_buttons(layout, armature, root_motion)
       
        self.draw_root_node_start(layout, armature, root_motion)
        
        self.draw_root_motion_settings(layout, armature, root_motion)

        self.draw_bone_offset(layout.box(), armature, root_motion, 'root')
        self.draw_bone_offset(layout.box(), armature, root_motion, 'hip')

class _PT_RM_020_Clip_030_Pose(CLIP_SUBPANEL_REQ):
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
        start_apply_start = col1.operator(RM_OT_apply_pose.bl_idname,text='To Start')

        col2 = row.column(align=True)
        col2.enabled = context.scene.frame_current != context.scene.frame_start
        start_apply_current = col2.operator(RM_OT_apply_pose.bl_idname,text='To Current')

        col3 = row.column(align=True)
        col3.enabled = not unity_clip.pose_start.startswith(unity_clip.name)
        start_new_current = col3.operator(RM_OT_new_pose.bl_idname,text='From Current')

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
        end_apply_end = col1.operator(RM_OT_apply_pose.bl_idname,text='To End')

        col2 = row.column(align=True)
        col2.enabled = context.scene.frame_current != context.scene.frame_end
        end_apply_current = col2.operator(RM_OT_apply_pose.bl_idname,text='To Current')

        col3 = row.column(align=True)
        col3.enabled = not unity_clip.pose_end.endswith(unity_clip.name)
        end_new_current = col3.operator(RM_OT_new_pose.bl_idname,text='From Current')

        end_apply_end.pose_name = unity_clip.pose_end
        end_apply_end.frame = unity_clip.frame_end
        end_apply_end.rooted = unity_clip.pose_end_rooted
        end_apply_current.pose_name = unity_clip.pose_end
        end_apply_current.frame = context.scene.frame_current
        end_apply_current.rooted = unity_clip.pose_end_rooted
        end_new_current.start = False
        end_new_current.frame = context.scene.frame_current

class VIEW_3D_PT_UI_Tool_RM_020_Clip_010_RootMotion(_PT_RM_020_Clip_010_RootMotion, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel):
    bl_parent_id = VIEW_3D_PT_UI_Tool_Unity_020_Clip.bl_idname
    bl_idname = "VIEW_3D_PT_UI_Tool_RM_020_Clip_010_RootMotion"

class VIEW_3D_PT_UI_Tool_RM_020_Clip_030_Pose(_PT_RM_020_Clip_030_Pose, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel):
    bl_parent_id = VIEW_3D_PT_UI_Tool_Unity_020_Clip.bl_idname
    bl_idname = "VIEW_3D_PT_UI_Tool_RM_020_Clip_030_Pose"



def register():
    bpy.types.Armature.root_motion_settings = bpy.props.PointerProperty(name='Root Motion Settings', type=ArmatureRootMotionSettings)

def unregister():
    del bpy.types.Armature.root_motion_settings