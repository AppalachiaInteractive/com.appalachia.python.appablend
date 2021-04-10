import bpy
from bpy.types import Menu, UIList
from cspy.polling import DOIF
from cspy.ui import PT_OPTIONS, PT_, UI
from cspy.animation_retargeting import *
from cspy.animation_retargeting_ops import *

class OBJECT_UL_targetbones(UIList):
    # Be careful not to shadow FILTER_ITEM!

    def draw_filter(self, context, layout):
        anim_ret = context.active_object.anim_ret
        # Nothing much to say here, it's usual UI code...
        row = layout.row()

        row.prop(anim_ret, "show_def", text='DEF', toggle=True)
        row.prop(anim_ret, "show_mch", text='MCH',  toggle=True)
        row.prop(anim_ret, "show_org", text='ORG',  toggle=True)
        row.prop(anim_ret, "show_fk", text='FK',  toggle=True)
        row.prop(anim_ret, "show_ik", text='IK',  toggle=True)
        row.prop(anim_ret, "filter_layers", text='LAYER',  toggle=True)

        row = layout.row()
        subrow = row.row(align=True)
        subrow.prop(self, "filter_name", text="")
        subrow.prop(self, "use_filter_invert", text="", icon='ARROW_LEFTRIGHT')

        subrow = row.row(align=True)
        subrow.prop(self, "use_filter_sort_alpha", text='', icon='SORTALPHA')
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

        d = context.active_object.data
        anim_ret = context.active_object.anim_ret

        for index, bone in enumerate(items):
            excluded = False
            found=False

            anim_ret_bone = bone.anim_ret_bone

            if not anim_ret_bone:
                excluded = True
            if not excluded and anim_ret_bone.source_bone_name == '':
                excluded = True
            if bone.name.startswith(ObjectAnimRet.prefix):
                excluded = True
            if not excluded and not anim_ret.show_def and 'DEF-' in bone.name:
                excluded = True
            if not excluded and not anim_ret.show_mch and 'MCH-' in bone.name:
                excluded = True
            if not excluded and not anim_ret.show_org and 'ORG-' in bone.name:
                excluded = True
            if not excluded and not anim_ret.show_fk and 'fk' in bone.name.lower():
                excluded = True
            if not excluded and not anim_ret.show_ik and 'ik' in bone.name.lower():
                excluded = True
            if not excluded and anim_ret.filter_layers:
                data_bone = d.bones[bone.name]
                for layer_id, layer in enumerate(d.layers):
                    if layer:
                        if data_bone.layers[layer_id]:
                            found=True
                            break

            if excluded or not found:
                filtered[index] &= ~self.bitflag_filter_item


        ordered = []

        # Reorder by name or average weight.
        if self.use_filter_sort_alpha:
            sort = [(idx, getattr(it, 'name', "")) for idx, it in enumerate(items)]

            ordered = helper_funcs.sort_items_helper(sort, lambda e: e[1].lower())

        return filtered, ordered

    def draw_item(self, _context, layout, _data, item, icon, _active_data_, _active_propname, _index):
        # assert(isinstance(item, bpy.types.VertexGroup))
        bone = item
        anim_ret_bone = bone.anim_ret_bone
        anim_ret_constraints = bone.anim_ret_constraints

        has_source = anim_ret_bone is not None and anim_ret_bone.source_bone_name != ''

        if self.layout_type in {'DEFAULT', 'COMPACT'}:

            layout.prop(bone, "name", text="", emboss=False, icon_value=icon)

            icon = Constants.ICON_ON if has_source else Constants.ICON_OFF
            layout.label(text="", icon=icon)

            constraint_hits = set()

            use_offset_bone = False

            for con in anim_ret_constraints:
                constraint_hits.add(con.constraint_type)
                use_offset_bone = con.use_offset_bone or use_offset_bone

            layout.label(text=str(anim_ret_bone.influence))
            layout.label(text="", icon= Constants.ICON_HIDE_OFF if anim_ret_bone.hide_off else Constants.ICON_HIDE_ON)
            layout.label(text="", icon= Constants.ICON_USE_MIRROR if anim_ret_bone.use_mirror else Constants.ICON_OFF)
            layout.label(text="", icon= Constants.ICON_USE_OFFSET_BONE if use_offset_bone else Constants.ICON_OFF)

            for key in constraint_hits:
                if key == '':
                    value = 'X'
                else:
                    value = Constants.CONSTRAINT_ICONS[key]
                layout.label(text="", icon= value)

        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

            import bpy

class OBJECT_PT_ObjectPanel(bpy.types.Panel, PT_, UI.PROPERTIES.WINDOW.DATA):
    bl_label = 'Animation Retargeting'
    bl_icon = cspy.icons.PLUGIN

    @classmethod
    def do_poll(cls, context):
        return DOIF.ACTIVE.HAS.BONES(context)

    def do_draw(self, context, scene, layout, obj):

        target_pose = obj.pose
        target_pbones = target_pose.bones

        anim_ret = obj.anim_ret

        col = layout.column(align=True)

        row = col.row(align=True)
        row.enabled = not anim_ret.is_frozen
        row.label(text='Cache')
        row.operator(AR_Update_Cache.bl_idname)
        row.separator()
        row.operator(AR_Restore_Cache.bl_idname)
        row.separator()
        row.operator(AR_Clear_Cache.bl_idname)
        row.operator(AR_Debug_Cache.bl_idname)
        row = col.row(align=True)
        row.label(text=AR_OPS_.get_cache_status(context))

        col.separator()

        row = col.row(align=True)
        row.enabled = not anim_ret.is_frozen
        row.prop(anim_ret, 'source')
        row.operator(AR_Synchronize_Bones.bl_idname, text='', icon=Constants.ICON_SYNC)

        row = row.split(align=True)
        row.enabled = True
        row.prop(anim_ret, 'is_frozen', text='', toggle=True, icon=Constants.ICON_FREEZE)

        source_obj = anim_ret.source

        if not source_obj or not source_obj.type == 'ARMATURE':
            return

        row = col.row(align=True)
        row.enabled = not anim_ret.is_frozen

        old_index = anim_ret.active_index

        row.template_list("OBJECT_UL_targetbones", "", target_pose, "bones", anim_ret, "active_index", rows=3)

        for bone in target_pbones:
            if bone.anim_ret_bone.bone_name != bone.name:
                bone.anim_ret_bone.bone_name = bone.name

            for cd in bone.anim_ret_constraints:
                cd.bone_name = bone.name

            for con in bone.constraints:
                if con.name.startswith(ObjectAnimRet.prefix):
                    if (con.target is not None and
                        con.subtarget is not None and
                        con.subtarget != ''
                        and con.subtarget not in con.target.data.bones
                    ):
                        con.subtarget = ''

        active_bone_name = anim_ret.get_active_bone_name(context)
        has_active_bone = active_bone_name != '' and active_bone_name in obj.data.bones

        row = col.row(align=True)
        col.enabled = not anim_ret.is_frozen

        if has_active_bone:
            active_pbone = target_pbones[active_bone_name]
            anim_ret_bone = active_pbone.anim_ret_bone
            BONE_PT_PoseBonePanel.draw_buttons(col, source_obj, active_pbone)
        else:
            print('skipping draw')

class BONE_PT_PoseBonePanel(bpy.types.Panel, PT_, UI.PROPERTIES.WINDOW.BONE):
    bl_label = 'Animation Retargeting'
    bl_icon = cspy.icons.ANIM_DATA

    @classmethod
    def do_poll(cls, context):
        return DOIF.ACTIVE.HAS.BONES(context) and DOIF.ACTIVE.HAS.ANIM_RET(context)        

    def do_draw(self, context, scene, layout, obj):
        layout.use_property_decorate = True
        anim_ret = obj.anim_ret
        layout.enabled = not anim_ret.is_frozen
        anim_ret_bone = get_active_pose_bone(context).anim_ret_bone
        source_obj = anim_ret.source

        row = layout.row()

        if not source_obj:
            row.label(text='Select the source object on the Object Properties panel', icon='INFO')
            return

        BONE_PT_PoseBonePanel.draw_buttons(layout, source_obj, get_active_pose_bone(context))

    @classmethod
    def draw_buttons(cls, layout, source_obj, pose_bone):

        anim_ret_bone = pose_bone.anim_ret_bone
        anim_ret_constraints = pose_bone.anim_ret_constraints

        row = layout.row()
        row.label(text=pose_bone.name)
        row.prop_search(anim_ret_bone, 'source_bone_name', source_obj.data, 'bones', text='')

        row = layout.row()

        row.operator(AR_Refresh_Constraints.bl_idname, text='', icon=Constants.ICON_REFRESH)
        row.prop(anim_ret_bone, 'use_mirror', text='', toggle=True, icon=Constants.ICON_USE_MIRROR)
        row.prop(anim_ret_bone, 'influence')

        row = layout.row()

        no_source = source_obj.pose.bones.get(anim_ret_bone.source_bone_name) is None

        row.label(text='Add a constraint:')

        for constraint in Constants.CONSTRAINTS:
            op = Constants.CONSTRAINT_OPS[constraint]
            icon = Constants.CONSTRAINT_ICONS[constraint]
            row.operator(op, text="", icon=icon)

        row = layout.row()

        def layout_state(layout, state):
            if state != 'ENABLED':
                layout = layout.split(align=True)

            layout.alert = (state == 'ALERT')
            layout.enabled = (state == 'ENABLED')

            return layout

        for cd in anim_ret_constraints:
            row = layout.row()
            state = 'ENABLED'
            if no_source:
                state = 'ALERT'

            if cd.constraint_type == '':
                icon = 'X'
            else:
                icon = Constants.CONSTRAINT_ICONS[cd.constraint_type]

            row.label(text=cd.name,icon=icon)
            icon = Constants.ICON_HIDE_OFF if cd.hide_off else Constants.ICON_HIDE_ON
            layout_state(row, state).prop(cd, 'hide_off', text='', toggle=True, icon=icon)
            row.prop_search(cd, 'source_bone_name', source_obj.pose, 'bones', text='')
            layout_state(row, state).prop(cd, 'use_offset_bone', text='', toggle=True, icon=Constants.ICON_USE_OFFSET_BONE)
            layout_state(row, state).prop(cd, 'influence', text='')
            layout_state(row, state).prop(cd, 'use_constraint', text='', toggle=True, icon='X')

def register():
    bpy.types.Object.anim_ret = bpy.props.PointerProperty(type=ObjectAnimRet)
    bpy.types.PoseBone.anim_ret_bone = bpy.props.PointerProperty(type=BoneAnimRet)
    bpy.types.PoseBone.anim_ret_constraints = bpy.props.CollectionProperty(type=ConstraintAnimRet)
    bpy.types.Object.anim_ret_bone_cache = bpy.props.CollectionProperty(type=BoneAnimRet)
    bpy.types.Object.anim_ret_constraints_cache = bpy.props.CollectionProperty(type=ConstraintAnimRet)

def unregister():
    del bpy.types.Object.anim_ret
    del bpy.types.PoseBone.anim_ret_bone
    del bpy.types.PoseBone.anim_ret_constraints
    del bpy.types.Object.anim_ret_bone_cache
    del bpy.types.Object.anim_ret_constraints_cache
