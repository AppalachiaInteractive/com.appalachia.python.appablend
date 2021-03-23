
class _Units:
    NONE = 'NONE'
    LENGTH = 'LENGTH'
    AREA = 'AREA'
    VOLUME = 'VOLUME'
    ROTATION = 'ROTATION'
    TIME = 'TIME'
    VELOCITY = 'VELOCITY'
    ACCELERATION = 'ACCELERATION'
    MASS = 'MASS'
    CAMERA = 'CAMERA'
    POWER = 'POWER'
class _SubtypeNumeric:
    NONE = 'NONE'
    PIXEL = 'PIXEL'
    UNSIGNED = 'UNSIGNED'
    PERCENTAGE = 'PERCENTAGE'
    FACTOR = 'FACTOR'
    ANGLE = 'ANGLE'
    TIME = 'TIME'
    DISTANCE = 'DISTANCE'
    DISTANCE_CAMERA = 'DISTANCE_CAMERA'
    POWER = 'POWER'
    TEMPERATURE = 'TEMPERATURE'
class _SubtypeVector:
    NONE = 'NONE'
    COLOR = 'COLOR'
    TRANSLATION = 'TRANSLATION'
    DIRECTION = 'DIRECTION'
    VELOCITY = 'VELOCITY'
    ACCELERATION = 'ACCELERATION'
    MATRIX = 'MATRIX'
    EULER = 'EULER'
    QUATERNION = 'QUATERNION'
    AXISANGLE = 'AXISANGLE'
    XYZ = 'XYZ'
    XYZ_LENGTH = 'XYZ_LENGTH'
    COLOR_GAMMA = 'COLOR_GAMMA'
    COORDINATES = 'COORDINATES'
    LAYER = 'LAYER'
    LAYER_MEMBER = 'LAYER_MEMBER'

class FloatProperty:
    class Subtypes (_SubtypeNumeric):
        pass
    class Units(_Units):
        pass


class FloatVectorProperty:
    class Subtypes (_SubtypeVector):
        pass

    class Units(_Units):
        pass

class IntProperty:
    class Subtypes (_SubtypeNumeric):
        pass

class StringProperty:
    class Subtypes:
        FILE_PATH = 'FILE_PATH'
        DIR_PATH = 'DIR_PATH'
        FILE_NAME = 'FILE_NAME'
        BYTE_STRING = 'BYTE_STRING'
        PASSWORD = 'PASSWORD'
        NONE = 'NONE'







