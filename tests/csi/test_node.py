import dataclasses

import pytest

from csi.domain.events import NodeDiscovered, NodeRestarted
from csi.domain.node import Node
from csi.domain.node_id import NodeId
from tests.csi.factories import frame

ID = NodeId(3)


# Trimite mai multe cadre
def feed(node, *frames):
    events = []
    for f in frames:
        node, new = node.record(f)
        events.extend(new)
    return node, events


# Nod: primul cadru il descopera
def test_first_frame_discovers_the_node():
    node, events = Node(ID).record(frame(seq=5, timestamp_us=100))
    assert events == (NodeDiscovered(ID),)
    assert (node.frames_received, node.frames_lost, node.elapsed_us) == (1, 0, 0)


# Nod: record nu schimba originalul
def test_record_does_not_change_the_original_node():
    original = Node(ID)
    original.record(frame())
    assert original == Node(ID)
    with pytest.raises(dataclasses.FrozenInstanceError):
        original.frames_lost = 1


# Nod: golul seq numara pierderi
def test_seq_gap_counts_lost_frames():
    node, _ = feed(Node(ID), frame(seq=1, timestamp_us=0), frame(seq=4, timestamp_us=30_000))
    assert node.frames_lost == 2


# Nod: seq trece 65535->0
def test_seq_wraps_from_65535_to_0_without_loss():
    node, _ = feed(Node(ID), frame(seq=65535, timestamp_us=0), frame(seq=0, timestamp_us=10_000))
    assert node.frames_lost == 0


# Nod: timpul trece peste 2^32
def test_timestamp_wrap_keeps_elapsed_time_growing():
    last = (1 << 32) - 4_000
    node, events = feed(Node(ID), frame(seq=0, timestamp_us=last), frame(seq=1, timestamp_us=6_000))
    assert node.elapsed_us == 10_000
    assert events == [NodeDiscovered(ID)]


# Nod: salt inapoi inseamna repornire
def test_large_backward_jump_is_a_restart():
    node, events = feed(Node(ID), frame(seq=900, timestamp_us=600_000_000), frame(seq=0, timestamp_us=3_000_000))
    assert events == [NodeDiscovered(ID), NodeRestarted(ID)]
    assert node.elapsed_us == 0
    assert node.last_frame.seq == 0
    node, _ = node.record(frame(seq=1, timestamp_us=3_010_000))
    assert (node.frames_lost, node.elapsed_us) == (0, 10_000)


# Nod: cadru intarziat, timp neschimbat
def test_late_frame_is_counted_but_does_not_move_time_back():
    node, events = feed(Node(ID), frame(seq=0, timestamp_us=0), frame(seq=2, timestamp_us=20_000),
                        frame(seq=1, timestamp_us=10_000))
    assert events == [NodeDiscovered(ID)]
    assert node.frames_received == 3
    assert node.elapsed_us == 20_000
    assert node.last_frame.seq == 2


# Nod: cadru strain respins
def test_frame_from_another_node_is_refused():
    with pytest.raises(ValueError):
        Node(ID).record(frame(node=4))
