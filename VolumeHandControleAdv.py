import cv2
import time
import numpy as np
import math
import HandTrackingModuleAdv as htm
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

wCam, hCam=640,720


cap =cv2.VideoCapture(0)
cap.set(3,wCam)
cap.set(4,hCam)

pTime=0
cTime=0

detector=htm.handDetector(detectionCon=0.7)


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
#volume.GetMute()
#volume.GetMasterVolumeLevel()
volRange=volume.GetVolumeRange()


minVol=volRange[0]
maxVol=volRange[1]
vol=0
volBar=400
volPer=0
area=0
while True:
    success, img=cap.read()

    #Find hand
    img= detector.findHands(img)
    lmList,bbox=detector.findPosition(img,draw=True)

    if(len(lmList)!=0):
        # Fliter based on size
        area=(bbox[2]-bbox[0])*(bbox[3]-bbox[1])//100
        #print(area)
        if 300<area<1000:
            # Find distance between index and thumb
            length,img,lineinfo=detector.findDistance(4,8,img)
            # convert volume
            volBar = np.interp(length, [50, 300], [400, 150])
            volPer = np.interp(length, [50, 300], [0, 100])
            # print(vol)
            #volume.SetMasterVolumeLevel(vol, None)
            # Reduce resolution to make it smoother
            smoothness = 10
            volPer = smoothness*round(volPer/smoothness)

            # Check fingers up
            fingers=detector.fingersUp()
            # if pinky is down set up volume
            if not fingers[4]:
                volume.SetMasterVolumeLevelScalar(volPer / 100, None)
                cv2.circle(img, (lineinfo[4], lineinfo[5]), 15, (255, 0, 0), cv2.FILLED)

            # drawings
            # frame rate

            # print(lmList[4],lmList[8])

            print(length)

            # hand range 300 to 50
            # vol range -65 to 0

            if length < 50:
                cv2.circle(img, (lineinfo[4], lineinfo[5]), 15, (255, 0, 0), cv2.FILLED)

    cv2.rectangle(img,(50,150),(85,400),(255,0,0),3)
    cv2.rectangle(img,(50,int(volBar)),(85,400),(255, 0, 0),cv2.FILLED)
    cVol=int(volume.GetMasterVolumeLevelScalar()*100)
    cv2.putText(img, f'Vol Set: {int(cVol)}', (400, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 0, 255), 3)

    cv2.imshow("img",img )
    cv2.waitKey(1)
