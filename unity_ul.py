import cspy
from cspy.unity import *
from cspy.unity_ops import *
from cspy.ui import PT_OPTIONS, PT_, UI
from cspy.polling import POLL
from cspy import subtypes

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
            sort = [(idx, getattr(it, 'frame_start', "")) for idx, it in enumerate(items)]

            ordered = helper_funcs.sort_items_helper(sort, lambda e: e[1] if not hasattr(e[1], 'lower') else e[1].lower())

        return filtered, ordered

    def draw_item(self, _context, layout, _data, item, icon, _active_data_, _active_propname, _index):
        try:
            if self.layout_type in {'DEFAULT', 'COMPACT'}:
                draw_clip_row(item, layout)

            elif self.layout_type == 'GRID':
                layout.alignment = 'CENTER'
                layout.label(text="", icon_value=icon)
        except Exception as inst:
            print(inst)
            raise
