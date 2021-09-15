#!/usr/bin/env python

import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np

cap = cv2.VideoCapture(0)
detector = HandDetector(detectionCon=0.8, maxHands=1)
BINARY_THREHOLD = 180

while True:
    success, img = cap.read()
    hands, img = detector.findHands(img)
    # hands = detector.findHands(img, draw=False)
    # imgg = ~cv2.cvtColor(img, cv2.COLOR_BGR2YUV_I420)

    # ret1, th1 = cv2.threshold(img, BINARY_THREHOLD, 255, cv2.THRESH_BINARY)
    # print(f'{ret1 = }\n{th1 = }\n')
    # ret2, th2 = cv2.threshold(th1, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # print(f'{ret2 = }\n{th2 = }\n')
    # blur = cv2.GaussianBlur(th2, (1, 1), 0)
    # ret3, th3 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # filtered = cv2.adaptiveThreshold(img.astype(np.uint8), 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 41)
    # kernel = np.ones((1, 1), np.uint8)
    # opening = cv2.morphologyEx(filtered, cv2.MORPH_OPEN, kernel)
    # closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
    # imgg = image_smoothening(img)
    # or_image = cv2.bitwise_or(imgg, closing)

    # imgg = cv2.bitwise_not(imgg)
    # imgg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # imgg = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # hue, _, _ = cv2.split(imgg)
    # blur = cv2.GaussianBlur(hue, (3,3), 0)
    # ret, th = cv2.threshold(blur, 100, 255, 0)
    # print(f'{ret = }\n{th = }\n')
    # if hands:
    #     distance, _, _ = detector.findDistance(hands[0]['lmList'][4], hands[0]['lmList'][8], img)
    #     x,y,w,h = hands[0]['bbox']
    #     # hands_area = x
    #     # print(hands)
    #     # print(distance)
    #     # [print(f'Fingers: {detector.fingersUp(x)}\nDistance: {thumb_index=!r}\n{x}\n{"="*80}') for x in hands]
    #     cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 255), 1)
    #     cv2.circle(img, (x, y), 5, (0, 0, 255), -1)
    #     cv2.circle(img, (x+w, y+h), 5, (255, 0, 0), -1)
    #     cv2.putText(img,f'Area: {(w*h)}',(10,50), cv2.FONT_HERSHEY_SIMPLEX,
    #                 1,(255,255,255),1,cv2.LINE_AA)
    #     imgg = imgg[y:y+h, x:x+w]
    #     print(imgg.shape)
    #     # np_img = np.array(imgg, dtype = 'float32')
    #     # print(f'{np_img.shape = }\n{np_img = }\n{"="*80}')
    #     # imgg = cv2.resize(imgg, (320, 120), cv2.INTER_AREA)

    cv2.imshow("Image", img)
    # cv2.imshow("Image", imgg)
    # cv2.imshow("Image", th)
    # cv2.imshow("Image", th3)
    # cv2.imshow("Image", imgg)
    # cv2.imshow("Image", or_image)
    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
