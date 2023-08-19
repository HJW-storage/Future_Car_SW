# #!/usr/bin/env python3
# # -*- coding:utf-8 -*-


# # import numpy as np
# # import cv2
# # from camera import Camera
# # import math


# # # =============================================
# # # 주행을 위한 알고리즘 클래스 정의
# # # =============================================
# # class LaneDetector:

# #     # ========================================
# #     # 변수 선언 및 초기화
# #     # ========================================
# #     def __init__(self):

# #         self.camera = Camera()
# #         # 슬라이딩 윈도우 출력 창 크기 좌우 확장 값으로, 좌우로 window_margin 만큼 커짐
# #         # 슬라이딩 윈도우 출력 창 가로 크기 : WIDTH + 2*window_margin
# #         self.window_margin = 20
# #         self.xycar_length = 0.46 # 0.35 meter
# #         self.xycar_width = 0.3
# #         self.leftx_mid, self.rightx_mid = self.camera.WIDTH *2 // 8, self.camera.WIDTH * 6 // 8  # 슬라이딩 윈도우 기준점 초기 좌표
# #         self.leftx_base, self.rightx_base = self.leftx_mid, self.rightx_mid  # 슬라이딩 윈도우 이전값

# #         self.left_a, self.left_b, self.left_c = [0], [0], [self.leftx_mid]  # 왼쪽 차선으로부터 나온 2차 곡선 방정식의 계수를 저장하기 위한 변수
# #         self.right_a, self.right_b, self.right_c = [0], [0], [self.rightx_mid]
# #         # 오른쪽 차선으로부터 나온 2차 곡선 방정식의 계수를 저장하기 위한 변수
# #         # 처음 차선이 인식되지 않는 경우를 대비하여, 초기값은 슬라이딩 윈도우 기준점으로부터 직진으로 방정식을 그리도록 함
# #         self.leftx_current, self.rightx_current = [self.leftx_mid], [self.rightx_mid]
# #         self.ref_diff = self.rightx_mid - self.leftx_mid
# #         self.ref_mid = self.ref_diff // 2
# #         self.lefty_current, self.righty_current = [480], [480]

# #         # 양쪽 차선 곡선 좌표 생성
# #         ### Linear y 값 생성 (0, 1, 2, ..., 479)
# #         self.ploty = np.linspace(0, self.camera.HEIGHT - 1, self.camera.HEIGHT)
# #         # self.ploty2 = np.linspace(0, (self.camera.HEIGHT+self.xycar_length) - 1, (self.camera.HEIGHT+self.xycar_length))
# #         self.wins_y = np.linspace(464, 16, 15) # 슬라이딩 윈도우의 y좌표값 

# #         # 양쪽 차선 인식 기준 x값 평균을 저장하는 변수, 이전 조향각을 저장하기위한 변수 선언.
# #         self.avg_middle, self.steering_memory = 0.0, 0.0
# #         self.right_aaa=0
# #         self.real_angle=0

# #         # making jiwhan
# #         self.has_switched = False # 처음에는 부호를 바꾸지 않았음. 양쪽 차선이 인식 안될 경우, 사용할 flag변수. 
# #         # making jiwhan

# #     # ========================================
# #     # 슬라이딩 윈도우
# #     # ====================
# #     # < input >
# #     # img : 입력 이미지
# #     # nwindows : 조사창 개수 (좌우 각각 nwindows개씩)
# #     # margin : 현재 기준 위치로부터 조사창의 좌우 길이 (-margin ~ +margin)
# #     #          조사창 가로 길이 : margin*2
# #     # minpix : 조사창 내부에서 차선이 검출된 것으로 판단할 최소 픽셀 개수
# #     # draw_windows : 결과창 출력 여부
# #     #
# #     # ====================
# #     # < return >
# #     # out_img : 출력 이미지
# #     # window_img : 슬라이딩 윈도우 출력을 위한 이미지 (너비 확장)
# #     # left_fitx : 왼쪽 차선 곡선 방정식 x 좌표
# #     # right_fitx : 오른쪽 차선 곡선 방정식 x 좌표
# #     # left_lane_detected : 왼쪽 차선 인식 여부
# #     # right_lane_detected : 오른쪽 차선 인식 여부
# #     #
# #     # ========================================


# #     def sliding_window(self, img, nwindows=7, margin=30, minpix=45, draw_windows=False):
# #         # 크기 3의 비어있는 배열 생성
# #         left_fit_ = np.empty(3)
# #         right_fit_ = np.empty(3)

# #         # 0과 1로 이진화된 영상을 3채널의 영상으로 만들기 위해 3개를 쌓은 후 *255
# #         out_img = np.dstack((img, img, img)) * 255
       
# #         # 너비의 중앙값
# #         midpoint = self.camera.WIDTH // 2

# #         # 조사창의 높이 설정
# #         # 전체 높이에서 설정한 조사창 개수만큼 나눈 값
# #         window_height = self.camera.HEIGHT // nwindows 

# #         # 0이 아닌 픽셀의 x,y 좌표 반환 (흰색 영역(차선)으로 인식할 수 있는 좌표)
# #         nonzero = img.nonzero() # 0이 아닌 것을 찾는다.
# #         nonzeroy = np.array(nonzero[0])
# #         nonzerox = np.array(nonzero[1])

# #         # 이전 프레임으로부터 기준점의 좌표를 받아옴
# #         # 양쪽 차선 확인 위치 업데이트
# #         # 이 값을 기준으로 조사창을 생성하여 차선 확인
# #         leftx_current = self.leftx_base
# #         rightx_current = self.rightx_base

# #         # 차선 확인 시 검출이 되지 않는 경우를 대비해서 바로 이전(화면상 바로 아래) 조사창으로부터 정보를 얻기 위한 변수
# #         # 이를 이용해서 조사창 위치의 변화량을 파악
# #         # 초기값으로는 현재 기준 좌표를 넣어줌
# #         leftx_past = leftx_current
# #         rightx_past = rightx_current
# #         rightx_past2 = rightx_past

# #         # 양쪽 차선 픽셀 인덱스를 담기 위한 빈 배열 선언
# #         # 차선의 방정식을 구하거나 차선 인식 판단 여부에 사용
# #         left_lane_inds = []
# #         right_lane_inds = []

# #         # 슬라이딩 윈도우 좌표 값을 담기 위한 빈 배열
# #         left_wins_x = []
# #         right_wins_x = []

# #         # 설정한 조사창 개수만큼 슬라이딩 윈도우 생성
# #         for window in range(nwindows):
            
# #             # makin jiwhan
# #             if window == 0:
# #                 # print("widno index ================================= {}".format(window))
# #                 # 조사창 크기 및 위치 설정
# #                 win_y_low = self.camera.HEIGHT - ((window + 1) * window_height)
# #                 # n번째 조사창 윗변 y 좌표 : (전체 높이) - (n * 조사창 높이)
# #                 win_y_high = self.camera.HEIGHT - (window * window_height)
# #                 # 양쪽 차선의 조사창의 너비를 현재 좌표로부터 margin만큼 양 옆으로 키움
# #                 win_xleft_low = int(self.leftx_base - margin)
# #                 win_xleft_high = int(self.leftx_base + margin)
# #                 win_xright_low = int(self.rightx_base - margin)
# #                 win_xright_high = int(self.rightx_base + margin)
# #             else: 
# #                 # 조사창 크기 및 위치 설정
# #                 win_y_low = self.camera.HEIGHT - ((window + 1) * window_height)
# #                 # n번째 조사창 윗변 y 좌표 : (전체 높이) - (n * 조사창 높이)
# #                 win_y_high = self.camera.HEIGHT - (window * window_height)
# #                 # 양쪽 차선의 조사창의 너비를 현재 좌표로부터 margin만큼 양 옆으로 키움
# #                 win_xleft_low = int(leftx_current - margin)
# #                 win_xleft_high = int(leftx_current + margin)
# #                 win_xright_low = int(rightx_current - margin)
# #                 win_xright_high = int(rightx_current + margin)
# #             # making jiwhan

# #             # # 이게 원본임. 
# #             # # 조사창 크기 및 위치 설정
# #             #     win_y_low = self.camera.HEIGHT - ((window + 1) * window_height)
# #             #     # n번째 조사창 윗변 y 좌표 : (전체 높이) - (n * 조사창 높이)
# #             #     win_y_high = self.camera.HEIGHT - (window * window_height)
# #             #     # 양쪽 차선의 조사창의 너비를 현재 좌표로부터 margin만큼 양 옆으로 키움
# #             #     win_xleft_low = int(leftx_current - margin)
# #             #     win_xleft_high = int(leftx_current + margin)
# #             #     win_xright_low = int(rightx_current - margin)
# #             #     win_xright_high = int(rightx_current + margin)

# #             # 조사창 그리기
# #             if draw_windows == True:
# #                 # cv2.rectangle(img, start(시작 좌표), end(종료 좌표), color, thickness)
# #                 # 왼쪽 차선
# #                 cv2.rectangle(out_img, (win_xleft_low, win_y_low), (win_xleft_high, win_y_high), (100, 100, 255), 3)
# #                 # 오른쪽 차선
# #                 cv2.rectangle(out_img, (win_xright_low, win_y_low), (win_xright_high, win_y_high), (100, 100, 255), 3)

# #             # 조사창 내부에서 0이 아닌 픽셀의 인덱스 저장
# #             good_left_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high)
# #                               & (nonzerox >= win_xleft_low) & (nonzerox < win_xleft_high)).nonzero()[0]
# #             good_right_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high)
# #                                & (nonzerox >= win_xright_low) & (nonzerox < win_xright_high)).nonzero()[0]

# #             # 양쪽 차선의 인덱스 저장
# #             left_lane_inds.append(good_left_inds)
# #             right_lane_inds.append(good_right_inds)

# #             # 조사창 내부에서 0이 아닌 픽셀 개수가 기준치를 넘으면 해당 픽셀들의 인덱스 평균값(x좌표 평균)으로 다음 조사창의 위치(x좌표)를 결정
# #             if len(good_left_inds) > minpix:
# #                 leftx = nonzerox[good_left_inds]
# #                 leftx_current = int(np.mean(leftx))
           
# #             if len(good_right_inds) > minpix:
# #                 rightx = nonzerox[good_right_inds]
# #                 rightx_current = int(np.mean(rightx))
               

# #             x_diff = rightx_current - leftx_current

# #             # 양쪽 차선 중 하나만 인식된 경우 반대편 차선에서 나타난 인덱스 변화량과 동일하게 인덱스 설정
# #             # 인식된 차선의 방향과 동일하게 그려짐
# #             if len(good_left_inds) < minpix:
# #                 if len(good_right_inds) < minpix:
# #                     leftx_current = leftx_current + (rightx_past - rightx_past2)
# #                 else:
# #                     if x_diff < self.camera.WIDTH // 2:
# #                         leftx_current = rightx_current - (self.camera.WIDTH // 2)
# #                     else:
# #                         leftx_current = leftx_current + (rightx_current - rightx_past)
                       
# #             elif len(good_right_inds) < minpix:
# #                 if x_diff < self.camera.WIDTH // 2:
# #                     rightx_current = leftx_current + (self.camera.WIDTH // 2)
# #                 else:
# #                     rightx_current = rightx_current + (leftx_current - leftx_past)

# #             # 가장 하단에 있는 첫번째 조사창에서 결정된 두번째 조사창의 좌표를 다음 프레임의 기준점으로 결정
# #             # 기준점의 위치가 고정되어 변화되는 차선을 따라가지 못하는 것을 방지하고,
# #             # 차선이 끊기거나 여러 개의 선이 나타날 때 큰 변화 없이 현재 인식중인 차선의 방향대로 따라가며 효과적인 차선 인식이 가능
# #                 # 왼쪽 차선의 기준점이 중앙 기준 우측으로 넘어가지 않도록 제한
# #             # if leftx_current > midpoint + 30:
# #             #     leftx_current = midpoint + 30
# #             if leftx_current > midpoint - 10:
# #                 leftx_current = midpoint - 10

# #             # 오른쪽 차선의 기준점이 중앙 기준 좌측으로 넘어가지 않도록 제한
# #             # if rightx_current < midpoint - 170:
# #             #     rightx_current = midpoint - 170
# #             # if rightx_current < midpoint - 30:
# #             #     rightx_current = midpoint - 30
# #             if rightx_current < midpoint + 10:
# #                 rightx_current = midpoint + 10


# #             if window == 0:
# #                 # 왼쪽 차선의 기준점이 왼쪽 화면 밖으로 나가지 않도록 제한
# #                 # if leftx_current < 8:
# #                 #     leftx_current = 8
# #                 if leftx_current < 10:
# #                     leftx_current = 10

# #                 # 오른쪽 차선의 기준점이 오른쪽 화면 밖으로 나가지 않도록 제한
# #                 # if rightx_current > self.camera.WIDTH - 7:
# #                 #     rightx_current = self.camera.WIDTH - 7
# #                 if rightx_current > self.camera.WIDTH - 10:
# #                     rightx_current = self.camera.WIDTH - 10                

# #             # 두번째 조사창의 현재 좌표를 다음 프레임의 기준점으로 설정
# #                 self.leftx_base = leftx_current                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             
# #                 self.rightx_base = rightx_current
           

# #             # 슬라이딩 윈도우 중앙 좌표 값 저장
# #             left_wins_x.append(leftx_current)
# #             right_wins_x.append(rightx_current)

# #             # 현재 인덱스 값을 이전 값으로 저장
# #             # 한쪽 차선이 인식되지 않은 경우 인식된 차선을 따라가기 위해 사용되는 변수
# #             leftx_past = leftx_current
# #             rightx_past2 = rightx_past
# #             rightx_past = rightx_current

# #         # 배열 연결
# #         left_lane_inds = np.concatenate(left_lane_inds)
# #         right_lane_inds = np.concatenate(right_lane_inds)

# #         # 양쪽 차선 픽셀 추출
# #         ### 0이 아닌 픽셀 중에서 왼쪽 차선으로 인식된 좌표만 가져옴
# #         leftx = nonzerox[left_lane_inds]
# #         lefty = nonzeroy[left_lane_inds]
# #         ### 0이 아닌 픽셀 중에서 오른쪽 차선으로 인식된 좌표만 가져옴
# #         rightx = nonzerox[right_lane_inds]
# #         righty = nonzeroy[right_lane_inds]

# #         # 차선으로 인식된 픽셀 수가 일정치 이상일 경우에만 차선이 인식된 것으로 판단
# #         ### 왼쪽 차선으로 인식된 좌표가 1000개 미만이라면 False, 이상이 middle_point라면 True
# #         if (leftx.size < 1000):
# #             left_lane_detected = False
# #         else:
# #             # left_lane_detected = False
# #             left_lane_detected = True
# #         ### 오른쪽 차선으로 인식된 좌표가 1000개 미만이라면 False, 이상이라면 True
# #         if (rightx.size < 1000):
# #             right_lane_detected = False
# #         else:
# #             right_lane_detected = True

# #         # 차선이 인식된 것으로 판단되었다면 검출된 좌표로부터 차선의 2차 곡선을 구함
# #         # 왼쪽 차선이 인식된 경우
# #         if left_lane_detected:
# #             # 검출된 차선 좌표들을 통해 왼쪽 차선의 2차 방정식 계수를 구함
# #             left_fit = np.polyfit(lefty, leftx, 1)

# #             # 왼쪽 차선 계수
# #             self.left_a.append(left_fit[0])
# #             self.left_b.append(left_fit[1])
# #             #self.left_c.append(left_fit[2])

# #         # 오른쪽 차선이 인식된 경우
# #         if right_lane_detected:
# #             # 검출된 차선 좌표들을 통해 오른쪽 차선의 2차 방정식 계수를 구함
# #             #right_fit = np.polyfit(righty, rightx, 2)
# #             right_fit = np.polyfit(righty, rightx, 1)
# #             #print("right_angle",right_fit)w

# #             # 오른쪽 차선 계수
# #             self.right_a.append(right_fit[0]) #1차직선의 기울기로 수정 
# #             self.right_b.append(right_fit[1])
# #             #self.right_c.append(right_fit[2])

# #         if draw_windows:
# #             # 차선으로 검출된 픽셀 값 변경
# #             # 왼쪽 차선은 파란색, 오른쪽 차선은 빨간색으로 표시
# #             out_img[nonzeroy[left_lane_inds], nonzerox[left_lane_inds]] = [255, 0, 0]
# #             out_img[nonzeroy[right_lane_inds], nonzerox[right_lane_inds]] = [0, 0, 255]

# #         # 계수마다 각각 마지막 10개의 평균으로 최종 계수 결정
# #         # 왼쪽 차선의 계수 결정
# #         left_fit_[0] = np.mean(self.left_a[-10:])
# #         left_fit_[1] = np.mean(self.left_b[-10:])
# #         #left_fit_[2] = np.mean(self.left_c[-10:])
# #         # 오른쪽 차선의 계수 결정
# #         right_fit_[0] = np.mean(self.right_a[-10:])
# #         right_fit_[1] = np.mean(self.right_b[-10:])
# #         #right_fit_[2] = np.mean(self.right_c[-10:])

# #         # y 값에 해당하는 x 값 결정
# #         # 왼쪽 차선
# #         left_fitx = left_fit_[0] * self.ploty + left_fit_[1]
# #         # 오른쪽 차선
# #         right_fitx = right_fit_[0] * self.ploty + right_fit_[1]  
# #         # 양쪽 모두 차선인식이 안됐다면 슬라이딩 윈도우 조사창 재설정
# #         if (left_lane_detected is False) and (right_lane_detected is False):
# #             self.leftx_base = self.leftx_mid
# #             # self.rightx_base = self.rightx_mid + 50
# #             self.rightx_base = self.rightx_mid

# #         # 출력 이미지, 양쪽 곡선 x 좌표, 차선 인식 여부 반환
# #         return out_img, left_fitx, right_fitx, left_lane_detected, right_lane_detected, leftx, rightx

# #     # sliding window 기준으로 가운데에 초록색 경로 그리기
# #     # def draw_path(self, img, left_fitx, right_fitx, draw_windows=False):
# #     #     left_fitx = np.array([left_fitx])
# #     #     right_fitx = np.array([right_fitx])

# #     #     path_x = np.concatenate([left_fitx, right_fitx], axis=0)
# #     #     # path_x = np.concatenate([right_fitx], axis=0)
# #     #     path_x = np.mean(path_x, axis=0).reshape(-1)

# #     #     path_y = self.ploty


# #     #     if draw_windows is True:
# #     #         for (x, y) in zip(path_x, path_y):
                
# #     #             cv2.circle(img, (int(x), int(y)), 3, (0, 255, 0), -1)
# #     #             #print("xy:", int(x), int(y))
                
# #     #     return path_x, path_y

# #     def draw_path(self, img, left_fitx, right_fitx, draw_windows=False, start_point=(320, 410)):
# #         left_fitx = np.array([left_fitx])
# #         right_fitx = np.array([right_fitx])
# #         # left_fitx = right_fitx-400


# #         path_x = np.concatenate([left_fitx, right_fitx], axis=0)
# #         path_x = np.mean(path_x, axis=0).reshape(-1)

# #         path_y = self.ploty

# #         # difference = path_x[0] - 320
# #         # path_x = path_x - difference
# #         # print("x {}/{}".format(path_x[0],path_x[-1]))
# #         # print("x {}/{}".format(path_y[0],path_y[-1]))

# #         if draw_windows is True:
# #             for (x, y) in zip(path_x, path_y):

# #                 cv2.circle(img, (int(x), int(y)), 3, (0, 255, 0), -1)
# #             # cv2.line(img,[int(path_x[0]),int(path_y[0])], [int(path_x[-1]),int(path_y[-1])],(0,255,0),3)

# #         return path_x, path_y
    
# #     def lerp_color(self,color1, color2, t):
# #         return tuple(map(int, color1 + t * (color2 - color1)))

# #     def get_position(self, right_fitx, path_x, path_y, img):
# #         right_fitx = np.array([right_fitx])
# #         mid_fitx = right_fitx - 160
# #         path_mid = np.mean(mid_fitx, axis=0).reshape(-1)
# #         color_start, color_end = np.array([0, 255, 0]), np.array([0, 0, 255])
# #         message = ""
# #         state = ""
# #         state_color = (255, 255, 255)

        
# #         base_diff = 330 - path_mid[-1]
# #         if abs(base_diff) > 10:
# #             message = "Path Regenerate"
# #             # print("---------------------------------------path regenerate---------------------------------------")
# #             if base_diff > 0:
# #                 path_x_new = np.linspace(path_mid[-1], (path_mid[-1] + base_diff*0.8) - 1, self.camera.HEIGHT)
# #             elif base_diff < 0:
# #                 path_x_new = np.linspace(330, (330 + base_diff*1.5) - 1, self.camera.HEIGHT)
# #             path_x = path_x_new

# #             max_base_diff = 50
# #             for (x, y) in zip(path_x, path_y):
# #                 t = abs(min(base_diff, max_base_diff)) / max_base_diff
# #                 color = self.lerp_color(color_start, color_end, t)
# #                 cv2.circle(img, (int(x), int(y)), 3, color, -1)
            
# #         else:
# #             path_x = path_x

# #         cv2.circle(img, (int(path_mid[-1]), int(path_y[-1])), 5, (0, 0, 255), 3)

# #         if 0 < abs(base_diff) < 10:
# #             state = "Stable"
# #             state_color = (0, 255, 0)
# #         elif 10 <= abs(base_diff) < 20:
# #             state = "Caution"
# #             state_color = (0, 255, 255) 
# #         elif 20 <= abs(base_diff) < 30:
# #             state = "Alert"
# #             state_color = (0, 165, 255)
# #         elif abs(base_diff) >= 30:
# #             state = "Serious"
# #             state_color = (0, 0, 255) 

# #         return path_x, path_y, base_diff, message, state,state_color



    

# #     def draw_dashed_line(self,img, pt1, pt2, color, thickness, dash_length):
# #         dist = np.linalg.norm(np.array(pt1) - np.array(pt2))
# #         dashes = int(dist / (2 * dash_length))
# #         for i in range(dashes):
# #             start = np.array(pt1) + i * 2 * dash_length * (np.array(pt2) - np.array(pt1)) / dist
# #             end = start + dash_length * (np.array(pt2) - np.array(pt1)) / dist
# #             start = tuple(map(int, start))
# #             end = tuple(map(int, end))
# #             img = cv2.line(img, start, end, color, thickness)

# #         return img


# #     # 곡률을 구하여 조향각 구하기
# #     def get_angle(self, path_x, path_y, left_lane_detected, right_lane_detected):

# #         # 차선 두 개 모두 인식 안될 경우
# #         # if left_lane_detected is False and right_lane_detected is False:
# #         if left_lane_detected is False and right_lane_detected is False:
        
            
# #             # # making jiwhan - 308~312 
# #             # # 가장 최근의 각도 값의 반대 방향으로 조향각 변화를 줌
# #             # direction = -self.steering_memory
# #             # # 현재 값을 저장
# #             # self.steering_memory = direction
# #             # print("no detection line ---------------------------------- reverse angle :{}".format(direction))

# #             # making jiwhan-------------------------------------------------------------------------------------
# #             # 양쪽 차선 모두 인식이 안되는 경우, 가장 마지막 조향각을 return함. 이 경우에는 다시 차선 안쪽으로 들어올 수가 없음.
# #             # 그래서 가장 마지막 조향각의 부호를 바꿔서 다시 차선 안쪽으로 들어가게 해야함.
# #             # if not self.has_switched:
# #             #     # 가장 최근의 각도 값의 반대 방향으로 조향각 변화를 줌
# #             #     direction = - (self.steering_memory + 10)
# #             #     # 현재 값을 저장
# #             #     self.steering_memory = direction
# #             #     self.has_switched = True # 부호를 바꾼 것을 표시
# #             # else:
# #             #     # 이전에 부호를 바꾼 경우 그 값을 사용
# #             #     direction = self.steering_memory
        
# #             # print("no detection line ---------------------------------- reverse angle :{}".format(direction))
# #             # return direction
# #             # making jiwhan-------------------------------------------------------------------------------------

# #             # 아래가 원본.
# #             # 양쪽 차선 모두 인식이 안되는 경우, 가장 마지막 조향각을 return함. 
# #             return self.steering_memory * 1.2

        
# #         # 차선 하나라도 인식될 경우
# #         else:
# #             # making eee
# #             self.has_switched = False # 다시 차선이 검출된 경우 부호 바꾸기를 e초기화
# #             # making jiwhan

# #             path = np.concatenate((path_x.reshape(-1, 1), path_y.reshape(-1, 1)), axis=1)
# #             baseline_x = np.full_like(path_x, 320)
# #             baseline = np.concatenate((baseline_x.reshape(-1, 1), path_y.reshape(-1, 1)), axis=1)
# #             base_diff = baseline[0,0] - path[0,0]

            

# #             self.avg_middle = np.mean(path_x, axis=0)

# #             point_a = path[0, :]  # Top Point
# #             point_b = path[-1, :]  # Bottom Pointself.leftx_mid
# #             point_m = [(point_a[0] + point_b[0]) / 2, (point_a[1] + point_b[1]) / 2]  # point_a와 point_b의 중점

# #             W = math.sqrt(((point_a[0] - point_b[0]) ** 2) + ((point_a[1] - point_b[1]) ** 2))
# #             H = math.sqrt(np.min(np.sum((path - point_m) ** 2, axis=1)))

# #             # print("middle_distance: {}".format(middle_dist))
# #             # print("point_a",point_a)
# #             # print("point_b",point_b)
           
# #             # print("xvalue" ,point_b[0]-point_a[0])

# #             # 640 pixel = 0.64m  ->  1 pixel = 0.001m
# #             radius = ((H / 2) + (W ** 2) / (8 * H)) * 0.001
# #             mod_angle = math.atan(480 / base_diff) * (180 / math.pi)

# #             # 2차 곡선 기울기 계수 구하기---------------------->1로 수정 
# #             direction = np.polyfit(path[:, 1], path[:, 0], deg = 1)[0] * 1000
# #             # direction = direction - mod_angle
# #             #print("dir",direction)
# #             #direction = self.right_aaa

# #             #2차곡선 기울기가 0인경우 ->직선인 경우 
# #             self.real_angle = direction

# #             # if direction > 85:
# #             #     direction = 0

# #             if direction > 0:
# #                 direction *= -0.35
# #                 if direction <= -5:
# #                     direction *= 0.4
# #                 elif direction <= -10:
# #                     direction *= 0.45
# #                 elif direction <= -15:
# #                     direction *= 0.55
# #                 elif direction <= -20.0:
# #                     direction = -20.0

                
# #             elif direction < 0:
# #                 direction *= -0.35
# #                 if direction >= -5:
# #                     direction *= 0.4
# #                 elif direction >= 10:
# #                     direction *= 0.45
# #                 elif direction >= 15:
# #                     direction *= 0.55
# #                 elif direction >= 20.0:
# #                     direction = 20.0

# #             # if -1.5<steering_angle<1.5 :
# #             #     if (point_a[0]-point_b[0]) > 0:
# #             #         #print('0, right',(point_a[0]-point_b[0])/10)
# #             #         steering_angle = (point_a[0]-point_b[0]) *0.1
# #             #     elif (point_a[0]-point_b[0]) < 0:
# #             #         #print('0, left',(point_a[0]-point_b[0])/10)
# #             #         steering_angle = (point_a[0]-point_b[0]) *0.1
# #             #     else:
# #             #         #print("0, straight")
# #             #         steering_angle = 0

# #             # if (point_a[0]-point_b[0]) > 0:
# #             # if (abs(steering_angle)) < 0.2:
# #             #     print('forward')
# #             #     direction = np.polyfit(path[:, 1], path[:, 0], deg = 1)[0]
# #             #     print(direction)
# #             #     print('forward2')
# #             #     direction = (point_a[0]-point_b[0]) * 0.1   
# #             #     print(direction)
# #             #     steering_angle = direction        

# #             # 두 차선 모두 인식 안될 경우를 위해 현재 값 저장
# #             self.steering_memory = direction

# #             return direction
    


# #     # ========================================
# #     # 슬라이딩 윈도우를 원본 이미지에 투영하기 위한 역변환 행렬 구하기
# #     # ========================================
# #     def inv_perspective_transform(self, img):
# #         result_img = cv2.warpPerspective(img, self.camera.inv_transform_matrix, (self.camera.WIDTH, self.camera.HEIGHT))
# #         return result_img


# #     # ========================================
# #     # 원본 이미지와 최종 처리된 이미지를 합치기
# #     # ========================================
# #     def combine_img(self, origin_img, result_img):
# #         return cv2.addWeighted(origin_img, 0.5, result_img, 1.0, 0.8)
    
# #     def draw_offset_lines(self,img, center_x=330, y_start=0, y_end=480, max_offset=50, color_start=(0,255,0), color_end=(0,0,255)):
# #         color_diff = np.array(color_end) - np.array(color_start)
# #         for offset in range(0, max_offset + 1, 10):
# #             left_x = center_x - offset
# #             right_x = center_x + offset
# #             color = tuple(map(int, color_start + color_diff * (offset / max_offset)))
# #             img = cv2.line(img, (left_x, y_start), (left_x, y_end), color, 1)
# #             img = cv2.line(img, (right_x, y_start), (right_x, y_end), color, 1)
# #         return img
    

    

# #     # ========================================
# #     # Main 함수
# #     # ========================================
# #     def process(self, origin_img):
# #         origin_img = cv2.resize(origin_img, (640,480), cv2.INTER_LINEAR) # (640, 480) : (width, height)  cv2.INTER_LINEAR : 쌍선형 보간법
# #         img = self.camera.pre_processing(origin_img)
        
# #         #cv2.line(img, (463,0),(410,480),(255,255,255),10)
        
# #         sliding_img, left_fitx, right_fitx, left_lane_detected, right_lane_detected, leftx, rightx = self.sliding_window(img, draw_windows=True)  # 슬라이딩 윈도우로 곡선 차선 인식

# #         # sliding window 기준으로 가운데에 초록색 경로 그리기
# #         path_x, path_y = self.draw_path(sliding_img, left_fitx, right_fitx, draw_windows=True)

# #         if rightx.size > leftx.size:
# #             path_x, path_y,base_diff,message,state,state_color = self.get_position(right_fitx,path_x, path_y,sliding_img)


# #         # 곡률을 구하여 조향각 구하기
# #         curvature_angle = self.get_angle(path_x, path_y, left_lane_detected, right_lane_detected)

# #         sliding_img = self.draw_dashed_line(sliding_img, (330,0),(330,480), (255, 255, 0), 2, 10)
# #         sliding_img = self.draw_offset_lines(sliding_img)

# #         direction = ""
# #         if curvature_angle < -5:
# #             direction = "Left"
# #         elif curvature_angle > 5:
# #             direction = "Right"
# #         else:
# #             direction = "Straight"
       
# #         # 주석 처리
# #         sliding_result_img = self.inv_perspective_transform(sliding_img)
# #         combined_img = self.combine_img(origin_img, sliding_result_img)
# #         cv2.putText(combined_img, 'Angle: {}'.format(int(curvature_angle)), (0, 30), 1, 2, (255, 255, 255), 2)
# #         # cv2.putText(combined_img, 'base_diff: {}'.format(int(base_diff)), (0, 60), 1, 2, (255, 255, 255), 2)
# #         # cv2.putText(combined_img, message, (320, 30), 1, 2, (255, 255, 255), 2)
# #         # cv2.putText(combined_img, state, (400, 60), 1, 2, state_color, 2)
# #         # cv2.putText(combined_img, direction, (0, 90), 1, 2, (255, 255, 255), 2)

# #         points = np.array([(0, 410), (50, 350), (590, 350), (640, 410)], dtype=np.int32)
# #         combined_img = cv2.polylines(combined_img, [points], True, (255, 255, 0), 1)
# #         combined_img = cv2.line(combined_img,(320, 350), (320, 410),(255,255,0),1)

# #         # cv2.putText(sliding_img, 'base_diff: {}'.format(int(base_diff)), (0, 25), 1, 2, (255, 255, 255), 2)


# #         cv2.imshow('Lane', combined_img)
# #         cv2.imshow('bird',sliding_img)

# #         return curvature_angle


# ######################################################################################################################3

# # import numpy as np
# # import cv2
# # from camera import Camera
# # import math


# # # =============================================
# # # 주행을 위한 알고리즘 클래스 정의
# # # =============================================
# # class LaneDetector:

# #     # ========================================
# #     # 변수 선언 및 초기화
# #     # ========================================
# #     def __init__(self):

# #         self.camera = Camera()
# #         # 슬라이딩 윈도우 출력 창 크기 좌우 확장 값으로, 좌우로 window_margin 만큼 커짐
# #         # 슬라이딩 윈도우 출력 창 가로 크기 : WIDTH + 2*window_margin
# #         self.window_margin = 20
# #         self.xycar_length = 0.46 # 0.35 meter
# #         self.xycar_width = 0.3
# #         self.leftx_mid, self.rightx_mid = self.camera.WIDTH *2 // 8, self.camera.WIDTH * 6 // 8  # 슬라이딩 윈도우 기준점 초기 좌표
# #         self.leftx_base, self.rightx_base = self.leftx_mid, self.rightx_mid  # 슬라이딩 윈도우 이전값

# #         self.left_a, self.left_b, self.left_c = [0], [0], [self.leftx_mid]  # 왼쪽 차선으로부터 나온 2차 곡선 방정식의 계수를 저장하기 위한 변수
# #         self.right_a, self.right_b, self.right_c = [0], [0], [self.rightx_mid]
# #         # 오른쪽 차선으로부터 나온 2차 곡선 방정식의 계수를 저장하기 위한 변수
# #         # 처음 차선이 인식되지 않는 경우를 대비하여, 초기값은 슬라이딩 윈도우 기준점으로부터 직진으로 방정식을 그리도록 함
# #         self.leftx_current, self.rightx_current = [self.leftx_mid], [self.rightx_mid]
# #         self.ref_diff = self.rightx_mid - self.leftx_mid
# #         self.ref_mid = self.ref_diff // 2
# #         self.lefty_current, self.righty_current = [480], [480]

# #         # 양쪽 차선 곡선 좌표 생성
# #         ### Linear y 값 생성 (0, 1, 2, ..., 479)
# #         self.ploty = np.linspace(0, self.camera.HEIGHT - 1, self.camera.HEIGHT)
# #         # self.ploty2 = np.linspace(0, (self.camera.HEIGHT+self.xycar_length) - 1, (self.camera.HEIGHT+self.xycar_length))
# #         self.wins_y = np.linspace(464, 16, 15) # 슬라이딩 윈도우의 y좌표값 

# #         # 양쪽 차선 인식 기준 x값 평균을 저장하는 변수, 이전 조향각을 저장하기위한 변수 선언.
# #         self.avg_middle, self.steering_memory = 0.0, 0.0
# #         self.right_aaa=0
# #         self.real_angle=0

# #         # making jiwhan
# #         self.has_switched = False # 처음에는 부호를 바꾸지 않았음. 양쪽 차선이 인식 안될 경우, 사용할 flag변수. 
# #         # making jiwhan

# #     # ========================================
# #     # 슬라이딩 윈도우
# #     # ====================
# #     # < input >
# #     # img : 입력 이미지
# #     # nwindows : 조사창 개수 (좌우 각각 nwindows개씩)
# #     # margin : 현재 기준 위치로부터 조사창의 좌우 길이 (-margin ~ +margin)
# #     #          조사창 가로 길이 : margin*2
# #     # minpix : 조사창 내부에서 차선이 검출된 것으로 판단할 최소 픽셀 개수
# #     # draw_windows : 결과창 출력 여부
# #     #
# #     # ====================
# #     # < return >
# #     # out_img : 출력 이미지
# #     # window_img : 슬라이딩 윈도우 출력을 위한 이미지 (너비 확장)
# #     # left_fitx : 왼쪽 차선 곡선 방정식 x 좌표
# #     # right_fitx : 오른쪽 차선 곡선 방정식 x 좌표
# #     # left_lane_detected : 왼쪽 차선 인식 여부
# #     # right_lane_detected : 오른쪽 차선 인식 여부
# #     #
# #     # ========================================


# #     def sliding_window(self, img, nwindows=7, margin=30, minpix=45, draw_windows=False):
# #         # 크기 3의 비어있는 배열 생성
# #         left_fit_ = np.empty(3)
# #         right_fit_ = np.empty(3)

# #         # 0과 1로 이진화된 영상을 3채널의 영상으로 만들기 위해 3개를 쌓은 후 *255
# #         out_img = np.dstack((img, img, img)) * 255
       
# #         # 너비의 중앙값
# #         midpoint = self.camera.WIDTH // 2

# #         # 조사창의 높이 설정
# #         # 전체 높이에서 설정한 조사창 개수만큼 나눈 값
# #         window_height = self.camera.HEIGHT // nwindows 

# #         # 0이 아닌 픽셀의 x,y 좌표 반환 (흰색 영역(차선)으로 인식할 수 있는 좌표)
# #         nonzero = img.nonzero() # 0이 아닌 것을 찾는다.
# #         nonzeroy = np.array(nonzero[0])
# #         nonzerox = np.array(nonzero[1])

# #         # 이전 프레임으로부터 기준점의 좌표를 받아옴
# #         # 양쪽 차선 확인 위치 업데이트
# #         # 이 값을 기준으로 조사창을 생성하여 차선 확인
# #         leftx_current = self.leftx_base
# #         rightx_current = self.rightx_base

# #         # 차선 확인 시 검출이 되지 않는 경우를 대비해서 바로 이전(화면상 바로 아래) 조사창으로부터 정보를 얻기 위한 변수
# #         # 이를 이용해서 조사창 위치의 변화량을 파악
# #         # 초기값으로는 현재 기준 좌표를 넣어줌
# #         leftx_past = leftx_current
# #         rightx_past = rightx_current
# #         rightx_past2 = rightx_past

# #         # 양쪽 차선 픽셀 인덱스를 담기 위한 빈 배열 선언
# #         # 차선의 방정식을 구하거나 차선 인식 판단 여부에 사용
# #         left_lane_inds = []
# #         right_lane_inds = []

# #         # 슬라이딩 윈도우 좌표 값을 담기 위한 빈 배열
# #         left_wins_x = []
# #         right_wins_x = []

# #         # 설정한 조사창 개수만큼 슬라이딩 윈도우 생성
# #         for window in range(nwindows):
            
# #             # makin jiwhan
# #             if window == 0:
# #                 print("widno index ================================= {}".format(window))
# #                 # 조사창 크기 및 위치 설정
# #                 win_y_low = self.camera.HEIGHT - ((window + 1) * window_height)
# #                 # n번째 조사창 윗변 y 좌표 : (전체 높이) - (n * 조사창 높이)
# #                 win_y_high = self.camera.HEIGHT - (window * window_height)
# #                 # 양쪽 차선의 조사창의 너비를 현재 좌표로부터 margin만큼 양 옆으로 키움
# #                 win_xleft_low = int(self.leftx_base - margin)
# #                 win_xleft_high = int(self.leftx_base + margin)
# #                 win_xright_low = int(self.rightx_base - margin)
# #                 win_xright_high = int(self.rightx_base + margin)
# #             else: 
# #                 # 조사창 크기 및 위치 설정
# #                 win_y_low = self.camera.HEIGHT - ((window + 1) * window_height)
# #                 # n번째 조사창 윗변 y 좌표 : (전체 높이) - (n * 조사창 높이)
# #                 win_y_high = self.camera.HEIGHT - (window * window_height)
# #                 # 양쪽 차선의 조사창의 너비를 현재 좌표로부터 margin만큼 양 옆으로 키움
# #                 win_xleft_low = int(leftx_current - margin)
# #                 win_xleft_high = int(leftx_current + margin)
# #                 win_xright_low = int(rightx_current - margin)
# #                 win_xright_high = int(rightx_current + margin)
# #             # making jiwhan

# #             # # 이게 원본임. 
# #             # # 조사창 크기 및 위치 설정
# #             #     win_y_low = self.camera.HEIGHT - ((window + 1) * window_height)
# #             #     # n번째 조사창 윗변 y 좌표 : (전체 높이) - (n * 조사창 높이)
# #             #     win_y_high = self.camera.HEIGHT - (window * window_height)
# #             #     # 양쪽 차선의 조사창의 너비를 현재 좌표로부터 margin만큼 양 옆으로 키움
# #             #     win_xleft_low = int(leftx_current - margin)
# #             #     win_xleft_high = int(leftx_current + margin)
# #             #     win_xright_low = int(rightx_current - margin)
# #             #     win_xright_high = int(rightx_current + margin)

# #             # 조사창 그리기
# #             if draw_windows == True:
# #                 # cv2.rectangle(img, start(시작 좌표), end(종료 좌표), color, thickness)
# #                 # 왼쪽 차선
# #                 cv2.rectangle(out_img, (win_xleft_low, win_y_low), (win_xleft_high, win_y_high), (100, 100, 255), 3)
# #                 # 오른쪽 차선
# #                 cv2.rectangle(out_img, (win_xright_low, win_y_low), (win_xright_high, win_y_high), (100, 100, 255), 3)

# #             # 조사창 내부에서 0이 아닌 픽셀의 인덱스 저장
# #             good_left_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high)
# #                               & (nonzerox >= win_xleft_low) & (nonzerox < win_xleft_high)).nonzero()[0]
# #             good_right_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high)
# #                                & (nonzerox >= win_xright_low) & (nonzerox < win_xright_high)).nonzero()[0]

# #             # 양쪽 차선의 인덱스 저장
# #             left_lane_inds.append(good_left_inds)
# #             right_lane_inds.append(good_right_inds)

# #             # 조사창 내부에서 0이 아닌 픽셀 개수가 기준치를 넘으면 해당 픽셀들의 인덱스 평균값(x좌표 평균)으로 다음 조사창의 위치(x좌표)를 결정
# #             if len(good_left_inds) > minpix:
# #                 leftx = nonzerox[good_left_inds]
# #                 leftx_current = int(np.mean(leftx))
           
# #             if len(good_right_inds) > minpix:
# #                 rightx = nonzerox[good_right_inds]
# #                 rightx_current = int(np.mean(rightx))
               

# #             x_diff = rightx_current - leftx_current

# #             # 양쪽 차선 중 하나만 인식된 경우 반대편 차선에서 나타난 인덱스 변화량과 동일하게 인덱스 설정
# #             # 인식된 차선의 방향과 동일하게 그려짐
# #             if len(good_left_inds) < minpix:
# #                 if len(good_right_inds) < minpix:
# #                     leftx_current = leftx_current + (rightx_past - rightx_past2)
# #                 else:
# #                     if x_diff < self.camera.WIDTH // 2:
# #                         leftx_current = rightx_current - (self.camera.WIDTH // 2)
# #                     else:
# #                         leftx_current = leftx_current + (rightx_current - rightx_past)
                       
# #             elif len(good_right_inds) < minpix:
# #                 if x_diff < self.camera.WIDTH // 2:
# #                     rightx_current = leftx_current + (self.camera.WIDTH // 2)
# #                 else:
# #                     rightx_current = rightx_current + (leftx_current - leftx_past)

# #             # 가장 하단에 있는 첫번째 조사창에서 결정된 두번째 조사창의 좌표를 다음 프레임의 기준점으로 결정
# #             # 기준점의 위치가 고정되어 변화되는 차선을 따라가지 못하는 것을 방지하고,
# #             # 차선이 끊기거나 여러 개의 선이 나타날 때 큰 변화 없이 현재 인식중인 차선의 방향대로 따라가며 효과적인 차선 인식이 가능
# #                 # 왼쪽 차선의 기준점이 중앙 기준 우측으로 넘어가지 않도록 제한
# #             # if leftx_current > midpoint + 30:
# #             #     leftx_current = midpoint + 30
# #             if leftx_current > midpoint - 10:
# #                 leftx_current = midpoint - 10

# #             # 오른쪽 차선의 기준점이 중앙 기준 좌측으로 넘어가지 않도록 제한
# #             # if rightx_current < midpoint - 170:
# #             #     rightx_current = midpoint - 170
# #             # if rightx_current < midpoint - 30:
# #             #     rightx_current = midpoint - 30
# #             if rightx_current < midpoint + 10:
# #                 rightx_current = midpoint + 10


# #             if window == 0:
# #                 # 왼쪽 차선의 기준점이 왼쪽 화면 밖으로 나가지 않도록 제한
# #                 # if leftx_current < 8:
# #                 #     leftx_current = 8
# #                 if leftx_current < 10:
# #                     leftx_current = 10

# #                 # 오른쪽 차선의 기준점이 오른쪽 화면 밖으로 나가지 않도록 제한
# #                 # if rightx_current > self.camera.WIDTH - 7:
# #                 #     rightx_current = self.camera.WIDTH - 7
# #                 if rightx_current > self.camera.WIDTH - 10:
# #                     rightx_current = self.camera.WIDTH - 10                

# #             # 두번째 조사창의 현재 좌표를 다음 프레임의 기준점으로 설정
# #                 self.leftx_base = leftx_current                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             
# #                 self.rightx_base = rightx_current
           

# #             # 슬라이딩 윈도우 중앙 좌표 값 저장
# #             left_wins_x.append(leftx_current)
# #             right_wins_x.append(rightx_current)

# #             # 현재 인덱스 값을 이전 값으로 저장
# #             # 한쪽 차선이 인식되지 않은 경우 인식된 차선을 따라가기 위해 사용되는 변수
# #             leftx_past = leftx_current
# #             rightx_past2 = rightx_past
# #             rightx_past = rightx_current

# #         # 배열 연결
# #         left_lane_inds = np.concatenate(left_lane_inds)
# #         right_lane_inds = np.concatenate(right_lane_inds)

# #         # 양쪽 차선 픽셀 추출
# #         ### 0이 아닌 픽셀 중에서 왼쪽 차선으로 인식된 좌표만 가져옴
# #         leftx = nonzerox[left_lane_inds]
# #         lefty = nonzeroy[left_lane_inds]
# #         ### 0이 아닌 픽셀 중에서 오른쪽 차선으로 인식된 좌표만 가져옴
# #         rightx = nonzerox[right_lane_inds]
# #         righty = nonzeroy[right_lane_inds]

# #         # 차선으로 인식된 픽셀 수가 일정치 이상일 경우에만 차선이 인식된 것으로 판단
# #         ### 왼쪽 차선으로 인식된 좌표가 1000개 미만이라면 False, 이상이 middle_point라면 True
# #         if (leftx.size < 1000):
# #             left_lane_detected = False
# #         else:
# #             # left_lane_detected = False
# #             left_lane_detected = True
# #         ### 오른쪽 차선으로 인식된 좌표가 1000개 미만이라면 False, 이상이라면 True
# #         if (rightx.size < 1000):
# #             right_lane_detected = False
# #         else:
# #             right_lane_detected = True

# #         # 차선이 인식된 것으로 판단되었다면 검출된 좌표로부터 차선의 2차 곡선을 구함
# #         # 왼쪽 차선이 인식된 경우
# #         if left_lane_detected:
# #             # 검출된 차선 좌표들을 통해 왼쪽 차선의 2차 방정식 계수를 구함
# #             left_fit = np.polyfit(lefty, leftx, 1)

# #             # 왼쪽 차선 계수
# #             self.left_a.append(left_fit[0])
# #             self.left_b.append(left_fit[1])
# #             #self.left_c.append(left_fit[2])

# #         # 오른쪽 차선이 인식된 경우
# #         if right_lane_detected:
# #             # 검출된 차선 좌표들을 통해 오른쪽 차선의 2차 방정식 계수를 구함
# #             #right_fit = np.polyfit(righty, rightx, 2)
# #             right_fit = np.polyfit(righty, rightx, 1)
# #             #print("right_angle",right_fit)w

# #             # 오른쪽 차선 계수
# #             self.right_a.append(right_fit[0]) #1차직선의 기울기로 수정 
# #             self.right_b.append(right_fit[1])
# #             #self.right_c.append(right_fit[2])

# #         if draw_windows:
# #             # 차선으로 검출된 픽셀 값 변경
# #             # 왼쪽 차선은 파란색, 오른쪽 차선은 빨간색으로 표시
# #             out_img[nonzeroy[left_lane_inds], nonzerox[left_lane_inds]] = [255, 0, 0]
# #             out_img[nonzeroy[right_lane_inds], nonzerox[right_lane_inds]] = [0, 0, 255]

# #         # 계수마다 각각 마지막 10개의 평균으로 최종 계수 결정
# #         # 왼쪽 차선의 계수 결정
# #         left_fit_[0] = np.mean(self.left_a[-10:])
# #         left_fit_[1] = np.mean(self.left_b[-10:])
# #         #left_fit_[2] = np.mean(self.left_c[-10:])
# #         # 오른쪽 차선의 계수 결정
# #         right_fit_[0] = np.mean(self.right_a[-10:])
# #         right_fit_[1] = np.mean(self.right_b[-10:])
# #         #right_fit_[2] = np.mean(self.right_c[-10:])

# #         # y 값에 해당하는 x 값 결정
# #         # 왼쪽 차선
# #         left_fitx = left_fit_[0] * self.ploty + left_fit_[1]
# #         # 오른쪽 차선
# #         right_fitx = right_fit_[0] * self.ploty + right_fit_[1]  
# #         # 양쪽 모두 차선인식이 안됐다면 슬라이딩 윈도우 조사창 재설정
# #         if (left_lane_detected is False) and (right_lane_detected is False):
# #             self.leftx_base = self.leftx_mid
# #             # self.rightx_base = self.rightx_mid + 50
# #             self.rightx_base = self.rightx_mid

# #         # 출력 이미지, 양쪽 곡선 x 좌표, 차선 인식 여부 반환
# #         return out_img, left_fitx, right_fitx, left_lane_detected, right_lane_detected

# #     # sliding window 기준으로 가운데에 초록색 경로 그리기
# #     # def draw_path(self, img, left_fitx, right_fitx, draw_windows=False):
# #     #     left_fitx = np.array([left_fitx])
# #     #     right_fitx = np.array([right_fitx])

# #     #     path_x = np.concatenate([left_fitx, right_fitx], axis=0)
# #     #     # path_x = np.concatenate([right_fitx], axis=0)
# #     #     path_x = np.mean(path_x, axis=0).reshape(-1)

# #     #     path_y = self.ploty


# #     #     if draw_windows is True:
# #     #         for (x, y) in zip(path_x, path_y):
                
# #     #             cv2.circle(img, (int(x), int(y)), 3, (0, 255, 0), -1)
# #     #             #print("xy:", int(x), int(y))
                
# #     #     return path_x, path_y

# #     def draw_path(self, img, left_fitx, right_fitx, draw_windows=False, start_point=(320, 410)):
# #         left_fitx = np.array([left_fitx])
# #         right_fitx = np.array([right_fitx])
# #         # left_fitx = right_fitx-400


# #         path_x = np.concatenate([left_fitx, right_fitx], axis=0)
# #         path_x = np.mean(path_x, axis=0).reshape(-1)

# #         path_y = self.ploty

# #         # difference = path_x[0] - 320
# #         # path_x = path_x - difference
# #         print("x {}/{}".format(path_x[0],path_x[-1]))
# #         print("x {}/{}".format(path_y[0],path_y[-1]))

# #         if draw_windows is True:
# #             for (x, y) in zip(path_x, path_y):

# #                 cv2.circle(img, (int(x), int(y)), 3, (0, 255, 0), -1)
# #             # cv2.line(img,[int(path_x[0]),int(path_y[0])], [int(path_x[-1]),int(path_y[-1])],(0,255,0),3)

# #         return path_x, path_y
    
# #     def lerp_color(self,color1, color2, t):
# #         return tuple(map(int, color1 + t * (color2 - color1)))

# #     def get_position(self, right_fitx, path_x, path_y, img):
# #         right_fitx = np.array([right_fitx])
# #         mid_fitx = right_fitx - 160
# #         path_mid = np.mean(mid_fitx, axis=0).reshape(-1)
# #         color_start, color_end = np.array([0, 255, 0]), np.array([0, 0, 255])
# #         message = ""
# #         state = ""
# #         state_color = (255, 255, 255)

        
# #         base_diff = 330 - path_mid[-1]
# #         if abs(base_diff) > 10:
# #             message = "Path Regenerate"
# #             print("---------------------------------------path regenerate---------------------------------------")
# #             if base_diff > 0:
# #                 path_x_new = np.linspace(path_mid[-1], (path_mid[-1] + base_diff*0.8) - 1, self.camera.HEIGHT)
# #             elif base_diff < 0:
# #                 path_x_new = np.linspace(330, (330 + base_diff*1.5) - 1, self.camera.HEIGHT)
# #             path_x = path_x_new

# #             max_base_diff = 50
# #             for (x, y) in zip(path_x, path_y):
# #                 t = abs(min(base_diff, max_base_diff)) / max_base_diff
# #                 color = self.lerp_color(color_start, color_end, t)
# #                 cv2.circle(img, (int(x), int(y)), 3, color, -1)
            
# #         else:
# #             path_x = path_x

# #         cv2.circle(img, (int(path_mid[-1]), int(path_y[-1])), 5, (0, 0, 255), 3)

# #         if 0 < abs(base_diff) < 10:
# #             state = "Stable"
# #             state_color = (0, 255, 0)
# #         elif 10 <= abs(base_diff) < 20:
# #             state = "Caution"
# #             state_color = (0, 255, 255) 
# #         elif 20 <= abs(base_diff) < 30:
# #             state = "Alert"
# #             state_color = (0, 165, 255)
# #         elif abs(base_diff) >= 30:
# #             state = "Serious"
# #             state_color = (0, 0, 255) 

# #         return path_x, path_y, base_diff, message, state,state_color



    

# #     def draw_dashed_line(self,img, pt1, pt2, color, thickness, dash_length):
# #         dist = np.linalg.norm(np.array(pt1) - np.array(pt2))
# #         dashes = int(dist / (2 * dash_length))
# #         for i in range(dashes):
# #             start = np.array(pt1) + i * 2 * dash_length * (np.array(pt2) - np.array(pt1)) / dist
# #             end = start + dash_length * (np.array(pt2) - np.array(pt1)) / dist
# #             start = tuple(map(int, start))
# #             end = tuple(map(int, end))
# #             img = cv2.line(img, start, end, color, thickness)

# #         return img


# #     # 곡률을 구하여 조향각 구하기
# #     def get_angle(self, path_x, path_y, left_lane_detected, right_lane_detected):

# #         # 차선 두 개 모두 인식 안될 경우
# #         # if left_lane_detected is False and right_lane_detected is False:
# #         if left_lane_detected is False and right_lane_detected is False:
        
            
# #             # # making jiwhan - 308~312 
# #             # # 가장 최근의 각도 값의 반대 방향으로 조향각 변화를 줌
# #             # direction = -self.steering_memory
# #             # # 현재 값을 저장
# #             # self.steering_memory = direction
# #             # print("no detection line ---------------------------------- reverse angle :{}".format(direction))

# #             # making jiwhan-------------------------------------------------------------------------------------
# #             # 양쪽 차선 모두 인식이 안되는 경우, 가장 마지막 조향각을 return함. 이 경우에는 다시 차선 안쪽으로 들어올 수가 없음.
# #             # 그래서 가장 마지막 조향각의 부호를 바꿔서 다시 차선 안쪽으로 들어가게 해야함.
# #             # if not self.has_switched:
# #             #     # 가장 최근의 각도 값의 반대 방향으로 조향각 변화를 줌
# #             #     direction = - (self.steering_memory + 10)
# #             #     # 현재 값을 저장
# #             #     self.steering_memory = direction
# #             #     self.has_switched = True # 부호를 바꾼 것을 표시
# #             # else:
# #             #     # 이전에 부호를 바꾼 경우 그 값을 사용
# #             #     direction = self.steering_memory
        
# #             # print("no detection line ---------------------------------- reverse angle :{}".format(direction))
# #             # return direction
# #             # making jiwhan-------------------------------------------------------------------------------------

# #             # 아래가 원본.
# #             # 양쪽 차선 모두 인식이 안되는 경우, 가장 마지막 조향각을 return함. 
# #             return self.steering_memory * 1.2

        
# #         # 차선 하나라도 인식될 경우
# #         else:
# #             # making eee
# #             self.has_switched = False # 다시 차선이 검출된 경우 부호 바꾸기를 e초기화
# #             # making jiwhan

# #             path = np.concatenate((path_x.reshape(-1, 1), path_y.reshape(-1, 1)), axis=1)
# #             baseline_x = np.full_like(path_x, 320)
# #             baseline = np.concatenate((baseline_x.reshape(-1, 1), path_y.reshape(-1, 1)), axis=1)
# #             base_diff = baseline[0,0] - path[0,0]

            

# #             self.avg_middle = np.mean(path_x, axis=0)

# #             point_a = path[0, :]  # Top Point
# #             point_b = path[-1, :]  # Bottom Pointself.leftx_mid
# #             point_m = [(point_a[0] + point_b[0]) / 2, (point_a[1] + point_b[1]) / 2]  # point_a와 point_b의 중점

# #             W = math.sqrt(((point_a[0] - point_b[0]) ** 2) + ((point_a[1] - point_b[1]) ** 2))
# #             H = math.sqrt(np.min(np.sum((path - point_m) ** 2, axis=1)))

# #             # print("middle_distance: {}".format(middle_dist))
# #             # print("point_a",point_a)
# #             # print("point_b",point_b)
           
# #             # print("xvalue" ,point_b[0]-point_a[0])

# #             # 640 pixel = 0.64m  ->  1 pixel = 0.001m
# #             radius = ((H / 2) + (W ** 2) / (8 * H)) * 0.001
# #             mod_angle = math.atan(480 / base_diff) * (180 / math.pi)

# #             # 2차 곡선 기울기 계수 구하기---------------------->1로 수정 
# #             direction = np.polyfit(path[:, 1], path[:, 0], deg = 1)[0] * 1000
# #             # direction = direction - mod_angle
# #             #print("dir",direction)
# #             #direction = self.right_aaa

# #             #2차곡선 기울기가 0인경우 ->직선인 경우 
# #             self.real_angle = direction

# #             # if direction > 85:
# #             #     direction = 0

# #             if direction > 0:
# #                 direction *= -0.35
# #                 if direction <= -5:
# #                     direction *= 0.4
# #                 elif direction <= -10:
# #                     direction *= 0.45
# #                 elif direction <= -15:
# #                     direction *= 0.55
# #                 elif direction <= -20.0:
# #                     direction = -20.0

                
# #             elif direction < 0:
# #                 direction *= -0.35
# #                 if direction >= -5:
# #                     direction *= 0.4
# #                 elif direction >= 10:
# #                     direction *= 0.45
# #                 elif direction >= 15:
# #                     direction *= 0.55
# #                 elif direction >= 20.0:
# #                     direction = 20.0

# #             # if -1.5<steering_angle<1.5 :
# #             #     if (point_a[0]-point_b[0]) > 0:
# #             #         #print('0, right',(point_a[0]-point_b[0])/10)
# #             #         steering_angle = (point_a[0]-point_b[0]) *0.1
# #             #     elif (point_a[0]-point_b[0]) < 0:
# #             #         #print('0, left',(point_a[0]-point_b[0])/10)
# #             #         steering_angle = (point_a[0]-point_b[0]) *0.1
# #             #     else:
# #             #         #print("0, straight")
# #             #         steering_angle = 0

# #             # if (point_a[0]-point_b[0]) > 0:
# #             # if (abs(steering_angle)) < 0.2:
# #             #     print('forward')
# #             #     direction = np.polyfit(path[:, 1], path[:, 0], deg = 1)[0]
# #             #     print(direction)
# #             #     print('forward2')
# #             #     direction = (point_a[0]-point_b[0]) * 0.1   
# #             #     print(direction)
# #             #     steering_angle = direction        

# #             # 두 차선 모두 인식 안될 경우를 위해 현재 값 저장
# #             self.steering_memory = direction

# #             return direction
    


# #     # ========================================
# #     # 슬라이딩 윈도우를 원본 이미지에 투영하기 위한 역변환 행렬 구하기
# #     # ========================================
# #     def inv_perspective_transform(self, img):
# #         result_img = cv2.warpPerspective(img, self.camera.inv_transform_matrix, (self.camera.WIDTH, self.camera.HEIGHT))
# #         return result_img


# #     # ========================================
# #     # 원본 이미지와 최종 처리된 이미지를 합치기
# #     # ========================================
# #     def combine_img(self, origin_img, result_img):
# #         return cv2.addWeighted(origin_img, 0.5, result_img, 1.0, 0.8)
    
# #     def draw_offset_lines(self,img, center_x=330, y_start=0, y_end=480, max_offset=50, color_start=(0,255,0), color_end=(0,0,255)):
# #         color_diff = np.array(color_end) - np.array(color_start)
# #         for offset in range(0, max_offset + 1, 10):
# #             left_x = center_x - offset
# #             right_x = center_x + offset
# #             color = tuple(map(int, color_start + color_diff * (offset / max_offset)))
# #             img = cv2.line(img, (left_x, y_start), (left_x, y_end), color, 1)
# #             img = cv2.line(img, (right_x, y_start), (right_x, y_end), color, 1)
# #         return img
    

    

# #     # ========================================
# #     # Main 함수
# #     # ========================================
# #     def process(self, origin_img):
# #         origin_img = cv2.resize(origin_img, (640,480), cv2.INTER_LINEAR) # (640, 480) : (width, height)  cv2.INTER_LINEAR : 쌍선형 보간법
# #         img = self.camera.pre_processing(origin_img)
        
# #         #cv2.line(img, (463,0),(410,480),(255,255,255),10)
        
# #         sliding_img, left_fitx, right_fitx, left_lane_detected, right_lane_detected = self.sliding_window(img, draw_windows=True)  # 슬라이딩 윈도우로 곡선 차선 인식

# #         # sliding window 기준으로 가운데에 초록색 경로 그리기
# #         path_x, path_y = self.draw_path(sliding_img, left_fitx, right_fitx, draw_windows=True)

# #         path_x, path_y,base_diff,message,state,state_color = self.get_position(right_fitx,path_x, path_y,sliding_img)


# #         # 곡률을 구하여 조향각 구하기
# #         curvature_angle = self.get_angle(path_x, path_y, left_lane_detected, right_lane_detected)

# #         sliding_img = self.draw_dashed_line(sliding_img, (330,0),(330,480), (255, 255, 0), 2, 10)
# #         sliding_img = self.draw_offset_lines(sliding_img)

# #         direction = ""
# #         if curvature_angle < -5:
# #             direction = "Left"
# #         elif curvature_angle > 5:
# #             direction = "Right"
# #         else:
# #             direction = "Straight"
       
# #         # 주석 처리
# #         sliding_result_img = self.inv_perspective_transform(sliding_img)
# #         combined_img = self.combine_img(origin_img, sliding_result_img)
# #         cv2.putText(combined_img, 'Angle: {}'.format(int(curvature_angle)), (0, 30), 1, 2, (255, 255, 255), 2)
# #         cv2.putText(combined_img, 'base_diff: {}'.format(int(base_diff)), (0, 60), 1, 2, (255, 255, 255), 2)
# #         cv2.putText(combined_img, message, (320, 30), 1, 2, (255, 255, 255), 2)
# #         cv2.putText(combined_img, state, (400, 60), 1, 2, state_color, 2)
# #         cv2.putText(combined_img, direction, (0, 90), 1, 2, (255, 255, 255), 2)

# #         points = np.array([(0, 410), (50, 350), (590, 350), (640, 410)], dtype=np.int32)
# #         combined_img = cv2.polylines(combined_img, [points], True, (255, 255, 0), 1)
# #         combined_img = cv2.line(combined_img,(320, 350), (320, 410),(255,255,0),1)

# #         # cv2.putText(sliding_img, 'base_diff: {}'.format(int(base_diff)), (0, 25), 1, 2, (255, 255, 255), 2)


# #         cv2.imshow('Lane', combined_img)
# #         cv2.imshow('bird',sliding_img)

# #         return curvature_angle


# ######################################################################################################################

# #!/usr/bin/env python3
# # -*- coding:utf-8 -*-


# import numpy as np
# import cv2
# from camera import Camera
# import math


# # =============================================
# # 주행을 위한 알고리즘 클래스 정의
# # =============================================
# class LaneDetector:

#     # ========================================
#     # 변수 선언 및 초기화
#     # ========================================
#     def __init__(self):

#         self.camera = Camera()
#         # 슬라이딩 윈도우 출력 창 크기 좌우 확장 값으로, 좌우로 window_margin 만큼 커짐
#         # 슬라이딩 윈도우 출력 창 가로 크기 : WIDTH + 2*window_margin
#         self.window_margin = 20
#         self.xycar_length = 0.46 # 0.35 meter
#         self.xycar_width = 0.3
#         self.leftx_mid, self.rightx_mid = self.camera.WIDTH *2 // 8, self.camera.WIDTH * 6 // 8  # 슬라이딩 윈도우 기준점 초기 좌표
#         self.leftx_base, self.rightx_base = self.leftx_mid, self.rightx_mid  # 슬라이딩 윈도우 이전값

#         self.left_a, self.left_b, self.left_c = [0], [0], [self.leftx_mid]  # 왼쪽 차선으로부터 나온 2차 곡선 방정식의 계수를 저장하기 위한 변수
#         self.right_a, self.right_b, self.right_c = [0], [0], [self.rightx_mid]
#         # 오른쪽 차선으로부터 나온 2차 곡선 방정식의 계수를 저장하기 위한 변수
#         # 처음 차선이 인식되지 않는 경우를 대비하여, 초기값은 슬라이딩 윈도우 기준점으로부터 직진으로 방정식을 그리도록 함
#         self.leftx_current, self.rightx_current = [self.leftx_mid], [self.rightx_mid]
#         self.ref_diff = self.rightx_mid - self.leftx_mid
#         self.ref_mid = self.ref_diff // 2
#         self.lefty_current, self.righty_current = [480], [480]

#         # 양쪽 차선 곡선 좌표 생성
#         ### Linear y 값 생성 (0, 1, 2, ..., 479)
#         self.ploty = np.linspace(0, self.camera.HEIGHT - 1, self.camera.HEIGHT)
#         # self.ploty2 = np.linspace(0, (self.camera.HEIGHT+self.xycar_length) - 1, (self.camera.HEIGHT+self.xycar_length))
#         self.wins_y = np.linspace(464, 16, 15) # 슬라이딩 윈도우의 y좌표값 

#         # 양쪽 차선 인식 기준 x값 평균을 저장하는 변수, 이전 조향각을 저장하기위한 변수 선언.
#         self.avg_middle, self.steering_memory = 0.0, 0.0
#         self.right_aaa=0
#         self.real_angle=0

#         # making jiwhan
#         self.has_switched = False # 처음에는 부호를 바꾸지 않았음. 양쪽 차선이 인식 안될 경우, 사용할 flag변수. 
#         # making jiwhan

#     # ========================================
#     # 슬라이딩 윈도우
#     # ====================
#     # < input >
#     # img : 입력 이미지
#     # nwindows : 조사창 개수 (좌우 각각 nwindows개씩)
#     # margin : 현재 기준 위치로부터 조사창의 좌우 길이 (-margin ~ +margin)
#     #          조사창 가로 길이 : margin*2
#     # minpix : 조사창 내부에서 차선이 검출된 것으로 판단할 최소 픽셀 개수
#     # draw_windows : 결과창 출력 여부
#     #
#     # ====================
#     # < return >
#     # out_img : 출력 이미지
#     # window_img : 슬라이딩 윈도우 출력을 위한 이미지 (너비 확장)
#     # left_fitx : 왼쪽 차선 곡선 방정식 x 좌표
#     # right_fitx : 오른쪽 차선 곡선 방정식 x 좌표
#     # left_lane_detected : 왼쪽 차선 인식 여부
#     # right_lane_detected : 오른쪽 차선 인식 여부
#     #
#     # ========================================


#     def sliding_window(self, img, nwindows=7, margin=30, minpix=45, draw_windows=False):
#         # 크기 3의 비어있는 배열 생성
#         left_fit_ = np.empty(3)
#         right_fit_ = np.empty(3)

#         # 0과 1로 이진화된 영상을 3채널의 영상으로 만들기 위해 3개를 쌓은 후 *255
#         out_img = np.dstack((img, img, img)) * 255
       
#         # 너비의 중앙값
#         midpoint = self.camera.WIDTH // 2

#         # 조사창의 높이 설정
#         # 전체 높이에서 설정한 조사창 개수만큼 나눈 값
#         window_height = self.camera.HEIGHT // nwindows 

#         # 0이 아닌 픽셀의 x,y 좌표 반환 (흰색 영역(차선)으로 인식할 수 있는 좌표)
#         nonzero = img.nonzero() # 0이 아닌 것을 찾는다.
#         nonzeroy = np.array(nonzero[0])
#         nonzerox = np.array(nonzero[1])

#         # 이전 프레임으로부터 기준점의 좌표를 받아옴
#         # 양쪽 차선 확인 위치 업데이트
#         # 이 값을 기준으로 조사창을 생성하여 차선 확인
#         leftx_current = self.leftx_base
#         rightx_current = self.rightx_base

#         # 차선 확인 시 검출이 되지 않는 경우를 대비해서 바로 이전(화면상 바로 아래) 조사창으로부터 정보를 얻기 위한 변수
#         # 이를 이용해서 조사창 위치의 변화량을 파악
#         # 초기값으로는 현재 기준 좌표를 넣어줌
#         leftx_past = leftx_current
#         rightx_past = rightx_current
#         rightx_past2 = rightx_past

#         # 양쪽 차선 픽셀 인덱스를 담기 위한 빈 배열 선언
#         # 차선의 방정식을 구하거나 차선 인식 판단 여부에 사용
#         left_lane_inds = []
#         right_lane_inds = []

#         # 슬라이딩 윈도우 좌표 값을 담기 위한 빈 배열
#         left_wins_x = []
#         right_wins_x = []

#         # 설정한 조사창 개수만큼 슬라이딩 윈도우 생성
#         for window in range(nwindows):
            
#             # makin jiwhan
#             if window == 0:
#                 print("widno index ================================= {}".format(window))
#                 # 조사창 크기 및 위치 설정
#                 win_y_low = self.camera.HEIGHT - ((window + 1) * window_height)
#                 # n번째 조사창 윗변 y 좌표 : (전체 높이) - (n * 조사창 높이)
#                 win_y_high = self.camera.HEIGHT - (window * window_height)
#                 # 양쪽 차선의 조사창의 너비를 현재 좌표로부터 margin만큼 양 옆으로 키움
#                 win_xleft_low = int(self.leftx_base - margin)
#                 win_xleft_high = int(self.leftx_base + margin)
#                 win_xright_low = int(self.rightx_base - margin)
#                 win_xright_high = int(self.rightx_base + margin)
#             else: 
#                 # 조사창 크기 및 위치 설정
#                 win_y_low = self.camera.HEIGHT - ((window + 1) * window_height)
#                 # n번째 조사창 윗변 y 좌표 : (전체 높이) - (n * 조사창 높이)
#                 win_y_high = self.camera.HEIGHT - (window * window_height)
#                 # 양쪽 차선의 조사창의 너비를 현재 좌표로부터 margin만큼 양 옆으로 키움
#                 win_xleft_low = int(leftx_current - margin)
#                 win_xleft_high = int(leftx_current + margin)
#                 win_xright_low = int(rightx_current - margin)
#                 win_xright_high = int(rightx_current + margin)
#             # making jiwhan

#             # # 이게 원본임. 
#             # # 조사창 크기 및 위치 설정
#             #     win_y_low = self.camera.HEIGHT - ((window + 1) * window_height)
#             #     # n번째 조사창 윗변 y 좌표 : (전체 높이) - (n * 조사창 높이)
#             #     win_y_high = self.camera.HEIGHT - (window * window_height)
#             #     # 양쪽 차선의 조사창의 너비를 현재 좌표로부터 margin만큼 양 옆으로 키움
#             #     win_xleft_low = int(leftx_current - margin)
#             #     win_xleft_high = int(leftx_current + margin)
#             #     win_xright_low = int(rightx_current - margin)
#             #     win_xright_high = int(rightx_current + margin)

#             # 조사창 그리기
#             if draw_windows == True:
#                 # cv2.rectangle(img, start(시작 좌표), end(종료 좌표), color, thickness)
#                 # 왼쪽 차선
#                 cv2.rectangle(out_img, (win_xleft_low, win_y_low), (win_xleft_high, win_y_high), (100, 100, 255), 3)
#                 # 오른쪽 차선
#                 cv2.rectangle(out_img, (win_xright_low, win_y_low), (win_xright_high, win_y_high), (100, 100, 255), 3)

#             # 조사창 내부에서 0이 아닌 픽셀의 인덱스 저장
#             good_left_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high)
#                               & (nonzerox >= win_xleft_low) & (nonzerox < win_xleft_high)).nonzero()[0]
#             good_right_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high)
#                                & (nonzerox >= win_xright_low) & (nonzerox < win_xright_high)).nonzero()[0]

#             # 양쪽 차선의 인덱스 저장
#             left_lane_inds.append(good_left_inds)
#             right_lane_inds.append(good_right_inds)

#             # 조사창 내부에서 0이 아닌 픽셀 개수가 기준치를 넘으면 해당 픽셀들의 인덱스 평균값(x좌표 평균)으로 다음 조사창의 위치(x좌표)를 결정
#             if len(good_left_inds) > minpix:
#                 leftx = nonzerox[good_left_inds]
#                 leftx_current = int(np.mean(leftx))
           
#             if len(good_right_inds) > minpix:
#                 rightx = nonzerox[good_right_inds]
#                 rightx_current = int(np.mean(rightx))
               

#             x_diff = rightx_current - leftx_current

#             # 양쪽 차선 중 하나만 인식된 경우 반대편 차선에서 나타난 인덱스 변화량과 동일하게 인덱스 설정
#             # 인식된 차선의 방향과 동일하게 그려짐
#             if len(good_left_inds) < minpix:
#                 if len(good_right_inds) < minpix:
#                     leftx_current = leftx_current + (rightx_past - rightx_past2)
#                 else:
#                     if x_diff < self.camera.WIDTH // 2:
#                         leftx_current = rightx_current - (self.camera.WIDTH // 2)
#                     else:
#                         leftx_current = leftx_current + (rightx_current - rightx_past)
                       
#             elif len(good_right_inds) < minpix:
#                 if x_diff < self.camera.WIDTH // 2:
#                     rightx_current = leftx_current + (self.camera.WIDTH // 2)
#                 else:
#                     rightx_current = rightx_current + (leftx_current - leftx_past)

#             # 가장 하단에 있는 첫번째 조사창에서 결정된 두번째 조사창의 좌표를 다음 프레임의 기준점으로 결정
#             # 기준점의 위치가 고정되어 변화되는 차선을 따라가지 못하는 것을 방지하고,
#             # 차선이 끊기거나 여러 개의 선이 나타날 때 큰 변화 없이 현재 인식중인 차선의 방향대로 따라가며 효과적인 차선 인식이 가능
#                 # 왼쪽 차선의 기준점이 중앙 기준 우측으로 넘어가지 않도록 제한
#             # if leftx_current > midpoint + 30:
#             #     leftx_current = midpoint + 30
#             if leftx_current > midpoint - 10:
#                 leftx_current = midpoint - 10

#             # 오른쪽 차선의 기준점이 중앙 기준 좌측으로 넘어가지 않도록 제한
#             # if rightx_current < midpoint - 170:
#             #     rightx_current = midpoint - 170
#             # if rightx_current < midpoint - 30:
#             #     rightx_current = midpoint - 30
#             if rightx_current < midpoint + 10:
#                 rightx_current = midpoint + 10


#             if window == 0:
#                 # 왼쪽 차선의 기준점이 왼쪽 화면 밖으로 나가지 않도록 제한
#                 # if leftx_current < 8:
#                 #     leftx_current = 8
#                 if leftx_current < 5:
#                     leftx_current = 5

#                 # 오른쪽 차선의 기준점이 오른쪽 화면 밖으로 나가지 않도록 제한
#                 # if rightx_current > self.camera.WIDTH - 7:
#                 #     rightx_current = self.camera.WIDTH - 7
#                 if rightx_current > self.camera.WIDTH - 5:
#                     rightx_current = self.camera.WIDTH - 5               

#             # 두번째 조사창의 현재 좌표를 다음 프레임의 기준점으로 설정
#                 self.leftx_base = leftx_current                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             
#                 self.rightx_base = rightx_current
           

#             # 슬라이딩 윈도우 중앙 좌표 값 저장
#             left_wins_x.append(leftx_current)
#             right_wins_x.append(rightx_current)

#             # 현재 인덱스 값을 이전 값으로 저장
#             # 한쪽 차선이 인식되지 않은 경우 인식된 차선을 따라가기 위해 사용되는 변수
#             leftx_past = leftx_current
#             rightx_past2 = rightx_past
#             rightx_past = rightx_current

#         # 배열 연결
#         left_lane_inds = np.concatenate(left_lane_inds)
#         right_lane_inds = np.concatenate(right_lane_inds)

#         # 양쪽 차선 픽셀 추출
#         ### 0이 아닌 픽셀 중에서 왼쪽 차선으로 인식된 좌표만 가져옴
#         leftx = nonzerox[left_lane_inds]
#         lefty = nonzeroy[left_lane_inds]
#         ### 0이 아닌 픽셀 중에서 오른쪽 차선으로 인식된 좌표만 가져옴
#         rightx = nonzerox[right_lane_inds]
#         righty = nonzeroy[right_lane_inds]

#         # 차선으로 인식된 픽셀 수가 일정치 이상일 경우에만 차선이 인식된 것으로 판단
#         ### 왼쪽 차선으로 인식된 좌표가 1000개 미만이라면 False, 이상이 middle_point라면 True
#         if (leftx.size < 1000):
#             left_lane_detected = False
#         else:
#             # left_lane_detected = False
#             left_lane_detected = True
#         ### 오른쪽 차선으로 인식된 좌표가 1000개 미만이라면 False, 이상이라면 True
#         if (rightx.size < 1000):
#             right_lane_detected = False
#         else:
#             right_lane_detected = True

#         # 차선이 인식된 것으로 판단되었다면 검출된 좌표로부터 차선의 2차 곡선을 구함
#         # 왼쪽 차선이 인식된 경우
#         if left_lane_detected:
#             # 검출된 차선 좌표들을 통해 왼쪽 차선의 2차 방정식 계수를 구함
#             left_fit = np.polyfit(lefty, leftx, 1)

#             # 왼쪽 차선 계수
#             self.left_a.append(left_fit[0])
#             self.left_b.append(left_fit[1])
#             #self.left_c.append(left_fit[2])

#         # 오른쪽 차선이 인식된 경우
#         if right_lane_detected:
#             # 검출된 차선 좌표들을 통해 오른쪽 차선의 2차 방정식 계수를 구함
#             #right_fit = np.polyfit(righty, rightx, 2)
#             right_fit = np.polyfit(righty, rightx, 1)
#             #print("right_angle",right_fit)w

#             # 오른쪽 차선 계수
#             self.right_a.append(right_fit[0]) #1차직선의 기울기로 수정 
#             self.right_b.append(right_fit[1])
#             #self.right_c.append(right_fit[2])

#         if draw_windows:
#             # 차선으로 검출된 픽셀 값 변경
#             # 왼쪽 차선은 파란색, 오른쪽 차선은 빨간색으로 표시
#             out_img[nonzeroy[left_lane_inds], nonzerox[left_lane_inds]] = [255, 0, 0]
#             out_img[nonzeroy[right_lane_inds], nonzerox[right_lane_inds]] = [0, 0, 255]

#         # 계수마다 각각 마지막 10개의 평균으로 최종 계수 결정
#         # 왼쪽 차선의 계수 결정
#         left_fit_[0] = np.mean(self.left_a[-10:])
#         left_fit_[1] = np.mean(self.left_b[-10:])
#         #left_fit_[2] = np.mean(self.left_c[-10:])
#         # 오른쪽 차선의 계수 결정
#         right_fit_[0] = np.mean(self.right_a[-10:])
#         right_fit_[1] = np.mean(self.right_b[-10:])
#         #right_fit_[2] = np.mean(self.right_c[-10:])

#         # y 값에 해당하는 x 값 결정
#         # 왼쪽 차선
#         left_fitx = left_fit_[0] * self.ploty + left_fit_[1]
#         # 오른쪽 차선
#         right_fitx = right_fit_[0] * self.ploty + right_fit_[1]  
#         # 양쪽 모두 차선인식이 안됐다면 슬라이딩 윈도우 조사창 재설정
#         if (left_lane_detected is False) and (right_lane_detected is False):
#             self.leftx_base = self.leftx_mid
#             # self.rightx_base = self.rightx_mid + 50
#             self.rightx_base = self.rightx_mid

#         # 출력 이미지, 양쪽 곡선 x 좌표, 차선 인식 여부 반환
#         return out_img, left_fitx, right_fitx, left_lane_detected, right_lane_detected, leftx, rightx

#     # sliding window 기준으로 가운데에 초록색 경로 그리기
#     # def draw_path(self, img, left_fitx, right_fitx, draw_windows=False):
#     #     left_fitx = np.array([left_fitx])
#     #     right_fitx = np.array([right_fitx])

#     #     path_x = np.concatenate([left_fitx, right_fitx], axis=0)
#     #     # path_x = np.concatenate([right_fitx], axis=0)
#     #     path_x = np.mean(path_x, axis=0).reshape(-1)

#     #     path_y = self.ploty


#     #     if draw_windows is True:
#     #         for (x, y) in zip(path_x, path_y):
                
#     #             cv2.circle(img, (int(x), int(y)), 3, (0, 255, 0), -1)
#     #             #print("xy:", int(x), int(y))
                
#     #     return path_x, path_y

#     def draw_path(self, img, left_fitx, right_fitx, draw_windows=False, start_point=(320, 410)):
#         left_fitx = np.array([left_fitx])
#         right_fitx = np.array([right_fitx])
#         # left_fitx = right_fitx-400


#         path_x = np.concatenate([left_fitx, right_fitx], axis=0)
#         path_x = np.mean(path_x, axis=0).reshape(-1)

#         path_y = self.ploty

#         # difference = path_x[0] - 320
#         # path_x = path_x - difference
#         print("x {}/{}".format(path_x[0],path_x[-1]))
#         print("x {}/{}".format(path_y[0],path_y[-1]))

#         if draw_windows is True:
#             for (x, y) in zip(path_x, path_y):

#                 cv2.circle(img, (int(x), int(y)), 3, (0, 255, 0), -1)
#             # cv2.line(img,[int(path_x[0]),int(path_y[0])], [int(path_x[-1]),int(path_y[-1])],(0,255,0),3)

#         return path_x, path_y
    
#     def lerp_color(self,color1, color2, t):
#         return tuple(map(int, color1 + t * (color2 - color1)))
    
#     def lane_info(self,leftx, rightx):
#         idx = 0
#         lane_msg = ""
#         if leftx.size > rightx.size:
#             lane_msg = "lane number 1"
#             idx = 1
#         elif leftx.size < rightx.size:
#             lane_msg = "lane number 2"
#             idx = 2
#         return idx, lane_msg

#     def get_position(self, leftx_fit,right_fitx, path_x, path_y, img,lane_idx):
#         right_fitx = np.array([right_fitx])
#         left_fitx = np.array([leftx_fit])
#         base_diff = 0
#         message = ""
#         state = ""
#         path_mid = []
#         lane_mid = 0
#         lane_direction = 0
#         path_x_new = []
#         lane_path = []
#         color_start, color_end = np.array([0, 255, 0]), np.array([0, 0, 255])
#         state_color = (255, 255, 255)        

#         if lane_idx == 1:
#             lane_mid = 330
#             mid_fitx = left_fitx + 180
#             path_mid = np.mean(mid_fitx, axis=0).reshape(-1)
#             base_diff = lane_mid- path_mid[-1]

#         elif lane_idx == 2:     
#             lane_mid = 310
#             mid_fitx = right_fitx - 180
#             path_mid = np.mean(mid_fitx, axis=0).reshape(-1)
#             base_diff = lane_mid- path_mid[-1]


#         if len(path_mid) > 0 and len(path_y) > 0:
#             lane_path = np.concatenate((path_mid.reshape(-1, 1), path_y.reshape(-1, 1)), axis=1)
#             lane_direction = np.polyfit(lane_path[:, 1], lane_path[:, 0], deg = 1)[0] * 1000

#             if lane_direction > 0:
#                 lane_direction *= -0.35
#                 if lane_direction <= -5:
#                     lane_direction *= 0.4
#                 elif lane_direction <= -10:
#                     lane_direction *= 0.45
#                 elif lane_direction <= -15:
#                     lane_direction *= 0.55
#                 elif lane_direction <= -20.0:
#                     lane_direction = -20.0

                
#             elif lane_direction < 0:
#                 lane_direction *= -0.35
#                 if lane_direction >= -5:
#                     lane_direction *= 0.4
#                 elif lane_direction >= 10:
#                     lane_direction *= 0.45
#                 elif lane_direction >= 15:
#                     lane_direction *= 0.55
#                 elif lane_direction >= 20.0:
#                     lane_direction = 20.0
            
#             cv2.circle(img, (int(path_mid[-1]), int(path_y[-1])), 5, (0, 0, 255), 3)
#         else:
#             print("list empty")
        

#         if abs(base_diff) > 10:
#             message = "Path Regenerate"
#             print("---------------------------------------path regenerate---------------------------------------")
#             if base_diff > 0:
#                 path_x_new = np.linspace(path_mid[-1], (path_mid[-1] + base_diff) - 1, self.camera.HEIGHT)
#             elif base_diff < 0:
#                 path_x_new = np.linspace(path_mid[-1], (path_mid[-1]+ base_diff) - 1, self.camera.HEIGHT)
#             path_x = path_x_new

#             max_base_diff = 50
#             for (x, y) in zip(path_x, path_y):
#                 t = abs(min(base_diff, max_base_diff)) / max_base_diff
#                 color = self.lerp_color(color_start, color_end, t)
#                 cv2.circle(img, (int(x), int(y)), 3, color, -1)
            
#         else:
#             path_x = path_x



#         if 0 < abs(base_diff) < 10:
#             state = "Stable"
#             state_color = (0, 255, 0)
#         elif 10 <= abs(base_diff) < 20:
#             state = "Caution"
#             state_color = (0, 255, 255) 
#         elif 20 <= abs(base_diff) < 30:
#             state = "Alert"
#             state_color = (0, 165, 255)
#         elif abs(base_diff) >= 30:
#             state = "Serious"
#             state_color = (0, 0, 255) 

#         return path_x, path_y, base_diff, message, state,state_color, lane_mid, lane_direction



    

#     def draw_dashed_line(self,img, pt1, pt2, color, thickness, dash_length):
#         dist = np.linalg.norm(np.array(pt1) - np.array(pt2))
#         dashes = int(dist / (2 * dash_length))
#         for i in range(dashes):
#             start = np.array(pt1) + i * 2 * dash_length * (np.array(pt2) - np.array(pt1)) / dist
#             end = start + dash_length * (np.array(pt2) - np.array(pt1)) / dist
#             start = tuple(map(int, start))
#             end = tuple(map(int, end))
#             img = cv2.line(img, start, end, color, thickness)

#         return img


#     # 곡률을 구하여 조향각 구하기
#     def get_angle(self, path_x, path_y, left_lane_detected, right_lane_detected):

#         # 차선 두 개 모두 인식 안될 경우
#         # if left_lane_detected is False and right_lane_detected is False:
#         if right_lane_detected is False:
        
            
#             # # making jiwhan - 308~312 
#             # # 가장 최근의 각도 값의 반대 방향으로 조향각 변화를 줌
#             # direction = -self.steering_memory
#             # # 현재 값을 저장
#             # self.steering_memory = direction
#             # print("no detection line ---------------------------------- reverse angle :{}".format(direction))

#             # making jiwhan-------------------------------------------------------------------------------------
#             # 양쪽 차선 모두 인식이 안되는 경우, 가장 마지막 조향각을 return함. 이 경우에는 다시 차선 안쪽으로 들어올 수가 없음.
#             # 그래서 가장 마지막 조향각의 부호를 바꿔서 다시 차선 안쪽으로 들어가게 해야함.
#             # if not self.has_switched:
#             #     # 가장 최근의 각도 값의 반대 방향으로 조향각 변화를 줌
#             #     direction = - (self.steering_memory + 10)
#             #     # 현재 값을 저장
#             #     self.steering_memory = direction
#             #     self.has_switched = True # 부호를 바꾼 것을 표시
#             # else:
#             #     # 이전에 부호를 바꾼 경우 그 값을 사용
#             #     direction = self.steering_memory
        
#             # print("no detection line ---------------------------------- reverse angle :{}".format(direction))
#             # return direction
#             # making jiwhan-------------------------------------------------------------------------------------

#             # 아래가 원본.
#             # 양쪽 차선 모두 인식이 안되는 경우, 가장 마지막 조향각을 return함. 
#             return self.steering_memory * 2

        
#         # 차선 하나라도 인식될 경우
#         else:
#             # making eee
#             self.has_switched = False # 다시 차선이 검출된 경우 부호 바꾸기를 e초기화
#             # making jiwhan

#             path = np.concatenate((path_x.reshape(-1, 1), path_y.reshape(-1, 1)), axis=1)
#             baseline_x = np.full_like(path_x, 320)
#             baseline = np.concatenate((baseline_x.reshape(-1, 1), path_y.reshape(-1, 1)), axis=1)
#             base_diff = baseline[0,0] - path[0,0]

            

#             self.avg_middle = np.mean(path_x, axis=0)

#             point_a = path[0, :]  # Top Point
#             point_b = path[-1, :]  # Bottom Pointself.leftx_mid
#             point_m = [(point_a[0] + point_b[0]) / 2, (point_a[1] + point_b[1]) / 2]  # point_a와 point_b의 중점

#             W = math.sqrt(((point_a[0] - point_b[0]) ** 2) + ((point_a[1] - point_b[1]) ** 2))
#             H = math.sqrt(np.min(np.sum((path - point_m) ** 2, axis=1)))

#             # print("middle_distance: {}".format(middle_dist))
#             # print("point_a",point_a)
#             # print("point_b",point_b)
           
#             # print("xvalue" ,point_b[0]-point_a[0])

#             # 640 pixel = 0.64m  ->  1 pixel = 0.001m
#             radius = ((H / 2) + (W ** 2) / (8 * H)) * 0.001
#             mod_angle = math.atan(480 / base_diff) * (180 / math.pi)

#             # 2차 곡선 기울기 계수 구하기---------------------->1로 수정 
#             direction = np.polyfit(path[:, 1], path[:, 0], deg = 1)[0] * 1000
#             # direction = direction - mod_angle
#             #print("dir",direction)
#             #direction = self.right_aaa

#             #2차곡선 기울기가 0인경우 ->직선인 경우 
#             self.real_angle = direction

#             # if direction > 85:
#             #     direction = 0

#             if direction > 0:
#                 direction *= -0.35
#                 if direction <= -5:
#                     direction *= 0.4
#                 elif direction <= -10:
#                     direction *= 0.45
#                 elif direction <= -15:
#                     direction *= 0.55
#                 elif direction <= -20.0:
#                     direction = -20.0

                
#             elif direction < 0:
#                 direction *= -0.35
#                 if direction >= -5:
#                     direction *= 0.4
#                 elif direction >= 10:
#                     direction *= 0.45
#                 elif direction >= 15:
#                     direction *= 0.55
#                 elif direction >= 20.0:
#                     direction = 20.0

#             # if -1.5<steering_angle<1.5 :
#             #     if (point_a[0]-point_b[0]) > 0:
#             #         #print('0, right',(point_a[0]-point_b[0])/10)
#             #         steering_angle = (point_a[0]-point_b[0]) *0.1
#             #     elif (point_a[0]-point_b[0]) < 0:
#             #         #print('0, left',(point_a[0]-point_b[0])/10)
#             #         steering_angle = (point_a[0]-point_b[0]) *0.1
#             #     else:
#             #         #print("0, straight")
#             #         steering_angle = 0

#             # if (point_a[0]-point_b[0]) > 0:
#             # if (abs(steering_angle)) < 0.2:
#             #     print('forward')
#             #     direction = np.polyfit(path[:, 1], path[:, 0], deg = 1)[0]
#             #     print(direction)
#             #     print('forward2')
#             #     direction = (point_a[0]-point_b[0]) * 0.1   
#             #     print(direction)
#             #     steering_angle = direction        

#             # 두 차선 모두 인식 안될 경우를 위해 현재 값 저장
#             self.steering_memory = direction

#             return direction
    


#     # ========================================
#     # 슬라이딩 윈도우를 원본 이미지에 투영하기 위한 역변환 행렬 구하기
#     # ========================================
#     def inv_perspective_transform(self, img):
#         result_img = cv2.warpPerspective(img, self.camera.inv_transform_matrix, (self.camera.WIDTH, self.camera.HEIGHT))
#         return result_img


#     # ========================================
#     # 원본 이미지와 최종 처리된 이미지를 합치기
#     # ========================================
#     def combine_img(self, origin_img, result_img):
#         return cv2.addWeighted(origin_img, 0.5, result_img, 1.0, 0.8)
    
#     def draw_offset_lines(self,img, center_x, y_start=0, y_end=480, max_offset=50, color_start=(0,255,0), color_end=(0,0,255)):
#         color_diff = np.array(color_end) - np.array(color_start)
#         for offset in range(0, max_offset + 1, 10):
#             left_x = center_x - offset
#             right_x = center_x + offset
#             color = tuple(map(int, color_start + color_diff * (offset / max_offset)))
#             img = cv2.line(img, (left_x, y_start), (left_x, y_end), color, 1)
#             img = cv2.line(img, (right_x, y_start), (right_x, y_end), color, 1)
#         return img
    

    

#     # ========================================
#     # Main 함수
#     # ========================================
#     def process(self, origin_img):
#         origin_img = cv2.resize(origin_img, (640,480), cv2.INTER_LINEAR) # (640, 480) : (width, height)  cv2.INTER_LINEAR : 쌍선형 보간법
#         img = self.camera.pre_processing(origin_img)
#         counter_msg = ""
        
#         #cv2.line(img, (463,0),(410,480),(255,255,255),10)
        
#         sliding_img, left_fitx, right_fitx, left_lane_detected, right_lane_detected, leftx, rightx = self.sliding_window(img, draw_windows=True)  # 슬라이딩 윈도우로 곡선 차선 인식



#         # sliding window 기준으로 가운데에 초록색 경로 그리기
#         path_x, path_y = self.draw_path(sliding_img, left_fitx, right_fitx, draw_windows=True)

        
#         # 현재 차량이 있는 차로의 정보 구하기
#         lane_idx, lane_msg = self.lane_info(leftx,rightx)

#         # 차로위에 있는 차량의 위치 정보를 토대로 경로 재설정
#         path_x_new, path_y_new,base_diff,message,state,state_color,lane_mid, lane_direction = self.get_position(left_fitx,right_fitx,path_x, path_y,sliding_img,lane_idx)


#         # 곡률을 구하여 조향각 구하기
#         curvature_angle = self.get_angle(path_x, path_y, left_lane_detected, right_lane_detected)
#         curvature_angle_new = self.get_angle(path_x_new, path_y_new, left_lane_detected, right_lane_detected)
#         if lane_direction * curvature_angle_new > 0:
#             pass
#         elif lane_direction * curvature_angle_new < 0:
#             counter_msg = "Counter Steerung"
#             if curvature_angle_new > 0:
#                 curvature_angle_new = 3
#             elif curvature_angle_new < 0:
#                 curvature_angle_new = -3
                


#         sliding_img = self.draw_dashed_line(sliding_img, (lane_mid,0),(lane_mid,480), (255, 255, 0), 2, 10)
#         sliding_img = self.draw_offset_lines(sliding_img,lane_mid)

#         direction = ""
#         if curvature_angle < -5:
#             direction = "Left"
#         elif curvature_angle > 5:
#             direction = "Right"
#         else:
#             direction = "Straight"
       
#         # 주석 처리
#         sliding_result_img = self.inv_perspective_transform(sliding_img)
#         combined_img = self.combine_img(origin_img, sliding_result_img)
#         cv2.putText(combined_img, 'Angle: {}'.format(int(curvature_angle_new)), (0, 30), 1, 2, (255, 255, 255), 2)
#         cv2.putText(combined_img, 'lane Angle: {}'.format(int(lane_direction)), (0, 60), 1, 2, (255, 255, 255), 2)
#         cv2.putText(combined_img, 'base_diff: {}'.format(int(base_diff)), (0, 90), 1, 2, (255, 255, 255), 2)
#         cv2.putText(combined_img, message, (320, 30), 1, 2, (255, 255, 255), 2)
#         cv2.putText(combined_img, state, (400, 60), 1, 2, state_color, 2)
#         cv2.putText(combined_img, counter_msg, (320, 90), 1, 2, (255, 255, 255), 2)
#         cv2.putText(combined_img, direction, (0, 120), 1, 2, (255, 255, 255), 2)
#         cv2.putText(combined_img, lane_msg, (0, 150), 1, 2, (255, 255, 255), 2)

#         points = np.array([(0, 410), (50, 350), (590, 350), (640, 410)], dtype=np.int32)
#         combined_img = cv2.polylines(combined_img, [points], True, (255, 255, 0), 1)
#         combined_img = cv2.line(combined_img,(320, 350), (320, 410),(255,255,0),1)

#         # cv2.putText(sliding_img, 'base_diff: {}'.format(int(base_diff)), (0, 25), 1, 2, (255, 255, 255), 2)


#         cv2.imshow('Lane', combined_img)
#         cv2.imshow('bird',sliding_img)

#         return curvature_angle

#!/usr/bin/env python3
# -*- coding:utf-8 -*-


import numpy as np
import cv2
from camera import Camera
import math


# =============================================
# 주행을 위한 알고리즘 클래스 정의
# =============================================
class LaneDetector:

    # ========================================
    # 변수 선언 및 초기화
    # ========================================
    def __init__(self):

        self.camera = Camera()
        # 슬라이딩 윈도우 출력 창 크기 좌우 확장 값으로, 좌우로 window_margin 만큼 커짐
        # 슬라이딩 윈도우 출력 창 가로 크기 : WIDTH + 2*window_margin
        self.window_margin = 20
        self.xycar_length = 0.46 # 0.35 meter
        self.xycar_width = 0.3
        self.leftx_mid, self.rightx_mid = self.camera.WIDTH *2 // 8, self.camera.WIDTH * 6 // 8  # 슬라이딩 윈도우 기준점 초기 좌표
        self.leftx_base, self.rightx_base = self.leftx_mid, self.rightx_mid  # 슬라이딩 윈도우 이전값

        self.left_a, self.left_b, self.left_c = [0], [0], [self.leftx_mid]  # 왼쪽 차선으로부터 나온 2차 곡선 방정식의 계수를 저장하기 위한 변수
        self.right_a, self.right_b, self.right_c = [0], [0], [self.rightx_mid]
        # 오른쪽 차선으로부터 나온 2차 곡선 방정식의 계수를 저장하기 위한 변수
        # 처음 차선이 인식되지 않는 경우를 대비하여, 초기값은 슬라이딩 윈도우 기준점으로부터 직진으로 방정식을 그리도록 함
        self.leftx_current, self.rightx_current = [self.leftx_mid], [self.rightx_mid]
        self.ref_diff = self.rightx_mid - self.leftx_mid
        self.ref_mid = self.ref_diff // 2
        self.lefty_current, self.righty_current = [480], [480]

        # 양쪽 차선 곡선 좌표 생성
        ### Linear y 값 생성 (0, 1, 2, ..., 479)
        self.ploty = np.linspace(0, self.camera.HEIGHT - 1, self.camera.HEIGHT)
        # self.ploty2 = np.linspace(0, (self.camera.HEIGHT+self.xycar_length) - 1, (self.camera.HEIGHT+self.xycar_length))
        self.wins_y = np.linspace(464, 16, 15) # 슬라이딩 윈도우의 y좌표값 

        # 양쪽 차선 인식 기준 x값 평균을 저장하는 변수, 이전 조향각을 저장하기위한 변수 선언.
        self.avg_middle, self.steering_memory = 0.0, 0.0
        self.right_aaa=0
        self.real_angle=0

        # making jiwhan
        self.has_switched = False # 처음에는 부호를 바꾸지 않았음. 양쪽 차선이 인식 안될 경우, 사용할 flag변수. 
        # making jiwhan

    # ========================================
    # 슬라이딩 윈도우
    # ====================
    # < input >
    # img : 입력 이미지
    # nwindows : 조사창 개수 (좌우 각각 nwindows개씩)
    # margin : 현재 기준 위치로부터 조사창의 좌우 길이 (-margin ~ +margin)
    #          조사창 가로 길이 : margin*2
    # minpix : 조사창 내부에서 차선이 검출된 것으로 판단할 최소 픽셀 개수
    # draw_windows : 결과창 출력 여부
    #
    # ====================
    # < return >
    # out_img : 출력 이미지
    # window_img : 슬라이딩 윈도우 출력을 위한 이미지 (너비 확장)
    # left_fitx : 왼쪽 차선 곡선 방정식 x 좌표
    # right_fitx : 오른쪽 차선 곡선 방정식 x 좌표
    # left_lane_detected : 왼쪽 차선 인식 여부
    # right_lane_detected : 오른쪽 차선 인식 여부
    #
    # ========================================


    def sliding_window(self, img, nwindows=7, margin=30, minpix=45, draw_windows=False):
        # 크기 3의 비어있는 배열 생성
        left_fit_ = np.empty(3)
        right_fit_ = np.empty(3)

        # 0과 1로 이진화된 영상을 3채널의 영상으로 만들기 위해 3개를 쌓은 후 *255
        out_img = np.dstack((img, img, img)) * 255
       
        # 너비의 중앙값
        midpoint = self.camera.WIDTH // 2

        # 조사창의 높이 설정
        # 전체 높이에서 설정한 조사창 개수만큼 나눈 값
        window_height = self.camera.HEIGHT // nwindows 

        # 0이 아닌 픽셀의 x,y 좌표 반환 (흰색 영역(차선)으로 인식할 수 있는 좌표)
        nonzero = img.nonzero() # 0이 아닌 것을 찾는다.
        nonzeroy = np.array(nonzero[0])
        nonzerox = np.array(nonzero[1])

        # 이전 프레임으로부터 기준점의 좌표를 받아옴
        # 양쪽 차선 확인 위치 업데이트
        # 이 값을 기준으로 조사창을 생성하여 차선 확인
        leftx_current = self.leftx_base
        rightx_current = self.rightx_base

        # 차선 확인 시 검출이 되지 않는 경우를 대비해서 바로 이전(화면상 바로 아래) 조사창으로부터 정보를 얻기 위한 변수
        # 이를 이용해서 조사창 위치의 변화량을 파악
        # 초기값으로는 현재 기준 좌표를 넣어줌
        leftx_past = leftx_current
        rightx_past = rightx_current
        rightx_past2 = rightx_past

        # 양쪽 차선 픽셀 인덱스를 담기 위한 빈 배열 선언
        # 차선의 방정식을 구하거나 차선 인식 판단 여부에 사용
        left_lane_inds = []
        right_lane_inds = []

        # 슬라이딩 윈도우 좌표 값을 담기 위한 빈 배열
        left_wins_x = []
        right_wins_x = []

        # 설정한 조사창 개수만큼 슬라이딩 윈도우 생성
        for window in range(nwindows):
            
            # makin jiwhan
            if window == 0:
                print("widno index ================================= {}".format(window))
                # 조사창 크기 및 위치 설정
                win_y_low = self.camera.HEIGHT - ((window + 1) * window_height)
                # n번째 조사창 윗변 y 좌표 : (전체 높이) - (n * 조사창 높이)
                win_y_high = self.camera.HEIGHT - (window * window_height)
                # 양쪽 차선의 조사창의 너비를 현재 좌표로부터 margin만큼 양 옆으로 키움
                win_xleft_low = int(self.leftx_base - margin)
                win_xleft_high = int(self.leftx_base + margin)
                win_xright_low = int(self.rightx_base - margin)
                win_xright_high = int(self.rightx_base + margin)
            else: 
                # 조사창 크기 및 위치 설정
                win_y_low = self.camera.HEIGHT - ((window + 1) * window_height)
                # n번째 조사창 윗변 y 좌표 : (전체 높이) - (n * 조사창 높이)
                win_y_high = self.camera.HEIGHT - (window * window_height)
                # 양쪽 차선의 조사창의 너비를 현재 좌표로부터 margin만큼 양 옆으로 키움
                win_xleft_low = int(leftx_current - margin)
                win_xleft_high = int(leftx_current + margin)
                win_xright_low = int(rightx_current - margin)
                win_xright_high = int(rightx_current + margin)
            # making jiwhan

            # # 이게 원본임. 
            # # 조사창 크기 및 위치 설정
            #     win_y_low = self.camera.HEIGHT - ((window + 1) * window_height)
            #     # n번째 조사창 윗변 y 좌표 : (전체 높이) - (n * 조사창 높이)
            #     win_y_high = self.camera.HEIGHT - (window * window_height)
            #     # 양쪽 차선의 조사창의 너비를 현재 좌표로부터 margin만큼 양 옆으로 키움
            #     win_xleft_low = int(leftx_current - margin)
            #     win_xleft_high = int(leftx_current + margin)
            #     win_xright_low = int(rightx_current - margin)
            #     win_xright_high = int(rightx_current + margin)

            # 조사창 그리기
            if draw_windows == True:
                # cv2.rectangle(img, start(시작 좌표), end(종료 좌표), color, thickness)
                # 왼쪽 차선
                cv2.rectangle(out_img, (win_xleft_low, win_y_low), (win_xleft_high, win_y_high), (100, 100, 255), 3)
                # 오른쪽 차선
                cv2.rectangle(out_img, (win_xright_low, win_y_low), (win_xright_high, win_y_high), (100, 100, 255), 3)

            # 조사창 내부에서 0이 아닌 픽셀의 인덱스 저장
            good_left_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high)
                              & (nonzerox >= win_xleft_low) & (nonzerox < win_xleft_high)).nonzero()[0]
            good_right_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high)
                               & (nonzerox >= win_xright_low) & (nonzerox < win_xright_high)).nonzero()[0]

            # 양쪽 차선의 인덱스 저장
            left_lane_inds.append(good_left_inds)
            right_lane_inds.append(good_right_inds)

            # 조사창 내부에서 0이 아닌 픽셀 개수가 기준치를 넘으면 해당 픽셀들의 인덱스 평균값(x좌표 평균)으로 다음 조사창의 위치(x좌표)를 결정
            if len(good_left_inds) > minpix:
                leftx = nonzerox[good_left_inds]
                leftx_current = int(np.mean(leftx))
           
            if len(good_right_inds) > minpix:
                rightx = nonzerox[good_right_inds]
                rightx_current = int(np.mean(rightx))
               

            x_diff = rightx_current - leftx_current

            # 양쪽 차선 중 하나만 인식된 경우 반대편 차선에서 나타난 인덱스 변화량과 동일하게 인덱스 설정
            # 인식된 차선의 방향과 동일하게 그려짐
            if len(good_left_inds) < minpix:
                if len(good_right_inds) < minpix:
                    leftx_current = leftx_current + (rightx_past - rightx_past2)
                else:
                    if x_diff < self.camera.WIDTH // 2:
                        leftx_current = rightx_current - (self.camera.WIDTH // 2)
                    else:
                        leftx_current = leftx_current + (rightx_current - rightx_past)
                       
            elif len(good_right_inds) < minpix:
                if x_diff < self.camera.WIDTH // 2:
                    rightx_current = leftx_current + (self.camera.WIDTH // 2)
                else:
                    rightx_current = rightx_current + (leftx_current - leftx_past)

            # 가장 하단에 있는 첫번째 조사창에서 결정된 두번째 조사창의 좌표를 다음 프레임의 기준점으로 결정
            # 기준점의 위치가 고정되어 변화되는 차선을 따라가지 못하는 것을 방지하고,
            # 차선이 끊기거나 여러 개의 선이 나타날 때 큰 변화 없이 현재 인식중인 차선의 방향대로 따라가며 효과적인 차선 인식이 가능
                # 왼쪽 차선의 기준점이 중앙 기준 우측으로 넘어가지 않도록 제한
            # if leftx_current > midpoint + 30:
            #     leftx_current = midpoint + 30
            if leftx_current > midpoint - 10:
                leftx_current = midpoint - 10

            # 오른쪽 차선의 기준점이 중앙 기준 좌측으로 넘어가지 않도록 제한
            # if rightx_current < midpoint - 170:
            #     rightx_current = midpoint - 170
            # if rightx_current < midpoint - 30:
            #     rightx_current = midpoint - 30
            if rightx_current < midpoint + 10:
                rightx_current = midpoint + 10


            if window == 0:
                # 왼쪽 차선의 기준점이 왼쪽 화면 밖으로 나가지 않도록 제한
                # if leftx_current < 8:
                #     leftx_current = 8
                if leftx_current < 5:
                    leftx_current = 5

                # 오른쪽 차선의 기준점이 오른쪽 화면 밖으로 나가지 않도록 제한
                # if rightx_current > self.camera.WIDTH - 7:
                #     rightx_current = self.camera.WIDTH - 7
                if rightx_current > self.camera.WIDTH - 5:
                    rightx_current = self.camera.WIDTH - 5               

            # 두번째 조사창의 현재 좌표를 다음 프레임의 기준점으로 설정
                self.leftx_base = leftx_current                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             
                self.rightx_base = rightx_current
           

            # 슬라이딩 윈도우 중앙 좌표 값 저장
            left_wins_x.append(leftx_current)
            right_wins_x.append(rightx_current)

            # 현재 인덱스 값을 이전 값으로 저장
            # 한쪽 차선이 인식되지 않은 경우 인식된 차선을 따라가기 위해 사용되는 변수
            leftx_past = leftx_current
            rightx_past2 = rightx_past
            rightx_past = rightx_current

        # 배열 연결
        left_lane_inds = np.concatenate(left_lane_inds)
        right_lane_inds = np.concatenate(right_lane_inds)

        # 양쪽 차선 픽셀 추출
        ### 0이 아닌 픽셀 중에서 왼쪽 차선으로 인식된 좌표만 가져옴
        leftx = nonzerox[left_lane_inds]
        lefty = nonzeroy[left_lane_inds]
        ### 0이 아닌 픽셀 중에서 오른쪽 차선으로 인식된 좌표만 가져옴
        rightx = nonzerox[right_lane_inds]
        righty = nonzeroy[right_lane_inds]

        # 차선으로 인식된 픽셀 수가 일정치 이상일 경우에만 차선이 인식된 것으로 판단
        ### 왼쪽 차선으로 인식된 좌표가 1000개 미만이라면 False, 이상이 middle_point라면 True
        if (leftx.size < 1000):
            left_lane_detected = False
        else:
            # left_lane_detected = False
            left_lane_detected = True
        ### 오른쪽 차선으로 인식된 좌표가 1000개 미만이라면 False, 이상이라면 True
        if (rightx.size < 1000):
            right_lane_detected = False
        else:
            right_lane_detected = True

        # 차선이 인식된 것으로 판단되었다면 검출된 좌표로부터 차선의 2차 곡선을 구함
        # 왼쪽 차선이 인식된 경우
        if left_lane_detected:
            # 검출된 차선 좌표들을 통해 왼쪽 차선의 2차 방정식 계수를 구함
            left_fit = np.polyfit(lefty, leftx, 1)

            # 왼쪽 차선 계수
            self.left_a.append(left_fit[0])
            self.left_b.append(left_fit[1])
            #self.left_c.append(left_fit[2])

        # 오른쪽 차선이 인식된 경우
        if right_lane_detected:
            # 검출된 차선 좌표들을 통해 오른쪽 차선의 2차 방정식 계수를 구함
            #right_fit = np.polyfit(righty, rightx, 2)
            right_fit = np.polyfit(righty, rightx, 1)
            #print("right_angle",right_fit)w

            # 오른쪽 차선 계수
            self.right_a.append(right_fit[0]) #1차직선의 기울기로 수정 
            self.right_b.append(right_fit[1])
            #self.right_c.append(right_fit[2])

        if draw_windows:
            # 차선으로 검출된 픽셀 값 변경
            # 왼쪽 차선은 파란색, 오른쪽 차선은 빨간색으로 표시
            out_img[nonzeroy[left_lane_inds], nonzerox[left_lane_inds]] = [255, 0, 0]
            out_img[nonzeroy[right_lane_inds], nonzerox[right_lane_inds]] = [0, 0, 255]

        # 계수마다 각각 마지막 10개의 평균으로 최종 계수 결정
        # 왼쪽 차선의 계수 결정
        left_fit_[0] = np.mean(self.left_a[-10:])
        left_fit_[1] = np.mean(self.left_b[-10:])
        #left_fit_[2] = np.mean(self.left_c[-10:])
        # 오른쪽 차선의 계수 결정
        right_fit_[0] = np.mean(self.right_a[-10:])
        right_fit_[1] = np.mean(self.right_b[-10:])
        #right_fit_[2] = np.mean(self.right_c[-10:])

        # y 값에 해당하는 x 값 결정
        # 왼쪽 차선
        left_fitx = left_fit_[0] * self.ploty + left_fit_[1]
        # 오른쪽 차선
        right_fitx = right_fit_[0] * self.ploty + right_fit_[1]  
        # 양쪽 모두 차선인식이 안됐다면 슬라이딩 윈도우 조사창 재설정
        if (left_lane_detected is False) and (right_lane_detected is False):
            self.leftx_base = self.leftx_mid
            # self.rightx_base = self.rightx_mid + 50
            self.rightx_base = self.rightx_mid

        # 출력 이미지, 양쪽 곡선 x 좌표, 차선 인식 여부 반환
        return out_img, left_fitx, right_fitx, left_lane_detected, right_lane_detected, leftx, rightx

    # sliding window 기준으로 가운데에 초록색 경로 그리기
    # def draw_path(self, img, left_fitx, right_fitx, draw_windows=False):
    #     left_fitx = np.array([left_fitx])
    #     right_fitx = np.array([right_fitx])

    #     path_x = np.concatenate([left_fitx, right_fitx], axis=0)
    #     # path_x = np.concatenate([right_fitx], axis=0)
    #     path_x = np.mean(path_x, axis=0).reshape(-1)

    #     path_y = self.ploty


    #     if draw_windows is True:
    #         for (x, y) in zip(path_x, path_y):
                
    #             cv2.circle(img, (int(x), int(y)), 3, (0, 255, 0), -1)
    #             #print("xy:", int(x), int(y))
                
    #     return path_x, path_y

    def draw_path(self, img, left_fitx, right_fitx, draw_windows=False, start_point=(320, 410)):
        left_fitx = np.array([left_fitx])
        right_fitx = np.array([right_fitx])
        # left_fitx = right_fitx-400


        path_x = np.concatenate([left_fitx, right_fitx], axis=0)
        path_x = np.mean(path_x, axis=0).reshape(-1)

        path_y = self.ploty

        # difference = path_x[0] - 320
        # path_x = path_x - difference
        print("x {}/{}".format(path_x[0],path_x[-1]))
        print("x {}/{}".format(path_y[0],path_y[-1]))

        if draw_windows is True:
            for (x, y) in zip(path_x, path_y):

                cv2.circle(img, (int(x), int(y)), 3, (0, 255, 0), -1)
            # cv2.line(img,[int(path_x[0]),int(path_y[0])], [int(path_x[-1]),int(path_y[-1])],(0,255,0),3)

        return path_x, path_y
    
    def lerp_color(self,color1, color2, t):
        return tuple(map(int, color1 + t * (color2 - color1)))
    
    def lane_info(self,right_lane_detected):
        idx = 0
        lane_msg = ""
        if right_lane_detected:
            lane_msg = "lane number 2"
            idx = 2
        else:
            lane_msg = "lane number 1"
            idx = 1
        return idx, lane_msg

    def get_position(self, left_fitx, right_fitx, path_x, path_y, img,lane_idx):
        right_fitx = np.array([right_fitx])
        left_fitx = np.array([left_fitx])
        base_diff = 0
        message = ""
        state = ""
        dv_msg = ""
        path_mid = []
        lane_mid = 0
        lane_direction = 0
        path_x_new = []
        lane_path = []
        color_start, color_end = np.array([0, 255, 0]), np.array([0, 0, 255])
        state_color = (255, 255, 255)        

        if lane_idx == 1:
            lane_mid = 320
            mid_fitx = left_fitx + 170
            path_mid = np.mean(mid_fitx, axis=0).reshape(-1)
            base_diff = lane_mid- path_mid[-1]

        elif lane_idx == 2:    
            lane_mid = 330
            mid_fitx = right_fitx - 160
            path_mid = np.mean(mid_fitx, axis=0).reshape(-1)
            base_diff = lane_mid- path_mid[-1]


        if len(path_mid) > 0 and len(path_y) > 0:
            lane_path = np.concatenate((path_mid.reshape(-1, 1), path_y.reshape(-1, 1)), axis=1)
            lane_direction = np.polyfit(lane_path[:, 1], lane_path[:, 0], deg = 1)[0] * 1000

            if lane_direction > 0:
                lane_direction *= -0.35
                if lane_direction <= -5:
                    lane_direction *= 0.4
                elif lane_direction <= -10:
                    lane_direction *= 0.45
                elif lane_direction <= -15:
                    lane_direction *= 0.55
                elif lane_direction <= -20.0:
                    lane_direction = -20.0

                
            elif lane_direction < 0:
                lane_direction *= -0.35
                if lane_direction >= 5:
                    lane_direction *= 0.4
                elif lane_direction >= 10:
                    lane_direction *= 0.45
                elif lane_direction >= 15:
                    lane_direction *= 0.55
                elif lane_direction >= 20.0:
                    lane_direction = 20.0
            
            cv2.circle(img, (int(path_mid[-1]), int(path_y[-1])), 5, (0, 0, 255), 3)
        else:
            print("list empty")
        

        if abs(base_diff) > 5:
            message = "Path Regenerate"
            print("---------------------------------------path regenerate---------------------------------------")
            if base_diff > 0:
                path_x_new = np.linspace(path_mid[-1], (path_mid[-1] + base_diff*0.6) - 1, self.camera.HEIGHT)
            elif base_diff < 0:
                path_x_new = np.linspace(path_mid[-1], (path_mid[-1]+ base_diff*0.6) - 1, self.camera.HEIGHT)
            path_x = path_x_new

            max_base_diff = 50
            for (x, y) in zip(path_x, path_y):
                t = abs(min(base_diff, max_base_diff)) / max_base_diff
                color = self.lerp_color(color_start, color_end, t)
                cv2.circle(img, (int(x), int(y)), 3, color, -1)
            
        else:
            path_x = path_x



        if 0 < abs(base_diff) < 10:
            state = "Stable"
            state_color = (0, 255, 0)
        elif 10 <= abs(base_diff) < 20:
            state = "Caution"
            state_color = (0, 255, 255) 
        elif 20 <= abs(base_diff) < 30:
            state = "Alert"
            state_color = (0, 165, 255)
        elif abs(base_diff) >= 30:
            state = "Serious"
            state_color = (0, 0, 255) 

        return path_x, path_y, base_diff, message, state,state_color, lane_mid, lane_direction



    

    def draw_dashed_line(self,img, pt1, pt2, color, thickness, dash_length):
        dist = np.linalg.norm(np.array(pt1) - np.array(pt2))
        dashes = int(dist / (2 * dash_length))
        for i in range(dashes):
            start = np.array(pt1) + i * 2 * dash_length * (np.array(pt2) - np.array(pt1)) / dist
            end = start + dash_length * (np.array(pt2) - np.array(pt1)) / dist
            start = tuple(map(int, start))
            end = tuple(map(int, end))
            img = cv2.line(img, start, end, color, thickness)

        return img


    # 곡률을 구하여 조향각 구하기
    def get_angle(self, path_x, path_y, left_lane_detected, right_lane_detected):

        # 차선 두 개 모두 인식 안될 경우
        if left_lane_detected is False and right_lane_detected is False:
        # if right_lane_detected is False:
        
            
            # # making jiwhan - 308~312 
            # # 가장 최근의 각도 값의 반대 방향으로 조향각 변화를 줌
            # direction = -self.steering_memory
            # # 현재 값을 저장
            # self.steering_memory = direction
            # print("no detection line ---------------------------------- reverse angle :{}".format(direction))

            # making jiwhan-------------------------------------------------------------------------------------
            # 양쪽 차선 모두 인식이 안되는 경우, 가장 마지막 조향각을 return함. 이 경우에는 다시 차선 안쪽으로 들어올 수가 없음.
            # 그래서 가장 마지막 조향각의 부호를 바꿔서 다시 차선 안쪽으로 들어가게 해야함.
            # if not self.has_switched:
            #     # 가장 최근의 각도 값의 반대 방향으로 조향각 변화를 줌
            #     direction = - (self.steering_memory + 10)
            #     # 현재 값을 저장
            #     self.steering_memory = direction
            #     self.has_switched = True # 부호를 바꾼 것을 표시
            # else:
            #     # 이전에 부호를 바꾼 경우 그 값을 사용
            #     direction = self.steering_memory
        
            # print("no detection line ---------------------------------- reverse angle :{}".format(direction))
            # return direction
            # making jiwhan-------------------------------------------------------------------------------------

            # 아래가 원본.
            # 양쪽 차선 모두 인식이 안되는 경우, 가장 마지막 조향각을 return함. 
            return self.steering_memory * 2

        
        # 차선 하나라도 인식될 경우
        else:
            # making eee
            self.has_switched = False # 다시 차선이 검출된 경우 부호 바꾸기를 e초기화
            # making jiwhan

            path = np.concatenate((path_x.reshape(-1, 1), path_y.reshape(-1, 1)), axis=1)
            baseline_x = np.full_like(path_x, 320)
            baseline = np.concatenate((baseline_x.reshape(-1, 1), path_y.reshape(-1, 1)), axis=1)
            base_diff = baseline[0,0] - path[0,0]

            

            # self.avg_middle = np.mealeftx_fitn(path_x, axis=0)
            self.avg_middle = np.mean(path_x, axis=0)

            point_a = path[0, :]  # Top Point
            point_b = path[-1, :]  # Bottom Pointself.leftx_mid
            point_m = [(point_a[0] + point_b[0]) / 2, (point_a[1] + point_b[1]) / 2]  # point_a와 point_b의 중점

            W = math.sqrt(((point_a[0] - point_b[0]) ** 2) + ((point_a[1] - point_b[1]) ** 2))
            H = math.sqrt(np.min(np.sum((path - point_m) ** 2, axis=1)))

            # print("middle_distance: {}".format(middle_dist))
            # print("point_a",point_a)
            # print("point_b",point_b)
           
            # print("xvalue" ,point_b[0]-point_a[0])

            # 640 pixel = 0.64m  ->  1 pixel = 0.001m
            radius = ((H / 2) + (W ** 2) / (8 * H)) * 0.001
            mod_angle = math.atan(480 / base_diff) * (180 / math.pi)

            # 2차 곡선 기울기 계수 구하기---------------------->1로 수정 
            direction = np.polyfit(path[:, 1], path[:, 0], deg = 1)[0] * 1000
            # direction = direction - mod_angle
            #print("dir",direction)
            #direction = self.right_aaa

            #2차곡선 기울기가 0인경우 ->직선인 경우 
            self.real_angle = direction

            # if direction > 85:
            #     direction = 0

            if direction > 0:
                direction *= -0.4
                if direction <= -5:
                    direction *= 0.45
                elif direction <= -10:
                    direction *= 0.5
                elif direction <= -15:
                    direction *= 0.55
                elif direction <= -20.0:
                    direction = -20.0

                
            elif direction < 0:
                direction *= -0.4
                if direction >= 5:
                    direction *= 0.45
                elif direction >= 10:
                    direction *= 0.5
                elif direction >= 15:
                    direction *= 0.55
                elif direction >= 20.0:
                    direction = 20.0

            # if -1.5<steering_angle<1.5 :
            #     if (point_a[0]-point_b[0]) > 0:
            #         #print('0, right',(point_a[0]-point_b[0])/10)
            #         steering_angle = (point_a[0]-point_b[0]) *0.1
            #     elif (point_a[0]-point_b[0]) < 0:
            #         #print('0, left',(point_a[0]-point_b[0])/10)
            #         steering_angle = (point_a[0]-point_b[0]) *0.1
            #     else:
            #         #print("0, straight")
            #         steering_angle = 0

            # if (point_a[0]-point_b[0]) > 0:
            # if (abs(steering_angle)) < 0.2:
            #     print('forward')
            #     direction = np.polyfit(path[:, 1], path[:, 0], deg = 1)[0]
            #     print(direction)
            #     print('forward2')
            #     direction = (point_a[0]-point_b[0]) * 0.1   
            #     print(direction)
            #     steering_angle = direction        

            # 두 차선 모두 인식 안될 경우를 위해 현재 값 저장
            self.steering_memory = direction

            return direction
    


    # ========================================
    # 슬라이딩 윈도우를 원본 이미지에 투영하기 위한 역변환 행렬 구하기
    # ========================================
    def inv_perspective_transform(self, img):
        result_img = cv2.warpPerspective(img, self.camera.inv_transform_matrix, (self.camera.WIDTH, self.camera.HEIGHT))
        return result_img


    # ========================================
    # 원본 이미지와 최종 처리된 이미지를 합치기
    # ========================================
    def combine_img(self, origin_img, result_img):
        return cv2.addWeighted(origin_img, 0.5, result_img, 1.0, 0.8)
    
    def draw_offset_lines(self,img, center_x, y_start=0, y_end=480, max_offset=50, color_start=(0,255,0), color_end=(0,0,255)):
        color_diff = np.array(color_end) - np.array(color_start)
        for offset in range(0, max_offset + 1, 10):
            left_x = center_x - offset
            right_x = center_x + offset
            color = tuple(map(int, color_start + color_diff * (offset / max_offset)))
            img = cv2.line(img, (left_x, y_start), (left_x, y_end), color, 1)
            img = cv2.line(img, (right_x, y_start), (right_x, y_end), color, 1)
        return img
    

    

    # ========================================
    # Main 함수
    # ========================================
    def process(self, origin_img):
        origin_img = cv2.resize(origin_img, (640,480), cv2.INTER_LINEAR) # (640, 480) : (width, height)  cv2.INTER_LINEAR : 쌍선형 보간법
        img = self.camera.pre_processing(origin_img)
        counter_msg = ""
        
        #cv2.line(img, (463,0),(410,480),(255,255,255),10)
        
        sliding_img, left_fitx, right_fitx, left_lane_detected, right_lane_detected, leftx, rightx = self.sliding_window(img, draw_windows=True)  # 슬라이딩 윈도우로 곡선 차선 인식



        # sliding window 기준으로 가운데에 초록색 경로 그리기
        path_x, path_y = self.draw_path(sliding_img, left_fitx, right_fitx, draw_windows=True)

        
        # 현재 차량이 있는 차로의 정보 구하기
        lane_idx, lane_msg = self.lane_info(right_lane_detected)

        # 차로위에 있는 차량의 위치 정보를 토대로 경로 재설정
        path_x_new, path_y_new,base_diff,message,state,state_color,lane_mid, lane_direction = self.get_position(left_fitx, right_fitx,path_x, path_y,sliding_img,lane_idx)


        # 곡률을 구하여 조향각 구하기
        curvature_angle = self.get_angle(path_x, path_y, left_lane_detected, right_lane_detected)
        curvature_angle_new = self.get_angle(path_x_new, path_y_new, left_lane_detected, right_lane_detected)
        if abs(curvature_angle) >= 6 and abs(base_diff) >= 20:
            pass
        # elif 4 <= abs(curvature_angle) < 6 and 10 <= abs(base_diff) < 20:
        #     if curvature_angle_new > 0:
        #         curvature_angle_new = 4
        #     elif curvature_angle_new < 0:
        #         curvature_angle_new = -4
        #     else:
        #         curvature_angle_new = 0
        # elif 2 <= abs(curvature_angle) < 4 and 0 <= abs(base_diff) < 10:
        #     if curvature_angle_new > 0:
        #         curvature_angle_new = 2
        #     elif curvature_angle_new < 0:
        #         curvature_angle_new = -2
        #     else:
        #         curvature_angle_new = 0
                


        sliding_img = self.draw_dashed_line(sliding_img, (lane_mid,0),(lane_mid,480), (255, 255, 0), 2, 10)
        sliding_img = self.draw_offset_lines(sliding_img,lane_mid)

        direction = ""
        if lane_direction < -5:
            direction = "Left"
        elif lane_direction > 5:
            direction = "Right"
        else:
            direction = "Straight"
       
        # 주석 처리
        sliding_result_img = self.inv_perspective_transform(sliding_img)
        combined_img = self.combine_img(origin_img, sliding_result_img)
        cv2.putText(combined_img, 'Angle: {}'.format(int(curvature_angle_new)), (0, 30), 1, 2, (255, 255, 255), 2)
        cv2.putText(combined_img, 'lane Angle: {}'.format(int(lane_direction)), (0, 60), 1, 2, (255, 255, 255), 2)
        cv2.putText(combined_img, 'base_diff: {}'.format(int(base_diff)), (0, 90), 1, 2, (255, 255, 255), 2)
        cv2.putText(combined_img, message, (320, 30), 1, 2, (255, 255, 255), 2)
        cv2.putText(combined_img, state, (400, 60), 1, 2, state_color, 2)
        cv2.putText(combined_img, counter_msg, (320, 90), 1, 2, (255, 255, 255), 2)
        cv2.putText(combined_img, direction, (0, 120), 1, 2, (255, 255, 255), 2)
        cv2.putText(combined_img, lane_msg, (0, 150), 1, 2, (255, 255, 255), 2)

        points = np.array([(0, 410), (50, 350), (590, 350), (640, 410)], dtype=np.int32)
        combined_img = cv2.polylines(combined_img, [points], True, (255, 255, 0), 1)
        combined_img = cv2.line(combined_img,(320, 350), (320, 410),(255,255,0),1)

        # cv2.putText(sliding_img, 'base_diff: {}'.format(int(base_diff)), (0, 25), 1, 2, (255, 255, 255), 2)


        cv2.imshow('Lane', combined_img)
        cv2.imshow('bird',sliding_img)

        return curvature_angle_new