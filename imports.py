import bpy

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
    filepath='',
    directory='', 
    filter_glob='*.fbx', 
    #files=None, 
    ui_tab='MAIN', 
    use_manual_orientation=False, 
    global_scale=1.0, 
    bake_space_transform=False, 
    use_custom_normals=True,
    use_image_search=True, 
    use_alpha_decals=False, 
    decal_offset=0.0, 
    use_anim=True, 
    anim_offset=1.0, 
    use_subsurf=False, 
    use_custom_props=True, 
    use_custom_props_enum_as_string=True, 
    ignore_leaf_bones=False, 
    force_connect_children=False, 
    automatic_bone_orientation=False, 
    primary_bone_axis='Y', 
    secondary_bone_axis='X', 
    use_prepost_rot=True, 
    axis_forward='-Z', 
    axis_up='Y'
    ):
    
    bpy.ops.import_scene.fbx(
        filepath=filepath, 
        directory=directory, 
        filter_glob=filter_glob,
        #files=files, 
        ui_tab=ui_tab,
        use_manual_orientation=use_manual_orientation, 
        global_scale=global_scale,
        bake_space_transform=bake_space_transform, 
        use_custom_normals=use_custom_normals,
        use_image_search=use_image_search,
        use_alpha_decals=use_alpha_decals, 
        decal_offset=decal_offset,
        use_anim=use_anim, 
        anim_offset=anim_offset,
        use_subsurf=use_subsurf, 
        use_custom_props=use_custom_props, 
        use_custom_props_enum_as_string=use_custom_props_enum_as_string,
        ignore_leaf_bones=ignore_leaf_bones,
        force_connect_children=force_connect_children,
        automatic_bone_orientation=automatic_bone_orientation,
        primary_bone_axis=primary_bone_axis,
        secondary_bone_axis=secondary_bone_axis,
        use_prepost_rot=use_prepost_rot, 
        axis_forward=axis_forward,
        axis_up=axis_up
        )

    return bpy.context.selected_objects