import bpy

def purge_unused():
    x =  {'FINISHED'}
    while 'FINISHED' in x:
        x = bpy.ops.outliner.orphans_purge()