
from memory_api import make_key, node_id_from_key, neighbors6, key_from_node_id

k = make_key(1, -2, 0, 3)
print("Key:", k)
nid = node_id_from_key(k)
print("NodeID:", nid)
print("Neighbors:", neighbors6(nid))
print("Back to key:", key_from_node_id(nid))
