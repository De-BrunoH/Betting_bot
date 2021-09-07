class BetException:
    def __init__(self, broker: str, event: str, screenshot_path: str, root_message: str, message: str='Bet runtime error.'):
        self.broker = broker
        self.event = event
        self.message = message
        self.screenshot = screenshot_path
        self.root_message = root_message