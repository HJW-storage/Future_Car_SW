#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import traffic_ex as tra
import cv2
import numpy as np
import ackermann_msgs 
import horse_power_sensor as HP_sensor

# if __name__ == "__main__":
env = tra.traffic()
cap = cv2.VideoCapture(0) # 웹캠 객체 생성
cap = HP_sensor.callback_real_cam


while True:
    ret_val, img = cap.read()  # 캠 이미지 불러오기

    roi = env.roi_setting(img)
    result = env.object_detection(img, sample=16, print_enable=True)  # 원 검출

    print("color", result)
    
    cv2.imshow("I Love Green", img)  # 불러온 이미지 출력하기
    if cv2.waitKey(10) == 27:
        break  # esc to quit