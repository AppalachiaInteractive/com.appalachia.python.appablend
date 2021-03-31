import cspy
from cspy import anim_layers
from cspy.anim_layers import *
from cspy.anim_layers_ops import *


class LAYERS_UL_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index, reversed):
        obj = bpy.context.object

        self.use_filter_sort_reverse = True
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            #row = layout.row()
            row = layout.row()
            icon = 'SOLO_ON' if item.solo else 'SOLO_OFF'
            row.prop(item,'solo', text = '', invert_checkbox=False, icon = icon, emboss=False)
            #split = row.split(factor=0.5)
            row.prop(item, "name", text="", emboss=False)
            split = row.split(factor=0)
            icon = 'HIDE_ON' if item.mute else 'HIDE_OFF'
            split.prop(item,'mute', text = '', invert_checkbox=False, icon = icon, emboss=False)

            icon = 'LOCKED' if item.lock else 'UNLOCKED'
            split.prop(item,'lock', text = '', invert_checkbox=False, icon = icon, emboss=False)

        elif self.layout_type in {'GRID'}:
            pass

    def invoke(self, context, event):
        pass

class ANIMLAYERS_PT_Panel(bpy.types.Panel):
    bl_label = "Animation Layers"
    bl_idname = "ANIMLAYERS_PT_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = "UI"
    bl_category = "Animation"


    @classmethod
    def poll(cls, context):
        return len(bpy.context.selected_objects)

    def draw(self, context):
        obj = context.object
        if obj is None:
            return
        layout = self.layout


        layout.prop(obj.als, 'track_list')
        layout.separator()

        if obj.als.track_list:
            row = layout.row()
            row.template_list("LAYERS_UL_list", "", context.object, "Anim_Layers", context.object, "track_list_index", rows=2)

            col = row.column(align=True)
            col.operator('anim.add_anim_layer', text="", icon = 'ADD')
            col.operator('anim.remove_anim_layer', text="", icon = 'REMOVE')
            col.separator()
            col.operator("anim.layer_move_up", text="", icon = 'TRIA_UP')
            col.operator("anim.layer_move_down", text="", icon = 'TRIA_DOWN')

            if not len(obj.Anim_Layers) or not len(obj.animation_data.nla_tracks):
                return
            if not hasattr(obj.animation_data, 'nla_tracks') or not len(obj.Anim_Layers) or obj.Anim_Layers[obj.track_list_index].lock: # not confirmed
                return
            track = obj.animation_data.nla_tracks[obj.track_list_index]

            col=layout.column(align = True)
            row = col.row()

            if not len(track.strips):
                return

            row.prop(track.strips[0], 'influence', slider = True, text = 'Influence')
            icon = 'KEY_DEHLT' if track.strips[0].fcurves[0].mute else 'KEY_HLT'
            row.prop(track.strips[0].fcurves[0],'mute', invert_checkbox = True, expand = True, icon_only=True, icon = icon)
            row = layout.row()
            row.prop(track.strips[0], 'blend_type', slider = True, text = 'Blend')

            merge_layers = layout.column()
            #merge_layers.operator("anim.layers_merge_down", text="New Baked Layer", icon = 'NLA')
            merge_layers.operator("anim.layers_merge_down", text="Merge / Bake", icon = 'NLA_PUSHDOWN')

            duplicateanimlayer = layout.row(align=True)
            duplicateanimlayer.operator('anim.duplicate_anim_layer', text="Duplicate Layer", icon = 'SEQ_STRIP_DUPLICATE')
            icon = 'LINKED' if obj.als.linked else 'UNLINKED'
            duplicateanimlayer.prop(obj.als, 'linked', icon_only=True, icon = icon)

            box = layout.box()
            box.label(text= 'Active Action:')
            box.template_ID(obj.animation_data, "action")

            box = layout.box()
            row = box.row()
            row.operator("anim.bones_in_layer", text="Select Bones in Layer", icon = 'BONE_DATA')
            row = box.row()
            row.operator("anim.layer_reset_keyframes", text="Reset Key Layer ", icon = 'KEYFRAME')
            row = box.row()
            row.operator("anim.layer_cyclic_fcurves", text="Cyclic Fcurves", icon = 'FCURVE')
            row.operator("anim.layer_cyclic_remove", text="Remove Fcurves", icon = 'X')

            box = layout.box()
            row = box.row()
            row.label(text= 'Keyframes From Multiple Layers:')
            row = box.row()
            split = row.split(factor=0.4, align = True)
            split.prop(obj.als, 'view_all_keyframes')
            split.prop(obj.als, 'view_all_type')
            if obj.als.view_all_keyframes:
                row = box.row()
                split = row.split(factor=0.4, align = True)
                split.prop(obj.als, 'edit_all_keyframes')
                split.prop(obj.als, 'only_selected_bones')

def register():

    bpy.types.Object.als = bpy.props.PointerProperty(type = AnimLayersSettings)
    bpy.types.Object.Anim_Layers = bpy.props.CollectionProperty(type = AnimLayersItems)
    bpy.types.Scene.AL_objects = bpy.props.CollectionProperty(type = AnimLayersObjects)
    bpy.types.Object.track_list_index = bpy.props.IntProperty(update = update_track_list)
    bpy.app.handlers.load_post.append(loadanimlayers)


def unregister():

    if loadanimlayers in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(loadanimlayers)
    if animlayers_undo_pre in bpy.app.handlers.undo_pre:
        bpy.app.handlers.undo_pre.remove(animlayers_undo_pre)
    if animlayers_undo_post in bpy.app.handlers.undo_post:
        bpy.app.handlers.undo_post.remove(animlayers_undo_post)
    remove_handler("animlayers_checks", bpy.app.handlers.depsgraph_update_pre)

    del bpy.types.Object.track_list_index
    del bpy.types.Object.als
    bpy.msgbus.clear_by_owner(bpy.context.scene)
    bpy.msgbus.clear_by_owner(bpy.context.object)
       