#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import cv2
import numpy as np
from matplotlib import pyplot as plt

class traffic:
    def __init__(self):
        self.upper_left_up = (0, 0)
        self.bottom_right_up = (640, 120)

        self.upper_left_down = (0, 240)
        self.bottom_right_down = (640, 480)

        self.upper_left_left = (0, 120)
        self.bottom_right_left = (150, 240)

        self.upper_left_right = (500, 120)
        self.bottom_right_right = (640, 240)
        self.NULL = 0
        self.VARIANCE = 30 # 브이는 밝기, 에스는 색의 진함.
        self.SATURATION = 150  # 색의 진함.

        self.RED, self.GREEN, self.BLUE, self.YELLOW = (0, 1, 2, 3)
        self.COLOR = ("RED", "GREEN", "BLUE", "YELLOW")
        self.DIRECTION = ("FORWARD", "LEFT", "RIGHT")
        self.HUE_THRESHOLD = ([0, 176], [40, 110], [110, 130], [10, 11])  # H - 색상 자체

    def roi_setting(self, img):
        rect_img_down = img[self.upper_left_down[1]: self.bottom_right_down[1], self.upper_left_down[0]: self.bottom_right_down[0]]

        sketcher_rect_down = rect_img_down
        sketcher_rect_down = self.sketch_transform(sketcher_rect_down)
        sketcher_rect_rgb_down = cv2.cvtColor(sketcher_rect_down, cv2.COLOR_GRAY2RGB)
        img[self.upper_left_down[1]: self.bottom_right_down[1], self.upper_left_down[0]: self.bottom_right_down[0]] = sketcher_rect_rgb_down

        # Up
        # r_up = cv2.rectangle(img, upper_left_up, bottom_right_up, (100, 50, 200), 5)
        rect_img_up = img[self.upper_left_up[1]: self.bottom_right_up[1], self.upper_left_up[0]: self.bottom_right_up[0]]

        sketcher_rect_up = rect_img_up
        sketcher_rect_up = self.sketch_transform(sketcher_rect_up)
        sketcher_rect_rgb_up = cv2.cvtColor(sketcher_rect_up, cv2.COLOR_GRAY2RGB)
        img[self.upper_left_up[1]: self.bottom_right_up[1], self.upper_left_up[0]: self.bottom_right_up[0]] = sketcher_rect_rgb_up

        # right
        # r_right = cv2.rectangle(img, upper_left_right, bottom_right_right, (100, 50, 200), 5)
        rect_img_right = img[self.upper_left_right[1]: self.bottom_right_right[1], self.upper_left_right[0]: self.bottom_right_right[0]]

        sketcher_rect_right = rect_img_right
        sketcher_rect_right = self.sketch_transform(sketcher_rect_right)
        sketcher_rect_rgb_right = cv2.cvtColor(sketcher_rect_right, cv2.COLOR_GRAY2RGB)
        img[self.upper_left_right[1]: self.bottom_right_right[1],
        self.upper_left_right[0]: self.bottom_right_right[0]] = sketcher_rect_rgb_right

        # left
        # r_left = cv2.rectangle(img, upper_left_left, bottom_right_left, (100, 50, 200), 5)
        rect_img_left = img[self.upper_left_left[1]: self.bottom_right_left[1], self.upper_left_left[0]: self.bottom_right_left[0]]

        sketcher_rect_left = rect_img_left
        sketcher_rect_left = self.sketch_transform(sketcher_rect_left)
        sketcher_rect_rgb_left = cv2.cvtColor(sketcher_rect_left, cv2.COLOR_GRAY2RGB)
        img[self.upper_left_left[1]: self.bottom_right_left[1], self.upper_left_left[0]: self.bottom_right_left[0]] = sketcher_rect_rgb_left

        return img

    def sketch_transform(self, img):
        image_grayscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return image_grayscale

    def rgb_conversion(self, img):
        img = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2RGB)
        return img

    def hsv_conversion(self, img):
        img = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2HSV)  # BGR -> HSV
        return img

    def gray_conversion(self, img):
        img = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2GRAY)
        return img

    def color_filtering(self, img, roi=None, print_enable=False):
        row, col, dim = img.shape

        hsv_img = self.hsv_conversion(img)
        h, s, v = cv2.split(hsv_img)

        s_cond = s > self.SATURATION
        if roi is self.RED:
            h_cond = (h < self.HUE_THRESHOLD[roi][0]) | (h > self.HUE_THRESHOLD[roi][1])
        else:
            h_cond = (h > self.HUE_THRESHOLD[roi][0]) & (h < self.HUE_THRESHOLD[roi][1])

        v[~h_cond], v[~s_cond] = 0, 0
        hsv_image = cv2.merge([h, s, v])
        result = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)  # 브이는 밝기, 에스는 색의 진함.
        if print_enable:
            # cv2.imshow('result', result)
            pass

        return result

    def hough_transform(self, img, rho=None, theta=None, threshold=None, mll=None, mlg=None, mode="lineP"):
        if mode == "line":
            return cv2.HoughLines(img.copy(), rho, theta, threshold)
        elif mode == "lineP":
            return cv2.HoughLinesP(img.copy(), rho, theta, threshold, lines=np.array([]),
                                   minLineLength=mll, maxLineGap=mlg)
        elif mode == "circle":
            return cv2.HoughCircles(img.copy(), cv2.HOUGH_GRADIENT, dp=1, minDist=80,
                                    param1=200, param2=20, minRadius=40, maxRadius=100)

            # 속성 주석처리 해주기!!
            # img : 입력 이미지
            # cv2.HOUGH_GRADIENT : gray 이미지
            # dp = 1 : 입력된 이미지와 동일한 해상도
            # minDist : 검출한 원의 중심과의 최소 거리값. 최소 거리값보다 작으면 원 검출 X
            # param1 : canny edge에게 전달되는 인자값
            # param2 : 검출 결과를 보면서 적당이 조정해야 되는 값.
            # 작으면 오류 높고 크면 검출률 낮아짐
            # minRadisu : 각각 원의 최소 반지름
            # maxRadisu : 각각 원의 최대 반지름


    def object_detection(self, img, sample=0, mode="circle", print_enable=False):
        result = None
        # replica = img.copy()
        for color in (self.RED, self.GREEN):
            extract = self.color_filtering(img, roi=color, print_enable=True)
            gray = self.gray_conversion(extract)
            circles = self.hough_transform(gray, mode=mode)
            if circles is not None: #circle이면
                for circle in circles[0]:
                    center, count = (int(circle[0]), int(circle[1])), 0

                    hsv_img = self.hsv_conversion(img)
                    h, s, v = cv2.split(hsv_img)

                    # Searching the surrounding pixels
                    for res in range(sample):
                        x, y = int(center[1] - sample / 2), int(center[0] - sample / 2)
                        s_cond = s[x][y] > self.SATURATION
                        if color is self.RED:
                            h_cond = (h[x][y] < self.HUE_THRESHOLD[color][0]) | (h[x][y] > self.HUE_THRESHOLD[color][1])
                            count += 1 if h_cond and s_cond else count
                        else:
                            h_cond = (h[x][y] > self.HUE_THRESHOLD[color][0]) & (h[x][y] < self.HUE_THRESHOLD[color][1])
                            count += 1 if h_cond and s_cond else count

                    if count > sample / 2:
                        result = self.COLOR[color]
                        cv2.circle(img, center, int(circle[2]), (0, 0, 255), 2)

        if print_enable:
            if result is not None:
                print(" ", result)
            # cv2.imshow('result', result)

        return result

    # def main_traffic(self, origin_img):
    #     img = cv2.resize(origin_img, (640, 480), cv2.INTER_LINEAR)
    #     # img = self.roi_setting(img)
        
    #     return img # return 후 메인문에서 프린트하장 장애물 주행 다 끝났다는 플래그 들어오고.


