from sdk.base import RobotApi


class RobotApiBuilder(RobotApi):
    """
    Shall we really use a builder pattern here?
    """

    def __init__(self):
        super().__init__()
        self.__call_api__ = lambda robot: (0, None)
        self.only_error_code = False

    def build(self):
        return self

    def set_api_call(self, api_call):
        self.__call_api__ = api_call
        return self

    def only_error_code(self):
        self.only_error_code = True
        return self
