import contextlib
import os
import threading
import time

from PyQt6.QtCore import QThread, pyqtSignal

from csi.dsp import analyze_recording
from csi.gui.frames import LiveTracker, frames_from_analysis
from csi.packets import PacketStream, load_recording

try:
    import serial
except ImportError:
    serial = None

MIN_FPS = 10.0
SERIAL_TIMEOUT_S = 0.05
POLL_MS = 2


class FrameSource(QThread):
    frame_ready = pyqtSignal(object)
    status_changed = pyqtSignal(str)

    def __init__(self, live, ports, baud_rate, fps, recording_path):
        super().__init__()
        self._live = live
        self._ports = tuple(ports)
        self._baud_rate = baud_rate
        self._fps = max(MIN_FPS, fps)
        self._recording_path = recording_path
        self._alarm_reset = threading.Event()

    def run(self):
        if self._live:
            connections = self._open_ports()
            if connections:
                self._run_live(connections)
                return
            self.status_changed.emit("Hardware ports unavailable. Falling back to Replay Mode.")
        self._run_replay()

    def stop(self):
        self.requestInterruption()
        self.wait()

    def reset_alarm(self):
        self._alarm_reset.set()

    def _open_ports(self):
        if serial is None:
            return []
        connections = []
        for port in self._ports:
            if not os.path.exists(port):
                continue
            try:
                connection = serial.Serial(port, baudrate=self._baud_rate, timeout=SERIAL_TIMEOUT_S)
                connection.dtr = False
                connection.rts = False
                connections.append(connection)
                self.status_changed.emit(f"Connected hardware port {port} @ {self._baud_rate}")
            except Exception as error:
                self.status_changed.emit(f"Failed opening {port}: {error}")
        return connections

    def _run_live(self, connections):
        tracker = LiveTracker()
        streams = [PacketStream() for _ in connections]
        interval_s = 1.0 / self._fps
        last_emit_s = time.monotonic()
        fresh = False
        try:
            while not self.isInterruptionRequested():
                if self._alarm_reset.is_set():
                    self._alarm_reset.clear()
                    tracker.reset_alarm()
                for connection, stream in zip(connections, streams):
                    waiting = connection.in_waiting
                    if waiting:
                        for packet in stream.feed(connection.read(waiting)):
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
            self.status_changed.emit(f"Serial stream error: {error}")
        finally:
            for connection in connections:
                with contextlib.suppress(Exception):
                    connection.close()

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
