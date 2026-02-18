
def enc7(v: int) -> int:
    if v < -3 or v > 3:
        raise ValueError("tick out of range [-3,3]")
    return v + 3

def dec7(d: int) -> int:
    if d < 0 or d > 6:
        raise ValueError("digit out of range [0,6]")
    return d - 3

def shell_inf(x: int, y: int, z: int) -> int:
    return max(abs(x), abs(y), abs(z))

def make_key(t: int, x: int, y: int, z: int) -> str:
    dx, dy, dz = enc7(x), enc7(y), enc7(z)
    r = shell_inf(x, y, z)
    if t < 0 or t > 2: raise ValueError("transform must be 0..2")
    return f"T{t}-D{dx}{dy}{dz}-S{r}"

def parse_key(key: str):
    t = int(key[1])
    dx, dy, dz = int(key[5]), int(key[6]), int(key[7])
    r = int(key[11])
    x, y, z = dec7(dx), dec7(dy), dec7(dz)
    return t, x, y, z, r

def node_id_from_parts(t:int, dx:int, dy:int, dz:int) -> int:
    cell = dx*49 + dy*7 + dz
    return t*343 + cell

def node_id_from_key(key: str) -> int:
    t, x, y, z, _ = parse_key(key)
    dx, dy, dz = enc7(x), enc7(y), enc7(z)
    return node_id_from_parts(t, dx, dy, dz)

def parts_from_node_id(node_id: int):
    t = node_id // 343
    cell = node_id % 343
    dx = cell // 49
    rem = cell % 49
    dy = rem // 7
    dz = rem % 7
    x, y, z = dec7(dx), dec7(dy), dec7(dz)
    return t, x, y, z

def key_from_node_id(node_id: int) -> str:
    t, x, y, z = parts_from_node_id(node_id)
    return make_key(t, x, y, z)

def neighbors6(node_id: int):
    t, x, y, z = parts_from_node_id(node_id)
    res = []
    for xx, yy, zz in ((x-1,y,z),(x+1,y,z),(x,y-1,z),(x,y+1,z),(x,y,z-1),(x,y,z+1)):
        if -3 <= xx <= 3 and -3 <= yy <= 3 and -3 <= zz <= 3:
            dx, dy, dz = enc7(xx), enc7(yy), enc7(zz)
            res.append(node_id_from_parts(t, dx, dy, dz))
    return res
