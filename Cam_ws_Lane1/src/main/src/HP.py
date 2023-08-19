#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import cv2
import rospy
from ackermann_msgs.msg import AckermannDriveStamped
import time
from horse_power_sensor import HPSensor


from controller import Stanley
#from lane_detector_jw import Camera
from lane_detector import LaneDetector
from obstacle_detector import Clustering
# from traffic import traffic

class HP:

    def __init__(self):
        self.rate = rospy.Rate(10)  # 20Hz로 토픽 발행
        self.motor_pub = rospy.Publisher('ackermann_cmd', AckermannDriveStamped, queue_size=20)
        self.motor_msg = AckermannDriveStamped()  # 제어를 위한 속도, 조향각 정보를 담고 있는 ackermann_cmd 호출
        #self.tra=traffic()
        self.sensor = HPSensor()
        self.sensor.init(self.rate)
       
        #self.lane_detector = Camera()
        self.lane_detector = LaneDetector()
        self.obstacle_detector = Clustering()
        self.stanley = Stanley()
        self.start_time = 0
        self.count = 0

        ###### 제어 변수 #######
        # self.speed = 40
        self.speed = 20
        self.steering_angle = 0
        ########################

        self.obflag = False

    def calc_speed(self, angle):  # 최저속도(min): 10.0, 최고속도: 50.0(50.0)
        if angle > 0:
            slope = -0.7

        elif angle < 0:
            slope = 0.7

        else:
            slope = 0.0
       
        speed = (slope * angle) + 50.0

        return speed

    def control(self):
        """
        try : 라이다를 통해 장애물이 존재 시 회피를 시작하는 부분
        except : 라이다에서 장애물이 측정 되지않아 NaN이 되면 ValueError로 차선 인식 주행
        """
        # 주행 시작하자마자 조향틀어지는 문제 해결 (1초 동안은 speed=5, angle = 0으로 강제 명령)
        if time.time() - self.start_time <= 1.0:
            self.motor_msg.drive.speed = 5
            self.motor_msg.drive.steering_angle = 0
            
        ############################################## 장애물 회피 ##############################################
        try:
           # traffic_img=self.tra.main_traffic(self.sensor.real_cam)
           # cv2.imshow('trffic',traffic_img)
            curvature_angle, lane_idx = self.lane_detector.process(self.sensor.cam)

            calc_angle = self.obstacle_detector.process(self.sensor.lidar_filtered, self.sensor.real_cam, lane_idx)

            # AckermannDrive에 메세지전달
            self.motor_msg.drive.speed = int(self.speed)
            self.motor_msg.drive.steering_angle = int(calc_angle)

            print("Current motor speed: {}, Current motor angle: {}".format(
                self.motor_msg.drive.speed, self.motor_msg.drive.steering_angle))

            self.motor_pub.publish(self.motor_msg)
        ##################################################################################################### 
            

        ############################################## 차선주행 ##############################################
        except ValueError:
            #cv2.imshow('frame', self.sensor.cam)

            # 차선 주행이 되면, FSM의 변환을 방지
            self.obstacle_detector.fsm.transition(False)

            curvature_angle = self.lane_detector.process(self.sensor.cam)
            # curvature_angle = self.lane_detector.lane_detecing(self.sensor.cam)

            steering_angle = self.stanley.control(self.lane_detector.avg_middle, 320 , 1, curvature_angle)
            # steering_angle *= 0.8 # 모터(아두이노)로 보내는 신호 
            
            # =======================================================
            # steering_angle = curvature_angle # 모터로 보내는 조향각
            # speed = self.calc_speed(steering_angle)

            # AckermannDrive에 메세지전달
            self.motor_msg.drive.speed = int(self.speed)
            self.motor_msg.drive.steering_angle = int(steering_angle)

            print("Current motor speed: {}, Current motor angle: {}".format(
                self.motor_msg.drive.speed, self.motor_msg.drive.steering_angle))

            self.motor_pub.publish(self.motor_msg)
            self.rate.sleep()
        #####################################################################################################