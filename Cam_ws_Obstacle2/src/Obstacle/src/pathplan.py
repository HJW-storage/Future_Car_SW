import numpy as np
import matplotlib.pyplot as plt
import math

class PolynomialTrajectoryPlanner:
    def __init__(self, start_pos, end_pos, start_vel, end_vel, T):
        self.start_pos = np.array(start_pos)  # [x, y]
        self.end_pos = np.array(end_pos)  # [x, y]
        self.start_vel = np.array(start_vel)  # [vx, vy]
        self.end_vel = np.array(end_vel)  # [vx, vy]
        self.T = T  # Total time to travel along the path

        self.A = np.array([
                            [1,      0,         0,         0],
                            [1, self.T, self.T**2, self.T**3],
                            [0,      1,         0,         0],
                            [0,      1,  2*self.T, 3*self.T**2]
                        ])

        self.path_x = self._get_path(0)
        self.path_y = self._get_path(1)

    def _get_path(self, index):
        """
        index  <0 : x축>, <1 : y축>
        """
        b = np.array([self.start_pos[index], self.end_pos[index], self.start_vel[index], self.end_vel[index]])
        coeff = np.linalg.solve(self.A, b)
        return np.poly1d(coeff[::-1])

    def generate_path(self, dt=1):
        """
        Generate the path as arrays of x and y coordinates.
        
        dt: time step
        """
        time_steps = np.arange(0, self.T, dt)
        x_coords = self.path_x(time_steps)
        y_coords = self.path_y(time_steps)

        # 차량의 yaw 각도를 구하기
        dX = np.diff(x_coords)
        dY = np.diff(y_coords)
        yaw = np.arctan(dY / dX)

        return x_coords, y_coords, yaw

    def visualize(self, dt=0.1):
        """
        Visualize the path as a plot of y vs. x.

        dt: time step
        """
        x_coords, y_coords , yaw= self.generate_path(dt)
        print("Yaw : {}".format(yaw))
        plt.plot(x_coords, y_coords)
        plt.show()


# 사용 예시
planner = PolynomialTrajectoryPlanner(start_pos=[0, 0], end_pos=[-0.3, 0.9], start_vel=[0, 10e-2], end_vel=[0, 10e-2], T=5.0)
planner.visualize(0.1)