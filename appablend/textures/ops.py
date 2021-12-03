from bmesh.types import BMFace, BMLoop
from mathutils import Vector
import bpy
import bmesh
from appablend.common.basetypes.ops import OPS_
from appablend.common.core.enums import icons
from appablend.common.core.polling import DOIF
from bpy.types import Context, Mesh, MeshUVLoop, MeshUVLoopLayer, Object, Operator

from appablend.common.core import modes


class TEXTURES_OT_TextureToMesh(OPS_, Operator):
    """Converts a texture to a mesh"""

    bl_idname = "textures.texture_to_mesh"
    bl_label = "Texture To Mesh"
    bl_icon = icons.TEXTURE

    @classmethod
    def do_poll(cls, context):
        return DOIF.ACTIVE.TYPE.IS_MESH(context) and DOIF.ACTIVE.HAS.DATA(context)

    def index_to_coordinate(self, idx, width):
        r = int(idx / width)
        c = idx % width
        return r, c

    def coordinate_to_index(self, r, c, width):
        return r * width + c

    def rgba_from_index(self, idx, pxs):
        start_raw_index = idx * 4
        return pxs[start_raw_index : start_raw_index + 4]

    def is_white(self, rgba):
        return rgba[0] == 1.0 and rgba[1] == 1.0 and rgba[2] == 1.0

    def create_mesh(self, original, obj_name, mesh_name, vlist, width, height, scale):
        s = scale / 2
        verts = []
        faces = []
        v_add = verts.extend
        f_add = faces.append

        for index, pixels in enumerate(vlist):
            pixel_x, pixel_y = pixels[:2]

            position_x = pixel_x * scale
            position_y = pixel_y * scale

            vertex_x_min = -s + position_x
            vertex_x_max = s + position_x
            vertex_y_min = -s + position_y
            vertex_y_max = s + position_y

            v_add(
                [
                    [vertex_x_min, vertex_y_max, 0],
                    [vertex_x_min, vertex_y_min, 0],
                    [vertex_x_max, vertex_y_min, 0],
                    [vertex_x_max, vertex_y_max, 0],
                ]
            )

            offset = index * 4
            f_add([0 + offset, 1 + offset, 2 + offset, 3 + offset])

        new_mesh: Mesh = bpy.data.meshes.new(obj_name)
        new_mesh.from_pydata(verts, [], faces)
        new_mesh.uv_layers.new(name = "UVMap")

        new_mesh.update()
        new_mesh_object: Object
        new_mesh_object = bpy.data.objects.new(obj_name, new_mesh)
        
        bpy.context.scene.collection.objects.link(new_mesh_object)

        new_mesh_object.active_material = original.active_material

        active_object, old_mode = modes.enter_mode_simple("EDIT")

        me = active_object.data
        bm = bmesh.from_edit_mesh(me)

        uv_layer = bm.loops.layers.uv[0]

        # adjust uv coordinates
        face: BMFace
        loop: BMLoop

        for face in bm.faces:
            for loop in face.loops:
                loop_uv = loop[uv_layer]

                co = loop.vert.co
                uv_x = (co.x / width)
                uv_y = (co.y / height)

                loop_uv.uv = Vector([uv_x, uv_y])

        bmesh.update_edit_mesh(me)

        modes.exit_mode(active_object, old_mode)

        return new_mesh_object

    def do_execute(self, context):
        obj: Object = context.active_object
        scale = 0.1

        for index, node in enumerate(obj.active_material.node_tree.nodes):

            if node.name == "Image Texture":
                img = node.image

        pixels = img.pixels
        pxs = list(pixels)

        w = width = img.size[0]
        h = height = img.size[1]

        verts = list()

        for widthIndex in range(w):
            for heightIndex in range(h):
                index = self.coordinate_to_index(heightIndex, widthIndex, w)
                rgba = self.rgba_from_index(index, pxs)

                if self.is_white(rgba):
                    verts.append([heightIndex, -widthIndex, 0.0])

        obj = self.create_mesh(
            obj, "dupli_object_0", "dupli_mesh_0", verts, width, height, scale
        )

        return {"FINISHED"}
