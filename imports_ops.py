import bpy
import cspy
from cspy.imports import *
from cspy.imports_maya import *
from cspy.ops import *
from cspy import files

class IMPORTS_OT_generate_maya_import_export_commands(OPS_, Operator):
    """Generates MEL commands for Maya import/export conversion of FBX animation-only files"""
    bl_idname = "imports.generate_maya_import_export_commands"
    bl_label = "Generate Maya Commands"

    @classmethod
    def do_poll(cls, context):
        return context.scene.import_settings.import_dir != ''

    def do_execute(self, context):
        scene = context.scene
      
        s = scene.import_settings
        
        abs_path = files.abspath(s.maya_import_dir)

        filepaths = [path for path in cspy.files.get_files_in_dir(abs_path, '','','.fbx', False, s.maya_import_recursive)]
       
        command, abs_maya_path = get_maya_import_command(s, filepaths)

        command_file = '{0}/export.mel'.format(abs_maya_path)
        with open(command_file, "w") as f:
            f.write(command)
            f.close()
        
        message = 'Processed {0} file paths.'.format(len(filepaths))
        self.report( {'INFO'}, message )
        
        return {'FINISHED'}

class IMPORTS_OT_import_directory(OPS_, Operator):
    """Imports the files in a directory"""
    bl_idname = "imports.import_directory"
    bl_label = "Import Directory"

    @classmethod
    def do_poll(cls, context):
        return context.scene.import_settings.import_dir != ''

    def do_execute(self, context):
        scene = context.scene
        key_offset = 1

        s = scene.import_settings

        path = files.abspath(s.import_dir)

        filepaths = [path for path in cspy.files.get_files_in_dir(path, '','','.fbx', False, s.import_recursive)]
        
        first_imported_object_name_set = None
        
        processed = 0

        for filepath in filepaths:
            cspy.utils.deselect_all()

            print(filepath)
            name = files.filename(filepath)

            print('Importing file {0}'.format(name))

            imported_object_names = [obj.name for obj in import_fbx(filepath)]
            
            armature = None
            for imported_object_name in imported_object_names:
                obj = bpy.data.objects[imported_object_name]
                if obj.type == 'ARMATURE':
                    armature = obj
                    break
                    
            if not armature:
                print('No Armature found in import of {0}'.format(name))
                for imported_object_name in imported_object_names:
                    ro = bpy.data.objects[imported_object_name]
                    bpy.data.objects.remove(ro)
                continue
            
            processed += 1
            action = armature.animation_data.action
            action.use_fake_user = True
            action.name = name
        
            if not first_imported_object_name_set:
                first_imported_object_name_set = imported_object_names
            else:
                for imported_object_name in imported_object_names:
                    ro = bpy.data.objects[imported_object_name]
                    bpy.data.objects.remove(ro)
       
        message = 'Processed {0} file paths.'.format(processed)
        self.report( {'INFO'}, message )

        return {'FINISHED'}
