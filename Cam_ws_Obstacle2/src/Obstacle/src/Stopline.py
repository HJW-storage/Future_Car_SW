#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import rospy
import cv2
from stopline_detector import StoplineDetector
from camera import Camera
from horse_power import HP
import numpy as np


rospy.init_node('obstacle_node')
#Parking_p=VerticalParking()
horse_power = HP()


if __name__ == '__main__':
	rospy.loginfo(rospy.get_name() + " started!")  # 노드 네임 출력
	while not rospy.is_shutdown():

		horse_power.control()
		#Parking_p.process()
		if cv2.waitKey(1) & 0xff == ord('q'): # 주석처리
			break
	cv2.destroyAllWindows()