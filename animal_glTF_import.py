import bpy
import cspy
from os import walk



def assign_empty_action_to_bone_action(empty, target_action):
    current_action= empty.animation_data.action

    new_group = target_action.groups.new(empty.name)

    for current_fcurve in current_action.fcurves:

        new_curve_name = cspy.bones.get_bone_data_path(empty.name, current_fcurve.data_path)

        new_curve = action.fcurves.new(new_curve_name, current_fcurve.index, new_group.name)

        for k in current_fcurve.keyframe_points:
            new_curve.keyframe_points.insert(k.co[0], k.co[1], options={'NEEDED','FAST'})

        new_curve.update()

def recursive_collapse_action(obj, action):

    if obj.children is not None and len(obj.children) > 0:
        for child in obj.children:
            recursive_collapse_action(child, action)

    recursive_collapse_action(obj, action)

def collapse_empty_based_actions(obj):
    if obj.animation_data is None:
        return
    current_action = obj.animation_data.action
    new_action_name = 'CONV_{0}'.format(current_action.name)
    new_action = bpy.data.actions.new(new_action_name)

    recursive_collapse_action(obj, new_action)

def get_best_mesh(meshes):
    max_verts = 0
    best_mesh = None

    for mesh in meshes:
        mesh.data.use_auto_smooth = False

        vert_count = len(mesh.data.vertices)
        if vert_count > max_verts:
            max_verts = vert_count
            best_mesh = mesh

    return best_mesh

def get_max_frame():
    max_frame = 0
    for action in bpy.data.actions:
        max_frame = max(max_frame, action.frame_range[1])
    return max_frame


def do_execute():

    current_file_path = bpy.data.filepath

    current_file_name = bpy.path.basename(current_file_path)
    current_directory = bpy.path.abspath("//")

    glTF_directory = current_directory.replace('_03_blend', '_02_glTF')

    glTF_file_basename = current_file_name.replace('.blend', '')
    glTF_file_name = '{0}.glb'.format(glTF_file_basename)
    full_glTF_path = '{0}{1}'.format(glTF_directory, glTF_file_name)

    cspy.imports.import_gltf(full_glTF_path)

    glTF_directory_files = cspy.files.get_files_in_dir(glTF_directory, glTF_file_basename)

    for directory_file in glTF_directory_files:
        if directory_file == full_glTF_path:
            continue
        import_gltf(directory_file)

    meshes = [obj for obj in bpy.data.objects if obj.type == 'MESH']

    best_mesh = get_best_mesh(meshes)

    for mesh in meshes:
        if mesh != best_mesh:
            bpy.data.objects.remove(mesh)

    max_frame = get_max_frame()

    bpy.context.scene.frame_start = 0
    bpy.context.scene.frame_end = max_frame

    parentless_objs = [o for o in bpy.data.objects if o.parent is None]

    for parentless_obj in parentless_objs:
        if parentless_obj.type != 'EMPTY':
            continue

        any_arms = False
        for child in parentless_obj.children:
            if child.type == 'ARMATURE':
                any_arms = True
                break

        if any_arms:
            continue

        collapse_empty_based_actions(parentless_obj)
        cspy.hierarchy.delete_hierarchy(parentless_obj)


    cspy.data.purge_unused()
    bpy.ops.screen.animation_play()
    