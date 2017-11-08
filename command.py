class Command(object):

    def __init__(self,command, response, cooldown):
        self.command = command
        self.response = response
        self.cooldown = cooldown

    def getName(self):
        return self.command

    def getResponse(self):
        return self.response

    def getCooldown(self):
        return self.cooldown
