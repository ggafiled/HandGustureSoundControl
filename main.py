import cv2
import numpy as np
from ctypes import cast, POINTER
from cvzone.HandTrackingModule import HandDetector
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

volRangeMin, volRangeMax, decibel = volume.GetVolumeRange()
vol = 0
volBar = np.interp(volume.GetMasterVolumeLevel(), [volRangeMin, volRangeMax], [400, 100])
volPercen = np.interp(volume.GetMasterVolumeLevel(), [volRangeMin, volRangeMax], [0, 100])
detectors = HandDetector(detectionCon= 0.8, maxHands=1)

cap = cv2.VideoCapture(0)
cap.set(3, 720)
cap.set(4, 480)

def createBar(source, volPercen, volBar):
    overlay = np.zeros_like(source, dtype=np.uint8)
    overlay = cv2.rectangle(overlay,(560,100), (580,400), (0,255,0), 2)
    overlay = cv2.rectangle(overlay, (580, int(volBar)), (560, 400), (255, 0, 0), -1)
    overlay = cv2.rectangle(overlay, (550,int(volBar)+8), (590,int(volBar)), (255,0,0), -1)
    overlay = cv2.putText(overlay, f"{int(volPercen)} %", (548, 420), cv2.FONT_HERSHEY_COMPLEX, 0.7, (255,0,0))
    return cv2.addWeighted(source, 0.9, overlay, 1, 0)

while cap.isOpened():
    success, frame = cap.read()
    frame = cv2.flip(frame, 1)
    frame = createBar(frame, volPercen, volBar)
    if success:
        hands, frame = detectors.findHands(frame, draw=True)
        if hands:
            fingersUp = detectors.fingersUp(hands[0])
            if fingersUp == [1, 1, 0, 0, 0]:
                print(fingersUp)
                lmList = hands[0]["lmList"]
                length, info, frame = detectors.findDistance(lmList[4], lmList[8], frame)

                print(length)
                vol = np.interp(length, [30, 250],[volRangeMin, volRangeMax])
                volPercen = np.interp(vol, [volRangeMin, volRangeMax], [0, 100])
                volBar = np.interp(vol, [volRangeMin, volRangeMax], [400, 100])

        volume.SetMasterVolumeLevel(vol, None)
        frame = createBar(frame, volPercen, volBar)
        cv2.imshow("Hand Control", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

cap.release()
cv2.destroyAllWindows()



