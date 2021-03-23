import bpy
import addon_utils
import sys
import os
import re
import time
import math
import cspy
from cspy.ops import OPS_, OPS_DIALOG
from cspy.ui import PT_OPTIONS, PT_, UI
from bpy.types import Header, Menu, Panel
from bpy.props import *
from mathutils import Vector, Color
import webbrowser
from . import utils

# CLASSES

# Arrays for ENUM properties
# Array to store different section type
mc_section_type_list = [
                ("DEFAULT","Default","A simple collection of properties that can be added right clicking on fields -> Add Property to the Menu"),
                ("COLLECTION","Collection List","Right clicking on them in the Outliner, you can add collections whose elements can be shown/hidden in the Menu. Only one collection will be shown at the same time.\nIdeal for: Outfit lists","OUTLINER_COLLECTION",1)
            ]
# Array to store possible icons to be used by properties and sections
mc_icon_list = [
                ("NONE","No Icon","No Icon"),
                ("USER", "Face", "Face","USER",1),
                ("HAIR", "Hair", "Hair","HAIR",2),
                ("MOD_CLOTH", "Cloth", "Cloth","MOD_CLOTH",3),
                ("MATERIAL", "Material", "Material","MATERIAL",4),
                ("ARMATURE_DATA", "Armature", "Armature","ARMATURE_DATA",5),
                ("MOD_ARMATURE", "Armature", "Armature","MOD_ARMATURE",6),
                ("EXPERIMENTAL", "Experimental", "Experimental","EXPERIMENTAL",7),
                ("WORLD", "World", "World","WORLD",8),
                ("PARTICLEMODE", "Comb", "Comb","PARTICLEMODE",9)
            ]

# Update functions for settings
# Function to avoid edit mode and fixed object while exiting edit mode
def mc_ms_editmode_update(self, context):
    
    if not self.ms_editmode:
        for obj in bpy.data.objects:
            obj.mc_edit_enable = False
    
    # context.scene.mc_settings.em_fixobj = False
    
    return

# Function to save the fixed object pointer to be used until the object is released
def mc_em_fixobj_update(self, context):
    
    if self.em_fixobj:
        self.em_fixobj_pointer = context.active_object
    
    return

# Class with all the settings variables
class MC_Settings(bpy.types.PropertyGroup):
    
    # Main Settings definitions
    ms_editmode: bpy.props.BoolProperty(name="Enable Edit Mode Tools",
                                        description="Unlock tools to customize the menu.\nDisable when the Menu is complete",
                                        default=False,
                                        update = mc_ms_editmode_update)
    ms_advanced: bpy.props.BoolProperty(name="Advanced Options",
                                        description="Unlock advanced options",
                                        default=False)
    ms_debug: bpy.props.BoolProperty(name="Debug mode",
                                        description="Unlock debug mode.\nMore messaged will be generated in the console.\nEnable it only if you encounter problems, as it might degrade general Blender performance",
                                        default=False)
    
    # Menu Specific properties
    mss_name: bpy.props.StringProperty(name="Name",
                                        description="Name of the menu.\nChoose the name of the menu to be shown before the properties",
                                        default="Object: ")
    mss_obj_name: bpy.props.BoolProperty(name="Show the Object Name",
                                        description="Show the Object name after the Name.\nFor instance, if the Name is \"Object: \", the shown name will be \"Object: name_of_object\"",
                                        default=True)

    mss_path_replace_old: bpy.props.StringProperty(name="Replace Old",
                                        description="Replace...",
                                        default='')
    mss_path_replace_new: bpy.props.StringProperty(name="Replace New",
                                        description="Replace with...",
                                        default='')
        
    # Edit mode properties
    em_fixobj: bpy.props.BoolProperty(name="Pin Object",
                                        description="Pin the Object you are using to edit the menu.\nThe object you pin will be considered as the target of all properties addition, and only this Object menu will be shown",
                                        default=False,
                                        update = mc_em_fixobj_update)
    em_fixobj_pointer : bpy.props.PointerProperty(type=bpy.types.Object)

# Class to store collections for section informations
class MCCollectionItem(bpy.types.PropertyGroup):
    collection : bpy.props.PointerProperty(name="Collection",type=bpy.types.Collection)

# Function to create an array of tuples for enum collections
def mc_collections_list(self, context):
    
    items = []
    
    i = 0
    for el in self.collections:
        items.append( (el.collection.name,el.collection.name,el.collection.name) )
        i = i + 1
        
    return items

# Function to update global collection properties
def mc_collections_list_update(self, context):
    
    for collection in self.collections:
        if collection.collection.name == self.collections_list:
            collection.collection.hide_viewport = False
            collection.collection.hide_render = False
        else:
            collection.collection.hide_viewport = True
            collection.collection.hide_render = True

def mc_collections_global_options_update(self, context):
    
    items = []
    
    i = 0
    for el in self.collections:
        for obj in el.collection.objects:
            
            if obj.type == "MESH":
                obj.data.use_auto_smooth = self.collections_global_normalautosmooth
            
            for modifier in obj.modifiers:
                if modifier.type == "CORRECTIVE_SMOOTH":
                    modifier.show_viewport = self.collections_global_smoothcorrection
                    modifier.show_render = self.collections_global_smoothcorrection
                elif modifier.type == "MASK":
                    modifier.show_viewport = self.collections_global_mask
                    modifier.show_render = self.collections_global_mask
                elif modifier.type == "SHRINKWRAP":
                    modifier.show_viewport = self.collections_global_shrinkwrap
                    modifier.show_render = self.collections_global_shrinkwrap
    
    if self.outfit_enable:
        for modifier in self.outfit_body.modifiers:
            if modifier.type == "MASK":
                if not self.collections_global_mask:
                    modifier.show_viewport = False
                    modifier.show_render = False
                else:
                    for el in self.collections:
                        for obj in el.collection.objects:
                            if obj.name in modifier.name and not obj.hide_viewport:
                                modifier.show_viewport = True
                                modifier.show_render = True
        
    return

# Poll function for the selection of mesh only in pointer properties
def mc_poll_mesh(self, object):
        return object.type == 'MESH'

# Class to store section informations
class MCSectionItem(bpy.types.PropertyGroup):
    # Global section options
    id : bpy.props.IntProperty(name="Section ID")
    name : bpy.props.StringProperty(name="Section Name")
    icon : bpy.props.StringProperty(name="Section Icon", default="")
    type : bpy.props.StringProperty(name="Section Type", default="DEFAULT")
    
    # COLLECTION type options
    collections_enable_global_smoothcorrection: bpy.props.BoolProperty(default=False)
    collections_enable_global_shrinkwrap: bpy.props.BoolProperty(default=False)
    collections_enable_global_mask: bpy.props.BoolProperty(default=False)
    collections_enable_global_normalautosmooth: bpy.props.BoolProperty(default=False)
    # COLLECTION type data
    collections: bpy.props.CollectionProperty(name="Section Collection List", type=MCCollectionItem)
    collections_list: bpy.props.EnumProperty(name="Section Collection List", items = mc_collections_list, update=mc_collections_list_update)
    collections_global_smoothcorrection: bpy.props.BoolProperty(name="Smooth Correction", default=True, update=mc_collections_global_options_update)
    collections_global_shrinkwrap: bpy.props.BoolProperty(name="Shrinkwrap", default=True, update=mc_collections_global_options_update)
    collections_global_mask: bpy.props.BoolProperty(name="Mask", default=True, update=mc_collections_global_options_update)
    collections_global_normalautosmooth: bpy.props.BoolProperty(name="Normals Auto Smooth", default=True, update=mc_collections_global_options_update)
    # Outfit variant
    outfit_enable : bpy.props.BoolProperty(name="Outfit", default=False)
    outfit_body : bpy.props.PointerProperty(name="Outfit Body", description = "The masks of this object will be switched on/off depending on which elements of the collections visibility", type=bpy.types.Object, poll=mc_poll_mesh)


# Class to store properties informations
class MCPropertyItem(bpy.types.PropertyGroup):
    name : bpy.props.StringProperty(name="Property Name")
    path: bpy.props.StringProperty(name="Property Path")
    id : bpy.props.StringProperty(name="Property Identifier")
    icon : bpy.props.EnumProperty(name="Property Icon", default="NONE",items=mc_icon_list)
    section : bpy.props.StringProperty(name="Section", default="Unsorted")
    hide : bpy.props.BoolProperty(name="Hide Property", default=False)


# COLLECTION MANAGEMENT FUNCTIONS

# ---- Properties only functions

# Function to remove a specific property from the collection
# Return 1 if the property was found and deleted
def mc_remove_property_item(collection, item):
    i=-1
    for el in collection:
        i=i+1
        if el.path == item[1] and el.id == item[2]:
            break
    if i>=0:
        collection.remove(i)
    
    return i>=0

# Function to add a specific property to the collection, if not already there
# Return 0 if the property has not been added because already in the properties list
def mc_add_property_item(collection, item):
    i=True
    for el in collection:
        if el.path == item[1] and el.id == item[2]:
            i=False
            break
    if i:
        add_item = collection.add()
        add_item.name = item[0]
        add_item.path = item[1]
        add_item.id = item[2]
    
    return i

# Function to find the index of a property
def mc_find_index(collection, item):
    i=-1
    for el in collection:
        i=i+1
        if el.path == item[1] and el.id == item[2]:
            break
    return i

# Function to clean properties of a single object
def mc_clean_single_properties(obj):
    obj.mc_properties.clear()

# Function to clean all the properties of every object
def mc_clean_properties():
    for obj in bpy.data.objects:
        obj.mc_properties.clear()

# Function to print the properties
def mc_print_properties():
    for obj in bpy.data.objects:
        for el in obj.mc_properties:
            print(el.id + " : property" + el.name + " with path "+el.path)

# ---- Sections only functions

# Function to create an array of tuples for enum properties
def mc_section_list(scene, context):
    
    settings = bpy.context.scene.mc_settings
    if settings.em_fixobj:
        obj = settings.em_fixobj_pointer
    else:
        obj = context.active_object
    
    items = []
    
    i = 0
    for el in obj.mc_sections:
        if el.type == "DEFAULT":
            items.append( (el.name,el.name,el.name,el.icon,i) )
            i = i + 1
        
    return items

# Function to clean sections of a single object
def mc_clean_single_sections(obj):
    obj.mc_sections.clear()
    
# Function to clean the sections of every object
def mc_clean_sections():
    for obj in bpy.data.objects:
        obj.mc_sections.clear()

# Function to find the index of a section from the name
def mc_find_index_section(collection, item):
    i=-1
    for el in collection:
        i=i+1
        if el.name == item[0]:
            break
    return i

# Function to find the index of a section from the ID
def mc_find_index_section_fromID(collection, item):
    i=-1
    for el in collection:
        i=i+1
        if el.id == item:
            break
    return i

# Function to iutput the ID of the element
def mc_sec_ID(elem):
    return elem.id

# ---- Sections and properties functions

# Function to find the length of a collection
def mc_len_collection(collection):    
    i=0
    for el in collection:
        i=i+1
    return i

def menu_func(self, context):    
    if hasattr(context, 'button_prop'):
            layout = self.layout
            layout.separator()
            layout.operator(MC_AddProperty.bl_idname)

