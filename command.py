class Command(object):

    def __init__(self,command, response, cooldown):
        self.command = command
        self.response = response
        self.cooldown = cooldown
