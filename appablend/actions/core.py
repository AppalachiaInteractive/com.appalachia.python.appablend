import bpy


class ActionOpHelper(bpy.types.PropertyGroup):
    action_loop_sync_internal: bpy.props.BoolProperty(name="Action Loop Sync Internal")

    def sync_action_loop(self):
        obj = bpy.context.active_object
        try:
            if not (obj and obj.animation_data and obj.animation_data.action):
                return

            action = obj.animation_data.action
            if not self.action_loop_sync_internal:
                return

            bpy.context.scene.frame_start = action.frame_range[0]
            bpy.context.scene.frame_end = action.frame_range[1]
        except:
            print("sync action loop failing...")

    def get_action_loop_sync(self):
        self.sync_action_loop()
        return self.action_loop_sync_internal

    def set_action_loop_sync(self, value):
        self.action_loop_sync_internal = value
        self.sync_action_loop()

    action_loop_sync: bpy.props.BoolProperty(
        name="Action Loop Sync", get=get_action_loop_sync, set=set_action_loop_sync
    )
