import bpy
import cspy
from mathutils import Vector, Matrix, Quaternion

def get_or_create_fcurve(action, data_path, array_index=-1, group=None):
    for fc in action.fcurves:
        if fc.data_path == data_path and (array_index < 0 or fc.array_index == array_index):
            return fc

    fc = action.fcurves.new(data_path, index=array_index)
    fc.group = group
    return fc

def add_keyframe_quat(action, quat, frame, data_path, group=None):
    for i in range(len(quat)):
        fc = get_or_create_fcurve(action, data_path, i, group)
        pos = len(fc.keyframe_points)
        fc.keyframe_points.add(1)
        fc.keyframe_points[pos].co = [frame, quat[i]]
        fc.update()


def frames_matching(action, data_path):
    frames = set()
    for fc in action.fcurves:
        if fc.data_path == data_path:
            fri = [int(kp.co[0]) for kp in fc.keyframe_points]
            frames.update(fri)
    return frames


def shift_fcurve_channels(action_prefix, bone_name, matrix):
    fcurve_prefix = 'pose.bones["{0}{1}'.format(bone_name, ''if bone_name == '' else '"].' )

    actions = [action for action in bpy.data.actions if action.name.startswith(action_prefix)]

    for action in actions:

        data_paths = set([fcurve.data_path for fcurve in action.fcurves if fcurve.data_path.startswith(fcurve_prefix)])

        for data_path in data_paths:

            fcurves = [fcurve for fcurve in action.fcurves if fcurve.data_path == data_path ]

            for data_type in ('location', 'quaternion'):

                curves = [fcurve for fcurve in fcurves if fcurve.data_path.endswith(data_type)]
                if not curves:
                    continue

                num_keys = max([len(fcurve.keyframe_points) for fcurve in curves])

                for i in range(num_keys):
                    frame = curves[0].keyframe_points[i].co[0]
                    key_in = [fcurve.keyframe_points[i].co[1] for fcurve in curves]
                    if data_type == 'location':
                        mat =  Matrix.Translation( key_in )
                        mat = matrix @ mat
                        key = mat.to_translation()
                    #elif data_type == 'scale':
                    #    mat =  Matrix.Scale( key_in, 4)
                    #    mat = matrix.inverted() @ mat
                    #    key = mat.to_translation()
                    else:
                        mat = Quaternion(key_in).to_matrix().to_4x4()
                        mat = matrix @ mat
                        key = mat.to_quaternion()

                    for a in range(0, len(curves)):
                        curves[a].keyframe_points[i].co[1] = key[a]

            for fcurve in fcurves:
                fcurve.update()
	