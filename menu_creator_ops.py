import bpy, cspy
from bpy.types import Operator
from cspy.ops import OPS_, OPS_DIALOG
from cspy.polling import POLL
from cspy.menu_creator import *


class MC_AddProperty(OPS_, Operator):
    """Add the property to the menu"""
    bl_idname = "object.add_property"
    bl_label = "Add property to Menu"

    @classmethod
    def do_poll(cls, context):
        return context.active_object is not None

    def do_execute(self, context):

        settings = bpy.context.scene.mc_settings
        if settings.em_fixobj:
            obj = settings.em_fixobj_pointer
        else:
            obj = context.active_object

        cspy.utils.dump(context, 'context')

        #if hasattr(context, 'button_pointer'):
        #    btn = context.button_pointer
        #    dump(btn, 'button_pointer')

        if hasattr(context, 'button_prop'):
            prop = context.button_prop
            cspy.utils.dump(prop, 'button_prop')

            try:
                bpy.ops.ui.copy_data_path_button(full_path=True)
            except:
                self.report({'WARNING'}, 'Menu Creator - Invalid selection.')
                return {'FINISHED'}

            base = context.window_manager.clipboard

            print(base)

            parts = cspy.utils.split_path(base)

            path = parts[len(parts)-1].strip('.')
            rna = base.replace(path, '').strip('.')

            name = prop.name

            if name in ['int','double','float','bool','string']:
                name = path.strip('[').strip(']').strip('\'').strip('\"')

            if obj.mc_enable:

                if mc_add_property_item(obj.mc_properties, [name,rna,path]):
                    self.report({'INFO'}, 'Menu Creator - Property added to the \'' + obj.name + '\' menu.')
                else:
                    self.report({'WARNING'}, 'Menu Creator - Property of \'' + obj.name + '\' was already added.')

            else:
                self.report({'ERROR'}, 'Menu Creator - Can not add property \'' + obj.name + '\'. No menu has been initialized.')

        #if hasattr(context, 'button_operator'):
        #    op = context.button_operator
        #    dump(op, 'button_operator')

        return {'FINISHED'}

class MC_AddCollection(OPS_, Operator):
    """Add the collection to the selected section"""
    bl_idname = "object.add_collection"
    bl_label = "Add collection to Menu"

    section: bpy.props.StringProperty()

    @classmethod
    def do_poll(cls, context):
        return context.active_object is not None

    def do_execute(self, context):

        settings = bpy.context.scene.mc_settings
        if settings.em_fixobj:
            obj = settings.em_fixobj_pointer
        else:
            obj = context.active_object

        add_coll = bpy.context.collection

        sec_index = mc_find_index_section(obj.mc_sections, self.section)

        i=True
        for el in obj.mc_sections[sec_index].collections:
            if el.collection == add_coll:
                i=False
                break
        if i:
            add_item = obj.mc_sections[sec_index].collections.add()
            add_item.collection = add_coll
            self.report({'INFO'}, 'Menu Creator - Collection has been added to section \''+self.section+'\'.')
        else:
            self.report({'WARNING'}, 'Menu Creator - Collection was already added to section \''+self.section+'\'.')

        return {'FINISHED'}

class WM_MT_button_context(bpy.types.Menu):
    bl_label = "Custom Action"

    def draw(self, context):
        pass

# Operator to clean all properties and sections from all objects
class MC_CleanAll(OPS_, Operator):
    """Clean all the menus.\nIf you choose reset, it will also delete all Menu options from all objects"""
    bl_idname = "ops.mc_cleanprop"
    bl_label = "Clean all the properties"

    reset : BoolProperty(default=False)

    def do_execute(self, context):

        mc_clean_properties()
        mc_clean_sections()

        if self.reset:
            for obj in bpy.data.objects:
                obj.mc_enable = False

        self.report({'INFO'}, 'Menu Creator - All the objects has been reset.')

        return {'FINISHED'}

# Operator to clean all properties and sections from an objects. If reset is on, it will also disable the menu for that object
class MC_CleanObject(OPS_, Operator):
    """Clean all the object properties.\nIf you choose reset, it will also delete all Menu options from the object"""
    bl_idname = "ops.mc_cleanpropobj"
    bl_label = "Clean the object"

    reset : BoolProperty(default=False)

    def do_execute(self, context):

        settings = bpy.context.scene.mc_settings
        if settings.em_fixobj:
            obj = settings.em_fixobj_pointer
        else:
            obj = context.active_object

        mc_clean_single_properties(obj)
        mc_clean_single_sections(obj)
        if self.reset:
            obj.mc_enable = False

        self.report({'INFO'}, 'Menu Creator - \'' + obj.name + '\' menu has been reset.')

        return {'FINISHED'}

# Operator to clean all properties and sections from an objects. If reset is on, it will also disable the menu for that object
class MC_ReplacePath(OPS_, Operator):
    """Replace the object property paths."""
    bl_idname = "ops.mc_replacepath"
    bl_label = "Replace the objects path"

    reset : BoolProperty(default=False)

    def do_execute(self, context):

        settings = bpy.context.scene.mc_settings
        if settings.em_fixobj:
            obj = settings.em_fixobj_pointer
        else:
            obj = context.active_object

        for property in obj.mc_properties:
            print(property.name)
            print(property.path)

            property.path = property.path.replace(
                settings.mss_path_replace_old, settings.mss_path_replace_new)

        self.report({'INFO'}, 'Menu Creator - \'' + obj.name + '\' path has been replaced.')

        return {'FINISHED'}

# Single Property settings
class MC_PropertySettings(OPS_, Operator):
    """Modify some of the property settings"""
    bl_idname = "ops.mc_propsettings"
    bl_label = "Property settings"
    bl_icon = "PREFERENCES"

    name : bpy.props.StringProperty(name='Name',
        description="Choose the name of the property")
    path : bpy.props.StringProperty()
    id : bpy.props.StringProperty()
    icon : bpy.props.EnumProperty(name='Icon',
        description="Choose the icon.\nNote that the icon name MUST respect Blender convention. All the icons can be found in the Icon Viewer default Blender addon.",items=mc_icon_list)
    section : bpy.props.EnumProperty(name='Section',
        description="Choose the icon.\nNote that the icon name MUST respect Blender convention. All the icons can be found in the Icon Viewer default Blender addon.",items=mc_section_list)

    def do_execute(self, context):

        settings = bpy.context.scene.mc_settings
        if settings.em_fixobj:
            obj = settings.em_fixobj_pointer
        else:
            obj = context.active_object

        i = mc_find_index(obj.mc_properties,[self.name,self.path,self.id])

        if i>=0:
            obj.mc_properties[i].name = self.name
            obj.mc_properties[i].icon = self.icon
            obj.mc_properties[i].section = self.section

        return {'FINISHED'}

    def invoke(self, context, event):

        settings = bpy.context.scene.mc_settings

        if settings.ms_debug:
            return context.window_manager.invoke_props_dialog(self, width=550)
        else:
            return context.window_manager.invoke_props_dialog(self)

    def do_draw(self, context, scene, layout, obj):

        settings = bpy.context.scene.mc_settings

        layout = self.layout

        layout.prop(self, "name")
        layout.prop(self, "icon")
        layout.prop(self, "section")

        layout.separator()
        layout.label(text="Property info", icon="INFO")
        box = layout.box()
        box.label(text="Identifier: "+self.id)

        if settings.ms_debug:
            layout.label(text="Full path", icon="RNA")
            box = layout.box()
            box.label(text=self.path+'.'+self.id)

# Swap Properties Operator
class MC_SwapProperty(OPS_, Operator):
    """Change the position of the property"""
    bl_idname = "ops.mc_swapprops"
    bl_label = "Change the property position"

    mod : BoolProperty(default=False) # False = down, True = Up

    name : bpy.props.StringProperty()
    path : bpy.props.StringProperty()
    id : bpy.props.StringProperty()

    def do_execute(self, context):

        settings = bpy.context.scene.mc_settings
        if settings.em_fixobj:
            obj = settings.em_fixobj_pointer
        else:
            obj = context.active_object
        col = obj.mc_properties
        col_len = mc_len_collection(col)

        i = mc_find_index(col,[self.name,self.path,self.id])

        item1 = [col[i].name,col[i].path,col[i].id,col[i].icon,col[i].section,col[i].hide]

        if i>=0:
            if self.mod:

                j=i
                while j>0:
                    j = j - 1
                    if col[j].section==col[i].section:
                        break
                if j>-1:

                    item2 = [col[j].name,col[j].path,col[j].id,col[j].icon,col[j].section,col[j].hide]

                    col[j].name = item1[0]
                    col[j].path = item1[1]
                    col[j].id = item1[2]
                    col[j].icon = item1[3]
                    col[j].section = item1[4]
                    col[j].hide = item1[5]
                    col[i].name = item2[0]
                    col[i].path = item2[1]
                    col[i].id = item2[2]
                    col[i].icon = item2[3]
                    col[i].section = item2[4]
                    col[i].hide = item2[5]

            else:

                j=i
                while j<col_len-1:
                    j=j+1
                    if col[j].section==col[i].section:
                        break
                if j<col_len:

                    item2 = [col[j].name,col[j].path,col[j].id,col[j].icon,col[j].section,col[j].hide]

                    col[j].name = item1[0]
                    col[j].path = item1[1]
                    col[j].id = item1[2]
                    col[j].icon = item1[3]
                    col[j].section = item1[4]
                    col[j].hide = item1[5]
                    col[i].name = item2[0]
                    col[i].path = item2[1]
                    col[i].id = item2[2]
                    col[i].icon = item2[3]
                    col[i].section = item2[4]
                    col[i].hide = item2[5]

        return {'FINISHED'}

# Operator to remove a property (button in UI)
class MC_RemoveProperty(OPS_, Operator):
    """Remove the property from the current menu"""
    bl_idname = "ops.mc_removeproperty"
    bl_label = "Remove the property"

    path : bpy.props.StringProperty()
    id : bpy.props.StringProperty()

    @classmethod
    def do_poll(cls, context):
        return context.active_object is not None

    def do_execute(self, context):

        settings = bpy.context.scene.mc_settings
        if settings.em_fixobj:
            obj = settings.em_fixobj_pointer
        else:
            obj = context.active_object
        props = obj.mc_properties

        mc_remove_property_item(obj.mc_properties,['',self.path,self.id])

        return {'FINISHED'}

# Operator to add a new section
class MC_AddSection(OPS_, Operator):
    """Add a new section to the section list."""
    bl_idname = "ops.mc_addsection"
    bl_label = "Add section"
    bl_icon = "PREFERENCES"

    name : bpy.props.StringProperty(name='Name',
        description="Choose the name of the section")
    icon : bpy.props.EnumProperty(name='Icon',
        description="Choose the icon.\nNote that the icon name MUST respect Blender convention. All the icons can be found in the Icon Viewer default Blender addon",items=mc_icon_list)
    type : bpy.props.EnumProperty(name='Type',
        description="Choose the section type",items=mc_section_type_list)

    def do_execute(self, context):

        settings = bpy.context.scene.mc_settings

        if settings.em_fixobj:
            obj = settings.em_fixobj_pointer
        else:
            obj = context.active_object
        sec_obj = obj.mc_sections
        sec_len = mc_len_collection(sec_obj)

        if self.name!="":

            i=True
            j=-1
            for el in sec_obj:
                j=j+1
                if el.name == self.name:
                    i=False
                    break
            if i:
                add_item = sec_obj.add()
                add_item.name = self.name
                add_item.type = self.type
                add_item.icon = self.icon
                add_item.id = sec_len

                self.report({'INFO'}, 'Menu Creator - Section \'' + self.name +'\' created.')
            else:
                self.report({'WARNING'}, 'Menu Creator - Cannot create a section with same name.')

        else:
            self.report({'ERROR'}, 'Menu Creator - Cannot create a section with this name.')

        return {'FINISHED'}

    def invoke(self, context, event):

        settings = bpy.context.scene.mc_settings

        if settings.ms_debug:
            return context.window_manager.invoke_props_dialog(self, width=550)
        else:
            return context.window_manager.invoke_props_dialog(self)

    def do_draw(self, context, scene, layout, obj):

        settings = bpy.context.scene.mc_settings

        layout = self.layout

        layout.prop(self, "name")
        layout.prop(self, "icon")
        layout.prop(self, "type")

# Section Property settings
class MC_SectionSettings(OPS_, Operator):
    """Modify the section settings."""
    bl_idname = "ops.mc_sectionsettings"
    bl_label = "Section settings"
    bl_icon = "PREFERENCES"

    name : bpy.props.StringProperty(name='Name',
        description="Choose the name of the section")
    icon : bpy.props.EnumProperty(name='Icon',
        description="Choose the icon.\nNote that the icon name MUST respect Blender convention. All the icons can be found in the Icon Viewer default Blender addon.",items=mc_icon_list)
    type : bpy.props.EnumProperty(name='Type',
        description="The Section type can not be changed after creation",items=mc_section_type_list)

    # COLLECTION type settings
    collections_enable_global_smoothcorrection : bpy.props.BoolProperty(name="Enable Global Smooth Correction")
    collections_enable_global_shrinkwrap : bpy.props.BoolProperty(name="Enable Global Shrinkwrap")
    collections_enable_global_mask : bpy.props.BoolProperty(name="Enable Global Mask")
    collections_enable_global_normalautosmooth : bpy.props.BoolProperty(name="Enable Global Normal Auto Smooth")
    # Outfit variant
    outfit_enable : bpy.props.BoolProperty(name="Outfit", description="With this option a Body entry will be added to the Section. This Body's masks will be enabled when elements of the collections are shown, and viceversa, if the masks are called the same name as the element of the collection")

    name_edit : bpy.props.StringProperty(name='Name',
        description="Choose the name of the section")
    ID : bpy.props.IntProperty()

    def do_execute(self, context):

        settings = bpy.context.scene.mc_settings

        if settings.em_fixobj:
            obj = settings.em_fixobj_pointer
        else:
            obj = context.active_object
        prop_obj = obj.mc_properties
        sec_obj = obj.mc_sections


        i = mc_find_index_section(sec_obj,[self.name,self.icon])

        if i>=0:

            for el in prop_obj:
                if el.section == self.name:
                    el.section = self.name_edit

            sec_obj[i].name = self.name_edit
            sec_obj[i].icon = self.icon
            sec_obj[i].collections_enable_global_smoothcorrection = self.collections_enable_global_smoothcorrection
            sec_obj[i].collections_enable_global_shrinkwrap = self.collections_enable_global_shrinkwrap
            sec_obj[i].collections_enable_global_mask = self.collections_enable_global_mask
            sec_obj[i].collections_enable_global_normalautosmooth = self.collections_enable_global_normalautosmooth
            sec_obj[i].outfit_enable = self.outfit_enable
            if obj.type == "MESH":
                sec_obj[i].outfit_body = obj

        return {'FINISHED'}

    def invoke(self, context, event):

        settings = bpy.context.scene.mc_settings

        if settings.em_fixobj:
            obj = settings.em_fixobj_pointer
        else:
            obj = context.active_object
        sec_obj = obj.mc_sections

        self.name_edit = self.name
        self.ID = mc_find_index_section(sec_obj,[self.name,self.icon])
        self.collections_enable_global_smoothcorrection = sec_obj[self.ID].collections_enable_global_smoothcorrection
        self.collections_enable_global_shrinkwrap = sec_obj[self.ID].collections_enable_global_shrinkwrap
        self.collections_enable_global_mask = sec_obj[self.ID].collections_enable_global_mask
        self.collections_enable_global_normalautosmooth = sec_obj[self.ID].collections_enable_global_normalautosmooth
        self.outfit_enable = sec_obj[self.ID].outfit_enable

        return context.window_manager.invoke_props_dialog(self)

    def do_draw(self, context, scene, layout, obj):

        settings = bpy.context.scene.mc_settings

        if settings.em_fixobj:
            obj = settings.em_fixobj_pointer
        else:
            obj = context.active_object
        sec_obj = obj.mc_sections

        layout = self.layout

        layout.prop(self, "name_edit")
        layout.prop(self, "icon")
        layout.separator()
        col = layout.column()
        col.enabled = False
        col.prop(self, "type")
        if self.type == "COLLECTION":
            layout.separator()
            row = layout.row()
            row.label(text="")
            row.scale_x = 3
            row.prop(self,"collections_enable_global_smoothcorrection")
            row = layout.row()
            row.label(text="")
            row.scale_x = 3
            row.prop(self,"collections_enable_global_shrinkwrap")
            row = layout.row()
            row.label(text="")
            row.scale_x = 3
            row.prop(self,"collections_enable_global_mask")
            row = layout.row()
            row.label(text="")
            row.scale_x = 3
            row.prop(self,"collections_enable_global_normalautosmooth")
            layout.separator()
            row = layout.row()
            row.label(text="")
            row.scale_x = 3
            row.prop(self,"outfit_enable")

# Operator to change Section position
class MC_SwapSection(OPS_, Operator):
    """Change the position of the section"""
    bl_idname = "ops.mc_swapsections"
    bl_label = "Change the section position"

    mod : BoolProperty(default=False) # False = down, True = Up

    name : bpy.props.StringProperty()
    icon : bpy.props.StringProperty()

    def do_execute(self, context):

        settings = bpy.context.scene.mc_settings
        if settings.em_fixobj:
            obj = settings.em_fixobj_pointer
        else:
            obj = context.active_object
        col = obj.mc_sections
        col_len = mc_len_collection(col)

        sec_index = mc_find_index_section(col,[self.name,self.icon])
        i = col[sec_index].id

        #item1 = [col[i].name,col[i].icon,col[i].type,col[i].collections]

        if self.mod and i > 0:
            j = mc_find_index_section_fromID(col, i-1)
            col[sec_index].id = i-1
            col[j].id = i
        elif not self.mod and i < col_len-1:
            j = mc_find_index_section_fromID(col, i+1)
            col[sec_index].id = i+1
            col[j].id = i

        #if self.mod and i > 0:
        #    j = i - 1
        #elif not self.mod and i < col_len-1:
        #    j = i + 1

            #item2 = [col[j].name,col[j].icon,col[j].type,col[j].collections]

            #col[j].name = item1[0]
            #col[j].icon = item1[1]
            #col[j].type = item1[2]
            #col[j].collections = item1[3]
            #col[i].name = item2[0]
            #col[i].icon = item2[1]
            #col[i].type = item2[2]
            #col[i].collections = item2[3]

        return {'FINISHED'}

# Delete Section
class MC_DeleteSection(OPS_, Operator):
    """Delete Section"""
    bl_idname = "ops.mc_deletesection"
    bl_label = "Section settings"

    name : bpy.props.StringProperty(name='Name',
        description="Choose the name of the section")

    def do_execute(self, context):

        settings = bpy.context.scene.mc_settings
        if settings.em_fixobj:
            obj = settings.em_fixobj_pointer
        else:
            obj = context.active_object
        sec_obj = obj.mc_sections

        i=-1
        for el in sec_obj:
            i=i+1
            if el.name == self.name:
                break

        if i>=0:

            j = sec_obj[i].id

            for k in range(j+1,len(sec_obj)):
                print(k)
                sec_obj[mc_find_index_section_fromID(sec_obj, k)].id = k-1

            sec_obj.remove(i)

        self.report({'INFO'}, 'Menu Creator - Section \'' + self.name +'\' deleted.')

        return {'FINISHED'}

# Operator to shiwtch visibility of an object
class MC_CollectionObjectVisibility(OPS_, Operator):
    """Chenge the visibility of the selected object"""
    bl_idname = "ops.mc_colobjvisibility"
    bl_label = "Hide/Unhide Object visibility"

    obj : bpy.props.StringProperty()
    sec : bpy.props.StringProperty()

    def do_execute(self, context):

        bpy.data.objects[self.obj].hide_viewport = not bpy.data.objects[self.obj].hide_viewport
        bpy.data.objects[self.obj].hide_render = not bpy.data.objects[self.obj].hide_render

        settings = bpy.context.scene.mc_settings
        if settings.em_fixobj:
            body_obj = settings.em_fixobj_pointer
        else:
            body_obj = context.active_object
        sec_obj = body_obj.mc_sections
        i = mc_find_index_section(sec_obj,[self.sec,''])

        if sec_obj[i].outfit_enable:
            for modifier in sec_obj[i].outfit_body.modifiers:
                if modifier.type == "MASK" and self.obj in modifier.name and sec_obj[i].collections_global_mask:
                    modifier.show_viewport = not bpy.data.objects[self.obj].hide_viewport
                    modifier.show_render = not bpy.data.objects[self.obj].hide_viewport

        return {'FINISHED'}

# Initial Configuration Operator
class MC_InitialConfiguration(OPS_, Operator):
    """Clean all the object properties"""
    bl_idname = "ops.mc_initialconfig"
    bl_label = "Clean all the properties"

    def do_execute(self, context):
        settings = bpy.context.scene.mc_settings
        if settings.em_fixobj:
            obj = settings.em_fixobj_pointer
        else:
            obj = context.active_object

        mc_clean_single_sections(obj)
        mc_clean_single_properties(obj)

        add_item = obj.mc_sections.add()
        add_item.id = 0
        add_item.name = "Unsorted"
        add_item.icon = "LIBRARY_DATA_BROKEN"

        obj.mc_enable = True

        self.report({'INFO'}, 'Menu Creator - Menu for \''+obj.name+'\' successfully created.')

        return {'FINISHED'}
