
import argparse
import csv
import time
from datetime import datetime

import cv2

import config as C
from alarm import Alarm


def parse_args():
    parser = argparse.ArgumentParser(
        description="Human Eye Detection and Alarm"
    )
    parser.add_argument("--camera", type=int, default=C.CAMERA_INDEX)
    parser.add_argument("--seconds", type=float,
                        default=C.ALARM_AFTER_SECONDS)
    parser.add_argument("--ignore-no-face", action="store_true")
    return parser.parse_args()


def log_event(event):
    C.LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    new_file = not C.LOG_PATH.exists()

    with open(C.LOG_PATH, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if new_file:
            writer.writerow(["time", "event"])
        writer.writerow([
            datetime.now().isoformat(timespec="seconds"), event
        ])


def main():
    args = parse_args()
    alarm_on_no_face = (
        C.ALARM_ON_NO_FACE and not args.ignore_no_face
    )

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades
        + "haarcascade_frontalface_default.xml"
    )
    eye_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_eye.xml"
    )

    if face_cascade.empty() or eye_cascade.empty():
        raise RuntimeError("OpenCV face/eye cascade files not found.")

    camera = cv2.VideoCapture(args.camera)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, C.FRAME_WIDTH)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, C.FRAME_HEIGHT)

    if not camera.isOpened():
        raise RuntimeError(
            f"Cannot open camera {args.camera}. Try --camera 1"
        )

    alarm = Alarm(C.SOUND_PATH)

    muted = False
    last_reaction = time.monotonic()
    alarm_active = False

    print("Eye alarm started. Press q to quit.")
    log_event("started")

    try:
        while True:
            success, frame = camera.read()
            if not success:
                print("Camera read failed.")
                break

            frame = cv2.flip(frame, 1)
            gray = cv2.equalizeHist(
                cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            )

            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=C.FACE_SCALE,
                minNeighbors=C.FACE_NEIGHBORS,
                minSize=C.FACE_MIN_SIZE
            )

            face_found = len(faces) > 0
            eyes_found = False

            for (x, y, w, h) in faces:
                cv2.rectangle(
                    frame, (x, y), (x + w, y + h),
                    (255, 120, 0), 2
                )

                # Search only in the upper part of the face.
                top = y
                bottom = min(y + int(h * 0.60), gray.shape[0])
                left = x
                right = min(x + w, gray.shape[1])

                face_top = gray[top:bottom, left:right]
                if face_top.size == 0:
                    continue

                eyes = eye_cascade.detectMultiScale(
                    face_top,
                    scaleFactor=C.EYE_SCALE,
                    minNeighbors=C.EYE_NEIGHBORS,
                    minSize=(max(10, w // 10), max(10, h // 20))
                )

                for (ex, ey, ew, eh) in eyes:
                    eyes_found = True
                    cv2.rectangle(
                        frame,
                        (left + ex, top + ey),
                        (left + ex + ew, top + ey + eh),
                        (0, 255, 0), 2
                    )

            now = time.monotonic()

            # IMPORTANT: visible eyes immediately stop the alarm
            # and restart the countdown.
            if eyes_found:
                last_reaction = now

                if alarm_active:
                    alarm.stop()
                    alarm_active = False
                    log_event("Eyes detected - alarm stopped")

            # Preserve the option to ignore missing faces.
            elif not face_found and not alarm_on_no_face:
                last_reaction = now

                if alarm_active:
                    alarm.stop()
                    alarm_active = False
                    log_event("No face - alarm stopped")

            elapsed = now - last_reaction
            remaining = max(0.0, args.seconds - elapsed)
            triggered = elapsed >= args.seconds

            if triggered and not alarm_active:
                alarm_active = True
                log_event(
                    "ALARM: no eye reaction"
                    if face_found else "ALARM: no face"
                )

            if alarm_active:
                if muted:
                    alarm.stop()
                else:
                    alarm.start()
            else:
                alarm.stop()

            if alarm_active:
                status = "ALARM! EYES NOT DETECTED"
                color = (0, 0, 255)
                cv2.rectangle(
                    frame, (0, 0),
                    (frame.shape[1] - 1, frame.shape[0] - 1),
                    (0, 0, 255), 6
                )
            elif eyes_found:
                status = "EYES OPEN - ALARM OFF"
                color = (0, 255, 0)
            elif face_found:
                status = "EYES CLOSED / NOT DETECTED"
                color = (0, 200, 255)
            else:
                status = "NO FACE DETECTED"
                color = (0, 200, 255)

            cv2.rectangle(
                frame, (0, 0), (frame.shape[1], 85),
                (0, 0, 0), -1
            )
            cv2.putText(
                frame, status, (10, 27),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, color, 2
            )
            cv2.putText(
                frame,
                f"Alarm in: {remaining:.1f}s | "
                f"{'MUTED' if muted else 'SOUND ON'}",
                (10, 55), cv2.FONT_HERSHEY_SIMPLEX,
                0.6, (255, 255, 255), 2
            )
            cv2.putText(
                frame, "q: Quit  r: Reset  m: Mute",
                (10, 77), cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (255, 255, 255), 1
            )

            cv2.imshow("Human Eye Sensor Alarm", frame)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

            elif key == ord("r"):
                last_reaction = time.monotonic()
                alarm.stop()
                alarm_active = False
                log_event("Timer reset")

            elif key == ord("m"):
                muted = not muted
                if muted:
                    alarm.stop()
                print("Alarm muted" if muted else "Alarm unmuted")

    finally:
        alarm.stop()
        camera.release()
        cv2.destroyAllWindows()
        log_event("stopped")


if __name__ == "__main__":
    main()
