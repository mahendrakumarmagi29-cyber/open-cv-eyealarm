# Webcam Eye Reaction Alarm (OpenCV)

Opens your webcam, detects your **face and eyes**, and if there is **no eye reaction
for 10 seconds** (eyes closed / not visible), it plays a loud **alarm sound**.
The alarm stops automatically when your eyes are detected again.

## Setup (Windows PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run
```powershell
python main.py
```
Options:
```powershell
python main.py --seconds 5          # change wait time
python main.py --camera 1           # use another camera
python main.py --ignore-no-face     # no alarm when nobody is in front of the camera
```

## Keys (click the video window first)
- `q` quit  - `r` reset timer  - `m` mute / unmute alarm

## How it works
1. Haar cascades find the face, then eyes in the upper part of the face.
2. Whenever eyes are seen, the timer resets (this is the "reaction").
3. If eyes are not seen for 10 s (or no face, if enabled) the alarm loops.
4. Events are saved in `logs/events.csv`.

The siren `alarm.wav` is generated automatically on first run.
You can replace it with your own `.wav` file of the same name.

## Tips
- Use good front lighting; face the camera straight on.
- If the alarm triggers while your eyes are open, move closer / improve light,
  or raise `EYE_NEIGHBORS` / lower it in `config.py`.
- Haar eye detection is basic and glasses can affect it. Educational project,
  not a safety system (e.g. do not rely on it for driver drowsiness).
