#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import rospy
import cv2
from vertical_parking1 import VerticalParking

rospy.init_node('Park_node')
#Parking_p=VerticalParking()
vertical_parking = VerticalParking()

if __name__ == '__main__':
	rospy.loginfo(rospy.get_name() + " started!")  # 노드 네임 출력
	while not rospy.is_shutdown():

		vertical_parking.process()
		#Parking_p.process()
		if cv2.waitKey(1) & 0xff == ord('q'): # 주석처리
			break
	cv2.destroyAllWindows()
