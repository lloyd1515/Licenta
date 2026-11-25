import pytest

from csi.application.ingest import IngestFrames, IngestResult
from csi.application.throughput import Throughput
from csi.domain.events import NodeDiscovered
from csi.domain.node_id import NodeId
from csi.infrastructure.memory_node_repository import InMemoryNodeRepository
from tests.csi.factories import wire_packet


# Ingest: decodare, depozit, evenimente
def test_ingest_decodes_updates_repository_and_reports_events():
    repo = InMemoryNodeRepository()
    ingest = IngestFrames(repo)
    result = ingest([wire_packet(node_id=3, seq=0), b"junk", wire_packet(node_id=4, seq=0),
                     wire_packet(node_id=3, seq=3, timestamp_us=40_000)])
    assert [f.node_id for f in result.frames] == [NodeId(3), NodeId(4), NodeId(3)]
    assert result.events == (NodeDiscovered(NodeId(3)), NodeDiscovered(NodeId(4)))
    assert [n.node_id for n in result.nodes] == [NodeId(3), NodeId(4)]
    assert repo.get(NodeId(3)).frames_lost == 2
    assert [n.node_id for n in repo.all()] == [NodeId(3), NodeId(4)]


# Ingest: starea ramane intre apeluri
def test_ingest_keeps_node_state_between_calls():
    repo = InMemoryNodeRepository()
    ingest = IngestFrames(repo)
    ingest([wire_packet(seq=10)])
    result = ingest([wire_packet(seq=12, timestamp_us=30_000)])
    assert result.events == ()
    assert result.nodes[0].frames_lost == 1


# Ingest: filtrul pastreaza un nod
def test_ingest_filter_keeps_only_one_node():
    result = IngestFrames(InMemoryNodeRepository(), only_node=NodeId(4))(
        [wire_packet(node_id=3), wire_packet(node_id=4)])
    assert [f.node_id for f in result.frames] == [NodeId(4)]


# Ingest: lot gol, rezultat gol
def test_ingest_of_nothing_is_empty():
    assert IngestFrames(InMemoryNodeRepository())(()) == IngestResult()


# Debit: doar fereastra curenta
def test_throughput_counts_only_the_window():
    t = Throughput(1.0).add(0.0, 5).add(0.5, 3).add(1.2, 2)
    assert t.total == 10
    assert t.per_second == 5.0


# Debit: obiectul nu se schimba
def test_throughput_is_immutable():
    start = Throughput(1.0)
    start.add(0.0, 4)
    assert start.total == 0


# Debit: fereastra invalida respinsa
@pytest.mark.parametrize("window", [0, -1])
def test_throughput_rejects_bad_window(window):
    with pytest.raises(ValueError):
        Throughput(window)


# Debit: numar negativ respins
def test_throughput_rejects_negative_count():
    with pytest.raises(ValueError):
        Throughput(1.0).add(0.0, -1)
