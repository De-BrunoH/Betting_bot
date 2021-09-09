from betting.bet_exceptions.BetException import BetException


class BetDeniedByBookieException(BetException):
    def __init__(self, broker: str, event: str, screenshot_path: str, root_message: str, message: str='Bet denied by bokie. See image.'):
        super().__init__(
            broker = broker,
            event = event,
            message = message,
            screenshot_path = screenshot_path,
            root_message = root_message
        )