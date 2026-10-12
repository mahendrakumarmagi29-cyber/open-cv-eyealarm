"""Cross-platform alarm sound (no extra packages needed)."""
import math
import platform
import struct
import subprocess
import wave
from pathlib import Path

SYSTEM = platform.system()


def create_alarm_wav(path: Path, seconds: float = 1.0, rate: int = 44100):
    """Generate a loud two-tone siren WAV file if it does not exist."""
    path = Path(path)
    if path.exists():
        return
    frames = bytearray()
    n = int(seconds * rate)
    for i in range(n):
        t = i / rate
        freq = 880 if int(t * 4) % 2 == 0 else 1320  # alternate tones
        value = int(32767 * 0.8 * math.sin(2 * math.pi * freq * t))
        frames += struct.pack("<h", value)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(bytes(frames))


class Alarm:
    def __init__(self, wav_path: Path):
        self.wav_path = Path(wav_path)
        create_alarm_wav(self.wav_path)
        self.playing = False
        self._proc = None

    def start(self):
        if self.playing:
            return
        self.playing = True
        if SYSTEM == "Windows":
            import winsound
            winsound.PlaySound(str(self.wav_path),
                               winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
        else:
            self._play_loop_posix()

    def _play_loop_posix(self):
        # Loop the wav with afplay (macOS) or aplay (Linux) via a shell loop.
        player = "afplay" if SYSTEM == "Darwin" else "aplay -q"
        try:
            self._proc = subprocess.Popen(
                f'while true; do {player} "{self.wav_path}"; done',
                shell=True, start_new_session=True)
        except Exception:
            print("\a", end="", flush=True)  # terminal bell fallback

    def stop(self):
        if not self.playing:
            return
        self.playing = False
        if SYSTEM == "Windows":
            import winsound
            winsound.PlaySound(None, winsound.SND_PURGE)
        elif self._proc is not None:
            import os, signal
            try:
                os.killpg(os.getpgid(self._proc.pid), signal.SIGTERM)
            except Exception:
                pass
            self._proc = None
