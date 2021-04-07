import bpy, cspy
from bpy.types import Operator
from cspy import ops, polling, unity, unity_keys, unity_clips, timeline
from cspy.ops import OPS_, OPS_DIALOG
from cspy.polling import POLL
from cspy.unity import *
from cspy.unity_clips import *
from cspy.timeline import *
from cspy.bones import *
from cspy.root_motion import *
from cspy.root_motion_mech import *


class RM_OT_refresh_settings(OPS_, Operator):
    bl_idname='rm.refresh_settings'
    bl_label = "Refresh and Transfer Root Motion Settings"

    @classmethod
    def do_poll(cls, context):
        return POLL.data_actions(context)
    
    def do_execute(self, context):
        for action in bpy.data.actions:
            if action.unity_clips:
                for clip in action.unity_clips:
                    clip.root_motion.copy_from_clip(clip)
        for armature in bpy.data.armatures:
            if armature.root_motion_settings:
                armature.root_motion_settings.copy_from_armature(armature)


class RM_OT_create_root_motion_setup(OPS_, Operator):
    bl_idname='rm.create_root_motion_setup'
    bl_label = "Create Root Motion Mech Rig"

    @classmethod
    def do_poll(cls, context):
        ao = get_active_unity_object(context)
        if not ao:
            return False        
        s = ao.data.root_motion_settings
        if not s:
            return False

        if s.original_root_bone == '':
            return False

        return True
    
    def do_execute(self, context):
        bpy.ops.rm.root_motion_settings_to_curves_all()

        create_root_motion_setup(context, get_active_unity_object(context))

class RM_OT_rm_curves:
    group_name = 'Root Motion Settings'

    @classmethod
    def do_poll(cls, context):
        return POLL.data_actions(context)

    def process_action(self, context, action):
        if len(action.unity_clips) != 1:
            return
    
        obj = get_active_unity_object(context)

        sync_with_scene_mode(context)

        clip = action.unity_clips[0]

        for ci, fcurve in cspy.iters.reverse_enumerate(action.fcurves):
            if fcurve.group and fcurve.group.name == self.group_name:
                for ki, key in cspy.iters.reverse_enumerate(fcurve.keyframe_points):
                    fcurve.keyframe_points.remove(key)
                action.fcurves.remove(fcurve)
                
        keys = RootMotionMetadata.root_motion_keys

        updated_paths = []

        for data_path in keys:
            value = getattr(clip.root_motion, data_path)
            has_length = getattr(value, '__len__', None)
            index_values = []

            if has_length:
                for i, v in enumerate(value):
                    index_values.append((i, v))
            else:
                index_values.append((-1, value))
            
            for i, v in index_values:
                path = data_path
                if i != -1:
                    path = '{0}_{1}'.format(data_path, i)

                if data_path.endswith('_start'):
                    path = path.replace('_start', '')
                elif data_path.endswith('_end'):
                    path = path.replace('_end','')

                updated_paths.append(path)
                fcurve = action.fcurves.find(path, index=-1)
                    
                if not fcurve:
                    fcurve = action.fcurves.new(path, index=-1, action_group=self.group_name)

                if not getattr(bpy.types.Object, path, None):                    
                    setattr(bpy.types.Object, path, bpy.props.FloatProperty(name=path))

                setattr(obj, path, v)

                s = clip.frame_start
                e = clip.frame_end+1

                if data_path.endswith('_start'):
                    k = cspy.actions.insert_keyframe(fcurve, s, v, needed=False, fast=True)
                elif data_path.endswith('_end'):
                    k = cspy.actions.insert_keyframe(fcurve, e, v, needed=False, fast=True)
                else:
                    k = cspy.actions.insert_keyframe(fcurve, s, v, needed=False, fast=True)
                    k = cspy.actions.insert_keyframe(fcurve, e, v, needed=False, fast=True)

        for data_path in updated_paths:
            fcurve = action.fcurves.find(data_path, index=-1)
            if fcurve is None:
                continue
            fcurve.update()

class RM_OT_root_motion_settings_to_curves(RM_OT_rm_curves, OPS_, Operator):
    """Adds animation curves for root motion settings."""
    bl_idname = "rm.root_motion_settings_to_curves"
    bl_label = "To Curves"

    def do_execute(self, context):
        obj = get_active_unity_object(context)
        action, clip = get_unity_action_and_clip(context)

        if action:
            self.process_action(context, action)

        return {'FINISHED'}

class RM_OT_root_motion_settings_to_curves_all(RM_OT_rm_curves, OPS_, Operator):
    """Adds animation curves for root motion settings to all actions."""
    bl_idname = "rm.root_motion_settings_to_curves_all"
    bl_label = "To Curves (All)"

    def do_execute(self, context):
        for action in bpy.data.actions:
            self.process_action(context, action)

        return {'FINISHED'}

class RM_OT_options:
    target: bpy.props.StringProperty('Target')
    operation: bpy.props.StringProperty('Operation')
    phase: bpy.props.StringProperty('Phase')

class RM_OT_root_offset:

    def do_execute(self, context):
        obj = get_active_unity_object(context)
        action, clip = get_unity_action_and_clip(context)

        root_bone_name = obj.data.root_motion_settings.hip_bone_name if self.operation == 'hip_start' or self.operation == 'hip_end' else obj.data.root_motion_settings.root_bone_name
        bone = obj.pose.bones.get(root_bone_name)

        self.set_offset(context, obj, action, clip, bone)
        
        bpy.ops.rm.root_motion_settings_to_curves()

        return {'FINISHED'}

def print_loc(prefix, loc):
    string = '[{0}]  x:{1}m,  y:{2}m,  z:{3}m'.format(
        prefix,
        loc.x,
        loc.y, 
        loc.z)
    print(string)

def print_quat(prefix, quat, order = 'XYZ'):
    euler = quat.to_euler(order)
    string = '[{0}]  x:{1},  y:{2},  z:{3}'.format(
        prefix,
        math.degrees(euler.x), 
        math.degrees(euler.y), 
        math.degrees(euler.z))
    print(string)

class RM_OT_root_motion_reset(RM_OT_root_offset, OPS_, Operator):
    """Resets the offset property."""
    bl_idname = "rm.root_offset_to_reset"
    bl_label = "Reset"

    def set_offset(self, context, armature, action, clip, root_pose_bone):
        if self.operation == 'start':
            clip.root_motion.root_node_start_location = [0,0,0]
            clip.root_motion.root_node_start_rotation = [0,0,0]
            
        elif self.operation == 'settings':
            clip.root_motion.root_motion_x_offset = 0
            clip.root_motion.root_motion_y_offset = 0
            clip.root_motion.root_motion_z_offset = 0
            clip.root_motion.root_motion_rot_offset = 0
            
        elif self.operation == 'root_start':
            clip.root_motion.root_bone_offset_location_start = [0,0,0]
            clip.root_motion.root_bone_offset_rotation_start = [0,0,0]
            
        elif self.operation == 'hip_start':
            clip.root_motion.hip_bone_offset_location_start = [0,0,0]
            clip.root_motion.hip_bone_offset_rotation_start = [0,0,0]
            
        elif self.operation == 'root_end':
            clip.root_motion.root_bone_offset_location_end = [0,0,0]
            clip.root_motion.root_bone_offset_rotation_end = [0,0,0]
            
        elif self.operation == 'hip_end':
            clip.root_motion.hip_bone_offset_location_end = [0,0,0]
            clip.root_motion.hip_bone_offset_rotation_end = [0,0,0]
            

class RM_OT_root_motion_set:
    def set_offset(self, context, armature, action, clip, pose_bone):
        pose_matrix, rest_matrix = self.get_matrices(context, armature, action, clip, pose_bone)
            
        pose_loc,pose_quat,_ = pose_matrix.decompose()
        rest_loc,rest_quat,_ = rest_matrix.decompose()

        diff_loc = rest_loc - pose_loc

        diff_rot = pose_quat.rotation_difference(rest_quat)
        diff_euler = diff_rot.to_euler('XYZ')

        set_loc, set_rot = clip.root_motion.root_node_start_location, clip.root_motion.root_node_start_rotation

        if self.operation == 'root_start':
            set_loc, set_rot = clip.root_motion.root_bone_offset_location_start, clip.root_motion.root_bone_offset_rotation_start
        elif self.operation == 'hip_start':
            set_loc, set_rot = clip.root_motion.hip_bone_offset_location_start, clip.root_motion.hip_bone_offset_rotation_start
        if self.operation == 'root_end':
            set_loc, set_rot = clip.root_motion.root_bone_offset_location_end, clip.root_motion.root_bone_offset_rotation_end
        elif self.operation == 'hip_end':
            set_loc, set_rot = clip.root_motion.hip_bone_offset_location_end, clip.root_motion.hip_bone_offset_rotation_end
        
        set_loc[0] = diff_loc[0]
        set_loc[1] = diff_loc[1]
        set_loc[2] = diff_loc[2]
        
        set_rot[0] = diff_euler.x
        set_rot[1] = diff_euler.y
        set_rot[2] = diff_euler.z

class RM_OT_root_motion_rest(RM_OT_root_motion_set, RM_OT_root_offset, OPS_, Operator):
    """Sets the root motion offset to return the root to its rest position."""
    bl_idname = "rm.root_offset_to_rest"
    bl_label = "To Rest"

    def  get_matrices(self, context, armature, action, clip, pose_bone):
        if self.operation == 'start':
            pose_matrix = armature.data.root_motion_settings.root_node.matrix_world
            rest_matrix = armature.matrix_world
        elif self.operation == 'root_start' or self.operation == 'root_end':
            pose_matrix = get_pose_bone_matrix_world(armature, pose_bone.name)
            rest_matrix = get_pose_bone_rest_matrix_world(armature, pose_bone.name)
        elif self.operation == 'hip_start' or self.operation == 'hip_end':
            pose_matrix = get_pose_bone_matrix_world(armature, pose_bone.name)
            rest_matrix = get_pose_bone_rest_matrix_world(armature, pose_bone.name)

        return pose_matrix, rest_matrix

class RM_OT_root_motion_cursor(RM_OT_root_motion_set, RM_OT_root_offset, OPS_, Operator):
    """Sets the root motion offset to return the root to the cursor."""
    bl_idname = "rm.root_offset_to_cursor"
    bl_label = "To Cursor"

    def  get_matrices(self, context, armature, action, clip, pose_bone):

        if self.operation == 'start':
            pose_matrix = armature.data.root_motion_settings.root_node.matrix_world
        elif self.operation == 'root_start' or self.operation == 'root_end':
            pose_matrix = armature.data.root_motion_settings.root_bone_offset.matrix_world
        elif self.operation == 'hip_start' or self.operation == 'hip_end':
            pose_matrix = armature.data.root_motion_settings.hip_bone_offset.matrix_world

        cursor = context.scene.cursor
        rest_matrix = cursor.matrix

        return pose_matrix, rest_matrix
            

class RM_OT_root_motion_scene:

    operation: bpy.props.StringProperty('Operation')

    @classmethod
    def do_poll(cls, context):
        return context.scene.unity_settings.mode == 'SCENE'
        
    def do_execute(self, context):        
        armature = get_active_unity_object(context)
        original_action, original_clip = get_unity_action_and_clip(context)

        root_bone_name = armature.data.root_motion_settings.hip_bone_name if self.operation == 'hip_start' or self.operation == 'hip_end' else armature.data.root_motion_settings.root_bone_name
        bone = armature.pose.bones.get(root_bone_name)

        context.scene.frame_set(1)
        scene = context.scene
        clips = scene.all_unity_clips

        for index in range(len(clips)):
            clip = clips[index]
            action = clip.action

            self.process_clip(context, armature, action, clip, index, bone)
        
        return {'FINISHED'}


class RM_OT_root_motion_rest_all(RM_OT_root_motion_scene, RM_OT_root_motion_set, OPS_, Operator):
    """Sets the root motion offset to return the root to its rest position for all scene clips."""
    bl_idname = "rm.root_offset_to_rest_all"
    bl_label = "To Rest (All)"
    
    operation: bpy.props.StringProperty('Operation')
    def process_clip(self, context, armature, action, clip, index, pose_bone):

        apply_clip_by_index(context, index)
        
        self.set_offset(context, armature, action, clip, pose_bone)
    
    def get_matrices(self, context, armature, action, clip, pose_bone):

        pose_matrix = armature.data.root_motion_settings.root_node.matrix_world
        rest_matrix = armature.matrix_world
         
        return pose_matrix, rest_matrix
            
class RM_OT_root_motion_push_rotation_offsets_all(RM_OT_root_motion_scene, OPS_, Operator):

    """Pushes rotation offsets to be applied to the root and hip bones for correction."""
    bl_idname = "rm.root_motion_push_rotation_offsets_all"
    bl_label = "Push Rotation Offsets"

    def process_clip(self, context, armature, action, clip, index, pose_bone):
        
        r = math.radians(clip.root_motion.root_motion_rot_offset)
        clip.root_motion.root_bone_offset_rotation_start.z = r
        clip.root_motion.root_bone_offset_rotation_end.z = r
        clip.root_motion.hip_bone_offset_rotation_start.z = r
        clip.root_motion.hip_bone_offset_rotation_end.z = r

class RM_OT_root_motion_push_location_offsets_all(RM_OT_root_motion_scene, OPS_, Operator):
    """Pushes location offsets to be applied to the root and hip bones for correction."""
    bl_idname = "rm.root_motion_push_location_offsets_all"
    bl_label = "Push Location Offsets"

    def process_clip(self, context, armature, action, clip, index, pose_bone):
        rm = clip.root_motion

        rm.hip_bone_offset_location_start.x = rm.root_node_start_location.x
        rm.hip_bone_offset_location_start.y = rm.root_node_start_location.y
        rm.hip_bone_offset_location_end.x = rm.root_node_start_location.x
        rm.hip_bone_offset_location_end.y = rm.root_node_start_location.y

