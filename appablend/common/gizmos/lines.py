import bgl
import bpy
import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Matrix, Vector

# Blend Modes
BLEND = 0
MULTIPLY_BLEND = 1
ADDITIVE_BLEND = 2


class LineRenderer:
    def __init__(self):
        # Useful for rendering in the same space of an object
        self.matrix = Matrix.Identity(4)
        # X-ray mode, draw through solid objects
        self.draw_on_top = False
        # Blend mode to choose, set it to one of the blend constants.
        self.blend_mode = BLEND
        # Width of the lines
        self.line_width = 2.5
        # Handler Placeholder
        self.draw_handler = None
        self.drawing = False

        self._coords = []
        self._colors = []
        self._line_shader = gpu.shader.from_builtin("3D_SMOOTH_COLOR")
        self._line_batch = batch_for_shader(
            self._line_shader, "LINES", {"pos": self._coords, "color": self._colors}
        )

    def __call__(self, *args, **kwargs):
        # __call__ Makes this object behave like a function.
        # So you can add it like a draw handler.
        self._draw()

    def coord_count(self):
        if self is None:
            return 0
        if self._coords is None:
            return 0

        return len(self._coords)

    def setup_handler(self):
        self.drawing = True
        if self.draw_handler is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "WINDOW")
            self.draw_handler = None

        self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(
            self, (), "WINDOW", "POST_VIEW"
        )
        self.drawing = True

    def remove_handler(self):
        self.drawing = False

        if self.draw_handler is None:
            return

        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "WINDOW")
        self.draw_handler = None

    def update_batch(self):
        # This takes the data rebuilds the shader batch.
        # Call it every time you clear the data or add new lines, otherwize,
        # You wont see changes in the viewport
        coords = [self.matrix @ coord for coord in self._coords]
        self._line_batch = batch_for_shader(
            self._line_shader, "LINES", {"pos": coords, "color": self._colors}
        )

    def add_line(
        self, start, end, color1=(1.0, 0.0, 0.0, 1.0), color2=(1.0, 0.0, 0.0, 1.0)
    ):
        # Simple add_line function, support color gradients,
        # if only color1 is specified, it will be solid color (color1 on both ends)
        # This doesnt render a line, it just adds the vectors and colors to the data
        # so after calling update_batch(), it will be converted in a buffer Object
        self._coords.append(Vector(start))
        self._coords.append(Vector(end))
        self._colors.append(color1)
        self._colors.append(color2)

    def add_lines(
        self, points, start_color=(1.0, 0.0, 0.0, 1.0), end_color=(1.0, 0.0, 0.0, 1.0)
    ):
        # Simple add_lines function, support color gradients,
        # if only color1 is specified, it will be solid color (color1 on both ends)
        # This doesnt render a line, it just adds the vectors and colors to the data
        # so after calling update_batch(), it will be converted in a buffer Object

        if end_color is None:
            end_color = start_color

        point_count = len(points)
        color_range = [0.0, 0.0, 0.0, 0.0]
        for i in range(4):
            color_range[i] = end_color[i] - start_color[i]

        for point_index in range(point_count - 1):
            first_point = points[point_index]
            second_point = points[point_index + 1]

            first_time = point_index / float(point_count - 1)
            first_color = (
                start_color[0] + (first_time * color_range[0]),
                start_color[1] + (first_time * color_range[1]),
                start_color[2] + (first_time * color_range[2]),
                start_color[3] + (first_time * color_range[3]),
            )

            second_time = (point_index + 1) / float(point_count - 1)
            second_color = (
                start_color[0] + (second_time * color_range[0]),
                start_color[1] + (second_time * color_range[1]),
                start_color[2] + (second_time * color_range[2]),
                start_color[3] + (second_time * color_range[3]),
            )

            self._coords.append(Vector(first_point))
            self._coords.append(Vector(second_point))
            self._colors.append(first_color)
            self._colors.append(second_color)

    def clear_data(self):
        # just clear all the data
        self._coords.clear()
        self._colors.clear()

    def _start_drawing(self):
        # This handles all the settings of the renderer before starting the draw stuff
        if self.blend_mode == BLEND:
            bgl.glEnable(bgl.GL_BLEND)

        elif self.blend_mode == MULTIPLY_BLEND:
            bgl.glEnable(bgl.GL_BLEND)
            bgl.glBlendFunc(bgl.GL_DST_COLOR, bgl.GL_ZERO)

        elif self.blend_mode == ADDITIVE_BLEND:
            bgl.glEnable(bgl.GL_BLEND)
            bgl.glBlendFunc(bgl.GL_ONE, bgl.GL_ONE)

        if self.draw_on_top:
            bgl.glDisable(bgl.GL_DEPTH_TEST)

        bgl.glLineWidth(self.line_width)

    def _stop_drawing(self):
        # just reset some OpenGL stuff to not interfere with other drawings in the viewport
        # its not absolutely necessary but makes it safer.
        bgl.glDisable(bgl.GL_BLEND)
        bgl.glLineWidth(1)
        if self.draw_on_top:
            bgl.glEnable(bgl.GL_DEPTH_TEST)

    def _draw(self):
        # This should be called by __call__,
        # just regular routines for rendering in the viewport as a draw_handler
        self._start_drawing()
        batch = self._line_batch
        self._line_shader.bind()
        batch.draw(self._line_shader)
        self._stop_drawing()
