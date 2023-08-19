#!/usr/bin/env python3
# -*- coding:utf-8 -*-


import rospy
import cv2
from horse_power import HP

rospy.init_node('xytron_driving')	# 노드 생성 
horse_power = HP()

if __name__ == '__main__':
	# rospy.get_name() : 현재 실행 중인 ros의 노드 이름을 반환.  
	rospy.loginfo(rospy.get_name() + " started!")  # 노드 네임 출력 (/xytron_driving started!)
	while not rospy.is_shutdown():	# ros 종료 때까지 무한 루프 실행
		horse_power.control()
		if cv2.waitKey(1) & 0xff == ord('q'): # 주석처리 
			# &(비트 연산) - 컴퓨터 운영체제 64비트 이므로 비트 연산자 사용한 것. 
			break
	cv2.destroyAllWindows()




