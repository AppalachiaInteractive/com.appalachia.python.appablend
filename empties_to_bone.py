import bpy
import math
from mathutils import Vector, Euler, Matrix
import cspy
from cspy import utils


TARGETS = ['ACTION', 'ACTION NAME', 'FILE', 'DIR']
TARGETS_ENUM =  cspy.utils.create_enum(TARGETS)
TARGETS_ENUM_DEF = 'ACTION'

class EB_blender_version:
    _string = bpy.app.version_string
    blender_v = bpy.app.version
    _float = blender_v[0]*100+blender_v[1]+blender_v[2]*0.01
    _char = bpy.app.version_char

blender_version = EB_blender_version()

def delete_edit_bone(editbone):
    bpy.context.active_object.data.edit_bones.remove(editbone)

def set_active_object(object_name):
     bpy.context.view_layer.objects.active = bpy.data.objects[object_name]
     bpy.data.objects[object_name].select_set(state=True)

def get_edit_bone(name):
    return bpy.context.object.data.edit_bones.get(name)

def get_pose_bone(name):
    return bpy.context.active_object.pose.bones.get(name)

def mat3_to_vec_roll(mat):
    vec = mat.col[1]
    vecmat = vec_roll_to_mat3(mat.col[1], 0)
    vecmatinv = vecmat.inverted()
    rollmat = vecmatinv @ mat
    roll = math.atan2(rollmat[0][2], rollmat[2][2])
    return vec, roll

def vec_roll_to_mat3(vec, roll):
    target = Vector((0, 0.1, 0))
    nor = vec.normalized()
    axis = target.cross(nor)
    if axis.dot(axis) > 0.0000000001: # this seems to be the problem for some bones, no idea how to fix
        axis.normalize()
        theta = target.angle(nor)
        bMatrix = Matrix.Rotation(theta, 3, axis)
    else:
        updown = 1 if target.dot(nor) > 0 else -1
        bMatrix = Matrix.Scale(updown, 3)
        bMatrix[2][2] = 1.0

    rMatrix = Matrix.Rotation(roll, 3, nor)
    mat = rMatrix @ bMatrix
    return mat

def align_bone_x_axis(edit_bone, new_x_axis):
    new_x_axis = new_x_axis.cross(edit_bone.y_axis)
    new_x_axis.normalize()
    dot = max(-1.0, min(1.0, edit_bone.z_axis.dot(new_x_axis)))
    angle = math.acos(dot)
    edit_bone.roll += angle
    dot1 = edit_bone.z_axis.dot(new_x_axis)
    edit_bone.roll -= angle * 2.0
    dot2 = edit_bone.z_axis.dot(new_x_axis)
    if dot1 > dot2:
        edit_bone.roll += angle * 2.0

def signed_angle(vector_u, vector_v, normal):
    normal = normal.normalized()
    a = vector_u.angle(vector_v)
    if vector_u.cross(vector_v).angle(normal) < 1:
        a = -a
    return a

def set_bone_layer(editbone, layer_idx, multi=False):
    editbone.layers[layer_idx] = True
    if multi:
        return
    for i, lay in enumerate(editbone.layers):
        if i != layer_idx:
            editbone.layers[i] = False

def _initialize_armature():
    scn = bpy.context.scene
    # store selected empties

    if scn.eb_source_object:
        cspy.utils.set_object_active(scn.eb_source_object)

    empties = [e for e in bpy.context.selected_objects if e.type == "EMPTY"]
    for e in empties:
        cspy.hierarchy.select_hierarchy(e)

    empties = [e for e in bpy.context.selected_objects if e.type == "EMPTY"]
    empties_names = [i.name for i in empties if i.type == "EMPTY"]

    """ for e in empties.copy():
        if not e.children or len(e.children) == 0:
            bpy.ops.object.empty_add()
            leaf = bpy.context.active_object
            leaf.parent = e
            leaf.location = Vector([0.0, 25.0, 0.0])
            leaf.name = 'end.{0}'.format(e.name)
            empties.append(leaf)
            empties_names.append(leaf.name)
            print(leaf.name) """

    # Create armature and bones
    # add a new armature
    empty = bpy.context.active_object
    armature_name = 'ARM_{0}'.format(bpy.context.active_object.name)
    bpy.ops.object.armature_add(enter_editmode=False, location=(0, 0, 0), rotation=(0,0,0))
    armature = bpy.context.active_object
    armature.parent = empty.parent
    armature.name = armature_name
    bpy.ops.object.mode_set(mode='EDIT')
    # delete the default bone
    b_to_del = armature.data.edit_bones[0]
    armature.data.edit_bones.remove(b_to_del)

    empty_primary_axis = None

    # create bones
    print("Create main bones chain...")
    bones_dict = {}
    for i, emp_name in enumerate(empties_names):
        emp = bpy.data.objects.get(emp_name)

        # store current action to automatically set baking length
        if i == 0:
            anim_data = emp.animation_data
            if anim_data:
                act = emp.animation_data.action
                if act:
                    scn.eb_current_empty_action = act.name

        mat = emp.matrix_world.copy()
        emp_x = Vector((mat[0][0],mat[1][0],mat[2][0]))
        emp_y =  Vector((mat[0][1],mat[1][1],mat[2][1]))
        emp_z = Vector((mat[0][2],mat[1][2],mat[2][2]))

        vec, roll = mat3_to_vec_roll(emp.matrix_world.to_3x3())
        new_bone = armature.data.edit_bones.new(emp_name)
        new_bone.head = emp.matrix_world.to_translation()
        new_bone.tail = new_bone.head + (vec)*scn.eb_bone_scale
        print('{0}: [{1}] to [{2}]'.format(emp_name, new_bone.head, new_bone.tail))
        new_bone.roll = roll
        parent_name = None
        children_name = None
        if emp.parent:
            parent_name = emp.parent.name
        if len(emp.children):
            children_name = [e.name for e in emp.children if e.type == "EMPTY"]

            # look for the empty objects primary axis by looking for the shortest distance
            # between a point between the empty and its child
            # TODO: support -X, -Y and -Z axes
            if empty_primary_axis == None and len(children_name) == 1:
                child_pos = emp.children[0].matrix_world.to_translation()

                point_on_vec = mat.to_translation() + emp_x.normalized()
                dist_x = (child_pos - point_on_vec).magnitude
                point_on_vec = mat.to_translation() + emp_y.normalized()
                dist_y = (child_pos - point_on_vec).magnitude
                point_on_vec = mat.to_translation() + emp_z.normalized()
                dist_z = (child_pos - point_on_vec).magnitude

                #print("dist x", dist_x)
                #print("dist y", dist_y)
                #print("dist z", dist_z)

                shortest_dist = sorted([dist_x, dist_y, dist_z])[0]
                if shortest_dist == dist_x:
                    empty_primary_axis = "X"
                elif shortest_dist == dist_y:
                    empty_primary_axis = "Y"
                else:
                    empty_primary_axis = "Z"
                print("Primary Axis:", empty_primary_axis)

        bones_dict[emp_name] = parent_name, children_name

    print("  parent bones...")
    for b in bones_dict:
        # parent bones
        bone_parent_name = bones_dict[b][0]
        if bone_parent_name == None:
            continue
        bone_parent = get_edit_bone(bone_parent_name)
        e_bone = get_edit_bone(b)
        if bone_parent:
            e_bone.parent = bone_parent

        emp = bpy.data.objects.get(e_bone.name)
        mat = emp.matrix_world.copy()
        emp_x = Vector((mat[0][0],mat[1][0],mat[2][0]))
        emp_y =  Vector((mat[0][1],mat[1][1],mat[2][1]))
        emp_z = Vector((mat[0][2],mat[1][2],mat[2][2]))

        # set tail position at children if Automatic Bones Orientation enabled
        if scn.eb_auto_bones_orientation:
            children_name = bones_dict[b][1]
            child_count = 0 if not children_name else len(children_name)

            set_tail_to_child = False

            if child_count == 1:
                emp_child = bpy.data.objects.get(children_name[0])
                loc = emp_child.matrix_world.to_translation()

                if loc != e_bone.head:# avoid zero length bone errors
                    print('{0}: [{1}]'.format(emp_child.name, abs((loc-e_bone.tail).magnitude)))
                    e_bone.tail = loc
                    set_tail_to_child = True

            if not set_tail_to_child:
                # if no children or multiple children, use the empty primary axis or parent bone vector to position the tail
                if child_count > 1:
                    # position the tail at the center of all children
                    # get center of all children positions
                    children_pos = Vector((0,0,0))
                    for n in children_name:
                        emp_child = bpy.data.objects.get(n)
                        loc = emp_child.matrix_world.to_translation()
                        children_pos += loc
                    children_average_pos = children_pos/len(children_name)
                    e_bone.tail = children_average_pos
                elif bone_parent:
                    vec = e_bone.head - bone_parent.head
                    if empty_primary_axis:
                        e_bone.tail = e_bone.head + (emp_x.normalized() * vec.magnitude*0.5)
                    else:
                        print("No primary axis yet, use parent bone vector", e_bone.name)
                        e_bone.tail = e_bone.head + vec
                    print('{0}: updated tail - [{1}]'.format(e_bone.name, e_bone.tail))


            # set roll according to user defined target axis
            target_axis = None
            if scn.eb_auto_target_axis == "X":
                target_axis = emp_x
            elif scn.eb_auto_target_axis == "-X":
                target_axis = -emp_x
            elif scn.eb_auto_target_axis == "Y":
                target_axis = emp_y
            elif scn.eb_auto_target_axis == "-Y":
                target_axis = -emp_y
            elif scn.eb_auto_target_axis == "Z":
                target_axis = emp_z
            elif scn.eb_auto_target_axis == "-Z":
                target_axis = -emp_z

            align_bone_x_axis(e_bone, target_axis)

    return bones_dict

def sync_bone_positions(armature_old):
    armature_new = bpy.context.active_object

    #armature_new.matrix_world = armature_old.matrix_world
    active, mode = cspy.utils.enter_mode(armature_old, cspy.bones.EDIT_MODE_SET)

    edit_bone_dict = cspy.bones.get_edit_bone_data_dict(armature_old)
    print('edit bone data dict length: {0}'.format(len(edit_bone_dict.keys())))

    cspy.utils.enter_mode(armature_new, cspy.bones.EDIT_MODE_SET)

    for bone in armature_new.data.edit_bones:
        bone_name = bone.name
        #print('Checking for bone {0}'.format(bone_name))
        bone = get_edit_bone(bone_name)

        if not bone_name in edit_bone_dict:
            print('{0} not found'.format(bone_name))
            #for key in edit_bone_dict.keys():
            #    print('KEY: {0}'.format(key))
            continue

        dict_values = edit_bone_dict[bone_name]

        bone.head = dict_values[0]
        bone.tail = dict_values[1]
        bone.roll = dict_values[2]
        bone.use_connect = dict_values[3]

    cspy.utils.exit_mode(active, mode)

def _create_norot_bones():
    print("Create NOROT bones chain...")
    # create a duplicate _NOROT bone chain in order to enable Inherit Rotation on the main one
    current_edit_bones = [e for e in bpy.context.active_object.data.edit_bones]
    for edit_bone in current_edit_bones:
        new_bone = bpy.context.active_object.data.edit_bones.new(edit_bone.name+"_NOROT")
        new_bone.head, new_bone.tail, new_bone.roll, new_bone.use_connect = edit_bone.head.copy(), edit_bone.tail.copy(), edit_bone.roll, edit_bone.use_connect
        #new_bone.head, new_bone.tail, new_bone.roll = edit_bone.head.copy(), edit_bone.tail.copy(), edit_bone.roll
        # disable inherit rotation (adding the Child Of constraint would lead to double transformation)
        new_bone.use_inherit_rotation = False
        set_bone_layer(new_bone, 1)

        #set parents
    print("  parent bones...")
    for edit_bone in bpy.context.active_object.data.edit_bones:
        if "_NOROT" in edit_bone.name or edit_bone.parent == None:
            continue
        norot_bone = get_edit_bone(edit_bone.name+"_NOROT")
        norot_bone.parent = get_edit_bone(edit_bone.parent.name+"_NOROT")

def _constrain_bones(bones_dict):
    print("Constrain bones...")
    # constrain bones
    scn = bpy.context.scene
    bpy.ops.object.mode_set(mode='POSE')
    armature = bpy.context.active_object
    for b in bones_dict:
        bone = get_pose_bone(b)
        bone_NOROT = get_pose_bone(b+"_NOROT")
        if bone_NOROT == None:
            continue
        emp = bpy.data.objects.get(b)
        # set NOROT bones constraints
        if scn.eb_auto_bones_orientation:
            cns = bone_NOROT.constraints.new("COPY_TRANSFORMS")
            cns.target = scn.eb_target_armature
            cns.subtarget = bone.name

            cns = bone_NOROT.constraints.new("CHILD_OF")
            cns.target = emp
            cns.inverse_matrix = cns.target.matrix_world.inverted()

            cns = bone_NOROT.constraints.new("COPY_LOCATION")
            cns.target = emp

            #dont screw with root or pelvis bones
            if bone_NOROT.parent:
                """ if len(bone_NOROT.children) == 0:
                    #print('no child damped track')
                    cns = bone_NOROT.constraints.new("DAMPED_TRACK")
                    cns.target = armature
                    cns.track_axis = 'TRACK_NEGATIVE_Y'
                    cns.subtarget = bone.parent.name """
                if len(bone_NOROT.children) == 1:
                #elif len(bone_NOROT.children) == 1:
                    #print('1 child damped track')
                    cns = bone_NOROT.constraints.new("DAMPED_TRACK")
                    cns_target_name = bone.children[0].name.replace('_NOROT', '')
                    cns_target = bpy.data.objects[cns_target_name]
                    cns.target = cns_target
                elif 'pelvis' in bone_NOROT.name.lower():
                    #print('pelvis case')
                    child_spines = [c for c in bone_NOROT.children if 'spine' in c.name.lower() or 'spine' == c.name.lower()]
                    if child_spines and len(child_spines) == 1:
                        cns = bone_NOROT.constraints.new("DAMPED_TRACK")
                        cns.track_axis = 'TRACK_NEGATIVE_Y'
                        cns_target_name = child_spines[0].name.replace('_NOROT', '')
                        cns_target = bpy.data.objects[cns_target_name]
                        cns.target = cns_target
                elif 'spine' in bone_NOROT.name.lower():
                    #print('spine case')
                    child_spines = [c for c in bone_NOROT.children if 'spine' in c.name.lower() or 'neck' in c.name.lower()]
                    if child_spines and len(child_spines) == 1:
                        cns = bone_NOROT.constraints.new("DAMPED_TRACK")
                        cns_target_name = child_spines[0].name.replace('_NOROT', '')
                        cns_target = bpy.data.objects[cns_target_name]
                        cns.target = cns_target
        else:
            # original orientation, use copy constraints
            cns_loc = bone_NOROT.constraints.new("COPY_LOCATION")
            emp = bpy.data.objects.get(b)
            cns_loc.target = emp

            cns_rot = bone_NOROT.constraints.new("COPY_ROTATION")
            emp = bpy.data.objects.get(b)
            cns_rot.target = emp

            cns_rot.invert_x = scn.eb_invert_x
            cns_rot.invert_y = scn.eb_invert_y
            cns_rot.invert_z = scn.eb_invert_z

        # set main bones constraints, just copy transforms
        cns_copy = bone.constraints.new("COPY_TRANSFORMS")
        cns_copy.target = bpy.context.active_object
        cns_copy.subtarget = bone_NOROT.name

def _duplicate_armature():
    bones_dict = _initialize_armature()

    sync_bone_positions(bpy.context.scene.eb_target_armature)

    _create_norot_bones()
    _constrain_bones(bones_dict)
    print("Armature duplicated")

def _create_armature():
    bones_dict = _initialize_armature()

    _create_norot_bones()
    _constrain_bones(bones_dict)
    print("Armature created")

def bake_anim(self, frame_start=0, frame_end=10, only_selected=False, bake_bones=True, bake_object=False, clear_constraints=False, shape_keys=False, _self=None, action_export_name=None):
    # similar to bpy.ops.nla.bake but faster

    scn = bpy.context.scene
    obj_data = []
    bones_data = []
    armature = bpy.data.objects.get(bpy.context.active_object.name)

    def get_bones_matrix():
        matrix = {}
        for pbone in armature.pose.bones:
            if only_selected and not pbone.bone.select:
                continue
            matrix[pbone.name] = armature.convert_space(pose_bone=pbone, matrix=pbone.matrix, from_space="POSE", to_space="LOCAL")
        return matrix

    def get_obj_matrix():
        parent = armature.parent
        matrix = armature.matrix_world
        if parent:
            return parent.matrix_world.inverted_safe() @ matrix
        else:
            return matrix.copy()

    # make list of meshes with valid shape keys
    sk_objects = []
    if shape_keys and _self and action_export_name:# bake shape keys value for animation export
        for ob_name in _self.char_objects:
            ob = bpy.data.objects.get(ob_name+"_arpexport")
            if ob.type != "MESH":
                continue
            if ob.data.shape_keys == None:
                continue
            if len(ob.data.shape_keys.key_blocks) == 0:
                continue
            if len(ob.data.shape_keys.key_blocks) <= 1:
                continue
            sk_objects.append(ob)

    # store matrices
    current_frame = scn.frame_current
    for f in range(int(frame_start), int(frame_end+1)):
        scn.frame_set(f)
        bpy.context.view_layer.update()
        # bones data
        if bake_bones:
            bones_data.append((f, get_bones_matrix()))
        # objects data
        if bake_object:
            obj_data.append((f, get_obj_matrix()))
        # shape keys data (for animation export only)
        for ob in sk_objects:
            for i, sk in enumerate(ob.data.shape_keys.key_blocks):
                if (sk.name == "Basis" or sk.name == "00_Basis") and i == 0:
                    continue
                #print(sk.name, float(f-int(frame_range[0])), sk.value)
                frame_in_action = float(f-int(frame_start))
                dict_entry = action_export_name+'|'+'BMesh#'+ob.data.name+'|Shape|BShape Key#'+sk.name+'|'+str(frame_in_action)
                #print(dict_entry, sk.value)
                _self.shape_keys_data[dict_entry] = sk.value

    # set new action
    if scn.eb_target_action:
        action = scn.eb_target_action
        action_name = action.name
        bpy.data.actions.remove(action)
        action = bpy.data.actions.new(action_name)
        scn.eb_target_action = action

    elif scn.eb_target_action_name != '':
        target_action_name = scn.eb_target_action_name.replace('.fbx','').replace('.Fbx','').replace('.FBX','')
        scn.eb_target_action_name = target_action_name
        if target_action_name in bpy.data.actions:
            action = bpy.data.actions[target_action_name]
            bpy.data.actions.remove(action)
            action = bpy.data.actions.new(target_action_name)
        else:
            action = bpy.data.actions.new(target_action_name)
    else:
        action = bpy.data.actions.new("Action")

    anim_data = armature.animation_data_create()
    anim_data.action = action

    def store_keyframe(bone_name, prop_type, fc_array_index, frame, value):
        fc_data_path  = cspy.bones.get_bone_data_path(bone.name, prop_type)
        fc_key = (fc_data_path, fc_array_index)
        if not keyframes.get(fc_key):
            keyframes[fc_key] = []
        keyframes[fc_key].extend((frame, value))


    # set transforms and store keyframes
    if bake_bones:
        for pbone in armature.pose.bones:
            if only_selected and not pbone.bone.select:
                continue
            if pbone.name.startswith('end.'):
                continue
            if '_NOROT' in pbone.name:
                continue
            euler_prev = None
            quat_prev = None
            keyframes = {}
            #print("BONES DATA", bones_data)
            for (f, matrix) in bones_data:
                pbone.matrix_basis = matrix[pbone.name].copy()

                for arr_idx, value in enumerate(pbone.location):
                    store_keyframe(pbone.name, "location", arr_idx, f, value)

                rotation_mode = pbone.rotation_mode
                if rotation_mode == 'QUATERNION':
                    if quat_prev is not None:
                        quat = pbone.rotation_quaternion.copy()
                        quat.make_compatible(quat_prev)
                        pbone.rotation_quaternion = quat
                        quat_prev = quat
                        del quat
                    else:
                        quat_prev = pbone.rotation_quaternion.copy()

                    for arr_idx, value in enumerate(pbone.rotation_quaternion):
                        store_keyframe(pbone.name, "rotation_quaternion", arr_idx, f, value)

                elif rotation_mode == 'AXIS_ANGLE':
                    for arr_idx, value in enumerate(pbone.rotation_axis_angle):
                        store_keyframe(pbone.name, "rotation_axis_angle", arr_idx, f, value)

                else:  # euler, XYZ, ZXY etc
                    if euler_prev is not None:
                        euler = pbone.rotation_euler.copy()
                        euler.make_compatible(euler_prev)
                        pbone.rotation_euler = euler
                        euler_prev = euler
                        del euler
                    else:
                        euler_prev = pbone.rotation_euler.copy()

                    for arr_idx, value in enumerate(pbone.rotation_euler):
                        store_keyframe(pbone.name, "rotation_euler", arr_idx, f, value)

                for arr_idx, value in enumerate(pbone.scale):
                    store_keyframe(pbone.name, "scale", arr_idx, f, value)

            # Add keyframes
            for fc_key, key_values in keyframes.items():
                data_path, index = fc_key
                fcurve = action.fcurves.find(data_path=data_path, index=index)
                if fcurve == None:
                    fcurve = action.fcurves.new(data_path, index=index, action_group=pbone.name)

                num_keys = len(key_values) // 2
                fcurve.keyframe_points.add(num_keys)
                fcurve.keyframe_points.foreach_set('co', key_values)
                if blender_version._float >= 290:# internal error when doing so with Blender 2.83, only for Blender 2.90 and higher
                    linear_enum_value = bpy.types.Keyframe.bl_rna.properties['interpolation'].enum_items['LINEAR'].value
                    fcurve.keyframe_points.foreach_set('interpolation', (linear_enum_value,) * num_keys)
                else:
                    for kf in fcurve.keyframe_points:
                        kf.interpolation = 'LINEAR'

            if clear_constraints:
                while len(pbone.constraints):
                    pbone.constraints.remove(pbone.constraints[0])

    if bake_object:
        euler_prev = None
        quat_prev = None

        for (f, matrix) in obj_data:
            name = "Action Bake"
            armature.matrix_basis = matrix

            armature.keyframe_insert("location", index=-1, frame=f, group=name)

            rotation_mode = armature.rotation_mode
            if rotation_mode == 'QUATERNION':
                if quat_prev is not None:
                    quat = armature.rotation_quaternion.copy()
                    quat.make_compatible(quat_prev)
                    armature.rotation_quaternion = quat
                    quat_prev = quat
                    del quat
                else:
                    quat_prev = armature.rotation_quaternion.copy()
                armature.keyframe_insert("rotation_quaternion", index=-1, frame=f, group=name)
            elif rotation_mode == 'AXIS_ANGLE':
                armature.keyframe_insert("rotation_axis_angle", index=-1, frame=f, group=name)
            else:  # euler, XYZ, ZXY etc
                if euler_prev is not None:
                    euler = armature.rotation_euler.copy()
                    euler.make_compatible(euler_prev)
                    armature.rotation_euler = euler
                    euler_prev = euler
                    del euler
                else:
                    euler_prev = armature.rotation_euler.copy()
                armature.keyframe_insert("rotation_euler", index=-1, frame=f, group=name)

            armature.keyframe_insert("scale", index=-1, frame=f, group=name)

    action.use_fake_user = True

    # restore current frame
    scn.frame_set(current_frame)

    for bone in armature.pose.bones:
        for constraint in bone.constraints:
            bone.constraints.remove(constraint)

def _initialize_empties(scn, armature):

    empties = {}
    top_level_empty = None
    bone_matrices = cspy.bones.get_edit_bone_matrices(armature)
    bone_tail_updates = {}

    for bone in armature.data.bones:
        bone_matrix = bone_matrices[bone.name]
        bpy.ops.object.empty_add()
        empty = bpy.context.active_object
        empty.name = bone.name
        empties[bone.name] = empty
        if bone.parent:
            empty.parent = empties[bone.parent.name]

            if not bone.children:
                empty_children = [obj for obj in bpy.data.objects if (obj.parent_type == 'BONE' and obj.parent == armature and obj.parent_bone == bone.name)]

                print('{0}: empty children {1}'.format(bone.name, empty_children))
                if empty_children:
                    loc = Vector([0.0, 0.0, 0.0])

                    for e in empty_children:
                        eloc, erot, esca = e.matrix_world.decompose()
                        loc += eloc

                    bone_tail_updates[bone.name] = loc / len(empty_children)

        else:
            if top_level_empty is None:
                top_level_empty = empty
        empty.matrix_world = armature.matrix_world @ bone_matrix

    for bone_name in bone_tail_updates.keys():
        bone_tail_update = bone_tail_updates[bone_name]
        #cspy.bones.set_world_tail(armature, bone_name, bone_tail_update)

    def consume_armature_child(child):
        if child.type != 'EMPTY':
            bpy.data.objects.remove(child)
        else:
            empty_name = child.name
            child.name = '{0}_ORIG'.format(child.name)
            child_matrix = child.matrix_world.copy()

            bpy.ops.object.empty_add()
            e = bpy.context.active_object
            e.name = empty_name
            empties[e.name] = e

            if child.children:
                for c in child.children:
                    consume_armature_child(c)

            if child.parent_type == 'BONE' and child.parent_bone != '':
                e.parent = empties[child.parent_bone]
            else:
                e.parent = empties[child.parent.name.replace('_ORIG','')]

            e.matrix_world = child_matrix

    for ac in armature.children:
        consume_armature_child(ac)

    new_empties = []
    for empty_name in empties.keys():
        empty = bpy.data.objects.get(empty_name)
        if empty and (not empty.children or len(empty.children) == 0):
            bpy.ops.object.empty_add()
            leaf = bpy.context.active_object
            leaf.parent = empty
            leaf.location = Vector([0.0, 100.0, 0.0])
            leaf.name = 'end.{0}'.format(empty.name)
            new_empties.append(leaf)

    for empty in new_empties:
        empties[empty.name] = empty

    return top_level_empty, empties

def _constrain_empties(scn, armature, empties):
    print("Constrain empties...")

    # constrain empties
    for empty_name in empties.keys():

        empty = bpy.data.objects[empty_name]

        cns_copy = empty.constraints.new("COPY_TRANSFORMS")

        if empty_name in armature.pose.bones:
            bone = armature.pose.bones[empty_name]
            cns_copy.target = armature
            cns_copy.subtarget = bone.name
        else:
            t = '{0}_ORIG'.format(empty_name)
            if t in bpy.data.objects:
                cns_copy.target = bpy.data.objects['{0}_ORIG'.format(empty_name)]
            else:
                cns_copy.target = bpy.data.objects[empty_name]

def _deconstruct_armature():
    print("")

    scn = bpy.context.scene

    if scn.eb_source_object and scn.eb_source_object.type == 'ARMATURE':
        cspy.utils.set_object_active(scn.eb_source_object)

    armature_name = bpy.context.active_object.name
    armature = bpy.data.objects.get(armature_name)
    frame_range = armature.animation_data.action.frame_range

    top_level_empty, empties = _initialize_empties(scn, armature)

    top_level_empty.parent = armature.parent
    _constrain_empties(scn, armature, empties)

    cspy.utils.deselect_all()

    cspy.utils.set_object_active(top_level_empty)
    cspy.utils.select_by_names(empties.keys())

    bpy.ops.nla.bake(frame_start=frame_range[0], frame_end=frame_range[1], visual_keying=True, clear_constraints=True, bake_types={'OBJECT'})

    for child in armature.children:
        cspy.hierarchy.delete_hierarchy(child)

    bpy.data.actions.remove(armature.animation_data.action)
    ad = armature.data

    bpy.data.objects.remove(armature)
    bpy.data.armatures.remove(ad)

    print("Armature deconstructed")
