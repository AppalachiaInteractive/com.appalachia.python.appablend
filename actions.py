import bpy
import cspy
import mathutils, math
from mathutils import Vector, Matrix, Quaternion, Euler

class INTERPOLATION:    
    """Constant, No interpolation, value of A gets held until B is encountered"""
    CONSTANT = 'CONSTANT'
    """Linear, Straight-line interpolation between A and B (i.e. no ease in/out)"""
    LINEAR = 'LINEAR'
    """Bezier, Smooth interpolation between A and B, with some control over curve shape"""
    BEZIER = 'BEZIER'
    """Sinusoidal, Sinusoidal easing (weakest, almost linear but with a slight curvature)"""
    SINE = 'SINE'
    """Quadratic, Quadratic easing"""
    QUAD = 'QUAD'
    """Cubic, Cubic easing"""
    CUBIC = 'CUBIC'
    """Quartic, Quartic easing"""
    QUART = 'QUART'
    """Quintic, Quintic easing"""
    QUINT = 'QUINT'
    """Exponential, Exponential easing (dramatic)"""
    EXPO = 'EXPO'
    """Circular, Circular easing (strongest and most dynamic)"""
    CIRC = 'CIRC'
    """Back, Cubic easing with overshoot and settle"""
    BACK = 'BACK'
    """Bounce, Exponentially decaying parabolic bounce, like when objects collide"""
    BOUNCE = 'BOUNCE'
    """Elastic"""
    ELASTIC = 'ELASTIC' 

    ALL = [CONSTANT, LINEAR, BEZIER, SINE, QUAD, CUBIC, QUART, QUINT, EXPO, CIRC, BACK, BOUNCE, ELASTIC]
    
class KEYFRAME:
    """Keyframe, Normal keyframe, e.g. for key poses."""
    KEYFRAME = 'KEYFRAME'

    """Breakdown, A breakdown pose, e.g. for transitions between key poses."""
    BREAKDOWN = 'BREAKDOWN'

    """Moving Hold, A keyframe that is part of a moving hold."""
    MOVING_HOLD = 'MOVING_HOLD'

    """Extreme, An ‘extreme’ pose, or some other purpose as needed."""
    EXTREME = 'EXTREME'

    """Jitter, A filler or baked keyframe for keying on ones, or some other purpose as needed."""
    JITTER = 'JITTER'

    ALL = [KEYFRAME, BREAKDOWN, MOVING_HOLD, EXTREME, JITTER]

def insert_keyframe_extreme_by_path_and_index(action, data_path, array_index, frame, value, replace=False, needed=True, fast=False):
    return insert_keyframe_by_path_and_index(action, data_path, array_index, frame, value, replace, needed, fast, KEYFRAME.EXTREME)  

def insert_keyframe_jitter_by_path_and_index(action, data_path, array_index, frame, value, replace=False, needed=True, fast=False):
    return insert_keyframe_by_path_and_index(action, data_path, array_index, frame, value, replace, needed, fast, KEYFRAME.JITTER)  

def insert_keyframe_movinghold_by_path_and_index(action, data_path, array_index, frame, value, replace=False, needed=True, fast=False):
    return insert_keyframe_by_path_and_index(action, data_path, array_index, frame, value, replace, needed, fast, KEYFRAME.MOVING_HOLD)    

def insert_keyframe_breakdown_by_path_and_index(action, data_path, array_index, frame, value,replace=False,  needed=True, fast=False):
    return insert_keyframe_by_path_and_index(action, data_path, array_index, frame, value, replace, needed, fast, KEYFRAME.BREAKDOWN)    

def insert_keyframe_by_path_and_index(action, data_path, array_index, frame, value, replace=False, needed=True, fast=False, keyframe_type=KEYFRAME.KEYFRAME):
    fcurve = action.fcurves.find(data_path, index=array_index)
    if fcurve:
        return insert_keyframe(fcurve, frame, value, replace, needed, fast, keyframe_type)    

def insert_keyframe_extreme_by_path(action, data_path, frame, value, replace=False, needed=True, fast=False):
    return insert_keyframe_by_path(action, data_path, frame, value, replace, needed, fast, KEYFRAME.EXTREME)  

def insert_keyframe_jitter_by_path(action, data_path, frame, value, replace=False, needed=True, fast=False):
    return insert_keyframe_by_path(action, data_path, frame, value, replace, needed, fast, KEYFRAME.JITTER)  

def insert_keyframe_movinghold_by_path(action, data_path, frame, value, replace=False, needed=True, fast=False):
    return insert_keyframe_by_path(action, data_path, frame, value, replace, needed, fast, KEYFRAME.MOVING_HOLD)    

def insert_keyframe_breakdown_by_path(action, data_path, frame, value,replace=False,  needed=True, fast=False):
    return insert_keyframe_by_path(action, data_path, frame, value, replace, needed, fast, KEYFRAME.BREAKDOWN)    

def insert_keyframe_by_path(action, data_path, frame, value, replace=False, needed=True, fast=False, keyframe_type=KEYFRAME.KEYFRAME):    
    try:
        indices = range(len(value))
    except TypeError:
        indices = [-1]
    
    results = []
    for index in indices:
        fcurve = action.fcurves.find(data_path, index=index)
        if fcurve:
            v = value if index == -1 else value[index]
            results.append(insert_keyframe(fcurve, frame, v, replace, needed, fast, keyframe_type))
    
    return results

def insert_keyframe_extreme(fcurve, frame, value, replace=False, needed=True, fast=False):
    return insert_keyframe(fcurve, frame, value, replace, needed, fast, KEYFRAME.EXTREME)  

def insert_keyframe_jitter(fcurve, frame, value, replace=False, needed=True, fast=False):
    return insert_keyframe(fcurve, frame, value, replace, needed, fast, KEYFRAME.JITTER)  

def insert_keyframe_movinghold(fcurve, frame, value, replace=False, needed=True, fast=False):
    return insert_keyframe(fcurve, frame, value, replace, needed, fast, KEYFRAME.MOVING_HOLD)    

def insert_keyframe_breakdown(fcurve, frame, value,replace=False,  needed=True, fast=False):
    return insert_keyframe(fcurve, frame, value, replace, needed, fast, KEYFRAME.BREAKDOWN)    

def insert_keyframe(fcurve, frame, value, replace=False, needed=True, fast=False, keyframe_type=KEYFRAME.KEYFRAME):
    options = set()
    if replace:
        options.add('REPLACE')
    if needed:
        options.add('NEEDED')
    if fast:
        options.add('FAST')

    k = fcurve.keyframe_points.insert(frame, value, options=options, keyframe_type=keyframe_type)
    k.type = keyframe_type
    return k

def select_all_frames(action):
    for f in action.fcurves:
        for k in f.keyframe_points:
            k.select_control_point = True

def deselect_all_frames(action):
    for f in action.fcurves:
        for k in f.keyframe_points:
            k.select_control_point = False

def sample_fcurve(action):
    start = action.frame_range[0]
    stop = action.frame_range[1]

    for fcurve in action.fcurves:
        kps = fcurve.keyframe_points
        points = []
        for index, key in enumerate(kps):
            selected = False
            if index == len(kps) - 1:
                continue

            next_key = kps[index+1]
            selected = key.select_control_point and next_key.select_control_point

            if selected:
                key_start = int(key.co[0]) + 1
                key_end = int(next_key.co[0])

                for frame in range(key_start, key_end):
                    value = fcurve.evaluate(frame)
                    points.append((frame, value))
        
        if len(points) > 0:
            print('[{0}]: adding {1} points to keying data path [{2}]'.format(action.name, len(points), fcurve.data_path))
            for point in points:
                insert_keyframe_breakdown(fcurve, point[0], point[1], replace=False, needed=False, fast=True)

            fcurve.update()

def simplify_fcurves(action):
    for fcurve in action.fcurves:
        kps = fcurve.keyframe_points
        kps_len = len(kps)

        remove_indices = []
        for index, key in enumerate(kps):
            if index == 0 or index == len(kps) - 1:
                continue
            
            v = key.co[1]

            prev_key = kps[index-1]
            next_key = kps[index+1]

            pv = prev_key.co[1]
            nv = next_key.co[1]

            avg = (pv+nv ) / 2.0

            if round(v, 4) == round(avg, 4):
                remove_indices.append(index)
                continue            
        
        for index in reversed(remove_indices):
            kps.remove(kps[index])
            
        fcurve.update()

def decorate_curves(action):
    for fcurve in action.fcurves:
        kps = fcurve.keyframe_points
        kps_len = len(kps)

        for index, key in enumerate(kps):
            if index == 0 or index == len(kps) - 1:
                key.type = cspy.actions.KEYFRAME.EXTREME
                continue
            
            if key.type == cspy.actions.KEYFRAME.EXTREME:
                continue

            kt = key.type

            v = key.co[1]

            prev_key = kps[index-1]
            next_key = kps[index+1]

            pv = prev_key.co[1]
            nv = next_key.co[1]

            avg = (pv+nv ) / 2.0

            if nv > v and v > pv:
                kt = cspy.actions.KEYFRAME.MOVING_HOLD
            elif nv < v and v < pv:
                kt = cspy.actions.KEYFRAME.MOVING_HOLD
            elif round(avg, 3) == round(v, 3):
                kt = cspy.actions.KEYFRAME.BREAKDOWN
            
            key.type = kt
        
    for curve in action.fcurves:
        fcurve.update()

    for unity_clip in action.unity_clips:
        unity_clip.decorate(action)

    for curve in action.fcurves:
        fcurve.update()


valid_bone_names = set()
valid_pose_bone_paths = set()
valid_data_paths = ['bbone_curveinx','bbone_curveiny','bbone_curveoutx','bbone_curveouty','bbone_easein','bbone_easeout','bbone_rollin','bbone_rollout','bbone_scaleinx','bbone_scaleiny','bbone_scaleoutx','bbone_scaleouty','bone_group_index','ik_linear_weight','ik_max_x','ik_max_y','ik_max_z','ik_min_x','ik_min_y','ik_min_z','ik_rotation_weight','ik_stiffness_x','ik_stiffness_y','ik_stiffness_z','ik_stretch','location','lock_ik_x','lock_ik_y','lock_ik_z','lock_location','lock_rotation','lock_rotation_w','lock_rotations_4d','lock_scale','rotation_axis_angle','rotation_euler','rotation_mode','rotation_quaternion','scale','use_custom_shape_bone_size','use_ik_limit_x','use_ik_limit_y','use_ik_limit_z','use_ik_linear_control','use_ik_rotation_control']
bad_groups = ['Action Bake']
bad_strings = ['_NOROT']

def clean_fcurves(action):
    if len(valid_bone_names == 0):        
        for armature in bpy.data.armatures:
            for bone in armature.bones:
                valid_bone_names.add(bone.name)
    if len(valid_pose_bone_paths) == 0:
        for bone_name in valid_bone_names:
            for valid_data_path in valid_data_paths:
                path = 'pose.bones["{0}"].{1}'.format(bone_name, valid_data_path)
                valid_pose_bone_paths.add(path)

    removals = []
    for fcurve in action.fcurves:
        data_path = fcurve.data_path
        if not data_path.startswith('pose.bones'):
            continue
        if not data_path in valid_pose_bone_paths:
            removals.append(fcurve)

    for bad_group in bad_groups:
        if bad_group in action.groups:
            group = action.groups[bad_group]
            for fcurve in [fc for fc in action.fcurves if fc.group == group]:  
                removals.append(fcurve)
                
    for bad_string in bad_strings:
        for fcurve in action.fcurves:
            if bad_string in fcurve.data_path: 
                removals.append(fcurve)

    for removal in removals:
        if removal:
            print('{0}: Removing fcurve [{1}]'.format(action.name, removal.data_path))
            action.fcurves.remove(removal)  


def data_path_from_bone(bone_name):
    return 'pose.bones["{0}"].'.format(bone_name)

def group_actions_by_bone():
    for armature in bpy.data.armatures:            
        for action in bpy.data.actions:
            for bone in armature.bones:                
                for fcurve in action.fcurves:
                    if fcurve.data_path.startswith(data_path_from_bone(bone.name)):                        
                        if bone.name in action.groups:
                            group = action.groups[bone.name]
                        else:
                            group = action.groups.new(bone.name)
                        fcurve.group = group

def group_actions_by_bone():
    for armature in bpy.data.armatures:            
        for action in bpy.data.actions:
            for bone in armature.bones:                
                for fcurve in action.fcurves:
                    if fcurve.data_path.startswith(data_path_from_bone(bone.name)):                        
                        if bone.name in action.groups:
                            group = action.groups[bone.name]
                        else:
                            group = action.groups.new(bone.name)
                        fcurve.group = group

def split_action(master_action, new_action_name, start, end):
    new_action = master_action.copy()
    new_action.use_fake_user = True
    new_action.name = new_action_name
    print('Splitting action {0} to create action {1} - frame {2} to frame {3}'.format(
        master_action.name, new_action.name, start, end
    ))

    for curve in new_action.fcurves:          
        value_start = curve.evaluate(start)
        value_end = curve.evaluate(end)
        curve.keyframe_points.insert(start, value_start, options={'NEEDED','FAST'})
        curve.keyframe_points.insert(end, value_end, options={'NEEDED','FAST'})

        for key in curve.keyframe_points:
            key.co[0] -= start
            key.handle_left[0] -= start
            key.handle_right[0] -= start  

        curve.update()

        key_start = 0
        key_end = key_start + (end - start)

        for idx, key in cspy.utils.enumerate_reversed(curve.keyframe_points):
            key = curve.keyframe_points[idx]
            frame = key.co[0]
            if frame < key_start or frame > key_end:
                curve.keyframe_points.remove(key, fast=True)

        curve.update()

    return new_action

def integrate_empties_action_into_bones(obj_names, master_name):
    master_action_names = []
    action_sets = {}

    for obj_name in obj_names:
        action_sets[obj_name] = []

    for action in bpy.data.actions:
        if action.name.startswith(master_name):
            master_action_names.append(action.name)
        else:
            for obj_name in obj_names:
                if action.name.startswith(obj_name):
                    action_sets[obj_name].append(action.name)
                    break
    
    for action_set_key in action_sets.keys():
        action_set = action_sets[action_set_key]

        for action_name in action_set:
            clean_name = action_name.replace('Animation Base Layer', ''
                ).replace(action_set_key, ''
                ).strip('|')

            master_action = None

            for master_action_name in master_action_names:
                clean_master_action_name = master_action_name.replace('Animation Base Layer', ''
                    ).replace(master_name, ''
                    ).strip('|')
                    
                if clean_master_action_name == clean_name:
                    master_action = bpy.data.actions[master_action_name]

            if master_action is None:
                continue                
            
            action = bpy.data.actions[action_name]

            if master_action == action:    
                continue

            for fcurve in action.fcurves:
                fcurve_data_path = 'pose.bones["{0}"].{1}'.format(action_set_key, fcurve.data_path)
                new_fcurve = master_action.fcurves.new(fcurve_data_path, index=fcurve.array_index)

                new_fcurve.keyframe_points.add(len(fcurve.keyframe_points))

                for index, key in enumerate(fcurve.keyframe_points):          
                    new_key = new_fcurve.keyframe_points[index]
                    new_key.co[0] = key.co[0]
                    new_key.co[1] = key.co[1]
                
                new_fcurve.update()
            
            bpy.data.actions.remove(action)
                
    for action_name in master_action_names:
        action = bpy.data.actions[action_name]

        for fcurve in action.fcurves:
            if not fcurve.data_path.startswith('pose.bones'):
                fcurve.data_path = 'pose.bones["{0}"].{1}'.format(master_name, fcurve.data_path)

def update_rotations_to_quat(obj, path_check, new_data_path_prefix=''):
    
    obj.rotation_mode = 'QUATERNION'
    actions = [action for action in bpy.data.actions if action.name.startswith(obj.name)]

    for action in actions:

        data_paths = set([fcurve.data_path for fcurve in action.fcurves if path_check(fcurve.data_path)])

        for data_path in data_paths:

            fcurves = [fcurve for fcurve in action.fcurves if fcurve.data_path == data_path ]
            group = next((fcurve.group for fcurve in fcurves if fcurve.group is not None), None)

            if not fcurves:
                continue

            frames = cspy.fcurves.frames_matching(action, data_path)
                        
            euler = Euler((0.0, 0.0, 0.0), 'XYZ')            
            degrees = [0.0, 0.0, 0.0]

            for fr in frames:
                for fc in fcurves:                   
                    euler[fc.array_index] = fc.evaluate(fr)
                    degrees[fc.array_index] = math.degrees(euler[fc.array_index])
                
                quat = euler.to_quaternion()

                cspy.fcurves.add_keyframe_quat(action, quat, fr, '{0}rotation_quaternion'.format(new_data_path_prefix), group)

            for fcurve in fcurves:
                action.fcurves.remove(fcurve)

def change_interpolation(action, interpolation):
    for fcurve in action.fcurves:
        for keyframe_point in fcurve.keyframe_points:
            keyframe_point.interpolation  = interpolation 

def change_keyframe_type(action, keyframe_type):
    for fcurve in action.fcurves:
        for keyframe_point in fcurve.keyframe_points:
            keyframe_point.type = keyframe_type
 
