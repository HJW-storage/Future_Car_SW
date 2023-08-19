#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import numpy as np
import math
from sklearn.cluster import DBSCAN
import os
######################
import rospy
from time import time
from ackermann_msgs.msg import AckermannDriveStamped
# from reprojection import RP
from FSM import FiniteStateMachine
######################

class Clustering:
    def __init__(self):

        # ROS 관련 #####################################################################################################
        self.rate = rospy.Rate(10)  # 30Hz로 토픽 발행
        self.motor_pub = rospy.Publisher('ackermann_cmd', AckermannDriveStamped, queue_size=20)  # motor msg publisher
        self.motor_msg = AckermannDriveStamped()  # xycar 제어를 위한 속도, 조향각 정보를 담고 있는 xycar_motor 호출

        # FSM 객체 생성
        self.fsm = FiniteStateMachine()
        ################################################################################################################


        # 클러스터 관련 (장애물 인식) ####################################################################################
        epsilon = 1.0   # 중심점 기준 반경 길이 (meter)
        min_sample = 30  # 클러스터로 묶기위한 최소 포인트 갯수, 이보다 작으면 노이즈로 간주
        ################################################################################################################

        # 클러스터링 수행 #############################################################################
        self.model = DBSCAN(eps=epsilon, min_samples=min_sample, algorithm='ball_tree', leaf_size=20)
        ##############################################################################################

        # LiDAR측정 범위 설정 #################################
        """
        최적값:
        
        LiDAR setting : [self.limit_range,  self.limit_degree]  &  HP : self.speed
                        [     1.4        ,         60        ]             20
        """

        self.limit_range = 1.6
        self.limit_degree = 45
        ######################################################

        # 제어관련 변수 ############################
        self.steering_angle = 0

        self.count = 0
        self.wait_flag = 0
       
        self.BOTH, self.LEFT, self.RIGHT = 0, 1, 2
        self.roi_setting = self.BOTH

        self.mission_finished = False
        ###########################################
    
    def coordinate_transform(self, msg):

        #################################################################################
        # Lidar 측정 각도 범위 배열 생성
        # msg.ranges 에는 라이다가 0.4도씩 회전하면서 측정되는 거리를 배열형태로 저장
        # 따라서, msg.ranges의 인덱스가 1 증가하면, 각도상에선 0.4도 증가한 것이 된다.
        # 결국 특정 인덱스에서 측정된 거리에 해당하는 각도를 알기 위해선
        # 라이다센서의 최소각도부터 시작 하여, 인덱스 값과 라이다 분해능을 곱하여 인덱스와 각도를 매칭시킨다.
        # 관계식 : 해당 인덱스에서의 각도 = angle_increment * index
        ##################################################################################
        degree = [(msg.angle_min + msg.angle_increment * idx) * (180 / math.pi) for idx, value in enumerate(msg.ranges)] # 해당 인덱스에서의 각도를 배열로 생성
        ranges = msg.ranges

        ranged_degree = np.array([])
        ranged_ranges = np.array([])
        
        # 원하는 각도 범위를 추출
        # 180도가 정면을 가리키며, 시계 방향으로 각도가 증가한다고 가정
        desired_center_angle = 90
        desired_min_angle = desired_center_angle - self.limit_degree  # -60 degrees from center
        desired_max_angle = desired_center_angle + self.limit_degree   # 60 degrees from center
        
        for idx, value in enumerate(msg.ranges):
            if (desired_min_angle <= degree[idx] <= desired_max_angle) and ranges[idx] <= self.limit_range:
                # 거리가 inf일때 오류 발생을 막기위함
                if ranges[idx] is np.inf:
                    ranges[idx] = np.NaN
                
                # 처리된 라이다 값만 전역 변수에 저장
                ranged_degree = np.append(ranged_degree, degree[idx])
                ranged_ranges = np.append(ranged_ranges, ranges[idx])

        # 각도를 라디안 단위로 변환
        thetas = np.deg2rad(ranged_degree)

        # 장애물의 상대 x, y 위치를 계산
        x = ranged_ranges * np.cos(thetas)
        y = ranged_ranges * np.sin(thetas)

        coordinate = np.column_stack((x, y))

        # 범위 내의 라이다 데이터 출력
        print("========================================")
        print("x : {}".format(x))
        print("y : {}".format(y))
        print("LiDAR data : {}".format(coordinate))
        print("========================================")

        return coordinate

    def clustering(self, data):

        centroid_list = []  # 중심점을 저장할 리스트 선언

        # 학습 시작
        # 반경(epsilon)내에 최소 20개의 포인트(min_sample)을 가지고 있을 경우 하나의 군집으로 판단이 된다.
        self.model.fit(data)

        for label in list(np.unique(self.model.labels_)):
            if label == -1: # label이 -1일 경우 Noise 성분
                continue

            label_index = np.where(self.model.labels_ == label)
            cluster = data[label_index]
            centroid = np.mean(cluster, axis=0)
            centroid_list.append(centroid)

        print("Detect : ",np.unique(self.model.labels_))

        return centroid_list
    
    ################################################################################################
    def avoidance(self, centroid_list):

        # 중심점 list에서 euclidean distance를 구함
        distance_list = [np.linalg.norm(centroid) for centroid in centroid_list]
       
        # 가장 거리가 가까운 점이 회피 대상이라 가정, x, y좌표가 반대로 출력되므로 역 인덱싱 적용
        closest_centroid = centroid_list[np.argmin(distance_list)][::-1]
        
        # 장애물과의 각도를 계산
        # angle = (math.atan(closest_centroid[1] / closest_centroid[0]) * (180 / math.pi)) 

        # print("centroid_list[0] : {}".format(centroid_list[0]))
        # print("angle : {}".format(angle))

        ############################################################
        # 장애물이 더 이상 감지되지 않는 경우
        detected_obstacle = bool(centroid_list)

        print("detected_obstacle {}".format(detected_obstacle))

        # 상태 전이 로직을 수행하기 전에 장애물 감지 여부를 전달합니다.
        self.fsm.transition(detected_obstacle)
        # self.fsm.transition(centroid_list)
        
        # 상태 기반 회피
        if self.fsm.current_state == "AvoidLeft":
            angle = -20

        elif self.fsm.current_state == "AvoidRight":
            angle = 20
        ############################################################

        # 최대, 최소 각도 제한
        if angle < 0.0:
            if angle <= -20.0: # 각도 범위 제한
                angle = -20.0
        elif angle > 0.0:
            if angle >= 20.0: # 각도 범위 제한
                angle = 20.0

        # print("angle : {}".format(angle))

        return angle
        
    def process(self, msg, img):

        # os.system("clear")
        coordinate = self.coordinate_transform(msg)
        centroid_list = self.clustering(coordinate)
        self.steering_angle = self.avoidance(centroid_list)

        print("centroid_list : {}".format(centroid_list))

        return self.steering_angle 