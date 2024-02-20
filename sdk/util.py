from sdk.base import RobotApi


class RobotApiBuilder(RobotApi):
    """
    Shall we really use a builder pattern here?
    """

    def __init__(self):
        super().__init__()
        self.__call_api__ = lambda robot: (0, None)
        self.__post_data_process__ = super().__post_data_process__
        self.only_error_code = False

    def build(self):
        return self

    def api_call(self, api_call):
        self.__call_api__ = api_call
        return self

    def post_data_process(self, post_data_process):
        self.__post_data_process__ = post_data_process
        return self

    def only_error_code(self):
        self.only_error_code = True
        return self
