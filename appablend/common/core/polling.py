import bpy


class CONTEXT_MODES:
    EDIT_MESH = "EDIT_MESH"
    EDIT_CURVE = "EDIT_CURVE"
    EDIT_SURFACE = "EDIT_SURFACE"
    EDIT_TEXT = "EDIT_TEXT"
    EDIT_ARMATURE = "EDIT_ARMATURE"
    EDIT_METABALL = "EDIT_METABALL"
    EDIT_LATTICE = "EDIT_LATTICE"
    POSE = "POSE"
    SCULPT = "SCULPT"
    PAINT_WEIGHT = "PAINT_WEIGHT"
    PAINT_VERTEX = "PAINT_VERTEX"
    PAINT_TEXTURE = "PAINT_TEXTURE"
    PARTICLE = "PARTICLE"
    OBJECT = "OBJECT"
    PAINT_GPENCIL = "PAINT_GPENCIL"
    EDIT_GPENCIL = "EDIT_GPENCIL"
    SCULPT_GPENCIL = "SCULPT_GPENCIL"
    WEIGHT_GPENCIL = "WEIGHT_GPENCIL"
    VERTEX_GPENCIL = "VERTEX_GPENCIL"


class OBJECT_TYPES:
    MESH = "MESH"
    CURVE = "CURVE"
    SURFACE = "SURFACE"
    META = "META"
    FONT = "FONT"
    HAIR = "HAIR"
    POINTCLOUD = "POINTCLOUD"
    VOLUME = "VOLUME"
    GPENCIL = "GPENCIL"
    ARMATURE = "ARMATURE"
    LATTICE = "LATTICE"
    EMPTY = "EMPTY"
    LIGHT = "LIGHT"
    LIGHT_PROBE = "LIGHT_PROBE"
    CAMERA = "CAMERA"
    SPEAKER = "SPEAKER"


class DOIF:
    class ACTIVE:
        @classmethod
        def OBJECT(cls, c):
            return c.active_object is not None

        class TYPE:
            @classmethod
            def IS(cls, c, data_type):
                return DOIF.ACTIVE.OBJECT(c) and c.active_object.type == data_type

            @classmethod
            def IS_ARMATURE(cls, c):
                return cls.IS(c, OBJECT_TYPES.ARMATURE)

            @classmethod
            def IS_CURVE(cls, c):
                return cls.IS(c, OBJECT_TYPES.CURVE)

            @classmethod
            def IS_MESH(cls, c):
                return cls.IS(c, OBJECT_TYPES.MESH)

            @classmethod
            def IS_EMPTY(cls, c):
                return cls.IS(c, OBJECT_TYPES.EMPTY)

        class HAS:
            @classmethod
            def DATA(cls, c):
                return DOIF.ACTIVE.OBJECT(c) and c.active_object.data is not None

            @classmethod
            def ANIMATION_DATA(cls, c):
                return (
                    DOIF.ACTIVE.OBJECT(c) and c.active_object.animation_data is not None
                )

            @classmethod
            def ACTION(cls, c):
                return (
                    cls.ANIMATION_DATA(c)
                    and c.active_object.animation_data.action is not None
                )

            @classmethod
            def _UNITY_CLIPS(cls, c):
                return (
                    cls.ACTION(c)
                    and c.active_object.animation_data.action.unity_clips is not None
                )

            @classmethod
            def NO_UNITY_CLIPS(cls, c):
                return not cls._UNITY_CLIPS(c)

            @classmethod
            def ONE_UNITY_CLIP(cls, c):
                return (
                    cls._UNITY_CLIPS(c)
                    and len(c.active_object.animation_data.action.unity_clips) == 1
                )

            @classmethod
            def SOME_UNITY_CLIPS(cls, c):
                return (
                    cls._UNITY_CLIPS(c)
                    and len(c.active_object.animation_data.action.unity_clips) > 0
                )

            @classmethod
            def MULTIPLE_UNITY_CLIPS(cls, c):
                return (
                    cls._UNITY_CLIPS(c)
                    and len(c.active_object.animation_data.action.unity_clips) > 1
                )

            @classmethod
            def SPLIT_UNITY_CLIPS(cls, c):
                return (
                    cls._UNITY_CLIPS(c)
                    and c.active_object.animation_data.action.unity_clips[
                        0
                    ].source_action
                    is not None
                )

            @classmethod
            def BONES(cls, c):
                return (
                    DOIF.ACTIVE.TYPE.IS_ARMATURE(c)
                    and len(c.active_object.data.bones) > 0
                )

            @classmethod
            def ANIM_RET(cls, c):
                return (
                    DOIF.ACTIVE.OBJECT(c)
                    and c.active_object.anim_ret.source != ""
                    and DOIF.ACTIVE.POSE_BONE(c)
                )

        @classmethod
        def POSE_BONE(cls, c):
            return c.active_pose_bone

    class MODE:
        @classmethod
        def IS(cls, c, mode):
            return c.mode == mode

        @classmethod
        def IS_EDIT_MESH(cls, c):
            return cls.IS(c, CONTEXT_MODES.EDIT_MESH)

        @classmethod
        def IS_EDIT_CURVE(cls, c):
            return cls.IS(c, CONTEXT_MODES.EDIT_CURVE)

        @classmethod
        def IS_EDIT_SURFACE(cls, c):
            return cls.IS(c, CONTEXT_MODES.EDIT_SURFACE)

        @classmethod
        def IS_EDIT_TEXT(cls, c):
            return cls.IS(c, CONTEXT_MODES.EDIT_TEXT)

        @classmethod
        def IS_EDIT_ARMATURE(cls, c):
            return cls.IS(c, CONTEXT_MODES.EDIT_ARMATURE)

        @classmethod
        def IS_EDIT_METABALL(cls, c):
            return cls.IS(c, CONTEXT_MODES.EDIT_METABALL)

        @classmethod
        def IS_EDIT_LATTICE(cls, c):
            return cls.IS(c, CONTEXT_MODES.EDIT_LATTICE)

        @classmethod
        def IS_POSE(cls, c):
            return cls.IS(c, CONTEXT_MODES.POSE)

        @classmethod
        def IS_SCULPT(cls, c):
            return cls.IS(c, CONTEXT_MODES.SCULPT)

        @classmethod
        def IS_PAINT_WEIGHT(cls, c):
            return cls.IS(c, CONTEXT_MODES.PAINT_WEIGHT)

        @classmethod
        def IS_PAINT_VERTEX(cls, c):
            return cls.IS(c, CONTEXT_MODES.PAINT_VERTEX)

        @classmethod
        def IS_PAINT_TEXTURE(cls, c):
            return cls.IS(c, CONTEXT_MODES.PAINT_TEXTURE)

        @classmethod
        def IS_PARTICLE(cls, c):
            return cls.IS(c, CONTEXT_MODES.PARTICLE)

        @classmethod
        def IS_OBJECT(cls, c):
            return cls.IS(c, CONTEXT_MODES.OBJECT)

        @classmethod
        def IS_PAINT_GPENCIL(cls, c):
            return cls.IS(c, CONTEXT_MODES.PAINT_GPENCIL)

        @classmethod
        def IS_EDIT_GPENCIL(cls, c):
            return cls.IS(c, CONTEXT_MODES.EDIT_GPENCIL)

        @classmethod
        def IS_SCULPT_GPENCIL(cls, c):
            return cls.IS(c, CONTEXT_MODES.SCULPT_GPENCIL)

        @classmethod
        def IS_WEIGHT_GPENCIL(cls, c):
            return cls.IS(c, CONTEXT_MODES.WEIGHT_GPENCIL)

        @classmethod
        def IS_VERTEX_GPENCIL(cls, c):
            return cls.IS(c, CONTEXT_MODES.VERTEX_GPENCIL)

    class ANIM_RET:
        @classmethod
        def IS_NOT_FROZEN(cls, c):
            return (
                DOIF.ACTIVE.HAS.ANIM_RET(c) and not c.active_object.anim_ret.is_frozen
            )

    class DATA:
        @classmethod
        def ACTIONS(cls, c):
            return len(bpy.data.actions) > 0

        @classmethod
        def ARMATURES(cls, c):
            return len(bpy.data.armatures) > 0

    class UNITY:
        class TARGET:
            @classmethod
            def _get_unity_target(cls, c):
                from appablend.common.models.unity import get_unity_target

                return get_unity_target(c)

            @classmethod
            def SET(cls, c):
                return cls._get_unity_target(c)

            class HAS:
                @classmethod
                def ACTION(cls, c):
                    uo = cls._get_unity_target(c)
                    return (
                        DOIF.UNITY.TARGET.SET(c)
                        and uo.animation_data
                        and uo.animation_data.action
                    )

                @classmethod
                def _UNITY_CLIPS(cls, c):
                    uo = cls._get_unity_target(c)
                    return (
                        cls.ACTION(c)
                        and uo.animation_data.action.unity_clips is not None
                    )

                @classmethod
                def NO_UNITY_CLIPS(cls, c):
                    return not cls._UNITY_CLIPS(c)

                @classmethod
                def ONE_UNITY_CLIP(cls, c):
                    uo = cls._get_unity_target(c)
                    return (
                        cls._UNITY_CLIPS(c)
                        and len(uo.animation_data.action.unity_clips) == 1
                    )

                @classmethod
                def SOME_UNITY_CLIPS(cls, c):
                    uo = cls._get_unity_target(c)
                    return (
                        cls._UNITY_CLIPS(c)
                        and len(uo.animation_data.action.unity_clips) > 0
                    )

                @classmethod
                def MULTIPLE_UNITY_CLIPS(cls, c):
                    uo = cls._get_unity_target(c)
                    return (
                        cls._UNITY_CLIPS(c)
                        and len(uo.animation_data.action.unity_clips) > 1
                    )

                @classmethod
                def SPLIT_UNITY_CLIPS(cls, c):
                    uo = cls._get_unity_target(c)
                    return (
                        cls._UNITY_CLIPS(c)
                        and uo.animation_data.action.unity_clips[0].source_action
                        is not None
                    )

            class IS:
                @classmethod
                def NOT_PROTECTED(cls, c):
                    uo = cls._get_unity_target(c)
                    DOIF.UNITY.TARGET.HAS.ACTION(
                        c
                    ) and not uo.animation_data.action.unity_metadata.clips_protected

        class SHEETS:
            @classmethod
            def HAS_PATH(cls, c):
                return c.scene.unity_settings.sheet_dir_path != ""

        class KEYS:
            @classmethod
            def HAS_PATH(cls, c):
                return c.scene.unity_settings.key_dir_path != ""

        class MODE:
            @classmethod
            def IS(cls, c, mode):
                return c.scene.unity_settings.mode == mode

            @classmethod
            def SCENE(cls, c):
                return DOIF.UNITY.TARGET.SET(c) and cls.IS(c, "SCENE")

            @classmethod
            def TARGET(cls, c):
                return DOIF.UNITY.TARGET.SET(c) and cls.IS(c, "TARGET")

            @classmethod
            def ACTIVE(cls, c):
                return DOIF.UNITY.TARGET.SET(c) and cls.IS(c, "ACTIVE")
