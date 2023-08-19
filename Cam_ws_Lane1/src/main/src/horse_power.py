#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import cv2
import rospy
from ackermann_msgs.msg import AckermannDriveStamped
from time import time
from horse_power_sensor import HPSensor
from collections import deque   # 큐 구현 자료구조를 사용하기 위함

from controller import Stanley  # controller.py 
#from lane_detector_jw import Camera
from lane_detector2 import LaneDetector  # lane_detector2.py 
from obstacle_detector import Clustering  # obstacle_detector.py 
# from traffic import traffic
from pynput import keyboard

class HP:

    def __init__(self):
        self.rate = rospy.Rate(10)  # 20Hz로 토픽 발행 #1초에 10번 반복할 수 있도록 타임슬롯 할당.
        self.motor_pub = rospy.Publisher('ackermann_cmd', AckermannDriveStamped, queue_size=20) # 토픽 발행
        self.motor_msg = AckermannDriveStamped()  # 제어를 위한 속도, 조향각 정보를 담고 있는 ackermann_cmd 호출
        #self.tra=traffic()
        self.sensor = HPSensor()
        self.sensor.init(self.rate)
       
        #self.lane_detector = Camera()
        self.lane_detector = LaneDetector()
        self.obstacle_detector = Clustering()
        self.stanley = Stanley()
        self.start_time = time()    # 시작 시간을 측정. 
        self.que_speed = deque()
        self.que_angle = deque()
        
        self.start_cnt = 0
        
        self.listener = keyboard.Listener(on_press=self.on_key_press)
        self.listener.start()

    def on_key_press(self, key):
        if key == keyboard.KeyCode.from_char('s'):
            self.start_cnt = 1
            print("------------- s키가 눌렸습니다. 시작하겠습니다. -------------------------")
        elif key == keyboard.KeyCode.from_char('c'):
            self.start_cnt = 0
            self.motor_msg.drive.speed = 0
            self.motor_msg.drive.steering_angle = 0
            print("speed : {}, angle : {}".format(self.motor_msg.drive.speed, self.motor_msg.drive.steering_angle))
            self.motor_pub.publish(self.motor_msg)
            print("------------- c키가 눌렸습니다. 정지하겠습니다. -------------------------")

    def calc_speed(self, angle):  # 최저속도(min): 10.0, 최고속도: 50.0(50.0)
        if angle > 0:
            slope = -0.23

        elif angle < 0:
            slope = 0.23

        else:
            slope = 0.0
       
        speed = (slope * angle) + 63.0

        return speed

    def control(self):
        # 주행 시작하자마자 조향틀어지는 문제 해결 (1초 동안은 speed=5, angle = 0으로 강제 명령)
        if time() - self.start_time <= 3.5: # time() : 현재 시간 
            self.motor_msg.drive.speed = 5
            self.motor_msg.drive.steering_angle = 0
            
        try:
           # traffic_img=self.tra.main_traffic(self.sensor.real_cam)
           # cv2.imshow('traffic',traffic_img)
            steering_angle = self.obstacle_detector.process(self.sensor.lidar_filtered, self.sensor.real_cam)
            
            # 장애물이 정면에 있으면 정지
            if abs(steering_angle) < 3:
                steering_angle = 0
                speed = 0
            else:
                speed = 10
       
        except ValueError:
            #cv2.imshow('frame', self.sensor.cam)
            curvature_angle = self.lane_detector.process(self.sensor.cam)
            #curvature_angle = self.lane_detector.lane_detecing(self.sensor.cam)

            steering_angle = self.stanley.control(self.lane_detector.avg_middle, 320 , 1, curvature_angle)
            #steering_angle *= 2.5 # 모터로 보내는 조향각
            #steering_angle = curvature_angle # 모터로 보내는 조향각
            speed = self.calc_speed(steering_angle)

        # 회전딜레이주기 
        
        print("append")
        self.que_speed.append(int(speed))
        self.que_angle.append(int(steering_angle))
        if len(self.que_speed) > 2:
            self.motor_msg.drive.speed = self.que_speed[0]
            self.motor_msg.drive.steering_angle = self.que_angle[0]
            # print("Current motor speed: {}, Current motor angle: {}".format(
            # self.motor_msg.drive.speed, self.lane_detector.real_angle))

            self.que_speed.popleft()
            self.que_angle.popleft()

        # self.motor_msg.drive.speed = int(speed)
        # self.motor_msg.drive.steering_angle = int(steering_angle)
        # print("Current motor speed: {}, Current motor angle: {}".format(
        # self.motor_msg.drive.speed, self.motor_msg.drive.steering_angle))    

        # motor_msg를 토픽에 담아 발행

        # 기존
        # self.motor_pub.publish(self.motor_msg) #if 문 안에넣기 또는 밖에넣기 골라야함
        # self.rate.sleep() 
        # 기존       
        if self.start_cnt == 1:
            # motor_msg를 토픽에 담아 발행 
            self.motor_pub.publish(self.motor_msg) #if 문 안에넣기 또는 밖에넣기 골라야함

            self.rate.sleep()


#######################################################################################################################


# #!/usr/bin/env python3
# # -*- coding:utf-8 -*-
# import cv2
# import rospy
# from ackermann_msgs.msg import AckermannDriveStamped
# from time import time
# from horse_power_sensor import HPSensor
# from collections import deque   # 큐 구현 자료구조를 사용하기 위함

# from controller import Stanley  # controller.py 
# #from lane_detector_jw import Camera
# from lane_detector2 import LaneDetector  # lane_detector2.py 
# from obstacle_detector import Clustering  # obstacle_detector.py 
# # from traffic import traffic
# import keyboard

# class HP:

#     def __init__(self):
#         self.rate = rospy.Rate(10)  # 20Hz로 토픽 발행 #1초에 10번 반복할 수 있도록 타임슬롯 할당.
#         self.motor_pub = rospy.Publisher('ackermann_cmd', AckermannDriveStamped, queue_size=20) # 토픽 발행
#         self.motor_msg = AckermannDriveStamped()  # 제어를 위한 속도, 조향각 정보를 담고 있는 ackermann_cmd 호출
#         #self.tra=traffic()
#         self.sensor = HPSensor()
#         self.sensor.init(self.rate)
       
#         #self.lane_detector = Camera()
#         self.lane_detector = LaneDetector()
#         self.obstacle_detector = Clustering()
#         self.stanley = Stanley()
#         self.start_time = time()    # 시작 시간을 측정. 
#         self.que_speed = deque()
#         self.que_angle = deque()
        
#         self.start_cnt = 0

#     def calc_speed(self, angle):  # 최저속도(min): 10.0, 최고속도: 50.0(50.0)
#         if angle > 0:
#             slope = -0.23

#         elif angle < 0:
#             slope = 0.23

#         else:
#             slope = 0.0
       
#         speed = (slope * angle) + 63.0

#         return speed

#     def control(self):
#         # 주행 시작하자마자 조향틀어지는 문제 해결 (1초 동안은 speed=5, angle = 0으로 강제 명령)
#         if time() - self.start_time <= 3.5: # time() : 현재 시간 
#             self.motor_msg.drive.speed = 5
#             self.motor_msg.drive.steering_angle = 0
            
#         try:
#            # traffic_img=self.tra.main_traffic(self.sensor.real_cam)
#            # cv2.imshow('traffic',traffic_img)
#             steering_angle = self.obstacle_detector.process(self.sensor.lidar_filtered, self.sensor.real_cam)
            
#             # 장애물이 정면에 있으면 정지
#             if abs(steering_angle) < 3:
#                 steering_angle = 0
#                 speed = 0
#             else:
#                 speed = 10
       
#         except ValueError:
#             #cv2.imshow('frame', self.sensor.cam)
#             curvature_angle = self.lane_detector.process(self.sensor.cam)
#             #curvature_angle = self.lane_detector.lane_detecing(self.sensor.cam)

#             steering_angle = self.stanley.control(self.lane_detector.avg_middle, 320 , 1, curvature_angle)
#             #steering_angle *= 2.5 # 모터로 보내는 조향각
#             #steering_angle = curvature_angle # 모터로 보내는 조향각
#             speed = self.calc_speed(steering_angle)

#         # 회전딜레이주기 
        
#         print("append")
#         self.que_speed.append(int(speed))
#         self.que_angle.append(int(steering_angle))
#         if len(self.que_speed) > 2:
#             self.motor_msg.drive.speed = self.que_speed[0]
#             self.motor_msg.drive.steering_angle = self.que_angle[0]
#             print("Current motor speed: {}, Current motor angle: {}".format(self.motor_msg.drive.speed, self.lane_detector.real_angle))

#             self.que_speed.popleft()
#             self.que_angle.popleft()

#         # self.motor_msg.drive.speed = int(speed)
#         # self.motor_msg.drive.steering_angle = int(steering_angle)
#         # print("Current motor speed: {}, Current motor angle: {}".format(
#         # self.motor_msg.drive.speed, self.motor_msg.drive.steering_angle))    


        # if keyboard.is_pressed('s'):
        #     self.start_cnt = 1
        #     print("------------- s키가 눌렸습니다. 시작하겠습니다. -------------------------")
        # elif keyboard.is_pressed('c'):
        #     self.start_cnt = 0
        #     print("------------- c키가 눌렸습니다. 정지하겠습니다. -------------------------")
        #     self.motor_msg.drive.speed = 0
        #     self.motor_msg.drive.steering_angle = 0
        #     self.motor_pub.publish(self.motor_msg) 

        # while self.start_cnt == 1:
        #     # motor_msg를 토픽에 담아 발행 
        #     self.motor_pub.publish(self.motor_msg) #if 문 안에넣기 또는 밖에넣기 골라야함

        #     self.rate.sleep()