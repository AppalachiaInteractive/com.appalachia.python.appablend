import bpy
import cspy
from cspy import icons, utils
import math

def get_rotation_euler(obj):
        if obj.rotation_mode == 'QUATERNION':
            rotation_euler = obj.rotation_quaternion.to_euler()
        else:
            rotation_euler = obj.rotation_euler
        return rotation_euler

def display_euler(layout, rotation_mode, euler):
    layout.label(text='Rotation Mode: {0}'.format(rotation_mode))

    text = 'Euler (Rads): [{0:.2f}, {1:.2f}, {2:.2f}]'.format(
        euler[0],
        euler[1],
        euler[2])
    layout.label(text=text)

    text = 'Euler (Deg): [{0:.2f}, {1:.2f}, {2:.2f}]'.format(
        math.degrees(euler[0]),
        math.degrees(euler[1]),
        math.degrees(euler[2]))
    layout.label(text=text)

def layout_euler(layout, obj):
    box = layout.box()
    rotation_euler = get_rotation_euler(obj)
    display_euler(box, obj.rotation_mode, rotation_euler)

class _PT_CONTEXT:
    ADDONS                  = 'addons'
    ANIMATION               = 'animation'
    BONE                    = 'bone'
    BONE_CONSTRAINT         = 'bone_constraint'
    COLLECTION              = 'collection'
    CONSTRAINT              = 'constraint'
    DATA                    = 'data'
    EDITING                 = 'editing'
    EXPERIMENTAL            = 'experimental'
    FILE_PATHS              = 'file_paths'
    INPUT                   = 'input'
    INTERFACE               = 'interface'
    KEYMAP                  = 'keymap'
    LIGHTS                  = 'lights'
    MATERIAL                = 'material'
    MODIFIER                = 'modifier'
    NAVIGATION              = 'navigation'
    OBJECT                  = 'object'
    OBJECTMODE              = 'objectmode'
    OUTPUT                  = 'output'
    PARTICLE                = 'particle'
    PHYSICS                 = 'physics'
    RENDER                  = 'render'
    SAVE_LOAD               = 'save_load'
    SCENE                   = 'scene'
    SHADERFX                = 'shaderfx'
    SYSTEM                  = 'system'
    TEXTURE                 = 'texture'
    THEMES                  = 'themes'
    VIEW_LAYER              = 'view_layer'
    VIEWPORT                = 'viewport'
    WORLD                   = 'world'

class _PT_CONTEXT_TOOLBAR:
    OBJECTMODE              = '.objectmode'
    ARMATURE_EDIT           = '.armature_edit'
    GREASEPENCIL_PAINT      = '.greasepencil_paint'
    GREASEPENCIL_SCULPT     = '.greasepencil_sculpt'
    GREASEPENCIL_VERTEX     = '.greasepencil_vertex'
    GREASEPENCIL_WEIGHT     = '.greasepencil_weight'
    IMAGEPAINT              = '.imagepaint'
    IMAGEPAINT_2D           = '.imagepaint_2d'
    MESH_EDIT               = '.mesh_edit'
    PAINT_COMMON            = '.paint_common'
    PAINT_COMMON_2D         = '.paint_common_2d'
    PARTICLEMODE            = '.particlemode'
    POSEMODE                = '.posemode'
    SCULPT_MODE             = '.sculpt_mode'
    UV_SCULPT               = '.uv_sculpt'
    VERTEXPAINT             = '.vertexpaint'
    WEIGHTPAINT             = '.weightpaint'

class _PT_SPACE_TYPE:
    VIEW_3D                 = 'VIEW_3D'
    IMAGE_EDITOR            = 'IMAGE_EDITOR'
    NODE_EDITOR             = 'NODE_EDITOR'
    SEQUENCE_EDITOR         = 'SEQUENCE_EDITOR'
    CLIP_EDITOR             = 'CLIP_EDITOR'
    DOPESHEET_EDITOR        = 'DOPESHEET_EDITOR'
    GRAPH_EDITOR            = 'GRAPH_EDITOR'
    NLA_EDITOR              = 'NLA_EDITOR'
    TEXT_EDITOR             = 'TEXT_EDITOR'
    CONSOLE                 = 'CONSOLE'
    INFO                    = 'INFO'
    TOPBAR                  = 'TOPBAR'
    STATUSBAR               = 'STATUSBAR'
    OUTLINER                = 'OUTLINER'
    PROPERTIES              = 'PROPERTIES'
    FILE_BROWSER            = 'FILE_BROWSER'
    PREFERENCES             = 'PREFERENCES'

class _PT_REGION_TYPE:
    '''The inspection window, usually for showing properties'''
    WINDOW                  = 'WINDOW'
    HEADER                  = 'HEADER'
    CHANNELS                = 'CHANNELS'
    TEMPORARY               = 'TEMPORARY'
    UI                      = 'UI'
    TOOLS                   = 'TOOLS'
    TOOL_PROPS              = 'TOOL_PROPS'
    PREVIEW                 = 'PREVIEW'
    HUD                     = 'HUD'
    NAVIGATION_BAR          = 'NAVIGATION_BAR'
    EXECUTE                 = 'EXECUTE'
    FOOTER                  = 'FOOTER'
    TOOL_HEADER             = 'TOOL_HEADER'

class _PT_CATEGORY:
    ANNOTATION              = 'Annotation'
    ATTRIBUTES              = 'Attributes'
    BOOKMARKS               = 'Bookmarks'
    CACHE                   = 'Cache'
    DRIVERS                 = 'Drivers'
    FILTER                  = 'Filter'
    FOOTAGE                 = 'Footage'
    IMAGE                   = 'Image'
    ITEM                    = 'Item'
    MASK                    = 'Mask'
    MODIFIERS               = 'Modifiers'
    OPTIONS                 = 'Options'
    PROXY                   = 'Proxy'
    SCOPES                  = 'Scopes'
    SOLVE                   = 'Solve'
    STABILIZATION           = 'Stabilization'
    STRIP                   = 'Strip'
    TEXT                    = 'Text'
    TOOL                    = 'Tool'
    TRACK                   = 'Track'
    VIEW                    = 'View'

class _PT_OPTION:
    DEFAULT_CLOSED          = 'DEFAULT_CLOSED'
    HIDE_HEADER             = 'HIDE_HEADER'
    INSTANCED               = 'INSTANCED'
    HEADER_LAYOUT_EXPAND    = 'HEADER_LAYOUT_EXPAND'
    DRAW_BOX                = 'DRAW_BOX'

class _PT_CONTEXT_PREFERENCES:
    ADDONS                  = 'addons'
    ANIMATION               = 'animation'
    EDITING                 = 'editing'
    EXPERIMENTAL            = 'experimental'
    FILE_PATHS              = 'file_paths'
    INPUT                   = 'input'
    INTERFACE               = 'interface'
    KEYMAP                  = 'keymap'
    LIGHTS                  = 'lights'
    NAVIGATION              = 'navigation'
    SAVE_LOAD               = 'save_load'
    SYSTEM                  = 'system'
    THEMES                  = 'themes'
    VIEWPORT                = 'viewport'

class _PT_CONTEXT_IMAGE_EDITOR_TOOLBAR:
    IMAGEPAINT_2D           = '.imagepaint_2d'
    PAINT_COMMON_2D         = '.paint_common_2d'
    UV_SCULPT               = '.uv_sculpt'

class _PT_CONTEXT_IMAGE_EDITOR:
    IMAGEPAINT_2D           = 'imagepaint_2d'
    PAINT_COMMON_2D         = 'paint_common_2d'
    UV_SCULPT               = 'uv_sculpt'

class _PT_CONTEXT_VIEW_3D:
    ALL                     = 'objectmode'
    OBJECTMODE              = 'objectmode'
    MESH_EDIT               = 'mesh_edit'
    ARMATURE_EDIT           = 'armature_edit'
    POSEMODE                = 'posemode'
    PARTICLEMODE            = 'particlemode'
    SCULPT_MODE             = 'sculpt_mode'
    VERTEXPAINT             = 'vertexpaint'
    WEIGHTPAINT             = 'weightpaint'
    IMAGEPAINT              = 'imagepaint'
    PAINT_COMMON            = 'paint_common'
    GREASEPENCIL_PAINT      = 'greasepencil_paint'
    GREASEPENCIL_SCULPT     = 'greasepencil_sculpt'
    GREASEPENCIL_VERTEX     = 'greasepencil_vertex'
    GREASEPENCIL_WEIGHT     = 'greasepencil_weight'

class _PT_CONTEXT_VIEW_3D_TOOLBAR:
    OBJECTMODE              = '.objectmode'
    MESH_EDIT               = '.mesh_edit'
    ARMATURE_EDIT           = '.armature_edit'
    POSEMODE                = '.posemode'
    PARTICLEMODE            = '.particlemode'
    SCULPT_MODE             = '.sculpt_mode'
    VERTEXPAINT             = '.vertexpaint'
    WEIGHTPAINT             = '.weightpaint'
    IMAGEPAINT              = '.imagepaint'
    PAINT_COMMON            = '.paint_common'
    GREASEPENCIL_PAINT      = '.greasepencil_paint'
    GREASEPENCIL_SCULPT     = '.greasepencil_sculpt'
    GREASEPENCIL_VERTEX     = '.greasepencil_vertex'
    GREASEPENCIL_WEIGHT     = '.greasepencil_weight'

class _PT_CONTEXT_PROPERTIES:
    COLLECTION              = 'collection'
    CONSTRAINT              = 'constraint'
    BONE_CONSTRAINT         = 'bone_constraint'
    DATA                    = 'data'
    BONE                    = 'bone'
    SHADERFX                = 'shaderfx'
    MATERIAL                = 'material'
    OBJECT                  = 'object'
    PARTICLE                = 'particle'
    PHYSICS                 = 'physics'
    SCENE                   = 'scene'
    TEXTURE                 = 'texture'
    RENDER                  = 'render'
    VIEW_LAYER              = 'view_layer'
    WORLD                   = 'world'
    MODIFIER                = 'modifier'

class PT_OPTIONS:
    DEFAULT_CLOSED          = {_PT_OPTION.DEFAULT_CLOSED}
    HIDE_HEADER             = {_PT_OPTION.HIDE_HEADER}

class UI:
    class VIEW_3D:
        bl_space_type=_PT_SPACE_TYPE.VIEW_3D
        class UI:
            bl_space_type=_PT_SPACE_TYPE.VIEW_3D
            bl_region_type=_PT_REGION_TYPE.UI
            class Tool:
                bl_space_type=_PT_SPACE_TYPE.VIEW_3D
                bl_region_type=_PT_REGION_TYPE.UI
                bl_category=_PT_CATEGORY.TOOL
            class View:
                bl_space_type=_PT_SPACE_TYPE.VIEW_3D
                bl_region_type=_PT_REGION_TYPE.UI
                bl_category=_PT_CATEGORY.VIEW
            class Item:
                bl_space_type=_PT_SPACE_TYPE.VIEW_3D
                bl_region_type=_PT_REGION_TYPE.UI
                bl_category=_PT_CATEGORY.ITEM
            class Menu:
                bl_space_type=_PT_SPACE_TYPE.VIEW_3D
                bl_region_type=_PT_REGION_TYPE.UI
                bl_category='Menu'
        class HEADER:
            bl_space_type=_PT_SPACE_TYPE.VIEW_3D
            bl_region_type=_PT_REGION_TYPE.HEADER
            class OVERLAY:
                bl_space_type=_PT_SPACE_TYPE.VIEW_3D
                bl_region_type=_PT_REGION_TYPE.HEADER
                bl_parent_id = 'VIEW3D_PT_overlay'
            class OVERLAY_EDIT_MESH:
                bl_space_type=_PT_SPACE_TYPE.VIEW_3D
                bl_region_type=_PT_REGION_TYPE.HEADER
                bl_parent_id = 'VIEW3D_PT_overlay_edit_mesh'
        class TOOLS:
            bl_space_type=_PT_SPACE_TYPE.VIEW_3D
            bl_region_type=_PT_REGION_TYPE.TOOLS
            class HIDE_HEADER:
                bl_space_type=_PT_SPACE_TYPE.VIEW_3D
                bl_region_type=_PT_REGION_TYPE.TOOLS
                bl_options = PT_OPTIONS.HIDE_HEADER
    class IMAGE_EDITOR:
        bl_space_type=_PT_SPACE_TYPE.IMAGE_EDITOR
        class TOOLS:
            bl_space_type=_PT_SPACE_TYPE.IMAGE_EDITOR
            bl_region_type = _PT_REGION_TYPE.TOOLS
            class Annotation:
                bl_space_type=_PT_SPACE_TYPE.IMAGE_EDITOR
                bl_region_type=_PT_REGION_TYPE.TOOLS
                bl_category = _PT_CATEGORY.ANNOTATION
        class UI:
            bl_space_type=_PT_SPACE_TYPE.IMAGE_EDITOR
            bl_region_type = _PT_REGION_TYPE.UI
            class Image:
                bl_space_type=_PT_SPACE_TYPE.IMAGE_EDITOR
                bl_region_type=_PT_REGION_TYPE.UI
                bl_category = _PT_CATEGORY.IMAGE
            class Mask:
                bl_space_type=_PT_SPACE_TYPE.IMAGE_EDITOR
                bl_region_type=_PT_REGION_TYPE.UI
                bl_category = _PT_CATEGORY.MASK
            class Tool:
                bl_space_type=_PT_SPACE_TYPE.IMAGE_EDITOR
                bl_region_type=_PT_REGION_TYPE.UI
                bl_category = _PT_CATEGORY.TOOL
            class View:
                bl_space_type=_PT_SPACE_TYPE.IMAGE_EDITOR
                bl_region_type=_PT_REGION_TYPE.UI
                bl_category = _PT_CATEGORY.VIEW
            class Scopes:
                bl_space_type=_PT_SPACE_TYPE.IMAGE_EDITOR
                bl_region_type=_PT_REGION_TYPE.UI
                bl_category = _PT_CATEGORY.SCOPES
    #class NODE_EDITOR:
    #    bl_space_type=_PT_SPACE_TYPE.NODE_EDITOR
    #class SEQUENCE_EDITOR:
    #    bl_space_type=_PT_SPACE_TYPE.SEQUENCE_EDITOR
    #class CLIP_EDITOR:
    #    bl_space_type=_PT_SPACE_TYPE.CLIP_EDITOR
    class DOPESHEET_EDITOR:
        bl_space_type=_PT_SPACE_TYPE.DOPESHEET_EDITOR
        class UI:
            bl_space_type=_PT_SPACE_TYPE.DOPESHEET_EDITOR
            bl_region_type = _PT_REGION_TYPE.UI
    class GRAPH_EDITOR:
        bl_space_type=_PT_SPACE_TYPE.GRAPH_EDITOR
        class UI:
            bl_space_type=_PT_SPACE_TYPE.GRAPH_EDITOR
            bl_region_type = _PT_REGION_TYPE.UI
            class Tool:
                bl_space_type=_PT_SPACE_TYPE.GRAPH_EDITOR
                bl_region_type = _PT_REGION_TYPE.UI
                bl_category = _PT_CATEGORY.TOOL
            class Drivers:
                bl_space_type=_PT_SPACE_TYPE.GRAPH_EDITOR
                bl_region_type = _PT_REGION_TYPE.UI
                bl_category = _PT_CATEGORY.DRIVERS
    class NLA_EDITOR:
        bl_space_type=_PT_SPACE_TYPE.NLA_EDITOR
        class UI:
            bl_space_type=_PT_SPACE_TYPE.NLA_EDITOR
            bl_region_type = _PT_REGION_TYPE.UI
            class Tool:
                bl_space_type=_PT_SPACE_TYPE.NLA_EDITOR
                bl_region_type=_PT_REGION_TYPE.UI
                bl_category = _PT_CATEGORY.TOOL
            class View:
                bl_space_type=_PT_SPACE_TYPE.NLA_EDITOR
                bl_region_type=_PT_REGION_TYPE.UI
                bl_category = _PT_CATEGORY.VIEW
    #class TEXT_EDITOR:
    #    bl_space_type=_PT_SPACE_TYPE.TEXT_EDITOR
    #class CONSOLE:
    #    bl_space_type=_PT_SPACE_TYPE.CONSOLE
    #class INFO:
    #    bl_space_type=_PT_SPACE_TYPE.INFO
    #class TOPBAR:
    #    bl_space_type=_PT_SPACE_TYPE.TOPBAR
    #class STATUSBAR:
    #    bl_space_type=_PT_SPACE_TYPE.STATUSBAR
    #class OUTLINER:
    #    bl_space_type=_PT_SPACE_TYPE.OUTLINER
    class PROPERTIES:
        bl_space_type=_PT_SPACE_TYPE.PROPERTIES
        class WINDOW:
            bl_space_type=_PT_SPACE_TYPE.PROPERTIES
            bl_region_type=_PT_REGION_TYPE.WINDOW
            class COLLECTION:
                bl_space_type=_PT_SPACE_TYPE.PROPERTIES
                bl_region_type=_PT_REGION_TYPE.WINDOW
                bl_context=_PT_CONTEXT_PROPERTIES.COLLECTION
            class CONSTRAINT:
                bl_space_type=_PT_SPACE_TYPE.PROPERTIES
                bl_region_type=_PT_REGION_TYPE.WINDOW
                bl_context=_PT_CONTEXT_PROPERTIES.CONSTRAINT
            class BONE_CONSTRAINT:
                bl_space_type=_PT_SPACE_TYPE.PROPERTIES
                bl_region_type=_PT_REGION_TYPE.WINDOW
                bl_context=_PT_CONTEXT_PROPERTIES.BONE_CONSTRAINT
            class DATA:
                bl_space_type=_PT_SPACE_TYPE.PROPERTIES
                bl_region_type=_PT_REGION_TYPE.WINDOW
                bl_context=_PT_CONTEXT_PROPERTIES.DATA
            class BONE:
                bl_space_type=_PT_SPACE_TYPE.PROPERTIES
                bl_region_type=_PT_REGION_TYPE.WINDOW
                bl_context=_PT_CONTEXT_PROPERTIES.BONE
            class SHADERFX:
                bl_space_type=_PT_SPACE_TYPE.PROPERTIES
                bl_region_type=_PT_REGION_TYPE.WINDOW
                bl_context=_PT_CONTEXT_PROPERTIES.SHADERFX
            class MATERIAL:
                bl_space_type=_PT_SPACE_TYPE.PROPERTIES
                bl_region_type=_PT_REGION_TYPE.WINDOW
                bl_context=_PT_CONTEXT_PROPERTIES.MATERIAL
            class OBJECT:
                bl_space_type=_PT_SPACE_TYPE.PROPERTIES
                bl_region_type=_PT_REGION_TYPE.WINDOW
                bl_context=_PT_CONTEXT_PROPERTIES.OBJECT
            class PARTICLE:
                bl_space_type=_PT_SPACE_TYPE.PROPERTIES
                bl_region_type=_PT_REGION_TYPE.WINDOW
                bl_context=_PT_CONTEXT_PROPERTIES.PARTICLE
            class PHYSICS:
                bl_space_type=_PT_SPACE_TYPE.PROPERTIES
                bl_region_type=_PT_REGION_TYPE.WINDOW
                bl_context=_PT_CONTEXT_PROPERTIES.PHYSICS
            class SCENE:
                bl_space_type=_PT_SPACE_TYPE.PROPERTIES
                bl_region_type=_PT_REGION_TYPE.WINDOW
                bl_context=_PT_CONTEXT_PROPERTIES.SCENE
            class TEXTURE:
                bl_space_type=_PT_SPACE_TYPE.PROPERTIES
                bl_region_type=_PT_REGION_TYPE.WINDOW
                bl_context=_PT_CONTEXT_PROPERTIES.TEXTURE
            class RENDER:
                bl_space_type=_PT_SPACE_TYPE.PROPERTIES
                bl_region_type=_PT_REGION_TYPE.WINDOW
                bl_context=_PT_CONTEXT_PROPERTIES.RENDER
            class VIEW_LAYER:
                bl_space_type=_PT_SPACE_TYPE.PROPERTIES
                bl_region_type=_PT_REGION_TYPE.WINDOW
                bl_context=_PT_CONTEXT_PROPERTIES.VIEW_LAYER
            class WORLD:
                bl_space_type=_PT_SPACE_TYPE.PROPERTIES
                bl_region_type=_PT_REGION_TYPE.WINDOW
                bl_context=_PT_CONTEXT_PROPERTIES.WORLD
            class MODIFIER:
                bl_space_type=_PT_SPACE_TYPE.PROPERTIES
                bl_region_type=_PT_REGION_TYPE.WINDOW
                bl_context=_PT_CONTEXT_PROPERTIES.MODIFIER
    #class FILE_BROWSER:
    #    bl_space_type=_PT_SPACE_TYPE.FILE_BROWSER
    #class PREFERENCES:
    #    bl_space_type=_PT_SPACE_TYPE.PREFERENCES

class PT_():
    bl_icon = cspy.icons.ERROR
    bl_options = PT_OPTIONS.DEFAULT_CLOSED
    bl_label = 'UNDEFINED'
    bl_order = 999999

    @classmethod
    def poll(cls, context):
        try:
            result = cls.do_poll(context)
            if callable(result):
                print('[EXCP] {0}:  [do_poll]  Must correct call [{1}]'.format(cspy.utils.get_logging_name(cls), result))
                return False
            return result
        except Exception:
            utils.print_exception('do_poll')
            return False

    def draw_header(self, context):
        try:
            self.layout.label(icon=self.bl_icon)
            
            scene = context.scene
            layout = self.layout
            obj = context.object
            self.finish_header(context, scene, layout, obj)
        except Exception:
            utils.print_exception('draw_header')
            return

    def finish_header(self, context, scene, layout, obj):
        pass

    def draw(self, context):
        try:
            scene = context.scene
            layout = self.layout
            obj = context.object
            self.do_draw(context, scene, layout, obj)
        except Exception:
            utils.print_exception('do_draw')
            raise
    