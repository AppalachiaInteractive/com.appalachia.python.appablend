import bpy
from appablend.common.actions import insert_keyframe
from appablend.common.utils import files


class UnityKeyframeData:
    def __init__(self):
        self.obj_name = ""
        self.clip_name = ""
        self.data_path = ""
        self.array_index = 0
        self.frame = 1
        self.value = 0.0

    @classmethod
    def parse_key_row(cls, row, key_offset):
        try:
            obj_name = row["obj_name"]
            obj_name = obj_name.replace("Avatar", "")
            clip_name = row["clip_name"]
            data_path = row["data_path"]
            array_index = int(row["array_index"])
            frame = int(row["frame"]) + key_offset
            value = float(row["value"])

            return obj_name, clip_name, data_path, array_index, frame, value
        except:
            print("Row parse exception: {0}".format(row))
            raise

    @classmethod
    def process_key_row(cls, row, key_offset):
        obj_name, clip_name, data_path, array_index, frame, value = cls.parse_key_row(
            row, key_offset
        )

        key_data = UnityKeyframeData()
        key_data.obj_name = obj_name
        key_data.clip_name = clip_name
        key_data.data_path = data_path
        key_data.array_index = array_index
        key_data.frame = frame
        key_data.value = value

        return key_data

    @classmethod
    def parse_key_files(cls, context, dir_path, key_offset):
        filepaths = files.get_files_in_dir(dir_path, "", "", ".keys.txt")

        headers, rows = files.parse_csvs(filepaths)

        metadatas = []

        key_datas = {}

        for row in rows:
            key_data = cls.process_key_row(row, key_offset)

            if not key_data.obj_name in key_datas:
                key_datas[key_data.obj_name] = {}

            obj_key_datas = key_datas[key_data.obj_name]

            if not key_data.clip_name in obj_key_datas:
                obj_key_datas[key_data.clip_name] = {}

            clip_key_datas = obj_key_datas[key_data.clip_name]

            if not key_data.data_path in clip_key_datas:
                clip_key_datas[key_data.data_path] = {}

            data_path_key_datas = clip_key_datas[key_data.data_path]

            if not key_data.array_index in data_path_key_datas:
                data_path_key_datas[key_data.array_index] = []

            array_index_key_datas = data_path_key_datas[key_data.array_index]

            array_index_key_datas.append(key_data)

        return key_datas

    @classmethod
    def process_key_files(cls, context, dir_path, key_offset, current_only):
        key_datas = cls.parse_key_files(context, dir_path, key_offset)

        modified_actions = set()

        for obj_name in key_datas.keys():
            obj_key_datas = key_datas[obj_name]

            for clip_name in obj_key_datas.keys():
                clip_key_datas = obj_key_datas[clip_name]

                for data_path in clip_key_datas.keys():
                    data_path_key_datas = clip_key_datas[data_path]

                    for array_index in data_path_key_datas.keys():

                        if obj_name not in bpy.data.actions:
                            continue

                        if (
                            current_only
                            and obj_name
                            != context.active_object.animation_data.action.name
                        ):
                            continue

                        action = bpy.data.actions[obj_name]

                        """ if clip_name not in action.unity_clips:
                            continue

                        unity_clip = action.unity_clips[clip_name] """

                        fcurve = action.fcurves.find(data_path, index=array_index)

                        if not fcurve:
                            fcurve = action.fcurves.new(data_path, index=array_index)

                        modified_actions.add(action)

                        keyframes = data_path_key_datas[array_index]

                        for keyframe in keyframes:
                            insert_keyframe(
                                fcurve,
                                keyframe.frame,
                                keyframe.value,
                                needed=True,
                                fast=True,
                            )

        for action in modified_actions:
            for fcurve in action.fcurves:
                fcurve.update()
