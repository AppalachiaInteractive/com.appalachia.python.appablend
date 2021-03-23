import cspy
from cspy.unity import *
from cspy.unity_ops import *
from cspy.ui import PT_OPTIONS, PT_, UI
from cspy.polling import POLL
from cspy import subtypes

def draw_clip(unity_clip, layout):
    box = layout.box()
    col = box.column(align=True)
    row = col.row(align=True)
    row_1 = row.split()
    row_1.enabled = False
    row_1.prop(unity_clip, 'action')
    row_2 = row.split()
    row_2.operator(UNITY_OT_sync_actions_with_clips.bl_idname, text='Sync')
    row_2.enabled = (unity_clip.action != unity_clip.id_data)
    col = box.column(align=True)
    col.prop(unity_clip, 'fbx_name')
    col.prop(unity_clip, 'name')
    col.enabled = False

    col = box.column(align=True)

    row = col.row(align=True)
    clamp_button = row.operator(UNITY_OT_clamp_to_clip.bl_idname)
    if unity_clip and unity_clip.action:
        clamp_button.action_name = unity_clip.action.name
        clamp_button.clip_name = unity_clip.name
    play_button = row.operator(UNITY_OT_clamp_to_clip_and_play.bl_idname)
    if unity_clip and unity_clip.action:
        play_button.action_name = unity_clip.action.name
        play_button.clip_name = unity_clip.name

    col.separator()
    row = col.row(align=True)
    row.prop(unity_clip, 'start_frame', text='Start')
    row.prop(unity_clip, 'stop_frame', text='Stop')
    row.prop(unity_clip, 'loop_time', text='Loop?')

    col.separator()
    row = col.row(align=True)
    row.prop(unity_clip, 'rot_bake_into',text='Bake Rot.')
    row.prop(unity_clip, 'y_bake_into', text='Bake Y')
    row.prop(unity_clip, 'xz_bake_into', text='Bake XZ')

    col.separator()
    row = col.row(align=True)
    row.prop(unity_clip, 'rot_offset', text='Rot. Offset')
    row.prop(unity_clip, 'y_offset', text='Y Offset')

def draw_clip_row(unity_clip, layout):
    layout.label(text=unity_clip.name)

class UNITY_UL_UnityClips(bpy.types.UIList):
    use_filter_sort_time: bpy.props.BoolProperty(name="Sort By Frame", default=True)

    show_exclusive: bpy.props.BoolProperty(name="Show Exclusive", default=False)
    show_loop: bpy.props.BoolProperty(name="Show Looping", default=False)
    show_bake_rot: bpy.props.BoolProperty(name="Show Baked Rot.", default=False)
    show_bake_y: bpy.props.BoolProperty(name="Show Baked Y.", default=False)
    show_bake_xz: bpy.props.BoolProperty(name="Show Baked XZ.", default=False)
    show_offset_rot: bpy.props.BoolProperty(name="Show Offset Rot.", default=False)
    show_offset_y: bpy.props.BoolProperty(name="Show Offset Y", default=False)

    hide_exclusive: bpy.props.BoolProperty(name="Hide Exclusive", default=False)
    hide_loop: bpy.props.BoolProperty(name="Hide Looping", default=False)
    hide_bake_rot: bpy.props.BoolProperty(name="Hide Baked Rot.", default=False)
    hide_bake_y: bpy.props.BoolProperty(name="Hide Baked Y.", default=False)
    hide_bake_xz: bpy.props.BoolProperty(name="Hide Baked XZ.", default=False)
    hide_offset_rot: bpy.props.BoolProperty(name="Hide Offset Rot.", default=False)
    hide_offset_y: bpy.props.BoolProperty(name="Hide Offset Y", default=False)

    def draw_filter(self, context, layout):
        row = layout.row()
        row.label(text="Show Only:")
        row.prop(self, "show_exclusive", text='Exclusive', toggle=True)
        row = layout.row()
        row.prop(self, "show_loop", text='Loop', toggle=True)
        row.prop(self, "show_offset_rot", text='Offs. Rot', toggle=True)
        row.prop(self, "show_offset_y", text='Offs. Y', toggle=True)
        row = layout.row()
        row.prop(self, "show_bake_rot", text='Bake Rot', toggle=True)
        row.prop(self, "show_bake_y", text='Bake Y', toggle=True)
        row.prop(self, "show_bake_xz", text='Bake XZ', toggle=True)

        row = layout.row()
        row.label(text="Hide:")
        row.prop(self, "hide_exclusive", text='Exclusive', toggle=True)
        row = layout.row()
        row.prop(self, "hide_loop", text='Loop', toggle=True)
        row.prop(self, "hide_offset_rot", text='Offs. Rot', toggle=True)
        row.prop(self, "hide_offset_y", text='Offs. Y', toggle=True)
        row = layout.row()
        row.prop(self, "hide_bake_rot", text='Bake Rot', toggle=True)
        row.prop(self, "hide_bake_y", text='Bake Y', toggle=True)
        row.prop(self, "hide_bake_xz", text='Bake XZ', toggle=True)

        row = layout.row()
        subrow = row.row(align=True)
        subrow.prop(self, "filter_name", text="")
        subrow.prop(self, "use_filter_invert", text="", icon='ARROW_LEFTRIGHT')

        subrow = row.row(align=True)
        subrow.prop(self, "use_filter_sort_alpha", text='', icon='SORTALPHA')
        subrow.prop(self, "use_filter_sort_time", text='', icon='SORTTIME')
        icon = 'SORT_ASC' if self.use_filter_sort_reverse else 'SORT_DESC'
        subrow.prop(self, "use_filter_sort_reverse", text="", icon=icon)

    def filter_items(self, context, data, propname):
        """Filter and order items in the list."""

        helper_funcs = bpy.types.UI_UL_list

        items = getattr(data, propname)

        # Filtering by name
        filtered = helper_funcs.filter_items_by_name(self.filter_name, self.bitflag_filter_item, items, "name", reverse=False)

        if not filtered:
            filtered = [self.bitflag_filter_item] * len(items)

        show_filter = self.show_loop or self.show_bake_rot or self.show_bake_xz or self.show_bake_y or self.show_offset_rot or self.show_offset_y
        hide_filter = self.hide_loop or self.hide_bake_rot or self.hide_bake_xz or self.hide_bake_y or self.hide_offset_rot or self.hide_offset_y

        for index, item in enumerate(items):
            excluded=False

            if not item:
                excluded = True

            if not excluded and show_filter:
                if self.show_exclusive: # all of them
                    included = (
                        (not self.show_loop or item.loop_time) and
                        (not self.show_bake_rot or item.rot_bake_into) and
                        (not self.show_bake_y or item.y_bake_into) and
                        (not self.show_bake_xz or item.xz_bake_into) and
                        (not self.show_offset_rot or item.rot_offset != 0.0) and
                        (not self.show_offset_y or item.y_offset != 0.0))
                else: # any of them
                    included = (
                        (self.show_loop and item.loop_time) or
                        (self.show_bake_rot and item.rot_bake_into) or
                        (self.show_bake_y and item.y_bake_into) or
                        (self.show_bake_xz and item.xz_bake_into) or
                        (self.show_offset_rot and item.rot_offset != 0.0) or
                        (self.show_offset_y and item.y_offset != 0.0))
                excluded = not included

            if not excluded and hide_filter:
                if self.hide_exclusive: # all of them
                    included = (
                        (not self.hide_loop or item.loop_time) and
                        (not self.hide_bake_rot or item.rot_bake_into) and
                        (not self.hide_bake_y or item.y_bake_into) and
                        (not self.hide_bake_xz or item.xz_bake_into) and
                        (not self.hide_offset_rot or item.rot_offset != 0.0) and
                        (not self.hide_offset_y or item.y_offset != 0.0))
                else: # any of them
                    included = (
                        (self.hide_loop and item.loop_time) or
                        (self.hide_bake_rot and item.rot_bake_into) or
                        (self.hide_bake_y and item.y_bake_into) or
                        (self.hide_bake_xz and item.xz_bake_into) or
                        (self.hide_offset_rot and item.rot_offset != 0.0) or
                        (self.hide_offset_y and item.y_offset != 0.0))
                excluded = not included

            if excluded:
                filtered[index] &= ~self.bitflag_filter_item

        ordered = []

        # Reorder by name or average weight.
        if self.use_filter_sort_alpha:
            sort = [(idx, getattr(it, 'name', "")) for idx, it in enumerate(items)]
        elif self.use_filter_sort_time:
            sort = [(idx, getattr(it, 'start_frame', "")) for idx, it in enumerate(items)]

            ordered = helper_funcs.sort_items_helper(sort, lambda e: e[1] if not hasattr(e[1], 'lower') else e[1].lower())

        return filtered, ordered

    def draw_item(self, _context, layout, _data, item, icon, _active_data_, _active_propname, _index):
        try:
            if self.layout_type in {'DEFAULT', 'COMPACT'}:
                #draw_clip(item, layout)
                draw_clip_row(item, layout)

            elif self.layout_type == 'GRID':
                layout.alignment = 'CENTER'
                layout.label(text="", icon_value=icon)
        except Exception as inst:
            print(inst)
            raise

def draw_clip_buttons(layout, scene, context):
    layout.prop(scene, 'unity_sheet_dir_path')
    row = layout.row(align=True)
    row.operator(UNITY_OT_refresh_clip_data.bl_idname)
    row.operator(UNITY_OT_refresh_clip_data_all.bl_idname)
    row = layout.row(align=True)
    row.operator(UNITY_OT_clear_clip_data.bl_idname)
    row.operator(UNITY_OT_clear_clip_data_all.bl_idname)
    row = layout.row(align=True)
    row.operator(UNITY_OT_sort_clip_data.bl_idname)
    row.operator(UNITY_OT_sort_clip_data_all.bl_idname)
    row = layout.row(align=True)
    row.prop(context.active_object.animation_data.action, 'unity_clip_template')
    row.operator(UNITY_OT_copy_clips_from_template.bl_idname)
    row = layout.row(align=True)
    row.operator(UNITY_OT_demarcate_clips.bl_idname)

class VIEW_3D_PT_UI_Tool_Unity(bpy.types.Panel, PT_, UI.VIEW_3D.UI.Tool):
    bl_label = "Unity"
    bl_idname = "VIEW_3D_PT_UI_Tool_Unity"
    bl_icon = cspy.icons.FILE_3D

    @classmethod
    def do_poll(cls, context):
        return POLL.active_object_animation_data(context)

    def do_draw(self, context, scene, layout, obj):
        draw_clip_buttons(layout, scene, context)

        action = obj.animation_data.action

        layout.template_list("UNITY_UL_UnityClips", "", action, "unity_clips", action, "unity_index", rows=2,maxrows=4)

        unity_clip = action.unity_clips[action.unity_index]
        draw_clip(unity_clip, layout)


class DOPESHEET_EDITOR_PT_UI_Tool_Unity(bpy.types.Panel, PT_, UI.DOPESHEET_EDITOR.UI):
    bl_label = "Unity"
    bl_idname = "DOPESHEET_EDITOR_PT_UI_Tool_Unity"
    bl_icon = cspy.icons.FILE_3D

    @classmethod
    def do_poll(cls, context):
        return POLL.active_object_animation_data(context)

    def do_draw(self, context, scene, layout, obj):
        draw_clip_buttons(layout, scene, context)

        action = obj.animation_data.action

        if len(action.unity_clips) == 0:
            return

        layout.template_list("UNITY_UL_UnityClips", "", action, "unity_clips", action, "unity_index", rows=2,maxrows=4)

        if action.unity_index < 0:
            return

        unity_clip = action.unity_clips[action.unity_index]
        draw_clip(unity_clip, layout)

def register():
    bpy.types.Scene.unity_sheet_dir_path = bpy.props.StringProperty(name="Sheet Dir Path", subtype=subtypes.StringProperty.Subtypes.DIR_PATH)
    bpy.types.Action.unity_clip_template = bpy.props.PointerProperty(name="Unity Clip Template", type=bpy.types.Action)
    bpy.types.Action.unity_clips = bpy.props.CollectionProperty(name="Unity Clips", type=UnityClipMetadata)
    bpy.types.Action.unity_index = bpy.props.IntProperty(name='Unity Index', default = 0, min=0)
    bpy.types.Action.unity_clips_protected = bpy.props.BoolProperty(name='Unity Clips Protected', default=False)
    bpy.types.Object.rot_bake_into = bpy.props.IntProperty(name="rot_bake_into", min=0,max=1,default=1)
    bpy.types.Object.rot_offset = bpy.props.FloatProperty(name="rot_offset", default=0.0)
    bpy.types.Object.y_bake_into = bpy.props.IntProperty(name="y_bake_into", min=0,max=1,default=1)
    bpy.types.Object.y_offset = bpy.props.FloatProperty(name="y_offset", default=0.0)
    bpy.types.Object.xz_bake_into = bpy.props.IntProperty(name="xz_bake_into", min=0,max=1,default=1)

def unregister():
    del bpy.types.Scene.unity_sheet_dir_path
    del bpy.types.Action.unity_clip_template
    del bpy.types.Action.unity_clips
    del bpy.types.Action.unity_index
    del bpy.types.Action.unity_clips_protected
    del bpy.types.Object.rot_bake_into
    del bpy.types.Object.rot_offset
    del bpy.types.Object.y_bake_into
    del bpy.types.Object.y_offset
    del bpy.types.Object.xz_bake_into