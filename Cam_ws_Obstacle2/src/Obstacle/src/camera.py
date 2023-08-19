# #!/usr/bin/env python3
# # -*- coding:utf-8 -*-
# import numpy as np
# import cv2

# class Camera:

#     def __init__(self):
#         self.WIDTH, self.HEIGHT = 640, 480  # 카메라 가로, 세로 크기

#         # ====================
#         # ROI - array 순서 : [좌하, 좌상, 우상, 우하]

#         # 카메라를 위한 roi


#         vertices = np.array([(40, 410), (140, 305),
#                                     (510, 305), (610, 410)],
#                                    dtype=np.int32)


#         # Bird's eye View 변환을 위한 src, dst point 설정 (src 좌표에서 dst 좌표로 투시 변환)
#         self.points_src = np.float32(list(vertices))
#         self.points_dst = np.float32(
#             [(100, self.HEIGHT), (100, 0), (self.WIDTH - 100, 0), (self.WIDTH - 100, self.HEIGHT)])

#         # 만든 src, dst point 를 이용하여 투시 변환 행렬 생성
#         self.transform_matrix = cv2.getPerspectiveTransform(self.points_src, self.points_dst)
#         # 원본 영상으로 되돌리기 위한 역변환 행렬
#         self.inv_transform_matrix = cv2.getPerspectiveTransform(self.points_dst, self.points_src)

#     # ========================================
#     # 반사광 제거
#     # ========================================
#     def glare_removal(self, img, radius=45):
#         img_lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
#         l_channel = img_lab[:, :, 0] # 밝기를 나타내는 채널
#         l_channel = cv2.medianBlur(l_channel, radius) # 메디안 필터링 (물체는 필요없고, 실제 조명과 가까워지게 블러링 강하게 적용)
#         inverse_l_channel = cv2.bitwise_not(l_channel) # 빛 반사가 높을수록 어두워지고, 빛반사가 없을수록 밝아짐(not연산자)
#         img_lab[:, :, 0] = img_lab[:, :, 0] // 2
#         img_lab[:, :, 0] += inverse_l_channel # 원본 L 채널과 합성
#         img_lab[:, :, 0] = img_lab[:, :, 0] // 2
#         img = cv2.cvtColor(img_lab, cv2.COLOR_LAB2BGR) # BGR로 변경
#         return img
   

#     # ========================================
#     # 흑백 영상 변환
#     # ========================================
#     def gray_scale(self, img):
#         return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 그레이 스케일 이미지로 변경하여 이미지 반환

    
#     # ========================================
#     # 노이즈 제거 
#     # ========================================
    
#     def denoise_frame(self, img):

#         kernel = np.ones((3, 3), np.float32) / 9   # 3x3 kernel 사용
#         denoised_frame = cv2.filter2D(img, -1, kernel)   # 프레임에 필터 적용.
        
#         return denoised_frame   # 노이즈 제거된 프레임 반환
    
#     # ========================================
#     # 가우시안 블러링
#     # ========================================
#     def gaussian_blur(self, img):
#         return cv2.GaussianBlur(img, (3, 3), 0)  # 노이즈 제거(솔트 & 페퍼 노이즈) 이미지 반환


#     # # ========================================
#     # # Bird's eye View 변환
#     # # ========================================
#     def perspective_transform(self, img):  # birds eye view
#         result_img = cv2.warpPerspective(img, self.transform_matrix, (self.WIDTH, self.HEIGHT))
#         return result_img  # 변환한 이미지 반환
    
#     # ========================================
#     # 모폴로지 
#     # ========================================    
#     def Morphology_opening(self,img):
#         k = cv2.getStructuringElement(cv2.MORPH_RECT, (7,7))
#         opening_img=cv2.morphologyEx(img, cv2.MORPH_OPEN, k)

#         return opening_img

#     # ========================================
#     # 윤곽선 검출
#     # ========================================
#     def canny_edges(self, img):

#         canny_edges = cv2.Canny(img, 80, 120) # 선 검출
        
#         return canny_edges  # 캐니 엣지
    
#     def make_canny(self,img):
#         # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#         # _, binary = cv2.threshold(gray, 190, 255, cv2.THRESH_BINARY)
#         # binary_gaussian = cv2.adaptiveThreshold(binary, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 5)
#         # blur = cv2.GaussianBlur(binary_gaussian, (5, 5), 0)
#         # blur = cv2.bilateralFilter(blur, 9, 75, 75)

#         canny_image = cv2.Canny(img, 80, 120)

#         return canny_image
    
#     # def make_canny(self,img):
    
#     #     _, binary = cv2.threshold(img, 190, 255, cv2.THRESH_BINARY)
#     #     binary_gaussian = cv2.adaptiveThreshold(binary, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 5)
#     #     blur = cv2.GaussianBlur(binary_gaussian, (5, 5), 0)
#     #     blur = cv2.bilateralFilter(blur, 9, 75, 75)

#     #     canny_image = cv2.Canny(blur, 80, 120)

#     #     return canny_image
#     # ========================================
#     # 영상 전처리
#     # ========================================
#     def pre_processing(self, img):
#         # img = self.glare_removal(img)
#         img = self.denoise_frame(img)
#         img = self.Morphology_opening(img)
#         img = self.gray_scale(img)
#         img = self.gaussian_blur(img)
#         img = self.canny_edges(img)
#         img = self.make_canny(img)
#         img = self.perspective_transform(img)

#         return img


#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import numpy as np
import cv2

class Camera:

    def __init__(self):
        self.WIDTH, self.HEIGHT = 640, 480  # 카메라 가로, 세로 크기

        # ====================
        # ROI - array 순서 : [좌하, 좌상, 우상, 우하]

        # 카메라를 위한 roi (ROI : 영상내의 관심 영역)
        vertices = np.array([(0, 410), (50, 350), #120,350
                                    (590, 350), (640, 410)], #540 590
                                   dtype=np.int32)   # 이게 각도가 많이 안틈.
         

        # Bird's eye View 변환을 위한 src, dst point 설정 (src 좌표에서 dst 좌표로 투시 변환)
        self.points_src = np.float32(list(vertices))
        self.points_dst = np.float32(
            [(100, self.HEIGHT), (100, 0), (self.WIDTH - 100, 0), (self.WIDTH - 100, self.HEIGHT)]) # 100

        # 만든 src, dst point 를 이용하여 투시 변환 행렬 생성
        self.transform_matrix = cv2.getPerspectiveTransform(self.points_src, self.points_dst)
        # 결과적으로 카메라의 관심 영역 roi 좌표 화면을 Bird Eye View로 보려고 투시 변환까지 한 것. 

        # 원본 영상으로 되돌리기 위한 역변환 행렬
        self.inv_transform_matrix = cv2.getPerspectiveTransform(self.points_dst, self.points_src)

    # ========================================
    # 반사광 제거
    # ========================================
    def glare_removal(self, img, radius=45):
        img_lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB) # L : 밝기, A : 색상(녹색~빨강), B : 색상(파랑~노랑)
        l_channel = img_lab[:, :, 0] # 밝기를 나타내는 채널(L채널)
        l_channel = cv2.medianBlur(l_channel, radius) # 메디안 필터링 (물체는 필요없고, 실제 조명과 가까워지게 블러링 강하게 적용). 급격한 밝기 변환를 제거.
        inverse_l_channel = cv2.bitwise_not(l_channel) # 비트 NOT 연산자 적용. 빛 반사가 높을수록 어두워지고, 빛반사가 없을수록 밝아짐(not연산자)
        img_lab[:, :, 0] = img_lab[:, :, 0] // 2
        img_lab[:, :, 0] += inverse_l_channel # 원본 L 채널의 절반값과 반전시킨 L 채널의 절반값을 합성
        img_lab[:, :, 0] = img_lab[:, :, 0] // 2 # 합성한 채널의 다시 2로 나눠준다. 
        img = cv2.cvtColor(img_lab, cv2.COLOR_LAB2BGR) # BGR로 변경
        return img
   

    # ========================================
    # 흑백 영상 변환
    # ========================================
    def gray_scale(self, img):
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 그레이 스케일 이미지로 변경하여 이미지 반환

    
    # ========================================
    # 노이즈 제거 
    # ========================================
    def denoise_frame(self, img):

        kernel = np.ones((3, 3), np.float32) / 9   # 3x3 kernel 사용
        denoised_frame = cv2.filter2D(img, -1, kernel)   # 프레임에 필터 적용.
        
        return denoised_frame   # 노이즈 제거된 프레임 반환
    
    # ========================================
    # 가우시안 블러링
    # ========================================
    def gaussian_blur(self, img):
        return cv2.GaussianBlur(img, (3, 3), 0)  # 노이즈 제거(솔트 & 페퍼 노이즈) 이미지 반환


    # # ========================================
    # # Bird's eye View 변환
    # # ========================================
    def perspective_transform(self, img):  # birds eye view
        result_img = cv2.warpPerspective(img, self.transform_matrix, (self.WIDTH, self.HEIGHT))
        return result_img  # 변환한 이미지 반환
    
    # ========================================
    # 모폴로지 
    # ========================================    
    def Morphology_opening(self,img):
        k = cv2.getStructuringElement(cv2.MORPH_RECT, (7,7))
        opening_img=cv2.morphologyEx(img, cv2.MORPH_OPEN, k)
        # 입력 이미지에 대해 열림 연산을 수행합니다. 먼저 침식(Erosion) 연산을 적용하여 작은 객체와 가장자리를 제거한 다음 
        # 팽창(Dilation) 연산을 적용합니다. 큰 객체는 유지되고 작은 객체 및 노이즈는 제거됩니다.
        # 결과적으로 주어진 이미지에서 노이즈를 제거하고 큰 객체만을 추출한다.
        return opening_img

    # ========================================
    # 윤곽선 검출
    # ========================================
    def canny_edges(self, img):
        canny_edges = cv2.Canny(img, 80, 120) # 선 검출
        # 하한 임계값(lower threshold)으로 80을, 상한 임계값(upper threshold)으로 120을 사용.
        # 이 범위 내의 기울기(gradient)를 가진 픽셀을 엣지로 간주하고 그 외 픽셀은 배경으로 간주
        return canny_edges  # 캐니 엣지
    
    def make_canny(self,img):
        # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # _, binary = cv2.threshold(gray, 190, 255, cv2.THRESH_BINARY)
        # binary_gaussian = cv2.adaptiveThreshold(binary, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 5)
        # blur = cv2.GaussianBlur(binary_gaussian, (5, 5), 0)
        # blur = cv2.bilateralFilter(blur, 9, 75, 75)

        canny_image = cv2.Canny(img, 80, 120)

        return canny_image
    
    # def make_canny(self,img):
    
    #     _, binary = cv2.threshold(img, 190, 255, cv2.THRESH_BINARY)
    #     binary_gaussian = cv2.adaptiveThreshold(binary, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 5)
    #     blur = cv2.GaussianBlur(binary_gaussian, (5, 5), 0)
    #     blur = cv2.bilateralFilter(blur, 9, 75, 75)

    #     canny_image = cv2.Canny(blur, 80, 120)

    #     return canny_image

    # ========================================
    # 영상 전처리
    # ========================================
    def pre_processing(self, img):
        # img = self.glare_removal(img)
        img = self.denoise_frame(img) # 노이즈 제거
        img = self.Morphology_opening(img) # 모폴로지 연산
        img = self.gray_scale(img) # 흑백 변환
        img = self.gaussian_blur(img) # 가우시안 블러링
        img = self.canny_edges(img) # 윤곽선 검출
        img = self.make_canny(img) # 윤곽선 검출
        img = self.perspective_transform(img) # Bird's eye View 변환

        return img