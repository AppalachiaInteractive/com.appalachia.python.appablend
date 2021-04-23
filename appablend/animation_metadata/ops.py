from appablend.common.actions import get_rotation_at_key
from appablend.common.basetypes.ops import OPS_
from appablend.common.models.unity import get_unity_action_and_clip
from bpy.types import Operator


class AM_OT_check_properties(OPS_, Operator):
    """Checks and assigns properties that are better not human-assigned."""

    bl_idname = "am.check_properties"
    bl_label = "Check Properties"

    @classmethod
    def do_poll(cls, context):
        action, clip, clip_index = get_unity_action_and_clip(context)
        return action

    def do_execute(self, context):
        action, clip, clip_index = get_unity_action_and_clip(context)

        first = action.frame_range[0]
        end = action.frame_range[1]

        start_rot = get_rotation_at_key(action, "Root", first)
        end_rot = get_rotation_at_key(action, "Root", end)

        print(start_rot)
        print(end_rot)

        return {"FINISHED"}
