from cspy.ui import PT_OPTIONS, PT_, UI
from cspy.polling import POLL
from cspy.bones_ops import *
from cspy.bones import *
from cspy.pose_correction import *
from cspy.pose_correction_ops import *
from cspy.timeline_ops import *

class _PT_PC_:
    @classmethod
    def do_poll(cls, context):
        return POLL.mode_POSE(context)

class VIEW_3D_PT_Pose_Correction(_PT_PC_, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel):
    bl_label = "Pose Correction"
    bl_idname = "VIEW_3D_PT_Pose_Correction"
    bl_icon = cspy.icons.GROUP_BONE

    def do_draw(self, context, scene, layout, obj):
        arm = context.active_object
        pose = arm.pose
        bone = context.active_pose_bone

        if bone:
            layout.label(text=bone.name,icon=cspy.icons.BONE_DATA)

class _PT_PC_AB:
    @classmethod
    def do_poll(cls, context):
        return POLL.mode_POSE(context) and POLL.active_pose_bone(context)
    
    def do_draw(self, context, scene, layout, obj):
        arm = context.active_object
        pose = arm.pose
        bone = context.active_pose_bone
        pose_correction = bone.pose_correction

        self.draw_pose_correction(context, scene, layout, obj, arm, pose, bone, pose_correction)

    def draw_lock(self, layout, alerting, pose_correction, pose, prop_name):
        row = layout.row(align=True)
        row.prop(pose_correction, '{0}_reference'.format(prop_name))

        row = layout.row(align=True)
        refop = row.operator(PC_OT_record_reference_from_bone.bl_idname)
        refop.prop_name = prop_name

        row = row.split()
        row.enabled = prop_name.lower() in ['location', 'transform']

        curop = row.operator(PC_OT_snap_cursor_to_reference.bl_idname)
        curop.prop_name = prop_name

        row = layout.row()
        row.alert = alerting
        lock_prop = '{0}_has_lock_bone'.format(prop_name)
        has_lock = getattr(pose_correction, lock_prop)
        
        row.prop(pose_correction, lock_prop, toggle=True, text='')
        
        row2 = row.split()
        row2.enabled = has_lock
        row2.prop_search(pose_correction, '{0}_lock_bone_name'.format(prop_name), pose, 'bones')

    def draw_clear(self, layout, alerting, pose_correction, pose, prop_name):
        pass
    
    def draw_location_negate(self, layout, alerting, pose_correction, pose):
        row = layout.row(align=True)
        row.prop(pose_correction, 'location_negate_type')

        nt = pose_correction.location_negate_type

        row = layout.row()
        row.alert = alerting
        row.prop_search(pose_correction, 'location_negate_bone_name', pose, 'bones', text='Bone')

        row = layout.row()

        if nt == 'OFFSET':
            row.prop(pose_correction, 'location_negate_co_offset', text='')
        elif nt == 'OBJECT':
            row.prop(pose_correction, 'location_negate_co_object', text='')
        elif nt == 'CANCEL':
            row.prop(pose_correction, 'location_negate_cancel_x', toggle=True, text='X')
            row.prop(pose_correction, 'location_negate_cancel_y', toggle=True, text='Y')
            row.prop(pose_correction, 'location_negate_cancel_z', toggle=True, text='Z')

    def draw_transform_negate(self, layout, alerting, pose_correction, pose):
        row = layout.row(align=True)
        row.prop(pose_correction, 'transform_negate_type')

        nt = pose_correction.transform_negate_type

        row = layout.row()
        row.alert = alerting
        row.prop_search(pose_correction, 'transform_negate_bone_name', pose, 'bones', text='Bone')


    def draw_influence(self, layout, valid, alerting, pose_correction, prop_name):
        row = layout.row(align=True)
        row.prop(pose_correction, prop_name)
        row.operator(PC_OT_insert_anchor_keyframe.bl_idname)

        row = layout.row(align=True)
        row.alert = alerting
        row.enabled = not row.alert and valid

    def draw_operator_buttons(self, layout, operator, alerting, prop_name):
        row = layout.row(align=True)
        row.alert = alerting
        row.operator(TIMELINE_OT_prev_frame.bl_idname, text='', icon=TIMELINE_OT_prev_frame.bl_icon)

        rwall = row.operator(operator, text='', icon=cspy.icons.PREV_KEYFRAME)
        rw    = row.operator(operator, text='', icon=cspy.icons.REW)
        cur   = row.operator(operator)
        ff    = row.operator(operator, text='', icon=cspy.icons.FF)
        ffall = row.operator(operator, text='', icon=cspy.icons.NEXT_KEYFRAME)
        
        row.operator(TIMELINE_OT_next_frame.bl_idname, text='', icon=TIMELINE_OT_next_frame.bl_icon)

        rwall.loop, rwall.advance, rwall.forward, rwall.prop_name = True,  True,  False, prop_name
        rw.loop,    rw.advance,    rw.forward   , rw.prop_name = False, True,  False, prop_name
        cur.loop,   cur.advance,   cur.forward  , cur.prop_name = False, False, False, prop_name
        ff.loop,    ff.advance,    ff.forward   , ff.prop_name = False, True,  True, prop_name
        ffall.loop, ffall.advance, ffall.forward, ffall.prop_name = True,  True,  True, prop_name

    def draw_pose_correction(self, context, scene, layout, obj, arm, pose, bone, pose_correction):
        prop_name = self.prop_name
        row = layout.row(align=True)
        alerting = pose_correction.get_poll_alert(arm, bone, prop_name)
        valid = pose_correction.get_poll_valid(context, prop_name)

        correction_type_prop = '{0}_correction_type'.format(prop_name)
        influence_prop = '{0}_influence'.format(prop_name)

        row.prop(pose_correction, correction_type_prop, text='Correction')

        correction_type = getattr(pose_correction, correction_type_prop)
        reference_frame = getattr(pose_correction, '{0}_reference_frame'.format(prop_name), 0)

        if correction_type == 'LOCK':            
            self.draw_lock(layout, alerting, pose_correction, pose, prop_name)
        elif correction_type == 'CLEAR':
            self.draw_clear(layout, alerting, pose_correction, pose, prop_name)
        elif correction_type == 'NEGATE':
            if prop_name == 'location':
                self.draw_location_negate(layout, alerting, pose_correction, pose)
            elif prop_name == 'transform':
                self.draw_transform_negate(layout, alerting, pose_correction, pose)

        self.draw_influence(layout, valid, alerting, pose_correction, influence_prop)
        self.draw_operator_buttons(layout, self.correct_op, scene.frame_current == reference_frame, prop_name)


class VIEW_3D_PT_Pose_Correction_01_LOC(_PT_PC_AB, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel):
    bl_label = "Location"
    bl_idname = "VIEW_3D_PT_Pose_Correction_01_LOC"
    bl_icon = cspy.icons.CON_LOCLIKE
    bl_parent_id = VIEW_3D_PT_Pose_Correction.bl_idname

    prop_name = 'location'
    correct_op = PC_OT_correct_pose_location.bl_idname

class VIEW_3D_PT_Pose_Correction_02_ROT(_PT_PC_AB, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel):
    bl_label = "Rotation"
    bl_idname = "VIEW_3D_PT_Pose_Correction_02_ROT"
    bl_icon = cspy.icons.CON_ROTLIKE
    bl_parent_id = VIEW_3D_PT_Pose_Correction.bl_idname

    prop_name = 'rotation'
    correct_op = PC_OT_correct_pose_rotation.bl_idname

class VIEW_3D_PT_Pose_Correction_04_TRN(_PT_PC_AB, UI.VIEW_3D.UI.Tool, PT_, bpy.types.Panel):
    bl_label = "Transform"
    bl_idname = "VIEW_3D_PT_Pose_Correction_04_TRN"
    bl_icon = cspy.icons.CON_TRANSFORM
    bl_parent_id = VIEW_3D_PT_Pose_Correction.bl_idname

    prop_name = 'transform'
    correct_op = PC_OT_correct_pose_transform.bl_idname

def register():
    bpy.types.PoseBone.pose_correction = bpy.props.PointerProperty(type=PoseCorrection)

def unregister():
    del bpy.types.PoseBone.pose_correction