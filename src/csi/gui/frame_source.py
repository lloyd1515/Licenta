import threading
import time

from PyQt6.QtCore import QThread, pyqtSignal

from csi.dsp import analyze_recording
from csi.gui.frames import LiveTracker, frames_from_analysis
from csi.packets import UDP_RECEIVE_BYTES, load_recording, open_udp_socket, parse_datagram

MIN_FPS = 10.0
POLL_MS = 2


class FrameSource(QThread):
    frame_ready = pyqtSignal(object)
    status_changed = pyqtSignal(str)

    def __init__(self, live, udp_port, fps, recording_path):
        super().__init__()
        self._live = live
        self._udp_port = udp_port
        self._fps = max(MIN_FPS, fps)
        self._recording_path = recording_path
        self._alarm_reset = threading.Event()

    def run(self):
        if self._live:
            sock = self._open_socket()
            if sock is not None:
                self._run_live(sock)
                return
            self.status_changed.emit("UDP port unavailable. Falling back to Replay Mode.")
        self._run_replay()

    def stop(self):
        self.requestInterruption()
        self.wait()

    def reset_alarm(self):
        self._alarm_reset.set()

    def _open_socket(self):
        try:
            sock = open_udp_socket(self._udp_port)
        except OSError as error:
            self.status_changed.emit(f"Failed opening UDP port {self._udp_port}: {error}")
            return None
        sock.setblocking(False)
        self.status_changed.emit(f"Listening for CSI nodes on UDP port {self._udp_port}")
        return sock

    def _run_live(self, sock):
        tracker = LiveTracker()
        interval_s = 1.0 / self._fps
        last_emit_s = time.monotonic()
        fresh = False
        try:
            while not self.isInterruptionRequested():
                if self._alarm_reset.is_set():
                    self._alarm_reset.clear()
                    tracker.reset_alarm()
                while True:
                    try:
                        data = sock.recv(UDP_RECEIVE_BYTES)
                    except BlockingIOError:
                        break
                    for packet in parse_datagram(data):
                        tracker.add(packet)
                        fresh = True
                now_s = time.monotonic()
                if fresh and now_s - last_emit_s >= interval_s:
                    frame = tracker.frame()
                    if frame is not None:
                        self.frame_ready.emit(frame)
                    last_emit_s = now_s
                    fresh = False
                self.msleep(POLL_MS)
        except Exception as error:
            self.status_changed.emit(f"UDP stream error: {error}")
        finally:
            sock.close()

    def _run_replay(self):
        try:
            analysis = analyze_recording(load_recording(self._recording_path))
        except Exception as error:
            self.status_changed.emit(f"Replay failed: {error}")
            return
        frames = frames_from_analysis(analysis)
        step = max(1, round(analysis.recording.rate_hz / self._fps))
        interval_s = 1.0 / self._fps
        next_s = time.monotonic()
        index = 0
        while not self.isInterruptionRequested():
            self.frame_ready.emit(frames[index])
            index += step
            if index >= len(frames):
                index = 0
            next_s += interval_s
            delay_s = next_s - time.monotonic()
            if delay_s > 0:
                self.msleep(int(delay_s * 1000))
            else:
                next_s = time.monotonic()
