import socket

RECV_BYTES = 2048
PORT_RANGE = (1, 65535)


# Sursa UDP neblocanta
class UdpDatagramSource:
    # Valideaza portul, deschide socket
    def __init__(self, port, host=""):
        if not PORT_RANGE[0] <= port <= PORT_RANGE[1]:
            raise ValueError(f"portul trebuie sa fie intre {PORT_RANGE[0]} si {PORT_RANGE[1]}, nu {port}")
        self.port = port
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self._sock.bind((host, port))
        except OSError as error:
            self._sock.close()
            raise OSError(f"Nu pot asculta pe UDP {port}: {error}") from error
        self._sock.setblocking(False)

    # Toate datagramele care asteapta
    def drain(self):
        datagrams = []
        while True:
            try:
                datagrams.append(self._sock.recv(RECV_BYTES))
            except BlockingIOError:
                return tuple(datagrams)

    # Inchide socket-ul
    def close(self):
        self._sock.close()
