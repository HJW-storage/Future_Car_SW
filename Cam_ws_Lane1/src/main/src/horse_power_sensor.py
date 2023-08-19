#!/usr/bin/env python3
# -*- coding:utf-8 -*-

#from Tkinter import N
import rospy
import numpy as np
from cv_bridge import CvBridge
from sensor_msgs.msg import Image, LaserScan
from std_msgs.msg import Int32MultiArray

class HPSensor:
    def __init__(self):
        self.ultra = [0]    # callback_ultra()에서 list형식으로 출력을 하려고 리스트 형식으로 초기화. 
        rospy.Subscriber("ultrasonic", Int32MultiArray,self.callback_ultra, queue_size=1)

        # video
        self.cam = None
        self.bridge = CvBridge()
        rospy.Subscriber("/camera0/usb_cam/image_raw", Image, self.callback_cam)

        # camera
        self.real_cam = None
        rospy.Subscriber("/camera0/usb_cam/image_raw", Image, self.callback_real_cam)

        # lidar filtered
        self.lidar_filtered = None
        rospy.Subscriber("scan_filtered", LaserScan, self.callback_lidar_filtered)

    def callback_ultra(self, msg):
        self.ultra = msg.data
        print(list(self.ultra))

    def callback_cam(self, msg):
        # Converting ROS image messages to OpenCV images. encoding = "bgr8"
        # "bgr8": 8비트 3채널 BGR (Blue-Green-Red) 이미지로, 0~255 범위의 정수값을 갖습니다. 칼라 이미지로 가장 대표적인 인코딩입니다.
        self.cam = self.bridge.imgmsg_to_cv2(msg, "bgr8")

    def callback_real_cam(self, msg):
        # Converting ROS image messages to OpenCV images. encoding = "bgr8"
        # "bgr8": 8비트 3채널 BGR (Blue-Green-Red) 이미지로, 0~255 범위의 정수값을 갖습니다. 칼라 이미지로 가장 대표적인 인코딩입니다.
        self.real_cam = self.bridge.imgmsg_to_cv2(msg, "bgr8") 

    def callback_lidar_filtered(self, msg):
        self.lidar_filtered = msg
        #print('rm', len(LaserScan.ranges))

    def init(self, rate):
        while self.cam is None:     # 카메라가 준비될 때까지 기다린다
            rate.sleep()
        rospy.loginfo("video ready")    # log 메시지 화면에 출력 

        while self.real_cam is None:    # usb 카메라가 준비될 때까지 기다린다
            rate.sleep()
        rospy.loginfo("usb_cam ready")    # log 메시지 화면에 출력 

        while self.lidar_filtered is None:  # 라이다가 준비될 때까지 기다린다
            rate.sleep()
        rospy.loginfo("filtered lidar ready")    # log 메시지 화면에 출력  

        while self.ultra is None:   # 초음파센서가 준비될 때까지 기다린다
            rate.sleep()
        rospy.loginfo("ultra ready")    # log 메시지 화면에 출력  
