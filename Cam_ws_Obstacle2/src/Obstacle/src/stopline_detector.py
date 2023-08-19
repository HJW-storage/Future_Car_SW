#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import cv2
from camera_traffic import Camera

# =============================================
# 주행을 위한 알고리즘 클래스 정의
# =============================================
class StoplineDetector:
    def __init__(self):

        self.camera = Camera()

        self.stopline_distance_pixel, self.prev_stopline_distance_lixel = self.camera.HEIGHT, self.camera.HEIGHT

        self.contour_list = []


        self.mission_stop_clear = 0  # 정지선 미션 클리어 여부
        self.detected = False

    def median_filter(self, data, arr_size=5):
        # 가운데 차선인식 안됐을경우 center_mid로 대체
        if np.isnan(data):
            data = 0

        if len(self.contour_list) >= arr_size:
            self.contour_list.pop(0)
        
        else:
            self.contour_list.append(data)
        
        filtered_center = np.median(self.contour_list)

        return filtered_center


    # ========================================
    # 흰색 영역 이진화
    # ========================================
    def white_threshold(self, frame):
        ret, masked_image = cv2.threshold(frame, 50, 255, cv2.THRESH_BINARY)
        return masked_image

    # ========================================
    # Crosswalk 윤곽선 그리기
    # ========================================
    def contour_cross(self, img, show):
        self.detected = False
        if show:
            check_img = np.dstack((img, img, img)) * 255
        contours, _ = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        
        filtered_countour = self.median_filter(len(contours))
        print('CONTOUR: ', filtered_countour)
        if filtered_countour > 9:
            for cnt in contours:

                x, y, w, h = cv2.boundingRect(cnt)

                if (w < self.camera.WIDTH // 2) or ((y+h)//2 < 240):
                    continue

                if show:
                    cv2.rectangle(check_img, (int(x), int(y)), (int(x+w), int(y+h)), (0, 0, 255), 2)
                
                if (y + h) >= 440:
                    self.detected = True

        # else:
        #     self.detected = False

        if show:
            cv2.imshow('contour img', check_img)


    def process(self, origin_img):
        img = self.camera.pre_processing(origin_img)

        self.contour_cross(img, show = True)
        # print('detected : {}'.format(self.detected))
        return self.detected
        
