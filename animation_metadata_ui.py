from cspy.animation_metadata import *
from cspy.polling import POLL
from cspy.ui import PT_OPTIONS, PT_, UI

class ANIMMETA_PT_SPLIT(bpy.types.Panel, PT_, UI.PROPERTIES.WINDOW.DATA):
    bl_label = 'Animation Splitting'
    bl_icon = cspy.icons.IMGDISPLAY

    @classmethod
    def do_poll(cls, context):
        return True
        #return POLL.active_ARMATURE(context)

    def do_draw(self, context, scene, layout, obj):        
        obj.animation_split.draw(layout, context)
        layout.operator(AS_Split_Action_Via_Sheet.bl_idname)
    

def register():  
    bpy.types.Object.animation_split = bpy.props.PointerProperty(type=AnimationSplit)
    bpy.types.Object.animation_split_clips = bpy.props.CollectionProperty(type=AnimationClipMetadata)
    bpy.types.Action.action_metadata = bpy.props.PointerProperty(type=ActionMetadata)

def unregister():    
    del bpy.types.Object.animation_split
    del bpy.types.Object.animation_split_clips
    del bpy.types.Action.action_metadata
