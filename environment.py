import configparser


class Environment:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")

    def get_config(self):
        return self.config
