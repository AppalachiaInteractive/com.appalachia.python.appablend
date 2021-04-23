import bpy
from appablend.animation_layers.core import (AnimLayersItems,
                                             AnimLayersObjects,
                                             AnimLayersSettings,
                                             animlayers_undo_post,
                                             animlayers_undo_pre,
                                             loadanimlayers, remove_handler,
                                             update_track_list)
from appablend.animation_layers.ops import ANIM_bones_in_layer
from appablend.common.basetypes.ui import PT_, UI
from appablend.common.core.enums import icons


class LAYERS_UL_list(bpy.types.UIList):
    def draw_item(
        self,
        context,
        layout,
        data,
        item,
        icon,
        active_data,
        active_propname,
        index,
        reversed,
    ):
        obj = bpy.context.object

        self.use_filter_sort_reverse = True
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            # row = layout.row()
            row = layout.row()
            icon = "SOLO_ON" if item.solo else "SOLO_OFF"
            row.prop(
                item, "solo", text="", invert_checkbox=False, icon=icon, emboss=False
            )
            # split = row.split(factor=0.5)
            row.prop(item, "name", text="", emboss=False)
            split = row.split(factor=0)
            icon = "HIDE_ON" if item.mute else "HIDE_OFF"
            split.prop(
                item, "mute", text="", invert_checkbox=False, icon=icon, emboss=False
            )

            icon = "LOCKED" if item.lock else "UNLOCKED"
            split.prop(
                item, "lock", text="", invert_checkbox=False, icon=icon, emboss=False
            )

        elif self.layout_type in {"GRID"}:
            pass

    def invoke(self, context, event):
        pass


class PT_AL_AnimLayers(PT_):
    bl_order = 0

    @classmethod
    def poll(cls, context):
        return len(bpy.context.selected_objects)


class PT_AL_AnimLayers_SUB(PT_):
    bl_order = 1

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if not obj or not obj.als or not obj.als.track_list:
            return False
        if not len(context.selected_objects):
            return False
        if not len(obj.Anim_Layers) or not len(obj.animation_data.nla_tracks):
            return False
        if (
            not hasattr(obj.animation_data, "nla_tracks")
            or not len(obj.Anim_Layers)
            or obj.Anim_Layers[obj.track_list_index].lock
        ):  # not confirmed
            return False
        return True


class VIEW_3D_PT_UI_Tool_AL_AnimLayers(
    UI.VIEW_3D.UI.Tool, PT_AL_AnimLayers, bpy.types.Panel
):
    bl_label = "Animation Layers"
    bl_idname = "VIEW_3D_PT_UI_Tool_AL_AnimLayers"
    bl_icon = icons.NLA

    def draw(self, context):
        obj = context.object
        if obj is None:
            return
        layout = self.layout

        row = layout.row()
        enabled = obj.als.track_list
        icon = icons.CHECKBOX_HLT if enabled else icons.CHECKBOX_DEHLT
        row.prop(obj.als, "track_list", text="", icon=icon, toggle=True)

        if obj.als.track_list:
            row.template_list(
                "LAYERS_UL_list",
                "",
                context.object,
                "Anim_Layers",
                context.object,
                "track_list_index",
                rows=2,
            )

            col = row.column(align=True)
            col.operator("anim.add_anim_layer", text="", icon="ADD")
            col.operator("anim.remove_anim_layer", text="", icon="REMOVE")

            col = row.column(align=True)
            col.operator("anim.layer_move_up", text="", icon="TRIA_UP")
            col.operator("anim.layer_move_down", text="", icon="TRIA_DOWN")

            if not len(obj.Anim_Layers) or not len(obj.animation_data.nla_tracks):
                return
            if (
                not hasattr(obj.animation_data, "nla_tracks")
                or not len(obj.Anim_Layers)
                or obj.Anim_Layers[obj.track_list_index].lock
            ):  # not confirmed
                return

            track = obj.animation_data.nla_tracks[obj.track_list_index]

            col = layout.column(align=True)
            row = col.row()

            row.prop(track.strips[0], "influence", slider=True, text="Influence")
            icon = "KEY_DEHLT" if track.strips[0].fcurves[0].mute else "KEY_HLT"
            row.prop(
                track.strips[0].fcurves[0],
                "mute",
                invert_checkbox=True,
                expand=True,
                icon_only=True,
                icon=icon,
            )
            # row = layout.row()
            row.prop(track.strips[0], "blend_type", slider=True, text="Blend")

            row = layout.row(align=True)
            # merge_layers.operator("anim.layers_merge_down", text="New Baked Layer", icon = 'NLA')
            row.operator(
                "anim.layers_merge_down", text="Merge / Bake", icon="NLA_PUSHDOWN"
            )

            # duplicateanimlayer = layout.row(align=True)
            row.operator(
                "anim.duplicate_anim_layer",
                text="Duplicate Layer",
                icon="SEQ_STRIP_DUPLICATE",
            )
            icon = "LINKED" if obj.als.linked else "UNLINKED"
            row.prop(obj.als, "linked", icon_only=True, icon=icon)


class VIEW_3D_PT_UI_Tool_AL_AnimLayers_040_ActiveAction(
    UI.VIEW_3D.UI.Tool, PT_AL_AnimLayers_SUB, bpy.types.Panel
):
    bl_label = "Active Action"
    bl_idname = "VIEW_3D_PT_UI_Tool_AL_AnimLayers_040_ActiveAction"
    bl_icon = icons.ACTION
    bl_parent_id = VIEW_3D_PT_UI_Tool_AL_AnimLayers.bl_idname

    def draw(self, context):
        obj = context.object
        layout = self.layout

        track = obj.animation_data.nla_tracks[obj.track_list_index]

        if not len(track.strips):
            return

        box = layout.box()
        box.template_ID(obj.animation_data, "action")

        box = layout.box()
        row = box.row()
        row.operator(
            ANIM_bones_in_layer.bl_idname,
            text="Select Bones in Layer",
            icon="BONE_DATA",
        )
        # row = box.row()
        row.operator(
            "anim.layer_reset_keyframes", text="Reset Key Layer ", icon="KEYFRAME"
        )
        row = box.row()
        row.operator("anim.layer_cyclic_fcurves", text="Cyclic Fcurves", icon="FCURVE")
        row.operator("anim.layer_cyclic_remove", text="Remove Fcurves", icon="X")


class VIEW_3D_PT_UI_Tool_AL_AnimLayers_050_MultipleLayers(
    UI.VIEW_3D.UI.Tool, PT_AL_AnimLayers_SUB, bpy.types.Panel
):
    bl_label = "Multiple Layers"
    bl_idname = "VIEW_3D_PT_UI_Tool_AL_AnimLayers_050_MultipleLayers"
    bl_icon = icons.SEQ_STRIP_META
    bl_parent_id = VIEW_3D_PT_UI_Tool_AL_AnimLayers.bl_idname

    def draw(self, context):
        obj = context.object
        layout = self.layout

        track = obj.animation_data.nla_tracks[obj.track_list_index]
        if not len(track.strips):
            return

        box = layout.box()
        row = box.row()
        split = row.split(factor=0.4, align=True)
        split.prop(obj.als, "view_all_keyframes")
        split.prop(obj.als, "view_all_type")
        if obj.als.view_all_keyframes:
            row = box.row()
            split = row.split(factor=0.4, align=True)
            split.prop(obj.als, "edit_all_keyframes")
            split.prop(obj.als, "only_selected_bones")


def register():

    bpy.types.Object.als = bpy.props.PointerProperty(type=AnimLayersSettings)
    bpy.types.Object.Anim_Layers = bpy.props.CollectionProperty(type=AnimLayersItems)
    bpy.types.Scene.AL_objects = bpy.props.CollectionProperty(type=AnimLayersObjects)
    bpy.types.Object.track_list_index = bpy.props.IntProperty(update=update_track_list)
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
