
import cspy
from cspy import files
import math

_command_rotate_every_frame = (
'    $start = `playbackOptions -query -animationStartTime`;'
'\n    $end = `playbackOptions -query -animationEndTime`;'
'\n\n    $bone_name="{0}";'
'\n    $bone_rot_x = $bone_name+".rx";'
'\n    $bone_rot_y = $bone_name+".ry";'
'\n    $bone_rot_z = $bone_name+".rz";'
'\n\n    select -r $bone_name;'
'\n\n    for ($index=$start; $index < $end; $index++) {{'
'\n        currentTime $index;'
'\n        if( `getAttr -k $bone_rot_x`||`getAttr -channelBox $bone_rot_x` )setKeyframe $bone_rot_x;'
'\n        if( `getAttr -k $bone_rot_y`||`getAttr -channelBox $bone_rot_y` )setKeyframe $bone_rot_y;'
'\n        if( `getAttr -k $bone_rot_z`||`getAttr -channelBox $bone_rot_z` )setKeyframe $bone_rot_z;'
'\n    }}'
'\n\n    for ($index=$start; $index < $end; $index++) {{'
'\n        currentTime $index;'
'\n        rotate -r -ws -fo {1:.1f} {2:.1f} {3:.1f};'
'\n        if( `getAttr -k $bone_rot_x`||`getAttr -channelBox $bone_rot_x` )setKeyframe $bone_rot_x;'
'\n        if( `getAttr -k $bone_rot_y`||`getAttr -channelBox $bone_rot_y` )setKeyframe $bone_rot_y;'
'\n        if( `getAttr -k $bone_rot_z`||`getAttr -channelBox $bone_rot_z` )setKeyframe $bone_rot_z;'
'\n    }}'
)

_command_rotate_once = (
'\n    print("Creating animation layer...\\n");'
'\n    animLayer  AnimLayer1;'
'\n    print("Setting animation layer defaults...\\n");'
'\n    setAttr AnimLayer1.rotationAccumulationMode 0;'
'\n    setAttr AnimLayer1.scaleAccumulationMode 1;'
'\n    print("Selecting target bone...\\n");'
'\n    select -r {0} ;'
'\n    print("Creating animation key layer for target bone...\\n");'
'\n    animLayer -e -addSelectedObjects AnimLayer1;'
'\n\n    rotate -r -ws -fo {1:.1f} {2:.1f} {3:.1f}; '
'\n    if( `getAttr -k "{0}.rx"`||`getAttr -channelBox "{0}.rx"` )setKeyframe "{0}.rx";'
'\n    if( `getAttr -k "{0}.ry"`||`getAttr -channelBox "{0}.ry"` )setKeyframe "{0}.ry";'
'\n    if( `getAttr -k "{0}.rz"`||`getAttr -channelBox "{0}.rz"` )setKeyframe "{0}.rz";'
)

def _get_command_rotation(maya_mode, bone_name, rotation):
    value = ''

    if rotation[0] != 0 or rotation[1] != 0 or rotation[2] != 0:
        
        if maya_mode == 'START':
            value = _command_rotate_once.format(
            bone_name,
            math.degrees(rotation[0]),
            math.degrees(rotation[1]),
            math.degrees(rotation[2])
            )
        else:
            value = _command_rotate_every_frame.format(
            bone_name,
            math.degrees(rotation[0]),
            math.degrees(rotation[1]),
            math.degrees(rotation[2])
            )


    return value

_command_base = (
'proc import_export (string $base_file, string $namespace, string $input, string $output)'
'\n{{'
'\n    print("Resetting scene...\\n");'
'\n    file -f -new;'
'\n    print("Importing base file...\\n");'
'\n    file -f -options "v=0;"  -ignoreVersion  -typ "mayaLT" -o $base_file;'
'\n    print("Importing animation scene...\\n");'
'\n    file -import -type "FBX" -ignoreVersion -ra true -rdn -mergeNamespacesOnClash false -namespace $namespace -options "v=0;" -importFrameRate true -importTimeRange "override" $input;'
'\n    print("Resetting timeline position...\\n");'
'\n    currentTime 0;'
'\n{1}'
'\n    print("Exporting file...\\n");'
'\n    file -force -options "v=0;" -type "FBX export" -ea $output;'
'\n    print("Export completed.\\n");'
'\n}}'
'\n\n$base_file = "{0}";'
'\n\n'
)

_import_command_template = '\nimport_export($base_file, "{0}", "{1}", "{2}/{0}.fbx");' 

def clean_path(p):
    return p.replace('\\', '/').replace('\\\\', '\\').replace('//','/').replace('//','/')

def get_maya_import_command(settings, filepaths):
    abs_maya_path = clean_path(files.abspath(settings.maya_export_dir))
    abs_template = clean_path(files.abspath(settings.maya_template))

    rotation_command = _get_command_rotation(
        settings.maya_mode,
        settings.maya_rot_bone_name, 
        settings.maya_rot_value,  
    )

    command = _command_base.format(abs_template, rotation_command)
      
    for filepath in filepaths:
        name = files.filename(filepath)

        command += _import_command_template.format(
            name, 
            clean_path(filepath),
            clean_path(abs_maya_path)
            )
    
    return command, abs_maya_path