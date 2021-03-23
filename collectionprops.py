import bpy

class _SortKey():
    def __init__(self):
        self.key = ''
        self.value = None
        self.index = 0

def sort(collection, prop='name', asc=True):
    n = len(collection)

    swapped = True

    while(swapped):
        swapped=False
        for i in range(n-1):
            c1 = collection[i]
            c2 = collection[i+1]

            c1v = getattr(c1, prop)
            c2v = getattr(c2, prop)

            if asc and c1v > c2v:
                swapped=True
                collection.move(i, i+1)
            elif not asc and c1v < c2v:
                collection.move(i, i+1)



