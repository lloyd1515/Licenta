import os
import threading

import numpy as np
import pytest

from csi.packets import PACKET_BYTES, Packet, encode_packet, open_udp_socket, parse_datagram
from csi.record import receive
from csi.udp_sim import send, simulated_packets

LOCALHOST = "127.0.0.1"
SIM_SPEED = 10.0
SIM_DURATION_S = 20.0
RECEIVE_MARGIN_S = 1.0
NODE_IDS = [1, 2, 3]
SAMPLES_PER_NODE = 5000


def _packet(seq=7):
    csi = np.arange(52) - 26 + 1j * (26 - np.arange(52))
    return Packet(node_id=2, rssi_dbm=-61, timestamp_us=123_456_789, seq=seq, csi=csi)


def test_encoded_packet_is_138_bytes_and_round_trips():
    packet = _packet()
    raw = encode_packet(packet)
    assert len(raw) == PACKET_BYTES == 138
    [parsed] = parse_datagram(raw)
    assert (parsed.node_id, parsed.rssi_dbm, parsed.timestamp_us, parsed.seq) == (2, -61, 123_456_789, 7)
    np.testing.assert_array_equal(parsed.csi, packet.csi)


def test_encode_clips_values_outside_int8():
    packet = Packet(1, -40, 0, 0, np.full(52, 500 - 500j))
    [parsed] = parse_datagram(encode_packet(packet))
    np.testing.assert_array_equal(parsed.csi, np.full(52, 127 - 128j))


@pytest.mark.parametrize("data", [b"", b"\x5a\xa5", b"\x00" * PACKET_BYTES, encode_packet(_packet())[:-1]])
def test_parse_datagram_rejects_short_or_unaligned_data(data):
    assert parse_datagram(data) == []


def test_parse_datagram_reads_several_packets():
    data = encode_packet(_packet(1)) + encode_packet(_packet(2))
    assert [packet.seq for packet in parse_datagram(data)] == [1, 2]


def _receive_simulation():
    sock = open_udp_socket(0, timeout_s=0.1)
    port = sock.getsockname()[1]
    sender = threading.Thread(target=send, args=(LOCALHOST, port, SIM_SPEED))
    sender.start()
    try:
        packets_by_node = receive(sock, SIM_DURATION_S / SIM_SPEED + RECEIVE_MARGIN_S)
    finally:
        sender.join()
        sock.close()
    return packets_by_node


def test_simulated_nodes_deliver_every_packet_over_udp():
    packets_by_node = _receive_simulation()
    assert [packets[0].node_id for packets in packets_by_node] == NODE_IDS
    assert [len(packets) for packets in packets_by_node] == [SAMPLES_PER_NODE] * len(NODE_IDS)

    expected = {}
    for _, packet in simulated_packets():
        expected.setdefault(packet.node_id, []).append(encode_packet(packet))
    for packets in packets_by_node:
        assert [encode_packet(p) for p in packets] == expected[packets[0].node_id]


def test_gui_live_source_reaches_alarm_from_simulated_udp_nodes():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PyQt6.QtCore import QEventLoop, QTimer
    from PyQt6.QtWidgets import QApplication

    from csi.fall_detector import FallState
    from csi.gui.frame_source import FrameSource

    app = QApplication.instance() or QApplication([])
    probe = open_udp_socket(0)
    port = probe.getsockname()[1]
    probe.close()

    source = FrameSource(live=True, udp_port=port, fps=20.0, recording_path=None)
    states = []
    messages = []
    source.frame_ready.connect(lambda frame: states.append(frame.state))
    source.status_changed.connect(messages.append)
    source.start()
    sender = threading.Thread(target=send, args=(LOCALHOST, port, SIM_SPEED))
    loop = QEventLoop()
    QTimer.singleShot(200, sender.start)
    QTimer.singleShot(int((SIM_DURATION_S / SIM_SPEED + 2 * RECEIVE_MARGIN_S) * 1000), loop.quit)
    loop.exec()
    sender.join()
    source.stop()
    app.processEvents()

    assert any("UDP port" in message for message in messages)
    assert FallState.ALARM in states
