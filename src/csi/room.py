import numpy as np

SPEED_OF_LIGHT_M_S = 3.0e8  # viteza luminii, m/s
CENTER_FREQ_HZ = 2.437e9  # Wi-Fi canal 6
WAVELENGTH_M = SPEED_OF_LIGHT_M_S / CENTER_FREQ_HZ  # lungime de undă ~12.3 cm
SUBCARRIER_SPACING_HZ = 312.5e3  # distanța între subpurtătoare
SUBCARRIER_COUNT = 52  # subpurtătoare folosite
SUBCARRIER_INDICES = tuple(i for i in range(-26, 27) if i != 0)  # indici -26..26, fără 0
ROOM_SIZE_M = 5.0  # latura camerei pătrate
ROOM_HALF_SIZE_M = ROOM_SIZE_M / 2  # centrul camerei = (0, 0)
NODE_POSITIONS_M = {1: (-2.0, 1.2), 2: (2.0, 1.2), 3: (0.0, -2.0)}  # pozițiile celor 3 ESP32
LINKS = ((1, 2), (2, 3), (3, 1))  # perechi emițător → receptor
DOPPLER_REFERENCE_HZ = 35.0  # prag Doppler pentru cădere


def link_name(link):  # text: "Link 1-2"
    return f"Link {link[0]}-{link[1]}"


def extra_path_m(point_xy, link):  # drum în plus prin reflexie
    tx = np.array(NODE_POSITIONS_M[link[0]])  # poziția emițătorului
    rx = np.array(NODE_POSITIONS_M[link[1]])  # poziția receptorului
    point = np.asarray(point_xy, dtype=float)  # poziția persoanei
    reflected = np.linalg.norm(point - tx, axis=-1) + np.linalg.norm(point - rx, axis=-1)  # TX→persoană→RX
    return reflected - np.linalg.norm(rx - tx)  # minus drumul direct
