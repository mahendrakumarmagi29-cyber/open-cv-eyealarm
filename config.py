from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SOUND_PATH = BASE_DIR / "alarm.wav"
LOG_PATH = BASE_DIR / "logs" / "events.csv"

CAMERA_INDEX = 0          # 0 = default webcam, try 1 if it does not open
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

ALARM_AFTER_SECONDS = 3  # no eye reaction for this long -> alarm
ALARM_ON_NO_FACE = True   # also alarm if nobody is in front of the camera

# Haar cascade tuning
FACE_SCALE = 1.2
FACE_NEIGHBORS = 5
FACE_MIN_SIZE = (100, 100)
EYE_SCALE = 1.1
EYE_NEIGHBORS = 6         # higher = fewer false eye detections
