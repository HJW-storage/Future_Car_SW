#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import numpy as np
import cv2
import matplotlib.pyplot as plt      # pip install matplotlib

class traffic:

    def __init__(self):

        self.NULL = 0
        self.VARIANCE = 30
        self.SATURATION = 150 #색의 진함.
    
        self.RED, self.GREEN, self.BLUE, self.YELLOW = (0, 1, 2, 3)
        self.COLOR = ("RED", "GREEN", "BLUE", "YELLOW")
        self.DIRECTION = ("FORWARD", "LEFT", "RIGHT")
        self.HUE_THRESHOLD = ([2, 176], [40, 110], [110, 130], [20, 40]) # H - 색상 자체 

    # def loop_break(self):
    #         if cv2.waitKey(10) & 0xFF == ord('q'):
    #             print("Camera Reading is ended.")
    #             return True
    #         else:
    #             return False
            
    def rgb_conversion(self, img):
        return cv2.cvtColor(img.copy(), cv2.COLOR_BGR2RGB)
        
    def hsv_conversion(self, img):
        return cv2.cvtColor(img.copy(), cv2.COLOR_BGR2HSV) # BGR -> HSV
    
    def gray_conversion(self, img):
        return cv2.cvtColor(img.copy(), cv2.COLOR_BGR2GRAY)    

    def color_extract(self, img, idx):
        result = img.copy()

        for i in range(self.RED+self.GREEN+self.BLUE):
            if i != idx:
                result[:, :, i] = np.zeros([self.row, self.col])

        return result

    def extract_rgb(self, img, print_enable=False):
        self.row, self.col, self.dim = img.shape

        img = self.rgb_conversion(img)

        # Image Color Separating
        img_red = self.color_extract(img, self.RED)
        img_green = self.color_extract(img, self.GREEN)
        img_blue = self.color_extract(img, self.BLUE)

        if print_enable:
            plt.figure(figsize=(12, 4))
            imgset = [img_red, img_green, img_blue]
            imglabel = ["RED", "GREEN", "BLUE"]

            for idx in range(self.RED+self.GREEN+self.BLUE):
                plt.subplot(1, 3, idx + 1)
                plt.xlabel(imglabel[idx])
                plt.imshow(imgset[idx])
            plt.show()

        return img_red[:, :, self.RED], img_green[:, :, self.GREEN], img_blue[:, :, self.BLUE]   

    def color_filtering(self, img, roi=None, print_enable=False):
        self.row, self.col, self.dim = img.shape

        hsv_img = self.hsv_conversion(img)
        h, s, v = cv2.split(hsv_img)

        s_cond = s > self.SATURATION
        if roi is self.RED:
            h_cond = (h < self.HUE_THRESHOLD[roi][0]) | (h > self.HUE_THRESHOLD[roi][1])
        else:
            h_cond = (h > self.HUE_THRESHOLD[roi][0]) & (h < self.HUE_THRESHOLD[roi][1])

        v[~h_cond], v[~s_cond] = 0, 0
        hsv_image = cv2.merge([h, s, v])
        result = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR) # 브이는 밝기, 에스는 색의 진함.
        if print_enable:
#            self.image_show(result)
            pass



        return result
    
    
    def gaussian_blurring(self, img, kernel_size=(None, None)):
        return cv2.GaussianBlur(img.copy(), kernel_size, 0)

    def canny_edge(self, img, lth, hth):
        return cv2.Canny(img.copy(), lth, hth)

    def histogram_equalization(self, gray):
        return cv2.equalizeHist(gray)

    def hough_transform(self, img, rho=None, theta=None, threshold=None, mll=None, mlg=None, mode="lineP"):
        if mode == "circle":
            return cv2.HoughCircles(img.copy(), cv2.HOUGH_GRADIENT, dp=1, minDist=80,
                                    param1=200, param2=40, minRadius=30, maxRadius=50)
    
    def object_detection(self, img, sample=0, mode="circle", print_enable=False):
        result = None
        replica = img.copy()
        for color in (self.RED, self.GREEN):
            extract = self.color_filtering(img, roi=color, print_enable=True)
            gray = self.gray_conversion(extract)
            circles = self.hough_transform(gray, mode=mode)
            if circles is not None:
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
                        cv2.circle(replica, center, int(circle[2]), (0, 0, 255), 2)

        if print_enable:
            if result is not None:
                print(" ", result)
            self.image_show(replica)

        return result
    
    
    def main_traffic(self, origin_img):
        img = cv2.resize(origin_img, (640,480), cv2.INTER_LINEAR)
        detection_img = self.object_detection(img)

        return detection_img