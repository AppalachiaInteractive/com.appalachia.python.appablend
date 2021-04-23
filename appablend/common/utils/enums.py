def create_enum(enum_items):
    keys = set()
    for enum_item_key in enum_items:
        keys.add(enum_item_key)

    enums = []
    for key in keys:
        item = (key, key.capitalize(), key.capitalize())
        enums.append(item)

    return enums


def create_enum_dict(enum_items):

    enums = []
    for description in enum_items:
        key = enum_items[description]
        item = (key, description, description)
        enums.append(item)

    return enums
