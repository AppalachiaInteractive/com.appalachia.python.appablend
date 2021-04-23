import bpy


def apply_pose_to_frame(context, armature, pose_name, frame):
    pose_index = armature.pose_library.pose_markers.find(pose_name)

    if pose_index == -1:
        return
    context.scene.frame_current = frame
    bpy.ops.poselib.apply_pose(pose_index=pose_index)
