import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from csi.app import parse_args
from csi.application.ingest import IngestFrames
from csi.domain.node_id import NodeId
from csi.infrastructure.memory_node_repository import InMemoryNodeRepository
from tests.csi.factories import wire_packet


# Sursa falsa cu loturi
class FakeSource:
    port = 5005

    # Loturile de datagrame date
    def __init__(self, batches):
        self._batches = list(batches)

    # Urmatorul lot sau gol
    def drain(self):
        return self._batches.pop(0) if self._batches else ()


# Argumente: implicite si filtru
def test_parse_args_defaults_and_filter():
    assert parse_args([]) == (5005, None)
    assert parse_args(["--port", "6000", "--node", "4"]) == (6000, NodeId(4))


# Argumente: nod invalid respins
def test_parse_args_rejects_bad_node():
    with pytest.raises(SystemExit):
        parse_args(["--node", "300"])


# UI: coloana pe nod, pierderi
def test_view_adds_one_column_per_node_and_shows_loss():
    from PyQt6.QtWidgets import QApplication

    from csi.ui.csi_view import CsiView

    app = QApplication.instance() or QApplication([])
    source = FakeSource([[wire_packet(node_id=3, seq=0), wire_packet(node_id=5, seq=0)],
                         [wire_packet(node_id=3, seq=2, timestamp_us=20_000)]])
    view = CsiView(source, IngestFrames(InMemoryNodeRepository()))
    view.timer.stop()
    view.refresh()
    view.refresh()
    assert list(view.columns) == [NodeId(3), NodeId(5)]
    assert "pierdute 1" in view.columns[NodeId(3)].spectrum.titleLabel.text
    assert view.throughput.total == 3
    view.close()
    app.processEvents()
