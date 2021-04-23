def in_rest_position(armature):
    return armature.data.pose_position == "REST"


def in_pose_position(armature):
    return armature.data.pose_position == "POSE"


def to_rest_position(armature):
    armature.data.pose_position = "REST"


def to_pose_position(armature):
    armature.data.pose_position = "POSE"
