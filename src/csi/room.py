import numpy as np

SPEED_OF_LIGHT_M_S = 3.0e8
CENTER_FREQ_HZ = 2.437e9
WAVELENGTH_M = SPEED_OF_LIGHT_M_S / CENTER_FREQ_HZ
SUBCARRIER_SPACING_HZ = 312.5e3
SUBCARRIER_COUNT = 52
SUBCARRIER_INDICES = tuple(i for i in range(-26, 27) if i != 0)
ROOM_SIZE_M = 5.0
ROOM_HALF_SIZE_M = ROOM_SIZE_M / 2
NODE_POSITIONS_M = {1: (-2.0, 1.2), 2: (2.0, 1.2), 3: (0.0, -2.0)}
LINKS = ((1, 2), (2, 3), (3, 1))
DOPPLER_REFERENCE_HZ = 35.0


def link_name(link):
    return f"Link {link[0]}-{link[1]}"


def extra_path_m(point_xy, link):
    tx = np.array(NODE_POSITIONS_M[link[0]])
    rx = np.array(NODE_POSITIONS_M[link[1]])
    point = np.asarray(point_xy, dtype=float)
    reflected = np.linalg.norm(point - tx, axis=-1) + np.linalg.norm(point - rx, axis=-1)
    return reflected - np.linalg.norm(rx - tx)
