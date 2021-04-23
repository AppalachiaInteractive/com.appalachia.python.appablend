def reverse_index(coll):
    return reversed(range(len(coll)))


def reverse_enumerate(coll):
    indices = reverse_index(coll)

    return [(index, coll[index]) for index in indices]
