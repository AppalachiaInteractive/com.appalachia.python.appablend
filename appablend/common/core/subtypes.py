from appablend.common.core.enums import (subtype_numeric, subtype_string,
                                         subtype_vector, units)


class ST_FloatProperty:
    class Subtypes(subtype_numeric):
        pass

    class Units(units):
        pass


class ST_FloatVectorProperty:
    class Subtypes(subtype_vector):
        pass

    class Units(units):
        pass


class ST_IntProperty:
    class Subtypes(subtype_numeric):
        pass


class ST_StringProperty:
    class Subtypes(subtype_string):
        pass
