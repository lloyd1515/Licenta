import argparse
import signal
import sys

from csi.application.ingest import IngestFrames
from csi.domain.node_id import NodeId
from csi.infrastructure.memory_node_repository import InMemoryNodeRepository
from csi.infrastructure.udp_source import UdpDatagramSource

DEFAULT_PORT = 5005
WINDOW_SIZE = (1400, 700)


# Citeste portul si filtrul nod
def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="UI simplu pentru CSI brut primit prin UDP.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"portul UDP (implicit {DEFAULT_PORT})")
    parser.add_argument("--node", type=int, help="arata doar pachetele acestui nod")
    args = parser.parse_args(argv)
    try:
        only_node = None if args.node is None else NodeId(args.node)
    except ValueError as error:
        parser.error(str(error))
    return args.port, only_node


# Leaga contextele si porneste UI
def main(argv=None):
    port, only_node = parse_args(argv)
    try:
        source = UdpDatagramSource(port)
    except (OSError, ValueError) as error:
        sys.exit(str(error))
    from PyQt6.QtWidgets import QApplication

    from csi.ui.csi_view import CsiView

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication(sys.argv)
    view = CsiView(source, IngestFrames(InMemoryNodeRepository(), only_node))
    view.resize(*WINDOW_SIZE)
    view.show()
    sys.exit(app.exec())
