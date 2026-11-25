import numpy as np

# Numarul de subpurtatoare
COUNT = 64
DATA_COUNT = 52


# Blocheaza scrierea in array
def _read_only(values):
    values.setflags(write=False)
    return values


# Ordinea k din buffer
BUFFER_INDICES = _read_only(np.concatenate([np.arange(0, 32), np.arange(-32, 0)]))
# Subpurtatoarele LLTF cu energie
DATA_INDICES = _read_only(np.concatenate([np.arange(-26, 0), np.arange(1, 27)]))
DATA_POSITIONS = _read_only(np.array([int(np.flatnonzero(k == BUFFER_INDICES)[0]) for k in DATA_INDICES]))
