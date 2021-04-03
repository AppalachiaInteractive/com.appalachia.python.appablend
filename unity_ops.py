import bpy, cspy
from bpy.types import Operator
from cspy import ops, polling, unity, unity_keys, unity_clips, timeline
from cspy.ops import OPS_, OPS_DIALOG
from cspy.polling import POLL
from cspy.unity import *
from cspy.unity_keys import *
from cspy.unity_clips import *
from cspy.timeline import *
from cspy.bones import *

class UNITY_OT_refresh_key_data(OPS_, Operator):
    """Refreshes animation key metadata from Unity"""
    bl_idname = "unity.refresh_key_data"
    bl_label = "Refresh Key Data"

    @classmethod
    def do_poll(cls, context):
        return POLL.active_object_unity_clips_split(context)

    def do_execute(self, context):
        obj = get_active_unity_object(context)
        scene = context.scene
        action = obj.animation_data.action

        clip = action.unity_clips[0]
        clip.refresh_keys()

        return {'FINISHED'}

class UNITY_OT_refresh_key_data_all(OPS_, Operator):
    """Refreshes all animation key metadata from Unity"""
    bl_idname = "unity.refresh_key_data_all"
    bl_label = "Refresh (All)"

    @classmethod
    def do_poll(cls, context):
        return len(bpy.data.actions) > 0 and context.scene.unity_settings.key_dir_path != ''

    def do_execute(self, context):
        obj = get_active_unity_object(context)
        scene = context.scene

        for action in bpy.data.actions:
            if len(action.unity_clips) != 1:
                continue

            clip = action.unity_clips[0]

            if clip.source_action is None:
                continue

            clip.refresh_keys()

        return {'FINISHED'}

class UNITY_OT_refresh_clip_data(OPS_, Operator):
    """Refreshes animation clip metadata from Unity"""
    bl_idname = "unity.refresh_clip_data"
    bl_label = "Refresh Clip Data"

    @classmethod
    def do_poll(cls, context):
        return POLL.active_unity_object(context) and context.scene.unity_settings.sheet_dir_path != ''

    def do_execute(self, context):
        obj = get_active_unity_object(context)
        scene = context.scene
        key_offset = 1

        path = bpy.path.abspath(scene.unity_settings.sheet_dir_path)
        action, clip = get_unity_action_and_clip(context)

        UnityClipMetadata.parse_clip_files(context, path, key_offset, action)
        sync_with_action_mode(context)
        return {'FINISHED'}

class UNITY_OT_refresh_clip_data_all(OPS_, Operator):
    """Refreshes animation clip metadata from Unity"""
    bl_idname = "unity.refresh_clip_data_all"
    bl_label = "Refresh (All)"

    @classmethod
    def do_poll(cls, context):
        return len(bpy.data.actions) > 0 and context.scene.unity_settings.sheet_dir_path != ''

    def do_execute(self, context):
        scene = context.scene
        key_offset = 1

        path = bpy.path.abspath(scene.unity_settings.sheet_dir_path)

        for action in bpy.data.actions:
            action.unity_metadata.clip_index = 0
        
        UnityClipMetadata.parse_clip_files(context, path, key_offset)
        sync_with_action_mode(context)
        return {'FINISHED'}

class UNITY_OT_clear_clip_data(OPS_, Operator):
    """Clears animation clip metadata from Unity for this action"""
    bl_idname = "unity.clear_clip_data"
    bl_label = "Clear Clip Data"

    @classmethod
    def do_poll(cls, context):
        return POLL.active_unity_object(context)  and not get_active_unity_object(context).animation_data.action.unity_metadata.clips_protected and context.scene.unity_settings.sheet_dir_path != ''

    def do_execute(self, context):
        obj = get_active_unity_object(context)

        action = obj.animation_data.action

        action.unity_clips.clear()

        return {'FINISHED'}

class UNITY_OT_clear_clip_data_all(OPS_, Operator):
    """Clears animation clip metadata from Unity for all actions"""
    bl_idname = "unity.clear_clip_data_all"
    bl_label = "Clear (All)"

    @classmethod
    def do_poll(cls, context):
        return len(bpy.data.actions) > 0 and context.scene.unity_settings.sheet_dir_path != ''

    def do_execute(self, context):

        for action in bpy.data.actions:
            if action.unity_metadata.master_action:
                continue
            if action.unity_metadata.clips_protected:
                continue
            action.unity_clips.clear()

        return {'FINISHED'}


class UNITY_OT_clamp_to_clip(OPS_, Operator):
    """Clamps scene play region to unity clip"""
    bl_idname = "unity.clamp_to_clip"
    bl_label = "Clamp To Clip"

    action_name: bpy.props.StringProperty(name="Action Name")
    clip_name: bpy.props.StringProperty(name="Clip Name")

    @classmethod
    def do_poll(cls, context):
        return POLL.active_unity_object(context)

    def do_execute(self, context):
        active_clip = bpy.data.actions[self.action_name].unity_clips[self.clip_name]

        clamp_to_unity_clip(context, active_clip)

        return {'FINISHED'}

class UNITY_OT_clamp_to_clip_and_play(OPS_, Operator):
    """Clamps scene play region to unity clip"""
    bl_idname = "unity.clamp_to_clip_and_play"
    bl_label = "Clamp & Play"

    action_name: bpy.props.StringProperty(name="Action Name")
    clip_name: bpy.props.StringProperty(name="Clip Name")

    @classmethod
    def do_poll(cls, context):
        return POLL.active_unity_object(context)

    def do_execute(self, context):
        active_clip = bpy.data.actions[self.action_name].unity_clips[self.clip_name]

        clamp_to_unity_clip(context, active_clip, True)

        return {'FINISHED'}

class UNITY_OT_decorate_action(OPS_, Operator):
    """Decorates actions with unity clip metadata"""
    bl_idname = "unity.decorate_action"
    bl_label = "Decorate Action"

    clip_name: bpy.props.StringProperty(name="Clip Name")

    @classmethod
    def do_poll(cls, context):
        return POLL.active_unity_object(context)

    def do_execute(self, context):
        action = get_active_unity_object(context).animation_data.action
        clip = action.unity_clips[clip_name]

        clip.decorate_action(action)

        return {'FINISHED'}

class UNITY_OT_decorate_action_all(OPS_, Operator):
    """Decorates actions with all relevant unity clip metadata"""
    bl_idname = "unity.decorate_action_all_clips"
    bl_label = "Decorate Using All Clips"

    @classmethod
    def do_poll(cls, context):
        try:
            return get_active_unity_object(context).animation_data.action.unity_clips
        except:
            return False

    def do_execute(self, context):
        action = get_active_unity_object(context).animation_data.action

        for clip in action.unity_clips:
            clip.decorate_action(action)

        return {'FINISHED'}

class UNITY_OT_sync_actions_with_clips(OPS_, Operator):
    """Syncs each unity clip's action property with its action owner"""
    bl_idname = "unity.sync_actions_with_clips"
    bl_label = "Sync Action and Clip Properties"

    @classmethod
    def do_poll(cls, context):
        return POLL.active_unity_object(context)

    def do_execute(self, context):
        action = get_active_unity_object(context).animation_data.action

        for clip in action.unity_clips:
            clip.action = action

        return {'FINISHED'}


class UNITY_OT_sort_clip_data(OPS_, Operator):
    """Sorts animation clip metadata from Unity for this action"""
    bl_idname = "unity.sort_clip_data"
    bl_label = "Sort Clip Data"

    @classmethod
    def do_poll(cls, context):
        return POLL.active_unity_object(context)

    def do_execute(self, context):
        obj = get_active_unity_object(context)

        action = obj.animation_data.action

        cspy.collectionprops.sort(action.unity_clips, 'frame_start')

        return {'FINISHED'}

class UNITY_OT_sort_clip_data_all(OPS_, Operator):
    """Sorts animation clip metadata from Unity for all actions"""
    bl_idname = "unity.sort_clip_data_all"
    bl_label = "Sort (All)"

    @classmethod
    def do_poll(cls, context):
        return len(bpy.data.actions) > 0

    def do_execute(self, context):
        for action in bpy.data.actions:
            cspy.collectionprops.sort(action.unity_clips, 'frame_start')

        return {'FINISHED'}

class UNITY_OT_copy_clips_from_template(OPS_, Operator):
    """Copy unity clip metadata from a template """
    bl_idname = "unity.copy_clips_from_template"
    bl_label = "Copy Clips From Template"

    @classmethod
    def do_poll(cls, context):
        return POLL.active_unity_object(context)

    def do_execute(self, context):
        action = get_active_unity_object(context).animation_data.action
        template = action.unity_clip_template

        action.unity_clips.clear()

        for clip in template.unity_clips:
            new_clip = action.unity_clips.add()
            new_clip.copy_from(clip)
            new_clip.action = action

        return {'FINISHED'}

class UNITY_OT_all_clips(OPS_):
    @classmethod
    def do_poll(cls, context):
        return POLL.active_unity_object(context) and get_active_unity_object(context).animation_data.action.unity_clips

    def do_execute(self, context):
        clips = get_filtered_clips(context)

        for clip in clips:
            self.do_clip(context, clip)

        return {'FINISHED'}

class UNITY_OT_decorate_clips(UNITY_OT_all_clips, Operator):
    """Use unity clip metadata """
    bl_idname = "unity.decorate_clips"
    bl_label = "Decorate All"

    def do_clip(self, context, clip):
        action = clip.action

        clip.decorate(action)

class UNITY_OT_demarcate_clips(UNITY_OT_all_clips, Operator):
    """Use unity clip metadata """
    bl_idname = "unity.demarcate_clips"
    bl_label = "Demarcate All"

    def do_clip(self, context, clip):
        action = clip.action

        for fcurve in action.fcurves:
            clip.demarcate(fcurve)

        for fcurve in action.fcurves:
            fcurve.update()

class UNITY_OT_get_current(OPS_, Operator):
    """Get the current clip based on the frame """
    bl_idname = "unity.get_current"
    bl_label = "Get Current"

    @classmethod
    def do_poll(cls, context):
        return POLL.active_unity_object(context) and get_active_unity_object(context).animation_data.action.unity_clips

    def do_execute(self, context):
        action = get_active_unity_object(context).animation_data.action

        for fcurve in action.fcurves:
            for clip in action.unity_clips:
                clip.demarcate(fcurve)

        for fcurve in action.fcurves:
            fcurve.update()

        return {'FINISHED'}

class UNITY_OT_update_master_clip_metadata(OPS_, Operator):
    """Use unity clip metadata to update the master action."""
    bl_idname = "unity.update_master_clip_metadata"
    bl_label = "Update Master Clip"

    @classmethod
    def do_poll(cls, context):
        return 'MASTER' in bpy.data.actions

    def do_execute(self, context):
        master_action_name = 'MASTER'
        master_action = bpy.data.actions[master_action_name]
        obj = get_active_unity_object(context)

        padding = 10
        round_to_nearest = 10

        master_action.unity_metadata.master_action = True
        master_action.unity_metadata.clips_protected = True
        master_action.unity_clips.clear()
        for marker in reversed(master_action.pose_markers):
            master_action.pose_markers.remove(marker)

        start = 1

        for action in bpy.data.actions:
            if action == master_action or action.name.endswith('Action') or action.name.endswith('_Layer') or 'PoseLib' in action.name:
                continue

            print('Getting metadata for action {0}'.format(action.name))

            if start != 1:
                start += padding                    # 47 + 10 = 57
                overlap = start % round_to_nearest  # 57 %  5 =  2
                offset = round_to_nearest - overlap #  5 -  2 =  3
                start += offset                     # 57 +  3 = 60  - clean frame start

            action_start = action.frame_range[0]
            action_end = action.frame_range[1]

            start -= action_start

            if action.unity_clips:
                for unity_clip in action.unity_clips:
                    new_clip = master_action.unity_clips.add()
                    new_clip.copy_from(unity_clip)

                    new_clip.action = master_action

                    new_clip.frame_start += start
                    new_clip.frame_end += start

            start += (action_end - action_start) + 1

        #print('Decorating {0} clips'.format(len(master_action.unity_clips)))
        #for clip in master_action.unity_clips:
        #    clip.decorate(master_action)

        for fc in master_action.fcurves:
            fc.update()

        return {'FINISHED'}

class UNITY_OT_remove_non_clip_keys(OPS_, Operator):
    """Delete keyframes not included in unity clips."""
    bl_idname = "unity.remove_non_clip_key"
    bl_label = "Remove Non-Clip Keys"

    @classmethod
    def do_poll(cls, context):
        return POLL.active_unity_object(context)

    def do_execute(self, context):
        action = get_active_unity_object(context).animation_data.action

        for fcurve in action.fcurves:
            for keyframe_point in reversed(fcurve.keyframe_points):
                f = keyframe_point.co[0]

                found = False
                for clip in action.unity_clips:
                    if f >= clip.frame_start and f <= clip.frame_end:
                        found = True
                    if found:
                        break

                if not found:
                    fcurve.keyframe_points.remove(keyframe_point)

        for fcurve in action.fcurves:
            fcurve.update()

        return {'FINISHED'}

class UNITY_OT_split_by_clip(OPS_, Operator):
    """Splits this action into as many clips."""
    bl_idname = "unity.split_by_clip"
    bl_label = "Split By Clip"

    @classmethod
    def do_poll(cls, context):
        return POLL.active_unity_object(context) and len(get_active_unity_object(context).animation_data.action.unity_clips) > 1

    def do_execute(self, context):
        action = get_active_unity_object(context).animation_data.action

        for clip in action.unity_clips:
            new_action_name = '{0}_{1}'.format(action.name, clip.name)
            new_clip_name = clip.name
            new_action = cspy.actions.split_action(action, new_action_name, clip.name, new_clip_name, clip.frame_start, clip.frame_end)

        UNITY_OT_refresh_scene_all_clips.do_execute(UNITY_OT_refresh_scene_all_clips, context)
        return {'FINISHED'}

class UNITY_OT_split_by_clip_all(OPS_, Operator):
    """Splits all actions into as many clips."""
    bl_idname = "unity.split_by_clip_all"
    bl_label = "Split By Clip (All)"

    @classmethod
    def do_poll(cls, context):
        return len(bpy.data.actions) > 1

    def do_execute(self, context):
        for action in bpy.data.actions:
            if action.unity_clips and len(action.unity_clips) > 1:
                for clip in action.unity_clips:
                    new_action_name = '{0}_{1}'.format(action.name, clip.name)
                    new_clip_name = clip.name
                    new_action = cspy.actions.split_action(action, new_action_name, clip.name, new_clip_name, clip.frame_start, clip.frame_end)

        UNITY_OT_refresh_scene_all_clips.do_execute(UNITY_OT_refresh_scene_all_clips, context)
        return {'FINISHED'}

class UNITY_OT_refresh_indices(OPS_, Operator):
    """Refreshes all unity action clip indices."""
    bl_idname = "unity.refresh_indices"
    bl_label = "Refresh Indices"

    @classmethod
    def do_poll(cls, context):
        return len(bpy.data.actions) > 1

    def do_execute(self, context):
        for action in bpy.data.actions:
            action.unity_settings.clip_index = 0

        return {'FINISHED'}

class UNITY_OT_bake:

    @classmethod
    def do_poll(cls, context):
        return POLL.active_object_unity_clips_some(context)

    def bake_action(self, context, obj, action, clip):
        obj.animation_data.action = clip.action

        context.scene.frame_start = clip.frame_start
        context.scene.frame_current = clip.frame_start
        context.scene.frame_end = clip.frame_end

        bpy.ops.nla.bake(
            frame_start=context.scene.frame_start,
            frame_end=context.scene.frame_end,
            step=1,
            only_selected=True,
            visual_keying=True ,
            clear_constraints=False,
            clear_parents=False,
            use_current_action=True,
            bake_types={'POSE'},
            )

class UNITY_OT_bake_clip(OPS_, UNITY_OT_bake, Operator):
    """Bake unity clip."""
    bl_idname = "unity.bake_clip"
    bl_label = "Bake Clip"

    def do_execute(self, context):
        obj = get_active_unity_object(context)
        action, clip = get_unity_action_and_clip(context)

        self.bake_action(context, obj, action, clip)

        return {'FINISHED'}

class UNITY_OT_bake_all_clips(OPS_, UNITY_OT_bake, Operator):
    """Bake all unity clips."""
    bl_idname = "unity.bake_all_clips"
    bl_label = "Bake All Clips"

    def do_execute(self, context):
        obj = get_active_unity_object(context)

        clips = get_filtered_clips(context)

        for clip in clips:
            self.bake_action(context, obj, clip.action, clip)

        return {'FINISHED'}


class UNITY_OT_refresh_split_clip(OPS_,  Operator):
    """Reloads the keys from the source clip into this action."""
    bl_idname = "unity.refresh_split_clip"
    bl_label = "Refresh Split Keys"

    @classmethod
    def do_poll(cls, context):
        return POLL.active_object_unity_clips_some(context) and len(bpy.data.actions) > 1

class UNITY_OT_refresh_split_clips_all(OPS_, Operator):
    """Reloads the keys from the source clip into all actions."""
    bl_idname = "unity.refresh_split_clips_all"
    bl_label = "Refresh Split Keys (All)"

    @classmethod
    def do_poll(cls, context):
        return POLL.active_unity_object(context) and len(bpy.data.actions) > 1

    def do_execute(self, context):
        for action in bpy.data.actions:
            if action.unity_clips and len(action.unity_clips) > 1:
                for clip in action.unity_clips:
                    new_action_name = '{0}_{1}'.format(action.name, clip.name)
                    new_clip_name = clip.name
                    new_action = cspy.actions.split_action(action, new_action_name, clip.name, new_clip_name, clip.frame_start, clip.frame_end)

        return {'FINISHED'}

class UNITY_OT_Set_By_Current_Frame(OPS_, Operator):
    """Sets the current clip to the one shown on screen."""
    bl_idname = "unity.set_by_current_frame"
    bl_label = "Set By Frame"

    action_name: bpy.props.StringProperty(name="Action Name")
    clip_name: bpy.props.StringProperty(name="Clip Name")

    @classmethod
    def do_poll(cls, context):
        return POLL.active_unity_object(context)

    def do_execute(self, context):
        action = get_active_unity_object(context).animation_data.action

        f = context.scene.frame_current
        for index, clip in enumerate(action.unity_clips):
            if f >= clip.frame_start and f <= clip.frame_end:
                action.unity_metadata.clip_index = index
                active_clip = clip
                break

        clamp_to_unity_clip(context, active_clip, True)

        return {'FINISHED'}

class UNITY_OT_apply_pose(OPS_, Operator):
    """Applies the pose library pose to the specified frame"""
    bl_idname = "unity.apply_pose"
    bl_label = "Apply Pose"

    pose_name: bpy.props.StringProperty(name='Pose Name')
    frame: bpy.props.IntProperty(name='Frame')
    rooted: bpy.props.BoolProperty(name='Rooted')

    @classmethod
    def do_poll(cls, context):
        return POLL.active_object_unity_clips(context)

    def do_execute(self, context):
        obj = get_active_unity_object(context)
        action = obj.animation_data.action

        for bone in obj.data.bones:
            if bone.parent is None and not self.rooted:
                bone.select = False
            else:
                bone.select = True


        apply_pose_to_frame(context, obj, self.pose_name, self.frame)

        return {'FINISHED'}

class UNITY_OT_new_pose(OPS_, Operator):
    """Adds the specified frame to the pose library"""
    bl_idname = "unity.new_pose"
    bl_label = "New Pose"

    frame: bpy.props.IntProperty(name='Frame')
    start: bpy.props.BoolProperty(name='Start?')

    @classmethod
    def do_poll(cls, context):
        return POLL.active_object_unity_clips(context)

    def do_execute(self, context):
        obj = get_active_unity_object(context)
        action = obj.animation_data.action
        clip = action.unity_clips[action.unity_metadata.clip_index]

        bpy.ops.poselib.pose_add(frame=self.frame)

        new_pose = obj.pose_library.pose_markers['Pose']
        new_pose.name = '{0} {1}'.format(clip.name, 'Start' if self.start else 'End')

        if self.start:
            clip.pose_start = new_pose.name
        else:
            clip.pose_end = new_pose.name

        return {'FINISHED'}

class UNITY_OT_Clamp_Keys(OPS_, Operator):
    """Clamps the keyframe to unity clip range using constant interpolation."""
    bl_idname = "unity.clamp_keys"
    bl_label = "Clamp Keys"

    @classmethod
    def do_poll(cls, context):
        return POLL.active_object_unity_clips(context)

    def do_execute(self, context):
        action = get_active_unity_object(context).animation_data.action

        start_ends, starts, ends, minf, maxf = get_clip_frame_range_analysis(action)

        for fcurve in action.fcurves:
            for keyframe_point in fcurve.keyframe_points:
                f = keyframe_point.co[0]

                if f in ends:
                    keyframe_point.interpolation = cspy.actions.INTERPOLATION.CONSTANT
                else:
                    keyframe_point.interpolation = cspy.actions.INTERPOLATION.LINEAR

        return {'FINISHED'}

class _UNITY_OT:
    def do_execute(self, context):
        obj = get_active_unity_object(context)
        action = obj.animation_data.action
        clip = None

        if action.unity_clips:
            clip = action.unity_clips[action.unity_metadata.clip_index]

        self.do_clip(context, obj, action, clip)

        return {'FINISHED'}

class UNITY_OT(_UNITY_OT):
    @classmethod
    def do_poll(cls, context):
        return POLL.active_unity_object(context)

class UNITY_OT_clip(_UNITY_OT):
    @classmethod
    def do_poll(cls, context):
        return POLL.active_object_unity_clips_some(context)

class UNITY_OT_decorate_clip(UNITY_OT_clip, OPS_, Operator):
    """Decorate the active clip."""
    bl_idname = "unity.decorate_clip"
    bl_label = "Decorate"

    def do_clip(self, context, obj, action, clip):
         clip.decorate(action)

class UNITY_OT_demarcate_clip(UNITY_OT_clip, OPS_, Operator):
    """Demarcate the active clip."""
    bl_idname = "unity.demarcate_clip"
    bl_label = "Demarcate"

    def do_clip(self, context, obj, action, clip):
        for fcurve in action.fcurves:
            clip.demarcate(fcurve)

        for fcurve in action.fcurves:
            fcurve.update()

class UNITY_OT_new_clip(UNITY_OT, OPS_, Operator):
    """Create a new clip."""
    bl_idname = "unity.new_clip"
    bl_label = "New"

    def do_clip(self, context, obj, action, clip):
        new_clip = action.unity_clips.add()
        if clip is not None:
            new_clip.copy_from(clip)
            new_clip.frame_start = clip.frame_end + 1
            new_clip.frame_end = new_clip.frame_start + 1
            new_clip.name = '{0} - New Clip'.format(clip.name)
            clip.can_edit = True
        else:
            new_clip.name = action.name
            new_clip.action = action
            new_clip.frame_start = action.frame_range[0]
            new_clip.frame_end = action.frame_range[1]

        new_clip.can_edit = True

class UNITY_OT_split_clip(UNITY_OT_clip, OPS_, Operator):
    """Split the active clip."""
    bl_idname = "unity.split_clip"
    bl_label = "Split"

    def do_clip(self, context, obj, action, clip):
        new_clip = action.unity_clips.add()
        new_clip.copy_from(clip)

        clip_range = clip.frame_end - clip.frame_start
        half = clip_range / 2

        clip.frame_end -= half
        new_clip.frame_start = clip.frame_end
        new_clip.name += ' Split'
        new_clip.can_edit = True
        clip.can_edit = True



class UNITY_OT_delete_clip(UNITY_OT_clip, OPS_, Operator):
    """Delete the active clip."""
    bl_idname = "unity.delete_clip"
    bl_label = "Delete"

    def do_clip(self, context, obj, action, clip):
        action.unity_clips.remove(action.unity_metadata.clip_index)

        if action.unity_metadata.clip_index > 0:
            action.unity_metadata.clip_index -= 1

class UNITY_OT_clean_single_clip_actions(OPS_, Operator):
    """Deletes clips from the action that do not match the action name"""
    bl_idname = "unity.clean_single_clip_actions"
    bl_label = "Clean Single Clip Actions"

    @classmethod
    def do_poll(cls, context):
        return POLL.active_object_unity_clips(context) and context.scene.unity_settings.mode == 'SCENE'

    def do_execute(self, context):
        scene = context.scene

        for action in bpy.data.actions:
            single_clip = False

            for clip in action.unity_clips:
                if clip.name == action.name:
                    single_clip = True
                    break

            if single_clip:
                print('Deleting extraneous unity actions from action {0}'.format(action.name))
                action.unity_metadata.clip_index = 0

                for index in reversed(range(len(action.unity_clips))):
                    clip = action.unity_clips[index]
                    if not clip.name == action.name:
                        action.unity_clips.remove(index)

        print('Done.')

class UNITY_OT_refresh_scene_all_clips(OPS_, Operator):
    """Refresh the scene level unity clip store."""
    bl_idname = "unity.refresh_scene_all_clips"
    bl_label = "Refresh"

    @classmethod
    def do_poll(cls, context):
        return context.scene.unity_settings.mode == 'SCENE'

    def do_execute(self, context):
        scene = context.scene
        scene.all_unity_clips.clear()

        for action in bpy.data.actions:
            for clip in action.unity_clips:

                copy = scene.all_unity_clips.add()
                copy.copy_from(clip)

        sync_with_action_mode(context)

        scene.unity_settings.clip_index = min(scene.unity_settings.clip_index, len (scene.all_unity_clips)-1)

        return {'FINISHED'}


class UNITY_OT_rm_curves:
    group_name = 'Root Motion Settings'

    @classmethod
    def do_poll(cls, context):
        return POLL.data_actions(context)

    def process_action(self, context, action):
        if len(action.unity_clips) != 1:
            return
    
        obj = get_active_unity_object(context)

        sync_with_scene_mode(context)

        clip = action.unity_clips[0]

        for ci, fcurve in cspy.iters.reverse_enumerate(action.fcurves):
            if fcurve.group and fcurve.group.name == self.group_name:
                for ki, key in cspy.iters.reverse_enumerate(fcurve.keyframe_points):
                    fcurve.keyframe_points.remove(key)
                action.fcurves.remove(fcurve)
                
        keys = UnityClipMetadata.root_motion_keys

        updated_paths = []

        for data_path in keys:
            value = getattr(clip, data_path)
            has_length = getattr(value, '__len__', None)
            index_values = []

            if has_length:
                for i, v in enumerate(value):
                    index_values.append((i, v))
            else:
                index_values.append((-1, value))
            
            for i, v in index_values:
                path = data_path
                if i != -1:
                    path = '{0}_{1}'.format(data_path, i)

                if data_path.endswith('_start'):
                    path = path.replace('_start', '')
                elif data_path.endswith('_end'):
                    path = path.replace('_end','')

                updated_paths.append(path)
                fcurve = action.fcurves.find(path, index=-1)
                    
                if not fcurve:
                    fcurve = action.fcurves.new(path, index=-1, action_group=self.group_name)

                if not getattr(bpy.types.Object, path, None):                    
                    setattr(bpy.types.Object, path, bpy.props.FloatProperty(name=path))

                setattr(obj, path, v)

                s = clip.frame_start
                e = clip.frame_end+1

                if data_path.endswith('_start'):
                    k = cspy.actions.insert_keyframe(fcurve, s, v, needed=False, fast=True)
                elif data_path.endswith('_end'):
                    k = cspy.actions.insert_keyframe(fcurve, e, v, needed=False, fast=True)
                else:
                    k = cspy.actions.insert_keyframe(fcurve, s, v, needed=False, fast=True)
                    k = cspy.actions.insert_keyframe(fcurve, e, v, needed=False, fast=True)

        for data_path in updated_paths:
            fcurve = action.fcurves.find(data_path, index=-1)
            if fcurve is None:
                continue
            fcurve.update()

class UNITY_OT_root_motion_settings_to_curves(UNITY_OT_rm_curves, OPS_, Operator):
    """Adds animation curves for root motion settings."""
    bl_idname = "unity.root_motion_settings_to_curves"
    bl_label = "To Curves"

    def do_execute(self, context):
        obj = get_active_unity_object(context)
        action, clip = get_unity_action_and_clip(context)

        if action:
            self.process_action(context, action)

        return {'FINISHED'}

class UNITY_OT_root_motion_settings_to_curves_all(UNITY_OT_rm_curves, OPS_, Operator):
    """Adds animation curves for root motion settings to all actions."""
    bl_idname = "unity.root_motion_settings_to_curves_all"
    bl_label = "To Curves (All)"

    def do_execute(self, context):
        for action in bpy.data.actions:
            self.process_action(context, action)

        return {'FINISHED'}


class UNITY_OT_root_offset:
    operation: bpy.props.StringProperty('Operation')

    def do_execute(self, context):
        obj = get_active_unity_object(context)
        action, clip = get_unity_action_and_clip(context)

        root_bone_name = obj.data.hip_bone_name if self.operation == 'hip_start' or self.operation == 'hip_end' else obj.data.root_bone_name
        bone = obj.pose.bones.get(root_bone_name)

        self.set_offset(context, obj, action, clip, bone)

        return {'FINISHED'}

def print_loc(prefix, loc):
    string = '[{0}]  x:{1}m,  y:{2}m,  z:{3}m'.format(
        prefix,
        loc.x,
        loc.y, 
        loc.z)
    print(string)

def print_quat(prefix, quat, order = 'XYZ'):
    euler = quat.to_euler(order)
    string = '[{0}]  x:{1},  y:{2},  z:{3}'.format(
        prefix,
        math.degrees(euler.x), 
        math.degrees(euler.y), 
        math.degrees(euler.z))
    print(string)

class UNITY_OT_root_motion_reset(UNITY_OT_root_offset, OPS_, Operator):
    """Resets the offset property."""
    bl_idname = "unity.root_offset_to_reset"
    bl_label = "Reset"

    def set_offset(self, context, armature, action, clip, root_pose_bone):
        if self.operation == 'start':
            clip.root_node_start_location = [0,0,0]
            clip.root_node_start_rotation = [0,0,0]
            
        elif self.operation == 'settings':
            clip.root_motion_x_offset = 0
            clip.root_motion_y_offset = 0
            clip.root_motion_z_offset = 0
            clip.root_motion_rot_offset = 0
            
        elif self.operation == 'root_start':
            clip.root_bone_offset_location_start = [0,0,0]
            clip.root_bone_offset_rotation_start = [0,0,0]
            
        elif self.operation == 'hip_start':
            clip.hip_bone_offset_location_start = [0,0,0]
            clip.hip_bone_offset_rotation_start = [0,0,0]
            
        elif self.operation == 'root_end':
            clip.root_bone_offset_location_end = [0,0,0]
            clip.root_bone_offset_rotation_end = [0,0,0]
            
        elif self.operation == 'hip_end':
            clip.hip_bone_offset_location_end = [0,0,0]
            clip.hip_bone_offset_rotation_end = [0,0,0]
            

class UNITY_OT_root_motion_set(UNITY_OT_root_offset):
    def set_offset(self, context, armature, action, clip, pose_bone):
        pose_matrix, rest_matrix = self.get_matrices(context, armature, action, clip, pose_bone)
            
        pose_loc,pose_quat,_ = pose_matrix.decompose()
        rest_loc,rest_quat,_ = rest_matrix.decompose()

        diff_loc = rest_loc - pose_loc

        print_loc('POSE', pose_loc)
        print_loc('REST', rest_loc)
        print_loc('DIFF', diff_loc)

        diff_rot = pose_quat.rotation_difference(rest_quat)
        print_quat('POSE', pose_quat)
        print_quat('REST', rest_quat)
        print_quat('DIFF', diff_rot)

        diff_euler = diff_rot.to_euler('XYZ')

        set_loc, set_rot = clip.root_node_start_location, clip.root_node_start_rotation

        if self.operation == 'root_start':
            set_loc, set_rot = clip.root_bone_offset_location_start, clip.root_bone_offset_rotation_start
        elif self.operation == 'hip_start':
            set_loc, set_rot = clip.hip_bone_offset_location_start, clip.hip_bone_offset_rotation_start
        if self.operation == 'root_end':
            set_loc, set_rot = clip.root_bone_offset_location_end, clip.root_bone_offset_rotation_end
        elif self.operation == 'hip_end':
            set_loc, set_rot = clip.hip_bone_offset_location_end, clip.hip_bone_offset_rotation_end
        
        set_loc[0] = diff_loc[0]
        set_loc[1] = diff_loc[1]
        set_loc[2] = diff_loc[2]

        set_rot[0] = diff_euler.x
        set_rot[1] = diff_euler.y
        set_rot[2] = diff_euler.z

class UNITY_OT_root_motion_rest(UNITY_OT_root_motion_set, OPS_, Operator):
    """Sets the root motion offset to return the root to its rest position."""
    bl_idname = "unity.root_offset_to_rest"
    bl_label = "To Rest"

    def  get_matrices(self, context, armature, action, clip, pose_bone):
        if self.operation == 'start':
            pose_matrix = armature.data.original_root_node.matrix_world
            rest_matrix = armature.matrix_world
        elif self.operation == 'root_start' or self.operation == 'root_end':
            pose_matrix = get_pose_bone_matrix_world(armature, pose_bone.name)
            rest_matrix = get_pose_bone_rest_matrix_world(armature, pose_bone.name)
        elif self.operation == 'hip_start' or self.operation == 'hip_end':
            pose_matrix = get_pose_bone_matrix_world(armature, pose_bone.name)
            rest_matrix = get_pose_bone_rest_matrix_world(armature, pose_bone.name)

        return pose_matrix, rest_matrix
            
        

class UNITY_OT_root_motion_cursor(UNITY_OT_root_motion_set, OPS_, Operator):
    """Sets the root motion offset to return the root to the cursor."""
    bl_idname = "unity.root_offset_to_cursor"
    bl_label = "To Cursor"

    def  get_matrices(self, context, armature, action, clip, pose_bone):

        if self.operation == 'start':
            pose_matrix = armature.data.original_root_node.matrix_world
        elif self.operation == 'root_start' or self.operation == 'root_end':
            pose_matrix = get_pose_bone_matrix_world(armature, root_pose_bone.name)
        elif self.operation == 'hip_start' or self.operation == 'hip_end':
            pose_matrix = armature.data.hip_bone_offset.matrix_world

        cursor = context.scene.cursor
        rest_matrix = cursor.matrix

        return pose_matrix, rest_matrix
            
