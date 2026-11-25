import socket
import time

import pytest

from csi.infrastructure.udp_source import UdpDatagramSource


# Port UDP liber local
def free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


# UDP: drain citeste tot
def test_drain_returns_all_waiting_datagrams_then_nothing():
    port = free_port()
    source = UdpDatagramSource(port, host="127.0.0.1")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender:
            sender.sendto(b"a", ("127.0.0.1", port))
            sender.sendto(b"bb", ("127.0.0.1", port))
        deadline = time.monotonic() + 1.0
        received = ()
        while len(received) < 2 and time.monotonic() < deadline:
            received += source.drain()
        assert received == (b"a", b"bb")
        assert source.drain() == ()
    finally:
        source.close()


# UDP: port invalid respins
@pytest.mark.parametrize("port", [0, 65536, -5])
def test_invalid_port_is_refused(port):
    with pytest.raises(ValueError):
        UdpDatagramSource(port)


# UDP: port ocupat, mesaj clar
def test_busy_port_gives_readable_error():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as holder:
        holder.bind(("127.0.0.1", 0))
        port = holder.getsockname()[1]
        with pytest.raises(OSError, match=f"Nu pot asculta pe UDP {port}"):
            UdpDatagramSource(port, host="127.0.0.1")
