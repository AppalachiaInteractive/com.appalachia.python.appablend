import bpy
import cspy
from cspy import subtypes

def import_gltf(
        filepath,
        filter_glob='*.glb;*.gltf',
        loglevel=0,
        import_pack_images=True,
        merge_vertices=True,
        import_shading='NORMALS',
        bone_heuristic='TEMPERANCE',
        guess_original_bind_pose=True
    ):

    print('Attempting to import glTF file at [{0}]'.format(path))

    bpy.ops.import_scene.gltf(
        filepath=filepath,
        filter_glob=filter_glob,
        loglevel=loglevel,
        import_pack_images=import_pack_images,
        merge_vertices=merge_vertices,
        import_shading=import_shading,
        bone_heuristic=bone_heuristic,
        guess_original_bind_pose=guess_original_bind_pose
        )

    return bpy.context.selected_objects

def import_fbx(
    filepath="",
    filter_glob="*.fbx;*.dae;*.obj;*.dxf;*.3ds",
    files=[],
    use_auto_bone_orientation=True,
    my_calculate_roll='None',
    my_bone_length=10,
    my_leaf_bone='Short',
    use_fix_attributes=False,
    use_only_deform_bones=False,
    use_vertex_animation=True,
    use_animation=True,
    use_triangulate=False,
    my_import_normal='Calculate',
    use_auto_smooth=True,
    my_angle=60,
    my_shade_mode='Smooth',
    my_scale=0.01,
    use_optimize_for_blender=True,
    use_edge_crease=True,
    my_edge_crease_scale=1):

    bpy.ops.better_import.fbx(
        filepath=filepath,
        filter_glob=filter_glob,
        files=files,
        use_auto_bone_orientation=use_auto_bone_orientation,
        my_calculate_roll=my_calculate_roll,
        my_bone_length=my_bone_length,
        my_leaf_bone=my_leaf_bone,
        use_fix_attributes=use_fix_attributes,
        use_only_deform_bones=use_only_deform_bones,
        use_vertex_animation=use_vertex_animation,
        use_animation=use_animation,
        use_triangulate=use_triangulate,
        my_import_normal=my_import_normal,
        use_auto_smooth=use_auto_smooth,
        my_angle=my_angle,
        my_shade_mode=my_shade_mode,
        my_scale=my_scale,
        use_optimize_for_blender=use_optimize_for_blender,
        use_edge_crease=use_edge_crease,
        my_edge_crease_scale=my_edge_crease_scale,
    )

    imported = bpy.context.selected_objects.copy()
    return imported

_MODES = {
    'Adjust At Animation Start':'START',
    'Adjust Every Frame':'EVERY',
}
MODE_ENUM = cspy.utils.create_enum_dict(_MODES)
_MODE_ENUM_DEF = 'START'

class ImportSettings(bpy.types.PropertyGroup):    
    import_dir: bpy.props.StringProperty(name="Import Directory", subtype=subtypes.StringProperty.Subtypes.DIR_PATH)
    
    import_recursive: bpy.props.BoolProperty(name="Import Recursive")

    maya_mode: bpy.props.EnumProperty(name='Mode', items=MODE_ENUM, default=_MODE_ENUM_DEF)
    maya_template: bpy.props.StringProperty(name="Maya Armature File", subtype=subtypes.StringProperty.Subtypes.FILE_PATH)

    maya_import_dir: bpy.props.StringProperty(name="Maya Import Directory", subtype=subtypes.StringProperty.Subtypes.DIR_PATH)    
    maya_import_recursive: bpy.props.BoolProperty(name="Maya Import Recursive")
    
    maya_rot_bone_name: bpy.props.StringProperty(name='Maya Rotation Bone')
    maya_rot_value: bpy.props.FloatVectorProperty(name='Maya Rotation Value', subtype=subtypes.FloatVectorProperty.Subtypes.EULER)
    maya_export_dir: bpy.props.StringProperty(name="Maya Export Directory", subtype=subtypes.StringProperty.Subtypes.DIR_PATH)
    