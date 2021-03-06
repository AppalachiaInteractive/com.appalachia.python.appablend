import bpy
from appablend.common.core.enums import icons
from appablend.unity.ops import UNITY_OT_refresh_scene_all_clips


def draw_clip_row(context, action, unity_clip, layout):
    try:

        if context.scene.unity_settings.mode == "SCENE":
            col1 = layout.column(align=True)
            col1.label(text=action.name)
            col2 = layout.row(align=True)
            col2.alignment = "RIGHT"
            col2.label(text=unity_clip.name)

        else:
            layout.label(text=unity_clip.name)
    except Exception as e:
        print("draw_clip_row: {0}: {1}".format(unity_clip.name, e))


class Unity_UL_Filters(bpy.types.PropertyGroup):
    filter_name: bpy.props.StringProperty(name="Filter By Name")
    use_name_invert: bpy.props.BoolProperty(name="Invert")

    use_filter_invert: bpy.props.BoolProperty(name="Invert")

    use_filter_clip_count: bpy.props.BoolProperty(
        name="Filter Clip Count", default=False
    )
    clip_count_single: bpy.props.BoolProperty(name="Filter Single", default=False)

    show_show: bpy.props.BoolProperty(
        name="Show Exclusive Show Settings", default=False
    )
    show_hide: bpy.props.BoolProperty(
        name="Show Exclusive Hide Settings", default=False
    )

    show_exclusive: bpy.props.BoolProperty(name="Show Exclusive", default=False)
    show_loop: bpy.props.BoolProperty(name="Show Looping", default=False)

    show_bake_rot: bpy.props.BoolProperty(name="Show Bake Rot.", default=False)
    show_bake_x: bpy.props.BoolProperty(name="Show Bake X", default=False)
    show_bake_y: bpy.props.BoolProperty(name="Show Bake Y", default=False)
    show_bake_z: bpy.props.BoolProperty(name="Show Bake z", default=False)
    show_offset_rot: bpy.props.BoolProperty(name="Show Offset Rot.", default=False)
    show_offset_x: bpy.props.BoolProperty(name="Show Offset X", default=False)
    show_offset_y: bpy.props.BoolProperty(name="Show Offset Y", default=False)
    show_offset_z: bpy.props.BoolProperty(name="Show Offset Z", default=False)

    hide_exclusive: bpy.props.BoolProperty(name="Hide Exclusive", default=False)
    hide_loop: bpy.props.BoolProperty(name="Hide Looping", default=False)

    hide_bake_rot: bpy.props.BoolProperty(name="Hide Bake Rot.", default=False)
    hide_bake_x: bpy.props.BoolProperty(name="Hide Bake X", default=False)
    hide_bake_y: bpy.props.BoolProperty(name="Hide Bake Y", default=False)
    hide_bake_z: bpy.props.BoolProperty(name="Hide Bake Z", default=False)
    hide_offset_rot: bpy.props.BoolProperty(name="Hide Offset Rot.", default=False)
    hide_offset_x: bpy.props.BoolProperty(name="Hide Offset X", default=False)
    hide_offset_y: bpy.props.BoolProperty(name="Hide Offset Y", default=False)
    hide_offset_z: bpy.props.BoolProperty(name="Hide Offset Z", default=False)

    def filter_items_by_name(self, pattern, item, propname="name", reverse=False):
        import fnmatch

        if not pattern or not item:  # Empty pattern or list = no filtering!
            return False

        # Implicitly add heading/trailing wildcards.
        pattern = "*" + pattern + "*"

        name = getattr(item, propname, None)

        # This is similar to a logical xor
        match = bool(name and fnmatch.fnmatch(name, pattern))
        should_filter = not match

        if reverse:
            return not should_filter

        return should_filter

    def should_filter(self, context, item):
        show_filter = (
            self.show_loop
            or self.show_bake_rot
            or self.show_bake_x
            or self.show_bake_y
            or self.show_bake_z
            or self.show_offset_rot
            or self.show_offset_x
            or self.show_offset_y
            or self.show_offset_z
        )
        hide_filter = (
            self.hide_loop
            or self.hide_bake_rot
            or self.hide_bake_x
            or self.hide_bake_y
            or self.hide_bake_z
            or self.hide_offset_rot
            or self.hide_offset_x
            or self.hide_offset_y
            or self.hide_offset_z
        )

        excluded = False

        if not item or not item.action:
            excluded = True

        excluded = excluded or item is None
        excluded = excluded or item.action is None
        excluded = excluded or item.action.unity_metadata is None
        excluded = excluded or item.action.unity_metadata.clips_hidden
        excluded = excluded or self.filter_items_by_name(
            self.filter_name, item, propname="name", reverse=self.use_name_invert
        )

        scene_mode = context.scene.unity_settings.mode == "SCENE"

        excluded = excluded or (
            scene_mode
            and (
                item.action.name.lower() == "master"
                or item.action.unity_metadata.master_action
            )
        )

        if not excluded and (scene_mode and self.use_filter_clip_count):
            if self.clip_count_single and len(item.action.unity_clips) != 1:
                excluded = True
            elif not self.clip_count_single and len(item.action.unity_clips) < 2:
                excluded = True

        if not excluded and show_filter:
            if self.show_exclusive:  # all of them
                included = (
                    (not self.show_loop or item.loop_time)
                    and (not self.show_bake_rot or item.root_motion_rot_bake_into)
                    and (not self.show_bake_x or item.root_motion_x_bake_into)
                    and (not self.show_bake_y or item.root_motion_y_bake_into)
                    and (not self.show_bake_z or item.root_motion_z_bake_into)
                    and (not self.show_offset_rot or item.root_motion_rot_offset != 0.0)
                    and (not self.show_offset_x or item.root_motion_x_offset != 0.0)(
                        not self.show_offset_y or item.root_motion_y_offset != 0.0
                    )(not self.show_offset_z or item.root_motion_z_offset != 0.0)
                )
            else:  # any of them
                included = (
                    (self.show_loop and item.loop_time)
                    or (self.show_bake_rot and item.root_motion_rot_bake_into)
                    or (self.show_bake_x and item.root_motion_x_bake_into)
                    or (self.show_bake_y and item.root_motion_y_bake_into)
                    or (self.show_bake_z and item.root_motion_z_bake_into)
                    or (self.show_offset_rot and item.root_motion_rot_offset != 0.0)
                    or (self.show_offset_x and item.root_motion_x_offset != 0.0)(
                        self.show_offset_y and item.root_motion_y_offset != 0.0
                    )(self.show_offset_z and item.root_motion_z_offset != 0.0)
                )
            excluded = not included

        if not excluded and hide_filter:
            if self.hide_exclusive:  # all of them
                included = (
                    (not self.hide_loop or item.loop_time)
                    and (not self.hide_bake_rot or item.rot_bake_into)
                    and (not self.hide_bake_x or item.x_bake_into)
                    and (not self.hide_bake_y or item.y_bake_into)
                    and (not self.hide_bake_z or item.z_bake_into)
                    and (not self.hide_offset_rot or item.rot_offset != 0.0)
                    and (not self.hide_offset_x or item.x_offset != 0.0)(
                        not self.hide_offset_y or item.y_offset != 0.0
                    )(not self.hide_offset_z or item.z_offset != 0.0)
                )
            else:  # any of them
                included = (
                    (self.hide_loop and item.loop_time)
                    or (self.hide_bake_rot and item.rot_bake_into)
                    or (self.hide_bake_x and item.x_bake_into)
                    or (self.hide_bake_y and item.y_bake_into)
                    or (self.hide_bake_z and item.z_bake_into)
                    or (self.hide_offset_rot and item.rot_offset != 0.0)
                    or (self.hide_offset_x and item.x_offset != 0.0)(
                        self.hide_offset_y and item.y_offset != 0.0
                    )(self.hide_offset_z and item.z_offset != 0.0)
                )
            excluded = not included

        return excluded

    def draw_clip_refresh(self, context, layout, row):
        if context.scene.unity_settings.mode == "SCENE":
            row.operator(
                UNITY_OT_refresh_scene_all_clips.bl_idname,
                icon=icons.FILE_REFRESH,
                text="",
            )

    def draw_name_search(self, context, layout, row):
        subrow = row.row(align=True)
        subrow.prop(self, "filter_name", text="")
        subrow.prop(self, "use_name_invert", text="", icon="ARROW_LEFTRIGHT")

    def draw_filter_clip_count(self, context, layout, row):
        scene_mode = context.scene.unity_settings.mode == "SCENE"

        subrow = row.row(align=True)
        subrow.enabled = scene_mode
        count_icon = (
            icons.SELECT_SUBTRACT if self.clip_count_single else icons.SELECT_EXTEND
        )
        subrow.prop(
            self,
            "use_filter_clip_count",
            text="",
            toggle=True,
            icon=icons.SELECT_INTERSECT,
        )

        subrow2 = subrow.split()
        subrow2.enabled = self.use_filter_clip_count
        subrow2.prop(self, "clip_count_single", text="", toggle=True, icon=count_icon)

    def draw_filter_show_hide(self, context, layout, subrow):

        subrow.prop(self, "show_show", text="", toggle=True, icon=icons.HIDE_OFF)
        subrow.prop(self, "show_hide", text="", toggle=True, icon=icons.HIDE_ON)

        if self.show_show:
            box = layout.box()
            row = box.row()
            row.label(text="Show Only:")
            row.prop(self, "show_exclusive", text="Exclusive", toggle=True)
            row.prop(self, "show_loop", text="Loop", toggle=True)
            row = box.row()
            row.prop(self, "show_offset_rot", text="Offs. Rot", toggle=True)
            row.prop(self, "show_offset_x", text="Offs. X", toggle=True)
            row.prop(self, "show_offset_y", text="Offs. Y", toggle=True)
            row.prop(self, "show_offset_z", text="Offs. Z", toggle=True)
            row = box.row()
            row.prop(self, "show_bake_rot", text="Bake Rot", toggle=True)
            row.prop(self, "show_bake_z", text="Bake X", toggle=True)
            row.prop(self, "show_bake_y", text="Bake Y", toggle=True)
            row.prop(self, "show_bake_z", text="Bake Z", toggle=True)

        if self.show_hide:
            box = layout.box()
            row = box.row()
            row.label(text="Hide:")
            row.prop(self, "hide_exclusive", text="Exclusive", toggle=True)
            row.prop(self, "hide_loop", text="Loop", toggle=True)
            row = box.row()
            row.prop(self, "hide_offset_rot", text="Offs. Rot", toggle=True)
            row.prop(self, "hide_offset_x", text="Offs. X", toggle=True)
            row.prop(self, "hide_offset_y", text="Offs. Y", toggle=True)
            row.prop(self, "hide_offset_z", text="Offs. Z", toggle=True)
            row = box.row()
            row.prop(self, "hide_bake_rot", text="Bake Rot", toggle=True)
            row.prop(self, "hide_bake_x", text="Bake X", toggle=True)
            row.prop(self, "hide_bake_y", text="Bake Y", toggle=True)
            row.prop(self, "hide_bake_z", text="Bake Z", toggle=True)

        subrow.prop(self, "use_filter_invert", text="", icon="ARROW_LEFTRIGHT")


class UNITY_UL_UnityClips(bpy.types.UIList):
    use_filter_sort_time: bpy.props.BoolProperty(name="Sort By Frame", default=True)

    def draw_filter(self, context, layout):
        row = layout.row()

        scene_filters = context.scene.unity_clip_filters

        scene_filters.draw_clip_refresh(context, layout, row)

        scene_filters.draw_name_search(context, layout, row)

        scene_filters.draw_filter_clip_count(context, layout, row)

        scene_mode = context.scene.unity_settings.mode == "SCENE"

        subrow = row.row(align=True)
        subrow.prop(self, "use_filter_sort_alpha", text="", icon="SORTALPHA")
        subrow.prop(self, "use_filter_sort_time", text="", icon="SORTTIME")
        icon = "SORT_ASC" if self.use_filter_sort_reverse else "SORT_DESC"
        subrow.prop(self, "use_filter_sort_reverse", text="", icon=icon)

        scene_filters.draw_filter_show_hide(context, layout, subrow)

    def filter_items(self, context, data, propname):
        """Filter and order items in the list."""

        helper_funcs = bpy.types.UI_UL_list

        items = getattr(data, propname)

        scene_filters = context.scene.unity_clip_filters

        filtered = [self.bitflag_filter_item] * len(items)

        for index, item in enumerate(items):
            excluded = scene_filters.should_filter(context, item)

            if excluded or scene_filters.use_filter_invert:
                filtered[index] &= ~self.bitflag_filter_item

        ordered = []

        # Reorder by name or average weight.
        if self.use_filter_sort_alpha:
            sort = [(idx, getattr(it, "name", "")) for idx, it in enumerate(items)]
        elif self.use_filter_sort_time:
            sort = [
                (idx, getattr(it, "frame_start", "")) for idx, it in enumerate(items)
            ]

            ordered = helper_funcs.sort_items_helper(
                sort, lambda e: e[1] if not hasattr(e[1], "lower") else e[1].lower()
            )

        return filtered, ordered

    def draw_item(
        self,
        _context,
        layout,
        _data,
        item,
        icon,
        _active_data_,
        _active_propname,
        _index,
    ):
        try:
            if not item or not item.action:
                return
            if self.layout_type in {"DEFAULT", "COMPACT"}:
                draw_clip_row(_context, item.action, item, layout)

            elif self.layout_type == "GRID":
                layout.alignment = "CENTER"
                layout.label(text="", icon_value=icon)
        except Exception as inst:
            print(inst)
            raise
