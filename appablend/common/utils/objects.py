def copy_from_to(f, t):
    try:
        from_props = set(dir(f))
        to_props = set(dir(t))

        common_props = [
            prop
            for prop in from_props.intersection(to_props)
            if (
                not prop.startswith("_")
                and not prop.startswith("bl_")
                and not prop.startswith("rna_")
                and not prop
                in set(
                    ["int", "float", "bool", "int_array", "float_array", "bool_array"]
                )
                and not callable(getattr(f, prop))
            )
        ]

        for prop in common_props:
            val = getattr(f, prop)

            copy = getattr(val, "copy_from", None)

            if copy and callable(copy):
                val_to = getattr(t, prop)
                copy_to = getattr(val_to, "copy_from", None)

                copy_to(val)

            else:
                setattr(t, prop, val)
    except Exception as e:
        namef = getattr(f, "name", str(f))
        namet = getattr(t, "name", str(t))

        print("copy_from_to: [{0}] to [{1}]: {2}".format(namef, namet, e))
        raise

def copy_from_existing(obj1, obj2, prop_names, delete):
    for prop_name in prop_names:
        if hasattr(obj2, prop_name):
            value = getattr(obj2, prop_name)
            setattr(obj1, prop_name, value)
            if delete:
                try:
                    delattr(obj2, prop_name)
                except AttributeError:
                    pass
