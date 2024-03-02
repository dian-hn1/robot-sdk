import threading
import time
import socket

from ctrl.base import ButtonController, TriggerController, DebounceController, MotionController, BaseController
from sdk import apis
from sdk.base import Robot, RobotException

port = 25656
host = '127.0.0.1'


class RosJoy(threading.Thread):
    def __init__(self, robot: Robot, host=host, port=port):
        super().__init__(daemon=False)
        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp.bind((host, port))
        self.prev_data = None

        self.robot = robot
        self.in_err = False
        self.started = False
        self.motion = apis.Motion()
        self.gripper = apis.Gripper()

        self.start_control = DebounceController(TriggerController(self.StartControl(self)))
        self.select_control = DebounceController(TriggerController(self.SelectControl(self)))
        self.x_control = DebounceController(TriggerController(self.MotionSpeedControl(self, -5)))
        self.y_control = DebounceController(TriggerController(self.MotionSpeedControl(self, 5)))
        self.lb_control = DebounceController(TriggerController(self.GripperControl(self, 0)))
        self.rb_control = DebounceController(TriggerController(self.GripperControl(self, 90)))
        self.lj_control = self.MotionControl(self, 2, [0.5, 0, 0, 0, 0, 0], [0, 0.5, 0, 0, 0, 0])
        self.rj_control = self.MotionControl(self, 2, [0, 0, 0.5, 0, 0, 0], [0, 0, 0, 0, 0, 0.5])
        self.cross_control = self.MotionControl(self, 2, [0, 0, 0, 0, 0.5, 0], [0, 0, 0, 0.5, 0, 0])
        self.stop_control = self.StopControl(self, 0.7)

    def run(self):
        while True:
            data, _ = self.udp.recvfrom(256)  # raw float data, not string
            current_ms = time.time_ns() // 1000000
            if self.prev_data is not None and self.prev_data["time"] - current_ms < 2:
                continue
            if len(data) != 16 * 4:
                continue
            data = self.data_unpack(data, current_ms)

            period = data["time"] - self.prev_data["time"] if self.prev_data is not None else 0
            if period < 0:
                # ?
                continue
            elif period > 100:
                # when the period is too long, the data is not valid
                self.robot.call(apis.Motion.stop_motion())
                self.robot.call(apis.Safety.clear_error())
                self.started = False
                self.in_err = False

            self.prev_data = data
            try:
                self.start_control.act(period, data["buttons"]["START"])
                self.select_control.act(period, data["buttons"]["SELECT"])
                if self.started and not self.in_err:
                    self.x_control.act(period, data["buttons"]["X"])
                    self.y_control.act(period, data["buttons"]["Y"])
                    self.lb_control.act(period, data["buttons"]["LB"])
                    self.rb_control.act(period, data["buttons"]["RB"])
                    self.lj_control.act(period, data["left_x"], data["left_y"])
                    self.rj_control.act(period, data["right_x"], data["right_y"])
                    self.cross_control.act(period, data["cross_x"], data["cross_y"])
                    self.stop_control.act(period, data["buttons"]["LT"], data["buttons"]["RT"])
            except RobotException as e:
                print(e)
                self.in_err = True
            except Exception as e:
                self.robot.call(apis.Motion.stop_motion())
                raise e

    @staticmethod
    def data_unpack(raw_data: bytes, current_time) -> dict:
        import struct
        raw_data = [x[0] for x in struct.iter_unpack('f', raw_data)]
        button_data = [False if x == 0 else True for x in raw_data[6:]]
        # 第一行6个数分别代表左摇杆横轴，左摇杆纵轴，右摇杆横轴，右摇杆纵轴，十字按键横向，十字按键纵向，均为左正右负。摇杆取值为[-1, 1]之间的6位浮点数，十字按键取值为-1或0或1
        # 第二行所有数均代表按钮状态，按下是1，未按下是0
        res_data = {
            "time": current_time,
            "left_x": raw_data[0],
            "left_y": raw_data[1],
            "right_x": raw_data[2],
            "right_y": raw_data[3],
            "cross_x": raw_data[4],
            "cross_y": raw_data[5],
            "buttons": {
                "A": button_data[0],
                "B": button_data[1],
                "X": button_data[2],
                "Y": button_data[3],
                "LB": button_data[4],
                "RB": button_data[5],
                "LT": raw_data[6 + 6],
                "RT": raw_data[6 + 7],  # they are not buttons, but triggers
                "SELECT": button_data[8],
                "START": button_data[9]
            }
        }

        res_data["cross_x"] = 0 if res_data["cross_x"] == 0 else (1 if res_data["cross_x"] > 0 else -1)
        res_data["cross_y"] = 0 if res_data["cross_y"] == 0 else (1 if res_data["cross_y"] > 0 else -1)
        return res_data

    class StartControl(ButtonController):
        def __init__(self, outer):
            super().__init__(outer.robot)
            self.outer = outer

        def act(self, _, status):
            if status:
                self.outer.started = True
                self.robot.call(apis.Safety.clear_error())
                self.outer.in_err = False
                self.robot.call(apis.Safety.enable_robot())
                self.robot.call(apis.Safety.mode_switch_auto())
                self.robot.call(apis.Motion.servo_start())
                self.robot.call(self.outer.gripper.activate(0))

    class SelectControl(ButtonController):
        """
        Now works as a stop button
        """

        def __init__(self, outer):
            super().__init__(outer.robot)
            self.outer = outer

        def act(self, _, status):
            if status:
                self.outer.started = False
                self.robot.call(apis.Motion.servo_end())
                self.robot.call(apis.Motion.stop_motion())
                self.robot.call(apis.Safety.clear_error())
                self.outer.in_err = False
                self.robot.call(self.outer.gripper.reset())
                self.robot.call(apis.Safety.disable_robot())
                # self.robot.call(apis.Safety.mode_switch_manual())

    class MotionSpeedControl(ButtonController):
        def __init__(self, outer, delta=5):
            super().__init__(outer.robot)
            self.outer = outer
            self.delta = delta

        def act(self, _, status):
            if status:
                speed = apis.Motion.vel + self.delta
                if speed < 0:
                    speed = 0
                elif speed > 100:
                    speed = 100
                print(f"Speed changed: {speed}")
                self.robot.call(self.outer.motion.set_speed(speed))

    class GripperControl(ButtonController):
        def __init__(self, outer, pos):
            super().__init__(outer.robot)
            self.robot = outer.robot
            self.outer = outer
            self.pos = pos

            outer.gripper.set_speed(40)
            outer.gripper.set_force(50)

        def act(self, _, status):
            if status:
                print(f"Gripper Position changed: {self.pos}")
                self.robot.call(self.outer.gripper.move(self.pos, block=False))

    class MotionControl(MotionController):
        def __init__(self, outer, mode, delta_h, delta_v):
            super().__init__(outer.robot)
            self.outer = outer
            self.motion = outer.motion
            self.mode = mode
            self.delta_h = delta_h
            self.delta_v = delta_v
            self.motion.set_speed(50)

        def act(self, period, horizontal, vertical):
            now_pos = [horizontal * self.delta_h[i] + vertical * self.delta_v[i] for i in range(6)]

            self.robot.call(self.motion.servo_cart(
                self.mode, now_pos, cmd_time=period / 1000.0, vel=self.motion.vel))

    class StopControl(BaseController):
        def __init__(self, outer, trigger_gate=0.7):
            super().__init__(outer.robot)
            self.outer = outer

        def act(self, _, lt, rt):
            if lt > 0.7 and rt > 0.7:
                self.robot.call(apis.Motion.servo_end())
                self.robot.call(apis.Motion.stop_motion())
