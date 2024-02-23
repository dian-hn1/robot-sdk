from enum import Enum


class BaseController:
    def __init__(self, robot):
        self.robot = robot
        self.act = lambda time, *args: None  # default act function, args are not defined

    def get_robot(self):
        return self.robot


class ButtonController(BaseController):
    def act(self, time, is_pressed):
        pass


class DebounceController(ButtonController):
    def __init__(self, wrapped_controller, debounce_time=50):
        """
        debounce controller for one-button controller.
        :param wrapped_controller: The controller to be wrapped.
        :param debounce_time: Debounce time in milliseconds.
        """
        super().__init__(wrapped_controller.get_robot())
        self.wrapped_controller = wrapped_controller
        self.debounce_time = debounce_time
        self.last_act_time = 0
        self.last_act_state = False

    def act(self, time, is_pressed):
        if is_pressed != self.last_act_state:
            self.last_act_state = is_pressed
            self.last_act_time = time
        elif time - self.last_act_time >= self.debounce_time:
            self.last_act_time = time
            self.wrapped_controller.act(time, is_pressed)


class TriggerController(ButtonController):
    def __init__(self, wrapped_controller):
        """
        trigger controller for one-button controller.
        trigger means the action will only be triggered after the button is pressed.
        :param wrapped_controller: The controller to be wrapped.
        :param trigger_time: Trigger time in milliseconds.
        """
        super().__init__(wrapped_controller.get_robot())
        self.wrapped_controller = wrapped_controller
        self.last_act_state = False

    def act(self, time, is_pressed):
        if is_pressed and not self.last_act_state:
            self.last_act_state = is_pressed  # thread safe
            self.wrapped_controller.act(time, is_pressed)
        self.last_act_state = is_pressed


class GateController(ButtonController):
    def __init__(self, wrapped_set_controller, wrapped_reset_controller):
        """
        gate controller for one-button controller.
        :param wrapped_set_controller: The controller to be wrapped for setting the gate.
        :param wrapped_reset_controller: The controller to be wrapped for resetting the gate.
        """
        super().__init__(wrapped_set_controller.get_robot())
        self.wrapped_set_controller = TriggerController(wrapped_set_controller)
        self.wrapped_reset_controller = TriggerController(wrapped_reset_controller)

    def act(self, time, is_pressed):
        self.wrapped_set_controller.act(time, is_pressed)
        self.wrapped_reset_controller.act(time, not is_pressed)
