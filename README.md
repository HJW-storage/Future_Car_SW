# 제2회 미래형자동차 자율주행 SW 경진대회
## collaborator
<table>
  <tr>
  <!--
  <td align="center"><b>Team Leader</b></sub></a><br /></td>
  <td align="center"><b>Autonomous Driving</b></sub></a><br /></td>
  <td align="center"><b>S/W</b></sub></a><br /></td>
  <td align="center"><b>S/W</b></sub></a><br /></td>
  -->
  </tr>
  <!--
    <td align="center"><a href="https://github.com/HJW-storage"><img src="https://user-images.githubusercontent.com/103934004/229440749-5e448f84-ee88-48d5-8d2e-22881c1d4baf.jpeg" width="100px;" alt=""/><br /><sub><b>Hong Ji Whan</b></sub></a><br /></td>
  -->
  </tr>
  <img src="https://github.com/HJW-storage/Future_Car_SW/assets/113449410/b4a24660-428a-4e2f-b5b1-f7e05f0b19fa" width = "480" height="360">
</table>

  
## 대회 소개
목적 : 미래차 자율주행 SW관련 교육, 실습, 경진대회를 통해 취업시장에서 요구되는 학부생들의 SW 기술 역량 강화 및 산업 홍보 도모<br/><br/><br/><br/><br/><br/>  

## 대회 개요(타임어택 주행, 미션(장애물, 신호등, 주차) 주행)
* 타임어택 주행
  - 자율주행차가 트랙을 2바퀴 주행하는 시간을 측정하여, 주행 시 차선을 벗어나지 않아야 하고 차선을 벗어날 경우 점수 삭감 또는 실격 처리
* 미션(장애물, 신호등, 주차) 주행
  - 주행 경로에 있는 장애물 차량을 회피하며 주행을 해야함.
  - 신호등의 신호(적색 신호, 녹색 신호)에 따라 정지 및 출발을 해야함.
  - 주차 구역에 주차된 차량을 피해 주어진 주차 공간에 주차를 해야함.<br/>
                  
## 시작 가이드
### 개발환경 및 사용언어, 사용툴
* 운영체제 : Ubuntu20.04  
* Ros noetic 사용
  
<img src="https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black" /> <img src="https://img.shields.io/badge/Python-14354C?style=for-the-badge&logo=python&logoColor=white" /> <img src="https://img.shields.io/badge/C%2B%2B-00599C?style=for-the-badge&logo=c%2B%2B&logoColor=white" /> <img src="https://img.shields.io/badge/Visual_Studio_Code-0078D4?style=for-the-badge&logo=visual%20studio%20code&logoColor=white" /> <img src="https://img.shields.io/badge/Arduino_IDE-00979D?style=for-the-badge&logo=arduino&logoColor=white" /><br/> 

## 동작 영상
### 전체 시나리오에 따른 동작 영상
#### <동작 개요>
리모컨으로 RC카 조종 → RC카는 리모컨의 명령에 따라 동작한다. → 해당 동작 방향에 장애물이 있다면 동작하지 않음. 장애물이 있다는 부저음을 울리고 적색 LED를 점등하여 운전자에게 장애물이 있다고 주의해달라는 신호를 전달한다. → 장애물 방향이 아닌 방향의 동작만 작동한다. → 운행 종료 후에는 EEPROM에 저장된 카운트를 백분율로 환산하여 LCD에 표시한다. 해당 정보는 운전자의 운전 패턴 분석 및 운전 취약 부분을 파악하는데 사용할 수 있다. 
* 주행 테스트 영상 https://www.youtube.com/watch?v=j78lOuiBxhw
* 센서 테스트 영상 https://www.youtube.com/watch?v=IxSM7H-Afjw
* 전방 장애물 인식, 전진 불가능 https://www.youtube.com/watch?v=5wfeqD1_rDc
* 후방 장애물 인식. 후진 불가능 https://www.youtube.com/watch?v=bDmryylZ1Io
* 좌측 장애물이 있어 좌회전만 불가능 https://www.youtube.com/watch?v=hXixcmgLJZ4

