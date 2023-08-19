#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import time
import rospy
import time
import numpy as np
import stopline_detector as sd
from std_msgs.msg import Int32MultiArray
## 0130 xycar_sensor -> ultrasonic, LaserScan 으로 바꾸기 
## 0130 xycar_msg.msg -> arduino로 보내는 msg로 바꾸기
from ackermann_msgs.msg import AckermannDriveStamped
from sensor_msgs.msg import LaserScan

#




class VerticalParking:

    def callback(self, msg):
        self.ultrasonic = msg

    def __init__(self):

        rospy.init_node('ultrasonic_sub')
        sub = rospy.Subscriber('ultrasonic', Int32MultiArray, self.callback)
        self.motor_pub = rospy.Publisher('ackermann_cmd', AckermannDriveStamped, queue_size=20)

        self.rate = rospy.Rate(50)  # 30Hz로 토픽 발행
        self.sensor.init(self.rate)

        self.motor_msg.angle = 0
        self.motor_msg.speed = 0
        
        self.lidar_right = 0

        self.right_memory = []
        self.right_back_memory = []
        self.left_back_memory = []
        self.left_memory = []

        self.right = 0
        self.right_back = 0
        self.left_back = 0
        self.left = 0

        self.dist = 0
        self.start = 0

        self.control_func = {
            'STATE 1': self.detect_right_wall_1,
            'STATE 2': self.detect_parking_space,
            'STATE 3': self.detect_right_wall_2,
            'STATE 4': self.parking_to_center,
            'STATE 5': self.parking,
            'STATE 6': self.exit_parking_space1,
            'STATE 7': self.exit_parking_space2,
            'STATE 8': self.check_stopline,
            'STATE 9': self.end_parking
        }
        self.STATE = 'STATE 2'

        self.steering_angle = 0
        self.mission_finished = False

    # ========================================
    # STATE 변경
    # ========================================
    def set_state(self, state):
        self.STATE = state
    
    # ========================================
    # 
    # ========================================
    def queue_size_check(self, *ultra_data):     
        for ultra in ultra_data:
            if len(list(ultra)) >= 5:
                ultra.pop(0)
    
    # ========================================
    # lidar 오른쪽 값 반환
    # ========================================
    def lidar_filter(self, msg):
        #lidar = np.array(msg[360:420])
        ##0130 수정<<
        lidar = np.array(msg[90:180])
        ## >>
        lidar = lidar[np.logical_not(np.isinf(lidar))]
        
        self.lidar_right = np.sum(lidar) / len(lidar)
        # print('lidar : ', self.lidar_right)

    # ========================================
    # Median Filter (Ultrasonic)
    # ========================================
    def median_filter(self, msg):
        self.right_memory.append(msg[1])
        self.right_back_memory.append(msg[0])

        self.left_back_memory.append(msg[6])
        self.left_memory.append(msg[5])

        self.queue_size_check(self.right_memory, self.right_back_memory, self.left_back_memory, self.left_memory)
        
        # Median Filter
        self.right = np.median(self.right_memory)
        self.right_back = np.median(self.right_back_memory)

        self.left_back = np.median(self.left_back_memory)
        self.left = np.median(self.left_memory)

    # ========================================
    # STATE 1
    # ========================================
    #lidar값 임상으로 얻어야함
    def detect_right_wall_1(self):
        if self.lidar_right >= 0.55:
            self.set_state('STATE 2')
            print('\n\n STATE 2 \n\n')
    
    # ========================================
    # STATE 2
    # ========================================
    def detect_parking_space(self):
        self.motor_msg.speed = 3
        self.dist += self.sensor.speed * 0.04
        
        
        #dist 값 확인해야 함
        if self.dist >= 5 and self.lidar_right == 0 :
            self.set_state('STATE 3')
            self.steering_angle = 0
            self.motor_msg.speed = 0
            self.dist = 0
            print('\n\n STATE 333333 \n\n')

    # ========================================
    # STATE 3
    # ========================================
    def detect_right_wall_2(self):
        self.motor_msg.speed = 3
        #조금가거나 많이exit_parking_space >= 5:
        self.set_state('STATE 4')
        print('\n\n STATE 4 \n\n')

    # ========================================
    # STATE 4
    # ========================================
    def parking_to_center(self):
        self.steering_angle = -20
        self.motor_msg.speed = 3

        # 중앙에 위치한 것으로 판단되면 STATE 7로 변경 / 500 값 확인
        if self.left_memory & self.right_memory < 500:
            self.steering_angle = 0
            self.motor_msg.speed = 0
            self.start = time.time()
            self.set_state('STATE 5')
            print('\n\n STATE 5 \n\n')

    # ========================================
    # STATE 5
    # ========================================
    def parking(self):
        # 타이머를 이용하여 3초간 정차
        if time.time() - self.start < 3:
            self.motor_msg.speed = 0
            self.steering_angle = 0
        else:
            # 3초간 정차 후 STATE 8으로 변경
            self.set_state('STATE 6')
            print('\n\n STATE 666666 \n\n')

    # ========================================
    # STATE 6
    # ========================================
    def exit_parking_space1(self):
        # 앞으로 일정 거리 전진
        self.motor_msg.speed = 3

        #초음파 값 확인
        if self.left_memory & self.right_memory < 500:
            self.steering_angle = 0
        else:
            self.set_state('STATE 7')
            print('\n\n STATE 77777 \n\n')

    # ========================================
    # STATE 7
    # ========================================
    def exit_parking_space2(self):
        # 우측 조향 후 우회전
        self.motor_msg.speed = 3
        self.steering_angle = 20
        self.set_state('STATE 8')
        print('\n\n STATE 8888 \n\n')

    # ========================================
    # STATE 8
    # ========================================
    
    def check_stopline(self):
        self.sd.process(self.sensor.cam)
        self.set_state('STATE 9')
        print('\n\n STATE 9999 \n\n')

    # ========================================
    # STATE 9 - 주차 종료
    # ========================================
    def end_parking(self):
        # 주차 미션 종료
        self.steering_angle = 0

        self.mission_finished = True
        print('\n--- MISSION FINISHED ---\n')

    # ========================================
    #
    # ========================================
    def process(self):
        rospy.loginfo('vertical parking')
        while not self.mission_finished:
            self.lidar_filter(self.sensor.lidar)
            self.median_filter(self.sensor.ultra)

            self.control_func[self.STATE]()

            self.motor_msg.angle = int(self.steering_angle)

            self.motor_pub.publish(self.motor_msg)

            self.rate.sleep()

        return self.mission_finished
