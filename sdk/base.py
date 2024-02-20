from fairino import Robot

# SDK: https://fr-documentation.readthedocs.io/zh-cn/latest/SDKManual/python_intro.html
# 机器人参数单位说明：机器人位置单位为毫米(mm)，姿态单位为度(°)。


class Robot():
    def __init__(self, ip="192.168.58.2"):
        self.instance = Robot.RPC(ip)

    def call(self, api):
        return api.invoke(self)


class RobotException(Exception):
    def __init__(self, robot, code, revocable=True):
        super().__init__(f"Robot error: {code}")
        self.robot = robot
        self.code = code
        self.revocable = revocable

    def get_robot(self):
        return self.robot

    def get_code(self):
        return self.code

    def revoke(self):
        if self.revocable:
            ref = self.robot.instance.ResetAllError()
            if ref != 0:
                raise RobotException(self.robot, ref)
        else:
            raise RuntimeError("This error is not revocable")


class RobotApi:
    """
    The API class is a wrapper for the robot instance.
    It provides a set of methods to control the robot.

    One API instance can only invoke once.
    """

    def __init__(self):
        self.only_error_code = False

    def __call_api__(self, robot: Robot):
        """
        Tha actual implementation of the API.
        :param robot:
        :return: [ret, data] where ret is the return code and data is the return data.
        """
        raise NotImplementedError("Not implemented")

    def invoke(self, robot: Robot):
        """
        Invoke the API.
        :param robot: the robot instance.
        :return: the return data.
        """
        # ret, data = self.__call_api__(robot)
        # if ret != 0:
        #     raise RobotException(robot, ret)

        ret = self.__call_api__(robot)
        if self.only_error_code and ret != 0:
            raise RobotException(robot, ret)
        ret, data = ret
        if ret != 0:
            raise RobotException(robot, ret)
        return data
