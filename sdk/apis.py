from sdk.util import RobotApiBuilder


class Common:
    """
    通用控制
    """

    @staticmethod
    def get_sdk_version():
        """
        获取SDK版本
        :return: {"sdk_version": str, "controller_version": str}
        """
        return (RobotApiBuilder()
                .api_call(
            lambda robot: robot.instance.GetSDKVersion())
                .post_data_process(
            lambda data: {
                "sdk_version": data[0],
                "controller_version": data[1]
            })
                .build())

    @staticmethod
    def get_controller_ip():
        """
        获取控制器IP地址
        :return: ip
        """
        return (RobotApiBuilder()
                .api_call(
            lambda robot: robot.instance.GetControllerIP())
                .build())

    @staticmethod
    def set_speed(vel):
        """
        设置全局速度
        :param vel: 速度百分比，范围[0~100]
        :return: null
        """
        if vel < 0 or vel > 100:
            raise ValueError("Invalid velocity")

        return (RobotApiBuilder()
                .set_only_error_code()
                .api_call(
            lambda robot: robot.instance.SetSpeed(vel))
                .build())

    @staticmethod
    def get_default_speed():
        """
        获取默认速度
        :return: vel
        """
        return (RobotApiBuilder()
                .api_call(
            lambda robot: robot.instance.GetDefaultTransVel())
                .build())

    @staticmethod
    def is_in_drag_teach():
        """
        查询机器人是否处于拖动示教模式
        :return: bool - False: 非拖动示教模式, True: 在拖动示教模式
        """
        return (RobotApiBuilder()
                .api_call(
            lambda robot: robot.instance.IsInDragTeach())
                .post_data_process(
            lambda data: data == 1)
                .build())

    @staticmethod
    def set_sys_var(var_id, value):
        """
        设置系统变量
        :param var_id: 变量编号，范围[1~20]
        :param value: 变量值
        :return: null
        """
        return (RobotApiBuilder()
                .set_only_error_code()
                .api_call(
            lambda robot: robot.instance.SetSysVarValue(var_id, value))
                .build())

    @staticmethod
    def get_sys_var(var_id):
        """
        获取系统变量值
        :param var_id: 变量编号，范围[1~20]
        :return: [var_value]
        """
        return (RobotApiBuilder()
                .api_call(
            lambda robot: robot.instance.GetSysVarValue(var_id))
                .build())

    @staticmethod
    def is_robot_motion_done():
        """
        查询机器人运动是否完成
        :return: [state: bool]
        """
        return (RobotApiBuilder()
                .api_call(
            lambda robot: robot.instance.GetRobotMotionDone())
                .post_data_process(
            lambda data: data == 1)
                .build())


class Safety:
    """
    机器人安全控制
    """

    def __init__(self):
        # raise NotImplementedError("This class is not supposed to be instantiated")
        pass

    @staticmethod
    def clear_error():
        """
        错误状态清除，只能清除可复位的错误
        :return: null
        """
        return (RobotApiBuilder()
                .set_only_error_code()
                .api_call(
            lambda robot: robot.instance.ResetAllError())
                .build())

    @staticmethod
    def get_error_code():
        """
        查询机器人错误码
        :return: [main_code sub_code]
        """
        return (RobotApiBuilder()
                .api_call(
            lambda robot: robot.instance.GetRobotErrorCode())
                .build())

    @staticmethod
    def mode_switch(mode):
        """
        控制机器人模式切换
        :param mode: 0: 自动模式, 1: 手动模式
        :return: null
        """
        if mode not in [0, 1]:
            raise ValueError("Invalid mode")
        return (RobotApiBuilder()
                .set_only_error_code()
                .api_call(
            lambda robot: robot.instance.Mode(mode))
                .build())

    @staticmethod
    def mode_switch_auto():
        """
        控制机器人自动模式切换
        :return: null
        """
        return Safety.mode_switch(0)

    @staticmethod
    def mode_switch_manual():
        """
        控制机器人手动模式切换
        :return: null
        """
        return Safety.mode_switch(1)

    @staticmethod
    def teach_mode_switch(teach_mode=True):
        """
        控制机器人进入或退出拖动示教模式
        :param teach_mode:
        :return: null
        """
        if teach_mode:
            teach_mode = 1
        else:
            teach_mode = 0

        return (RobotApiBuilder()
                .set_only_error_code()
                .api_call(
            lambda robot: robot.instance.DragTeachSwitch(teach_mode))
                .build())

    @staticmethod
    def enable_robot(state=True):
        """
        控制机器人使能
        :param state: 0: 关闭, 1: 打开
        :return: null
        """
        if state:
            state = 1
        else:
            state = 0
        return (RobotApiBuilder()
                .set_only_error_code()
                .api_call(
            lambda robot: robot.instance.RobotEnable(state))
                .build())

    @staticmethod
    def disable_robot():
        """
        控制机器人关闭
        :return: null
        """
        return Safety.enable_robot(False)

    @staticmethod
    def wait_ms(t_ms):
        """
        等待指定时间
        :param t_ms: 单位[ms]
        :return: null
        """
        return (RobotApiBuilder()
                .set_only_error_code()
                .api_call(
            lambda robot: robot.instance.WaitMs(t_ms))
                .build())

    @staticmethod
    def wait_ms_internal(t_ms):
        """
        等待指定时间，并非指令
        :param t_ms: 单位[ms]
        :return: null
        """
        import time
        return (RobotApiBuilder()
                .set_only_error_code()
                .api_call(
            lambda robot: time.sleep(t_ms / 1000))
                .build())


class Motion:
    """
    机器人运动控制
    """

    vel = 20
    """
    速度百分比，[0~100]
    """

    acc = 100
    """
    加速度百分比，[0~100]
    """

    tool = 0
    """
    工具号，[0~14]
    """

    user = 0
    """
    工件号，[0~14]
    """

    def __init__(self, vel=20, acc=100, tool=0, user=0):
        self.vel = vel
        self.acc = acc
        self.tool = tool
        self.user = user

    def set_vel(self, vel):
        """
        设置机器人运动速度
        :param vel: 速度百分比，[0~100]
        :return: null
        """
        if vel < 0 or vel > 100:
            raise ValueError("Invalid velocity")
        self.vel = vel
        return self

    def set_acc(self, acc):
        """
        设置机器人运动加速度
        :param acc: 加速度百分比，[0~100]
        :return: null
        """
        if acc < 0 or acc > 100:
            raise ValueError("Invalid acceleration")
        self.acc = acc
        return self

    def set_speed(self, vel):
        """
        设置速度百分比
        :param vel: 速度百分比，[0~100]
        :return: null
        """
        if vel < 0 or vel > 100:
            raise ValueError("Invalid velocity")

        self.vel = vel
        Motion.vel = vel
        return Common.set_speed(vel)

    def set_tool(self, tool):
        """
        设置工具号
        :param tool: 工具号，[0~14]
        :return: null
        """
        if tool < 0 or tool > 14:
            raise ValueError("Invalid tool")
        Motion.tool = tool
        return self

    def set_user(self, user):
        """
        设置工件号
        :param user: 工件号，[0~14]
        :return: null
        """
        if user < 0 or user > 14:
            raise ValueError("Invalid user")
        Motion.user = user
        return self

    def clone(self):
        return (Motion()
                .set_acc(self.acc)
                .set_vel(self.vel)
                .set_tool(self.tool)
                .set_user(self.user))

    def jog_move(self, ref, nb, direction, max_dis, vel=-1, acc=-1):
        """
        jog点动，非阻塞
        :param ref: 0 - 关节点动, 2 - 基坐标系点动, 4 - 工具坐标系点动, 8 - 工件坐标系点动
        :param nb: 1 - 1关节(x轴), 2 - 2关节(y轴), 3 - 3关节(z轴), 4 - 4关节(rx), 5 - 5关节(ry), 6 - 6关节(rz)
        :param direction: 0 - 负方向，1 - 正方向
        :param max_dis: 单次点动最大角度 / 距离，单位 ° 或 mm
        :param vel: 速度百分比，[0~100]
        :param acc: 加速度百分比，[0~100]
        :return: null
        """
        if ref not in [0, 2, 4, 8]:
            raise ValueError("Invalid ref")
        if nb not in [1, 2, 3, 4, 5, 6]:
            raise ValueError("Invalid nb")
        if direction not in [0, 1]:
            raise ValueError("Invalid dir")

        if vel < 0:
            vel = self.vel
        if acc < 0:
            acc = self.acc

        return (RobotApiBuilder()
                .set_only_error_code()
                .api_call(
            lambda robot: robot.instance.StartJOG(ref, nb, direction, max_dis, vel, acc))
                .build())

    @staticmethod
    def jog_stop(ref):
        """
        jog点动减速停止
        :param ref: 1 - 关节点动停止, 3 - 基坐标系点动停止, 5 - 工具坐标系点动停止, 9 - 工件坐标系点动停止
        :return: null
        """
        if ref not in [1, 3, 5, 9]:
            raise ValueError("Invalid ref")

        return (RobotApiBuilder()
                .set_only_error_code()
                .api_call(
            lambda robot: robot.instance.StopJOG(ref))
                .build())

    @staticmethod
    def jog_stop_immediately():
        """
        jog点动立即停止
        :return: null
        """
        return (RobotApiBuilder()
                .set_only_error_code()
                .api_call(
            lambda robot: robot.instance.ImmStopJOG())
                .build())

    @staticmethod
    def servo_start():
        """
        伺服运动开始
        :return: null
        """
        return (RobotApiBuilder()
                .set_only_error_code()
                .api_call(
            lambda robot: robot.instance.ServoMoveStart())
                .build())

    @staticmethod
    def servo_joint(joint_pos, acc=0.0, vel=0.0, cmd_time=0.008, filter_time=0.0, gain=0.0):
        """
        关节空间伺服模式运动
        :param joint_pos: 目标关节位置，单位[°]
        :param acc: 加速度，范围 [0~100]，暂不开放，默认为 0.0
        :param vel: 速度，范围 [0~100]，暂不开放，默认为 0.0
        :param cmd_time: 指令下发周期，单位s，建议范围[0.001~0.0016], 默认为0.008
        :param filter_time: 滤波时间，单位 [s]，暂不开放， 默认为0.0
        :param gain: 目标位置的比例放大器，暂不开放， 默认为0.0
        :return: null
        """
        return (RobotApiBuilder()
                .set_only_error_code()
                .api_call(
            lambda robot: robot.instance.ServoJ(joint_pos, acc, vel, cmd_time, filter_time, gain))
                .build())

    @staticmethod
    def servo_cart(mode, desc_pos, pos_gain=None, acc=0.0, vel=0.0, cmd_time=0.008, filter_time=0.0, gain=0.0):
        """
        笛卡尔空间伺服模式运动
        :param mode: 0-绝对运动(基坐标系)，1-增量运动(基坐标系)，2-增量运动(工具坐标系)
        :param desc_pos: 目标笛卡尔位置/目标笛卡尔位置增量
        :param pos_gain: 位姿增量比例系数，仅在增量运动下生效，范围 [0~1], 默认为 [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        :param acc: 加速度，范围 [0~100]，暂不开放，默认为 0.0
        :param vel: 速度，范围 [0~100]，暂不开放，默认为 0.0
        :param cmd_time: 指令下发周期，单位s，建议范围[0.001~0.0016], 默认为0.008
        :param filter_time: 滤波时间，单位 [s]，暂不开放， 默认为0.0
        :param gain: 目标位置的比例放大器，暂不开放， 默认为0.0
        :return: null
        """
        if pos_gain is None:
            pos_gain = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        return (RobotApiBuilder()
                .set_only_error_code()
                .api_call(
            lambda robot: robot.instance.ServoCart(mode, desc_pos, pos_gain, acc, vel, cmd_time, filter_time, gain))
                .build())

    @staticmethod
    def servo_end():
        """
        伺服运动结束
        :return: null
        """
        return (RobotApiBuilder()
                .set_only_error_code()
                .api_call(
            lambda robot: robot.instance.ServoMoveEnd())
                .build())

    def move_joint(self, joint_pos, tool=-1, user=-1, desc_pos=None, vel=-1, acc=-1, ovl=100.0,
                   exaxis_pos=None, blend_time=-1.0, offset_flag=0, offset_pos=None):
        """
        关节空间运动
        :param joint_pos: 目标关节位置，单位[°]；
        :param tool: 工具号，[0~14]；
        :param user: 工件号，[0~14]；
        :param desc_pos: 目标笛卡尔位姿，单位[mm][°] 默认初值为[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]，默认值调用正运动学求解返回值;
        :param vel: 速度百分比，[0~100] 默认20.0;
        :param acc: 加速度百分比，[0~100]，暂不开放；
        :param ovl: 速度缩放因子，[0~100] 默认100.0;
        :param exaxis_pos: 外部轴 1 位置 ~ 外部轴 4 位置 默认[0.0, 0.0, 0.0, 0.0];
        :param blend_time: [-1.0] - 运动到位(阻塞)，[0~500.0] - 平滑时间(非阻塞)，单位[ms] 默认 -1.0;
        :param offset_flag: [0] - 不偏移，[1] - 工件 / 基坐标系下偏移，[2] - 工具坐标系下偏移 默认 0;
        :param offset_pos: 位姿
        """
        if offset_pos is None:
            offset_pos = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        if exaxis_pos is None:
            exaxis_pos = [0.0, 0.0, 0.0, 0.0]
        if desc_pos is None:
            desc_pos = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        if tool < 0:
            tool = self.tool
        if user < 0:
            user = self.user
        if vel < 0:
            vel = self.vel
        if acc < 0:
            acc = self.acc

        return (RobotApiBuilder()
                .set_only_error_code()
                .api_call(
            lambda robot: robot.instance.MoveJ(joint_pos, tool, user,
                                               desc_pos, vel, acc, ovl, exaxis_pos, blend_time, offset_flag,
                                               offset_pos))
                .build())

    def move_cart(self, desc_pos, tool=-1, user=-1, vel=-1, acc=0.0, ovl=100.0, blend_time=-1.0, config=-1):
        """
        笛卡尔空间点到点运动
        :param desc_pos: 目标笛卡尔位置；
        :param tool: 工具号，[0~14]；
        :param user: 工件号，[0~14]；
        :param vel: 速度，范围 [0~100]，默认为 20.0;
        :param acc: 加速度，范围 [0~100]，暂不开放,默认为 0.0;
        :param ovl: 速度缩放因子，[0~100]，默认为 100.0;
        :param blend_time: [-1.0]-运动到位 (阻塞)，[0~500]-平滑时间 (非阻塞)，单位 [ms] 默认为 -1.0;
        :param config: 关节配置，[-1]-参考当前关节位置求解，[0~7]-依据关节配置求解 默认为 -1
        """
        if tool < 0:
            tool = self.tool
        if user < 0:
            user = self.user
        if vel < 0:
            vel = self.vel
        if acc < 0:
            acc = self.acc  # 暂不开放

        return (RobotApiBuilder()
                .set_only_error_code()
                .api_call(
            lambda robot: robot.instance.MoveCart(desc_pos, tool, user, vel, acc, ovl, blend_time, config))
                .build())

    def move_line(self, desc_pos, tool=-1, user=-1, joint_pos=None, vel=-1, acc=0.0, ovl=100.0, blend_radius=-1.0,
                  exaxis_pos=None, search=0, offset_flag=0, offset_pos=None):
        """
        笛卡尔空间直线运动
        :param desc_pos: 目标笛卡尔位姿，单位[mm][°]；
        :param tool: 工具号，[0~14]；
        :param user: 工件号，[0~14]；
        :param joint_pos: 目标关节位置，单位[°] 默认初值为[0.0,0.0,0.0,0.0,0.0,0.0]，默认值调用逆运动学求解返回值;
        :param vel: 速度百分比，[0~100] 默认20.0；
        :param acc: 加速度百分比，[0~100]，暂不开放 默认0.0；
        :param ovl: 速度缩放因子，[0~100] 默认100.0；
        :param blend_radius: blendR:[-1.0]-运动到位 (阻塞)，[0~1000]-平滑半径 (非阻塞)，单位 [mm] 默认-1.0;
        :param exaxis_pos: 外部轴 1 位置 ~ 外部轴 4 位置 默认[0.0,0.0,0.0,0.0];
        :param search: [0]-不焊丝寻位，[1]-焊丝寻位；
        :param offset_flag: offset_flag:[0]-不偏移，[1]-工件/基坐标系下偏移，[2]-工具坐标系下偏移 默认 0;
        :param offset_pos: 位姿偏移量，单位 [mm][°] 默认[0.0,0.0,0.0,0.0,0.0,0.0]
        :return: null
        """
        if offset_pos is None:
            offset_pos = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        if exaxis_pos is None:
            exaxis_pos = [0.0, 0.0, 0.0, 0.0]
        if joint_pos is None:
            joint_pos = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        if tool < 0:
            tool = self.tool
        if user < 0:
            user = self.user
        if vel < 0:
            vel = self.vel
        if acc < 0:
            acc = self.acc

        return (RobotApiBuilder()
                .set_only_error_code()
                .api_call(
            lambda robot: robot.instance.MoveL(desc_pos, tool, user,
                                               joint_pos, vel, acc, ovl, blend_radius, exaxis_pos, search,
                                               offset_flag, offset_pos))
                .build())

    def move_circle(self, desc_pos_p, tool_p, user_p, desc_pos_t, tool_t, user_t, joint_pos_p=None,
                    joint_pos_t=None, vel_p=-1, acc_p=-1, exaxis_pos_p=None, offset_flag_p=0,
                    vel_t=-1, acc_t=-1, exaxis_pos_t=None, offset_flag_t=0, offset_pos_t=None, ovl=100.0,
                    blend_radius=-1.0):
        """
        笛卡尔空间圆弧运动
        :param desc_pos_p: 路径点笛卡尔位姿，单位[mm][°]；
        :param tool_p: 路径点工具号，[0~14];
        :param user_p: 路径点工件号，[0~14];
        :param desc_pos_t: 目标点笛卡尔位姿，单位[mm][°];
        :param tool_t: 工具号，[0~14]；
        :param user_t: 工件号，[0~14]；
        :param joint_pos_p: 路径点关节位置，单位[°] 默认初值为[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]，默认值调用逆运动学求解返回值;
        :param joint_pos_t: 目标点关节位置，单位[°] 默认初值为[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]，默认值调用逆运动学求解返回值;
        :param vel_p: 路径点速度百分比，[0~100] 默认20.0；
        :param acc_p: 路径点加速度百分比，[0~100] 暂不开放, 默认0.0
        :param exaxis_pos_p: 路径点外部轴 1 位置 ~ 外部轴 4 位置 默认[0.0, 0.0, 0.0, 0.0];
        :param offset_flag_p: 路径点是否偏移[0] - 不偏移，[1] - 工件 / 基坐标系下偏移，[2] - 工具坐标系下偏移 默认0;
        :param vel_t: 目标点速度百分比，[0~100] 默认20.0；
        :param acc_t: 目标点加速度百分比，[0~100] 暂不开放 默认0.0；
        :param exaxis_pos_t: 目标点外部轴 1 位置 ~ 外部轴 4 位置 默认[0.0, 0.0, 0.0, 0.0];
        :param offset_flag_t: 目标点是否偏移[0] - 不偏移，[1] - 工件 / 基坐标系下偏移，[2] - 工具坐标系下偏移 默认0;
        :param offset_pos_t: 目标点位姿偏移量，单位[mm][°] 默认[0.0, 0.0, 0.0, 0.0, 0.0, 0.0];
        :param ovl::速度缩放因子，[0~100] 默认100.0;
        :param blend_radius: [-1.0] - 运动到位(阻塞)，[0~1000] - 平滑半径(非阻塞)，单位[mm] 默认 -1.0;
        :return: null
        """
        if joint_pos_p is None:
            joint_pos_p = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        if joint_pos_t is None:
            joint_pos_t = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        if offset_pos_t is None:
            offset_pos_t = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        if exaxis_pos_t is None:
            exaxis_pos_t = [0.0, 0.0, 0.0, 0.0]
        if exaxis_pos_p is None:
            exaxis_pos_p = [0.0, 0.0, 0.0, 0.0]

        if vel_p < 0:
            vel_p = self.vel
        if acc_p < 0:
            acc_p = self.acc
        if vel_t < 0:
            vel_t = self.vel
        if acc_t < 0:
            acc_t = self.acc

        return (RobotApiBuilder()
                .set_only_error_code()
                .api_call(
            lambda robot: robot.instance.MoveC(desc_pos_p, tool_p, user_p, desc_pos_t, tool_t, user_t,
                                               joint_pos_p, joint_pos_t, vel_p, acc_p, exaxis_pos_p, offset_flag_p,
                                               vel_t, acc_t, exaxis_pos_t, offset_flag_t, offset_pos_t, ovl,
                                               blend_radius))
                .build())

    def move_circle_descartes(self, desc_pos_p, tool_p, user_p, desc_pos_t, tool_t=-1, user_t=-1,
                              joint_pos_p=None, joint_pos_t=None, vel_p=-1, acc_p=-1, exaxis_pos_p=None,
                              vel_t=-1, acc_t=-1, exaxis_pos_t=None, ovl=100.0, offset_flag=0, offset_pos=None):
        """
        笛卡尔空间整圆运动
        :param desc_pos_p: 路径点笛卡尔位姿，单位[mm][°]
        :param tool_p: 工具号，[0~14]
        :param user_p: 工件号，[0~14]
        :param desc_pos_t: 目标点笛卡尔位姿，单位[mm][°]
        :param tool_t: 工具号，[0~14]
        :param user_t: 工件号，[0~14]
        :param joint_pos_p: 路径点关节位置，单位[°] 默认初值为[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]，默认值调用逆运动学求解返回值
        :param joint_pos_t: 目标点关节位置，单位[°] 默认初值为[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]，默认值调用逆运动学求解返回值
        :param vel_p: 速度百分比，[0~100]
        :param acc_p: 路径点加速度百分比，[0~100]
        :param exaxis_pos_p: 路径点外部轴1位置~外部轴4位置 默认[0.0, 0.0, 0.0, 0.0]
        :param vel_t: 目标点速度百分比，[0~100]
        :param acc_t: 目标点加速度百分比，[0~100]
        :param exaxis_pos_t: 标点外部轴1位置~外部轴4位置 默认[0.0, 0.0, 0.0, 0.0]
        :param ovl: 速度缩放因子，[0~100]
        :param offset_flag: 是否偏移[0] - 不偏移，[1] - 工件/基坐标系下偏移，[2] - 工具坐标系下偏移 默认0
        :param offset_pos: 位姿偏移量，单位[mm][°] 默认[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        :return: null
        """
        if offset_pos is None:
            offset_pos = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        if exaxis_pos_t is None:
            exaxis_pos_t = [0.0, 0.0, 0.0, 0.0]
        if exaxis_pos_p is None:
            exaxis_pos_p = [0.0, 0.0, 0.0, 0.0]
        if joint_pos_t is None:
            joint_pos_t = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        if joint_pos_p is None:
            joint_pos_p = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        if tool_p < 0:
            tool_p = self.tool
        if user_p < 0:
            user_p = self.user
        if tool_t < 0:
            tool_t = tool_p
        if user_t < 0:
            user_t = user_p
        if vel_p < 0:
            vel_p = self.vel
        if acc_p < 0:
            acc_p = self.acc
        if vel_t < 0:
            vel_t = self.vel
        if acc_t < 0:
            acc_t = self.acc

        return (RobotApiBuilder()
                .set_only_error_code()
                .api_call(
            lambda robot: robot.instance.Circle(desc_pos_p, tool_p, user_p, desc_pos_t, tool_t, user_t,
                                                joint_pos_p, joint_pos_t, vel_p, acc_p, exaxis_pos_p,
                                                vel_t, acc_t, exaxis_pos_t, ovl, offset_flag, offset_pos))
                .build())

    def move_spiral(self, desc_pos, param, tool=-1, user=-1, joint_pos=None, vel=-1, acc=-1, exaxis_pos=None, ovl=100.0,
                    offset_flag=0, offset_pos=None):
        """
        笛卡尔空间螺旋线运动
        :param desc_pos: 目标笛卡尔位姿，单位[mm][°]
        :param tool: 工具号，[0~14]
        :param user: 工件号，[0~14]
        :param param: [circle_num, circle_angle, rad_init, rad_add, rotaxis_add, rot_direction(0顺, 1逆)]：
        :param joint_pos: 目标关节位置，单位[°] 默认初值为[0.0,0.0,0.0,0.0,0.0,0.0]，默认值调用逆运动学求解返回值
        :param vel: 速度百分比，[0~100] 默认20.0
        :param acc: 加速度百分比，[0~100] 默认100.0
        :param exaxis_pos: 外部轴 1 位置 ~ 外部轴 4 位置 默认[0.0,0.0,0.0,0.0]
        :param ovl: 速度缩放因子，[0~100] 默认100.0
        :param offset_flag: [0]-不偏移，[1]-工件/基坐标系下偏移，[2]-工具坐标系下偏移 默认 0
        :param offset_pos: 位姿偏移量，单位 [mm][°] 默认[0.0,0.0,0.0,0.0,0.0,0.0]
        :return: null
        """
        if offset_pos is None:
            offset_pos = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        if exaxis_pos is None:
            exaxis_pos = [0.0, 0.0, 0.0, 0.0]
        if joint_pos is None:
            joint_pos = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        if vel < 0:
            vel = self.vel
        if acc < 0:
            acc = self.acc
        if tool < 0:
            tool = self.tool
        if user < 0:
            user = self.user

        return (RobotApiBuilder()
                .set_only_error_code()
                .api_call(
            lambda robot: robot.instance.NewSpiral(desc_pos, tool, user, param,
                                                   joint_pos, vel, acc, exaxis_pos, ovl, offset_flag, offset_pos))
                .build())

    @staticmethod
    def stop_motion():
        """
        终止运动，使用终止运动需运动指令为非阻塞状态
        :return: null
        """
        return (RobotApiBuilder()
                .set_only_error_code()
                .api_call(
            lambda robot: robot.instance.StopMotion())
                .build())


class Gripper:
    """
    机器人夹爪控制
    """

    def __init__(self, index=0, speed=50, force=20):
        self.index = index
        self.pos = 100
        self.speed = speed
        self.force = force

    def set_speed(self, speed):
        """
        设置夹爪速度
        :param speed: 速度百分比，范围[0~100]
        :return: null
        """
        if speed < 0 or speed > 100:
            raise ValueError("Invalid speed")
        self.speed = speed
        return RobotApiBuilder().build()

    def set_force(self, force):
        """
        设置夹爪力度
        :param force: 力度百分比，范围[0~100]
        :return: null
        """
        if force < 0 or force > 100:
            raise ValueError("Invalid force")
        self.force = force
        return RobotApiBuilder().build()

    @staticmethod
    def get_config():
        """
        获取夹爪配置 - [number,company,device,softversion] 后面的参数暂不使用
        :return: number
        """
        return (RobotApiBuilder()
                .api_call(
            lambda robot: robot.instance.GetGripperConfig())
                .post_data_process(lambda data: data[0])
                .build())

    def activate(self):
        """
        激活夹爪
        :return: null
        """
        return (RobotApiBuilder()
                .set_only_error_code()
                .api_call(
            lambda robot: robot.instance.ActGripper(self.index, 1))
                .build())

    def reset(self):
        """
        复位夹爪
        :return: null
        """
        return (RobotApiBuilder()
                .set_only_error_code()
                .api_call(
            lambda robot: robot.instance.ActGripper(self.index, 0))
                .build())

    def deactivate(self):
        return self.reset()

    def move(self, pos, maxtime=30000, block=True):
        """
        控制夹爪运动
        :param pos: 位置百分比，范围[0~100]
        :param maxtime: 最大等待时间，范围[0~30000]，单位[ms]
        :param block: 0-阻塞，1-非阻塞
        :return: null
        """
        block = 0 if block else 1
        self.pos = pos

        return (RobotApiBuilder()
                .set_only_error_code()
                .api_call(
            lambda robot: robot.instance.MoveGripper(self.index, pos, self.speed, self.force, maxtime, block))
                .build())

    @staticmethod
    def get_status():
        """
        获取夹爪状态
        :return: [fault,status] fault:0-无错误，1-有错误 status:0-夹爪未激活，1-夹爪激活
        """
        return (RobotApiBuilder()
                .api_call(
            lambda robot: robot.instance.GetGripperMotionDone())
                .build())

    @staticmethod
    def is_motion_done():
        """
        夹爪是否运动完成
        :return: status 运动是否完成
        """
        return (Gripper.get_status()
                       .post_data_process(
            lambda data: data[1] == 1))

    @staticmethod
    def set_config(company, device, soft_version=0, bus=0):
        # sh*t api by Fairino
        """
        配置夹爪
        :param company: 夹爪厂商，1-Robotiq，2-慧灵，3-天机，4-大寰，5-知行
        :param device: 设备号，Robotiq(0-2F-85系列)，慧灵(0-NK系列,1-Z-EFG-100)，天机(0-TEG-110)，大寰(0-PGI-140)，知行(0-CTPM2F20)
        :param soft_version: 软件版本号，暂不使用，默认为0
        :param bus: 设备挂载末端总线位置，暂不使用，默认为0
        :return: null
        """
        return (RobotApiBuilder()
                .set_only_error_code()
                .api_call(
            lambda robot: robot.instance.SetGripperConfig(company, device, soft_version, bus))
                .build())

    @staticmethod
    def compute_pre_pick(desc_pos, z_length, z_angle):
        # making second sh*t api by Fairino
        """
        计算预抓取点-视觉
        :param desc_pos: 夹抓取点笛卡尔位姿
        :param z_length: z轴偏移量
        :param z_angle: 绕z轴旋转偏移量
        """
        return (RobotApiBuilder()
                .api_call(
            lambda robot: robot.instance.ComputePrePick(desc_pos, z_length, z_angle))
                .build())

    @staticmethod
    def compute_post_pick(desc_pos, z_length, z_angle):
        # making third sh*t api by Fairino
        """
        计算撤退点-视觉
        :param desc_pos: 夹抓取点笛卡尔位姿
        :param z_length: z轴偏移量
        :param z_angle: 绕z轴旋转偏移量
        """
        return (RobotApiBuilder()
                .api_call(
            lambda robot: robot.instance.ComputePostPick(desc_pos, z_length, z_angle))
                .build())
