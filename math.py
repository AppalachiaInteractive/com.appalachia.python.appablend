import bgl, blf, bmesh, bpy, gpu
from mathutils import Matrix, Vector


def angle_signed(
        a: Vector,
        b: Vector,
        c: Vector,
):
    v1 = a - b
    v2 = c - b

    return Vector.angle_signed(v1, v2)


def smoothstep_V(edge0: Vector, edge1: Vector, x: float) -> Vector:
    t = smoothstep(x)
    return Vector([
        lerp(edge0[0], edge1[0], t),
        lerp(edge0[1], edge1[1], t),
        lerp(edge0[2], edge1[2], t),
    ])


def smootherstep_V(edge0: Vector, edge1: Vector, x: float) -> Vector:
    t = smootherstep(x)
    return Vector([
        lerp(edge0[0], edge1[0], t),
        lerp(edge0[1], edge1[1], t),
        lerp(edge0[2], edge1[2], t),
    ])


def smoothstep(x: float) -> float:
    x = clamp(x, 0.0, 1.0)
    # Evaluate polynomial
    return x * x * (3.0 - 2.0 * x)


def smootherstep(x: float) -> float:
    x = clamp(x, 0.0, 1.0)
    # Evaluate polynomial
    return x * x * x * (x * (x * 6.0 - 15.0) + 10.0)


def clamp(
        x: float,
        lowerlimit: float,
        upperlimit: float
) -> float:
    if x < lowerlimit:
        x = lowerlimit
    if x > upperlimit:
        x = upperlimit
    return x


def inv_scale(v1: Vector, v2: Vector) -> Vector:
    return Vector([
        v1[0] / v2[0],
        v1[1] / v2[1],
        v1[2] / v2[2]
    ])


def scale(v1: Vector, v2: Vector) -> Vector:
    return Vector([
        v1[0] * v2[0],
        v1[1] * v2[1],
        v1[2] * v2[2]
    ])


def lerp(
        f1: float,
        f2: float,
        t: float
 ) -> float:
    return f1 + ((f2 - f1) * t)


def interpolate(
        v1: Vector,
        v2: Vector,
        t: float
                ) -> Vector:
    return Vector(
        [
            lerp(v1[0], v2[0], t[0]),
            lerp(v1[1], v2[1], t[1]),
            lerp(v1[2], v2[2], t[2])
        ])


def distance(v1, v2):
    d = (Vector(v1) - Vector(v2)).length
    return d


def average_v2(v1, v2):
    return (v1 + v2) / 2.0


def average_v3(v1, v2, v3):
    return (v1 + v2 + v3) / 3.0


def closer_v2(ref, v1, v2):
    d1 = (Vector(ref) - Vector(v1)).length
    d2 = (Vector(ref) - Vector(v2)).length

    if d1 < d2:
        return v1
    else:
        return v2


def further_v2(ref, v1, v2):
    d1 = (Vector(ref) - Vector(v1)).length
    d2 = (Vector(ref) - Vector(v2)).length

    if d1 > d2:
        return v1
    else:
        return v2


def further_v3(ref, v1, v2, v3):
    d1 = (Vector(ref) - Vector(v1)).length
    d2 = (Vector(ref) - Vector(v2)).length
    d3 = (Vector(ref) - Vector(v3)).length

    if d1 > d2 and d1 > d3:
        return v1
    elif d2 > d1 and d2 > d3:
        return v2
    else:
        return v3

