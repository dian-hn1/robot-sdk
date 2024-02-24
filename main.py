from ctrl.rosjoy import RosJoy
from sdk.base import Robot

# Path: main.py
if __name__ == "__main__":
    robot = Robot()
    rosjoy = RosJoy(robot)
    rosjoy.start()
