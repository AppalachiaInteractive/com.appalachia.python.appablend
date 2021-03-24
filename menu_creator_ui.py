import bpy
import cspy
from cspy.ui import PT_OPTIONS, PT_, UI
from cspy.menu_creator import *
from cspy.menu_creator_ops import *


def mc_panel_poll(context):
    settings = bpy.context.scene.mc_settings
    if settings.em_fixobj:
        obj = settings.em_fixobj_pointer
    else:
        obj = context.active_object

    return getattr(obj, 'mc_enable', False)

def mc_collection_menu(self, context):
    self.layout.separator()
    self.layout.menu(OUTLINER_MT_Collection_Menu.bl_idname)

 # Collection for Collection List sections properties

class MC_MT_Collection_Menu(bpy.types.Menu):
    bl_idname = 'MC_MT_Collection_Menu'
    bl_label = 'Add Collection to Section'

    def draw(self, context):
        settings = bpy.context.scene.mc_settings
        if settings.em_fixobj:
            obj = settings.em_fixobj_pointer
        else:
            obj = context.active_object

        layout = self.layout

        no_col_sec = True
        for sec in obj.mc_sections:
            if sec.type == "COLLECTION":
                layout.operator(MC_AddCollection.bl_idname, text=sec.name).section = sec.name
                no_col_sec = False

        if no_col_sec:
            layout.label(text="No Collection List sections found")

class MC_PT_InitialConfiguration_Panel(bpy.types.Panel, PT_, UI.VIEW_3D.UI.Menu):
    bl_idname = "MC_PT_InitialConfiguration_Panel"
    bl_label = "Initial Configuration"

    @classmethod
    def do_poll(cls, context):
        return not mc_panel_poll(context)

    def do_draw(self, context, scene, layout, obj):
        layout.label(text="Menu Configuration")
        layout.operator('ops.mc_initialconfig', text="Create Menu")

class MC_PT_Panel(bpy.types.Panel, PT_, UI.VIEW_3D.UI.Menu):
    bl_idname = "MC_PT_Panel"
    bl_label = "Menu"

    @classmethod
    def do_poll(cls, context):
        return mc_panel_poll(context)

    def do_draw(self, context, scene, layout, obj):

        settings = bpy.context.scene.mc_settings
        if settings.em_fixobj:
            obj = settings.em_fixobj_pointer
        else:
            obj = context.active_object
        mc_col = obj.mc_properties
        mcs_col = obj.mc_sections
        mc_col_len = mc_len_collection(mc_col)
        mcs_col_len = mc_len_collection(mcs_col)

        layout = self.layout

        row = layout.row(align=False)
        menu_name = settings.mss_name
        if settings.mss_obj_name:
            menu_name = menu_name+obj.name
        row.label(text=menu_name)

        if settings.ms_editmode:
            row.prop(obj, "mc_edit_enable", text="",icon="MODIFIER")
            row.operator("ops.mc_addsection",text="",icon="ADD")
            if settings.em_fixobj:
                row.prop(settings,"em_fixobj",icon="PINNED", text="")
            else:
                row.prop(settings,"em_fixobj",icon="UNPINNED", text= "")
        else:
            if settings.em_fixobj:
                row.prop(settings,"em_fixobj",icon="PINNED", text="")
            else:
                row.prop(settings,"em_fixobj",icon="UNPINNED", text= "")

        if mc_col_len>0:

            for sec in sorted(mcs_col, key = mc_sec_ID):

                if sec.type == "DEFAULT":

                    sec_empty = True
                    sec_hidden = True
                    for el in mc_col:
                        if el.section == sec.name:
                            sec_empty = False
                            if not el.hide:
                                sec_hidden = False

                    if (sec_empty and sec.name == "Unsorted") or (not obj.mc_edit_enable and not sec_empty and sec_hidden):
                        continue
                    else:
                        row = layout.row(align=False)
                        if sec.icon == "NONE":
                            row.label(text=sec.name)
                        else:
                            row.label(text=sec.name,icon=sec.icon)

                        if obj.mc_edit_enable:

                            if sec.name != "Unsorted":
                                ssett_button = row.operator("ops.mc_sectionsettings", icon="PREFERENCES", text="")
                                ssett_button.name = sec.name
                                ssett_button.icon = sec.icon
                                ssett_button.type = sec.type

                            row2 = row.row(align=True)
                            sup_button = row2.operator("ops.mc_swapsections", icon="TRIA_UP", text="")
                            sup_button.mod = True
                            sup_button.name = sec.name
                            sup_button.icon = sec.icon
                            sdown_button = row2.operator("ops.mc_swapsections", icon="TRIA_DOWN", text="")
                            sdown_button.mod = False
                            sdown_button.name = sec.name
                            sdown_button.icon = sec.icon

                        box = layout.box()
                        if sec_empty and sec.name != "Unsorted":
                            row = box.row(align=False)
                            row.label(text="Section Empty", icon="ERROR")
                            row.operator("ops.mc_deletesection",text="",icon="X").name = sec.name

                    for el in mc_col:

                        if el.section == sec.name:

                            el_index = mc_find_index(mc_col,[el.name,el.path,el.id])

                            if obj.mc_edit_enable:

                                row = box.row(align=False)
                                if el.icon !="NONE":
                                    row.label(text=el.name,icon=el.icon)
                                else:
                                    row.label(text=el.name)

                                sett_button = row.operator("ops.mc_propsettings", icon="PREFERENCES", text="")
                                sett_button.name = el.name
                                sett_button.path = el.path
                                sett_button.id = el.id
                                sett_button.icon = el.icon
                                sett_button.section = el.section

                                row2 = row.row(align=True)
                                up_button = row2.operator("ops.mc_swapprops", icon="TRIA_UP", text="")
                                up_button.mod = True
                                up_button.name = el.name
                                up_button.path = el.path
                                up_button.id = el.id
                                down_button = row2.operator("ops.mc_swapprops", icon="TRIA_DOWN", text="")
                                down_button.mod = False
                                down_button.name = el.name
                                down_button.path = el.path
                                down_button.id = el.id

                                if el.hide:
                                    row.prop(el, "hide", text="", icon = "HIDE_ON")
                                else:
                                    row.prop(el, "hide", text="", icon = "HIDE_OFF")

                                del_button = row.operator("ops.mc_removeproperty", icon="X", text="")
                                del_button.path = el.path
                                del_button.id = el.id
                            else:

                                if not el.hide:
                                    row = box.row(align=False)
                                    if el.icon !="NONE":
                                        row.label(text=el.name,icon=el.icon)
                                    else:
                                        row.label(text=el.name)

                                    row.scale_x=1.0
                                    row.prop(eval(el.path), el.id, text="")

                elif sec.type == "COLLECTION":

                    sec_empty = True
                    for el in sec.collections:
                        sec_empty = False
                        break

                    row = layout.row(align=False)
                    if sec.icon == "NONE":
                        row.label(text=sec.name)
                    else:
                        row.label(text=sec.name,icon=sec.icon)

                    if obj.mc_edit_enable:

                        ssett_button = row.operator("ops.mc_sectionsettings", icon="PREFERENCES", text="")
                        ssett_button.name = sec.name
                        ssett_button.icon = sec.icon
                        ssett_button.type = sec.type

                        row2 = row.row(align=True)
                        sup_button = row2.operator("ops.mc_swapsections", icon="TRIA_UP", text="")
                        sup_button.mod = True
                        sup_button.name = sec.name
                        sup_button.icon = sec.icon
                        sdown_button = row2.operator("ops.mc_swapsections", icon="TRIA_DOWN", text="")
                        sdown_button.mod = False
                        sdown_button.name = sec.name
                        sdown_button.icon = sec.icon

                        if sec.outfit_enable:
                            box = layout.box()
                            box.prop(sec,"outfit_body", text="Body", icon="OUTLINER_OB_MESH")

                    box = layout.box()
                    if sec_empty:
                        row = box.row(align=False)
                        row.label(text="No Collection Assigned", icon="ERROR")
                        row.operator("ops.mc_deletesection",text="",icon="X").name = sec.name

                    #for collection in sec.collections:
                        #box.label(text=collection.collection.name)
                    if len(sec.collections)>0:
                        box.prop(sec,"collections_list", text="")
                        box2 = box.box()
                        if len(bpy.data.collections[sec.collections_list].objects)>0:
                            for obj2 in bpy.data.collections[sec.collections_list].objects:
                                row = box2.row()
                                #row.label(text=obj.name, icon='OUTLINER_OB_'+obj.type)
                                #row2 = row.row(align=True)
                                if obj2.hide_viewport:
                                    vop=row.operator("ops.mc_colobjvisibility",text=obj2.name, icon='OUTLINER_OB_'+obj2.type)
                                    vop.obj = obj2.name
                                    vop.sec = sec.name
                                else:
                                    vop = row.operator("ops.mc_colobjvisibility",text=obj2.name, icon='OUTLINER_OB_'+obj2.type, depress = True)
                                    vop.obj = obj2.name
                                    vop.sec = sec.name
                                #row2.prop(obj,'hide_viewport',text="", emboss = False)
                                #row2.prop(obj,'hide_render',text="", emboss = False)
                        else:
                            box2.label(text="This Collection seems empty", icon="ERROR")

                        if sec.collections_enable_global_smoothcorrection or sec.collections_enable_global_shrinkwrap or sec.collections_enable_global_mask or sec.collections_enable_global_normalautosmooth:
                            box.label(text= sec.name+" Global Properties", icon="MODIFIER")
                            box2 = box.box()
                            if sec.collections_enable_global_smoothcorrection:
                                box2.prop(sec,"collections_global_smoothcorrection")
                            if sec.collections_enable_global_shrinkwrap:
                                box2.prop(sec,"collections_global_shrinkwrap")
                            if sec.collections_enable_global_mask:
                                box2.prop(sec,"collections_global_mask")
                            if sec.collections_enable_global_normalautosmooth:
                                box2.prop(sec,"collections_global_normalautosmooth")

        else:
            box = layout.box()
            box.label(text="No property added yet.",icon="ERROR")

class MC_PT_Settings_Panel(bpy.types.Panel, PT_, UI.VIEW_3D.UI.Menu):
    bl_idname = "MC_PT_Settings_Panel"
    bl_label = "Settings"

    @classmethod
    def do_poll(cls, context):
        return mc_panel_poll(context)

    def do_draw(self, context, scene, layout, obj):

        settings = bpy.context.scene.mc_settings

        # Main Settings
        layout.label(text="Main Settings",icon="SETTINGS")
        box = layout.box()

        box.prop(settings,"ms_editmode")
        box.prop(settings,"ms_debug")
        box.prop(settings,"ms_advanced")

        # Menu specific settings
        layout.label(text="Menu Settings",icon="SETTINGS")
        box = layout.box()

        box.prop(settings,"mss_name")
        box.prop(settings,"mss_obj_name")

        layout.label(text="Reset functions",icon="SETTINGS")
        box = layout.box()

        box.prop(settings,"mss_path_replace_old")
        box.prop(settings,"mss_path_replace_new")
        box.operator('ops.mc_replacepath', text="Replace Path", icon="ERROR")

        #box.operator('ops.mc_cleanpropobj', text="Clean object")
        box.operator('ops.mc_cleanpropobj', text="Reset Object", icon="ERROR").reset = True
        #box.operator('ops.mc_cleanprop', text="Clean all objects")
        box.operator('ops.mc_cleanprop', text="Reset All Objects", icon="ERROR").reset = True

def menu_func(self, context):
    if hasattr(context, 'button_prop'):
            layout = self.layout
            layout.separator()
            layout.operator(MC_AddProperty.bl_idname)


def register():
    bpy.types.Object.mc_properties = bpy.props.CollectionProperty(type=MCPropertyItem)
    bpy.types.Object.mc_sections = bpy.props.CollectionProperty(type=MCSectionItem)
    bpy.types.Scene.mc_settings = bpy.props.PointerProperty(type=MC_Settings)
    bpy.types.Object.mc_enable = bpy.props.BoolProperty(name="", default=False)
    bpy.types.Object.mc_edit_enable = bpy.props.BoolProperty(name="Edit Mode", default=False, description="Enable edit mode in this menu.\nActivating this option you will have access to various tools to modify properties and sections")

    if hasattr(bpy.types, 'WM_MT_button_context'): bpy.types.WM_MT_button_context.append(menu_func)

def unregister():
    del bpy.types.Object.mc_properties
    del bpy.types.Object.mc_sections
    del bpy.types.Scene.mc_settings
    del bpy.types.Object.mc_enable
    del bpy.types.Object.mc_edit_enable

    if hasattr(bpy.types, 'WM_MT_button_context'): bpy.types.WM_MT_button_context.remove(menu_func)
    