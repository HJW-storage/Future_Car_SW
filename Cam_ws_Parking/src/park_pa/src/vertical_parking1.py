#! /usr/bin/env python3
# -*- coding:utf-8 -*-

import rospy
import time
import numpy as np
import stopline_detector as sd

## 0130 xycar_sensor -> ultrasonic, LaserScan 으로 바꾸기 
## 0130 xycar_msg.msg -> arduino로 보내는 msg로 바꾸기
from ackermann_msgs.msg import AckermannDriveStamped
from horse_power_sensor import HPSensor
#from obstacle_detector import Clustering
from pynput import keyboard # 키보드 입력을 위한 라이브러리 선언.

class VerticalParking:
    
    def __init__(self):
        
        self.rate = rospy.Rate(10)
        #rospy.init_node('ultrasonic_sub')
        
        self.motor_pub = rospy.Publisher('ackermann_cmd', AckermannDriveStamped, queue_size=100)

        self.motor_msg = AckermannDriveStamped()
        #self.obstacle_detector = Clustering()

        self.sensor = HPSensor()
        self.sensor.init(self.rate)

        # 차량 조향각과 속도 
        self.motor_msg.drive.steering_angle = -2
        self.motor_msg.drive.speed = 0
        
        self.lidar_right = 0

        # 초음파 센서 값 저장 배열 선언
        self.right_memory = []
        self.right_back_memory = []
        self.right_front_memory = []
        self.left_front_memory = []
        self.left_back_memory = []
        self.left_memory = []
        

        # 초음파 센서 값.
        self.right = 0
        self.right_back = 0
        self.right_front = 0
        self.left_front = 0
        self.left_back = 0
        self.left = 0

        self.dist = 0
        self.start = 0
        self.mission_finished = False

        #making jiwhan
        self.state1_cnt = 0
        self.state2_cnt = 0

        self.start_cnt = 0
        #making jiwhan

        # 키보드 입력을 위해 선언.
        self.listener = keyboard.Listener(on_press=self.on_key_press)
        self.listener.start()
        
        #check last
        self.control_func = {
            'STATE 1': self.go_staright,
            'STATE 2': self.pass_first_wall,
            'STATE 3': self.pass_second_wall,
            'STATE 4': self.into_room,
            'STATE 5': self.avoid_crash,
            'STATE 6': self.backward,
            'STATE 6-1': self.checking,
            'STATE 7': self.stay,
            'STATE 8': self.exit,
            'STATE 9': self.out_line,
            'STATE 10': self.end_parking
        }
        self.STATE = 'STATE 1'

    def on_key_press(self, key):
        if key == keyboard.KeyCode.from_char('s'):
            self.start_cnt = 1
            print("------------- s키가 눌렸습니다. 시작하겠습니다. -------------------------")
        elif key == keyboard.KeyCode.from_char('c'):
            self.start_cnt = 0
            self.motor_msg.drive.speed = 0
            self.motor_msg.drive.steering_angle = 0
            # print("speed : {}, angle : {}".format(self.motor_msg.drive.speed, self.motor_msg.drive.steering_angle))
            self.motor_pub.publish(self.motor_msg)
            print("------------- c키가 눌렸습니다. 정지하겠습니다. -------------------------")


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
            # 크기가 5 이상인 경우 첫 번째 요소를 삭제
            if len(list(ultra)) >= 5:
                ultra.pop(0)    
    
    # ========================================
    # lidar 오른쪽 값 반환
    # ========================================

    # ========================================
    # Median Filter (Ultrasonic)
    # ========================================
    def median_filter(self, *msg):
        self.right_memory.append(msg[1])
        self.right_back_memory.append(msg[0])
        self.right_front_memory.append(msg[2])
        self.left_front_memory.append(msg[3])
        self.left_back_memory.append(msg[5])
        self.left_memory.append(msg[4])

        self.queue_size_check(self.right_memory, self.right_back_memory, self.left_back_memory, self.left_memory)
        
        # Median Filter - 중앙값 구하기.
        self.right = np.median(self.right_memory)
        self.right_back = np.median(self.right_back_memory)
        #print("right back:",self.right_back)
        self.right_front = np.median(self.right_front_memory)
        self.left_front = np.median(self.left_front_memory)
        self.left_back = np.median(self.left_back_memory)
        self.left = np.median(self.left_memory)
    
    #1. 앞으로 쭉가기
    #go straight
    #2. 라이다 오른쪽에 a번차 지나감 or 초음파 오른쪽(2번)에 a번차 지나감
    #pass first wall
    #3. 라이다 오른쪽에 b번차 지나감 or 초음파 오른쪽(2번)에 b번차 지나감-> 오른쪽 뒤 초음파(1번)에 b번차 인식되면 멈춤
    #pass second wall
    #4. 오른쪽으로 핸들꺾고, 후진 -> 왼쪽 뒤 초음파(6번) 에 a번차 부딪히기 직전에 멈춤
    #into room
    #5. 왼쪽으로 핸들꺽고, 전진 -> 1초 후 멈춤
    #avoid crash
    #6. 핸들 똑바로하고 후진 -> 왼쪽뒤(6번),오른쪽뒤(1번) 초음파 간격확인 -> 너무 가까우면 반대쪽으로 핸들틀고 직진-> 다시후진
    #bachward

   

    #6-1. (기준정해야됨) 라이다오른쪽에 b번차 감지되면 정지.
    #7. 앞으로 나갔다가 핸들이빠이 꺽고 나가기    


    # ========================================
    # STATE 1 go straight
    # ========================================
    def go_staright(self):
        self.motor_msg.drive.speed = 3
        self.motor_msg.drive.steering_angle = -1
        # 첫번째 차량 검출 전까지 직진
        # 수정 가능 변수
        if 300 < self.right < 520:
            self.state1_cnt += 1
            self.start = time.time()
            # 초음파 값이 튀는 것을 방지하고자 state1_cnt를 도입. 어느정도 방지한다.
            if self.state1_cnt == 5:
                self.set_state('STATE 2')
                print("초음파 오른쪽 값 self.right: {}-------------------------".format(self.right))
                print('\n\n STATE 2 \n\n')

    # ========================================
    # STATE 2 pass first wall
    # ========================================
    def pass_first_wall(self):
        self.motor_msg.drive.speed = 3
        self.motor_msg.drive.steering_angle = -1
        #변수 75 -check second wall
        # 첫번째 차량을 지나고, 첫번쨰와 두번째 차량의 중간쯤 까지의 동작. 
        if(time.time() - self.start > 4) and self.right > 1000:
            self.start = time.time()
            print("초음파 오른쪽 값 self.right: {}-------------------------".format(self.right))
            self.set_state('STATE 3')
            print('\n\n STATE 3 \n\n')
            
    # ========================================
    # STATE 3 pass second wall
    # ========================================
    def pass_second_wall(self):
        self.motor_msg.drive.speed = 3
        self.motor_msg.drive.steering_angle = -2
        #self.dist += self.motor_msg.drive.speed
            
        #dist 값 확인해야 함
        #변수 2.1
        #두번째 차량을 향해서 직진 3초하고, 두번째 차량이 감지되면 다음 상태로 넘어감. 
        # if (time.time() - self.start > 0.5) and (100 < self.right < 1000):
        if (time.time() - self.start > 3):
            self.start = time.time()
            print("초음파 오른쪽 값 self.right: {}-------------------------".format(self.right))
            self.set_state('STATE 4')
            print('\n\n STATE 4 \n\n')

    # ========================================
    # STATE 4 into room
    # ========================================
    def into_room(self):
        if time.time() - self.start < 3:
            # 왼쪽으로 바퀴 조향.
            self.motor_msg.drive.steering_angle = 20
            self.motor_msg.drive.speed = 0
        elif 3 < time.time() - self.start < 8:
            # 바퀴는 왼쪽인 상태로 직진.
            self.motor_msg.drive.speed = 3
        elif 8 < time.time() - self.start < 10:
            # 후진 준비. 바퀴 오른쪽으로 조향.
            self.motor_msg.drive.steering_angle = -20
            self.motor_msg.drive.speed = 0
        elif 10 < time.time() - self.start < 15:
            # 후진.
            self.motor_msg.drive.speed = -3
        #조금가거나 많이 exit_parking_space >= 5:
        #변수 400
        elif (time.time() - self.start) > 15 or (self.left_back < 2000):
            print("초음파 오른쪽 값 self.left_back: {}-------------------------".format(self.left_back))
            self.start = time.time()
            self.set_state('STATE 5')
            print('\n\n STATE 5 \n\n')

    # ========================================
    # STATE 5 avoid crash
    # ========================================
    def avoid_crash(self):
        #print('start time:', self.start)
        # 변수 3 (가는 시간)
        if time.time() - self.start < 3:
            self.motor_msg.drive.speed = 0
            # 바퀴 왼쪽 조향. 
            self.motor_msg.drive.steering_angle = 20
        if 3 < time.time() - self.start < 5:
            # 바퀴 왼쪽인 상태로 직진. 
            self.motor_msg.drive.speed = 3
        elif time.time() - self.start > 5: 
            self.start = time.time()
            self.set_state('STATE 6')
            print('\n\n STATE 6 \n\n')

    # ========================================
    # STATE 6 backward
    # ========================================
    def backward(self):
        # 후진 동작 진행.
        if time.time() - self.start < 3:
            # 오른쪽 조향. 후진.
            self.motor_msg.drive.steering_angle = -20
            self.motor_msg.drive.speed = -3
        # if 3 < time.time() - self.start < 4:
        #     self.motor_msg.drive.speed = -3
        elif (3 < time.time() - self.start < 9):
            # self.motor_msg.drive.speed = 0
            self.motor_msg.drive.speed = -3
            self.motor_msg.drive.steering_angle = 10
        # elif (7 < time.time() - self.start < 10):
        #     self.motor_msg.drive.speed = -3
            
        #변수 560
        elif (time.time() - self.start > 10) or (self.left_front < 1000 and self.left <1000) or (self.right_front < 2000 and self.right < 2000):
            self.start = time.time()
            self.set_state('STATE 7')
            print('\n\n STATE 7 \n\n')
        elif self.right_back < 150  or self.left_back < 150 :
            self.motor_msg.drive.speed = 0
            self.start = time.time()
            self.set_state('STATE 6-1')
            print('\n\n STATE 6-1 \n\n')

    # ========================================
    # STATE 6-1 checking
    # ========================================
    def checking(self):
        if time.time() - self.start < 3:
            self.motor_msg.drive.speed = 0
            self.motor_msg.drive.steering_angle = 20
        elif (time.time() - self.start < 8):
            self.motor_msg.drive.speed = 3
            self.motor_msg.drive.steering_angle = 20
        elif 8 < time.time() - self.start < 12:
            self.start = time.time()
            self.motor_msg.drive.speed = -3
            self.motor_msg.drive.steering_angle = -20
            self.set_state('STATE 7')
            print('\n\n STATE 7 \n\n')

        # 타이머를 이용하여 3초간 정차

        #if time.time() - self.start < 3:
        #    self.motor_msg.drive.speed = 0
        #    self.steering_angle = 0
        #else:
        #    # 3초간 정차 후 STATE 8으로 변경
        #    self.set_state('STATE 6')
        #    print('\n\n STATE 666666 \n\n')

    # ========================================
    # STATE 7 stay
    # ========================================
    def stay(self):
        # 3초 대기
        self.motor_msg.drive.speed = 0
        self.motor_msg.drive.steering_angle = -1

        if time.time() - self.start > 5:
            self.start = time.time()
            self.set_state('STATE 8')
            print('\n\n STATE 8 \n\n')

    # ========================================
    # STATE 8 exit
    # ========================================
    def exit(self):
        
        if time.time() - self.start < 2:
            # 바퀴 일자로 전진. steering_angle = -1로 한 이유는 차가 왼쪽으로 치우치는 경향이 있어서 의도적으로 오른쪽 각도를 살짝 줌.
            self.motor_msg.drive.steering_angle = -1
            self.motor_msg.drive.speed = 3
        elif 2 < time.time() - self.start < 3.5:
            # 오른쪽 조향, 전진.
            self.motor_msg.drive.steering_angle = -20
            self.motor_msg.drive.speed = 3
        else:
            # self.motor_msg.drive.speed = 3
            # # 왼쪽조향. 
            # self.steering_angle = 20
            self.start = time.time()
            self.set_state('STATE 9')
            print('\n\n STATE 9 \n\n')

    # ========================================
    # STATE 9 out line
    # ========================================
    def out_line(self):
        if time.time() - self.start < 4:
            # 오른쪽 조향, 전진.
            self.motor_msg.drive.steering_angle = -20
            self.motor_msg.drive.speed = 20
        elif 4 <= time.time() - self.start < 5:
            # 오른쪽 조향, 전진.
            self.motor_msg.drive.steering_angle = 20
            self.motor_msg.drive.speed = 0
        elif 5 <= time.time() - self.start < 7:
            # 오른쪽 조향, 후진.
            self.motor_msg.drive.steering_angle = 20
            self.motor_msg.drive.speed = -5
        # 8월 16일 추가한 부분. 
        # elif 4 < time.time() - self.start < 6:
        #     self.motor_msg.drive.steering_angle = 20
        #     self.motor_msg.drive.speed = -3
        # elif 6 < time.time() - self.start < 8:
        #     self.motor_msg.drive.steering_angle = 0
        #     self.motor_msg.drive.speed = 3
        else:
            self.set_state('STATE 10')
            self.start = time.time()
            # self.motor_msg.drive.steering_angle = 0
            print('\n\n STATE 10 \n\n')


    # ========================================
    # STATE 10 - 주차 종료
    # ========================================
    def end_parking(self):
        # 주차 미션 종료
        if time.time() - self.start < 2:
            self.motor_msg.drive.steering_angle = -20
            self.motor_msg.drive.speed = 3
        elif 2 <= time.time() - self.start < 4:
            # self.motor_msg.drive.steering_angle = 0
            self.motor_msg.drive.speed = 5
        elif 4 <= time.time() - self.start < 6:
            self.motor_msg.drive.steering_angle = +1
            self.motor_msg.drive.speed = 1   
        elif 6 <= time.time() - self.start < 11:
            self.motor_msg.drive.steering_angle = +1
            self.motor_msg.drive.speed = 20

        else:
            self.mission_finished = True
            print('\n--- MISSION FINISHED ---\n')

    # ========================================
    #
    # ========================================
    def process(self):
        # rospy.loginfo('vertical parking')
        

        if self.start_cnt == 1:
        # 주차 미션 종료되기 전까지 반복 실행.
            while not self.mission_finished:
                # print("일: {}, 이: {}, 삼: {}, 사: {}, 오: {}, 육: {}".format(
                # self.sensor.ultra_1,
                # self.sensor.ultra_2,
                # self.sensor.ultra_3,
                # self.sensor.ultra_4,
                # self.sensor.ultra_5,
                # self.sensor.ultra_6))

                self.median_filter(self.sensor.ultra_1,self.sensor.ultra_2,self.sensor.ultra_3,self.sensor.ultra_4,self.sensor.ultra_5,self.sensor.ultra_6)

                self.control_func[self.STATE]()

                #self.motor_msg.drive.steering_angle = int(self.steering_angle)

                self.motor_pub.publish(self.motor_msg)

                self.rate.sleep()

            return self.mission_finished