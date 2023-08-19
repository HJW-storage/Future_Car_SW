class FiniteStateMachine:
    """
    장애물을 카운트 하여 조향의 방향을 정하는 디시젼 메이킹
    """
    def __init__(self):
        self.current_state = "FollowLane"

    def transition(self, detected_obstacle, lane_idx):
        
        if detected_obstacle:

            # 현재 상태와 장애물 감지 횟수를 기반으로 상태 전이
            if self.current_state == "FollowLane":

                if lane_idx == 1:  # 첫 번째 장애물 감지
                    self.current_state = "AvoidRight"
                    self.obstacle_count = 2

                elif lane_idx == 2 :  # 두 번째 장애물 감지
                    self.current_state = "AvoidLeft"


        else:
            self.current_state = "FollowLane"


        print("obstacle_cout : {}".format(self.obstacle_count))
        print("fsm ================== {}".format(self.current_state))