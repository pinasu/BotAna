class Command(object):

    def __init__(self,command, response, cooldown, tipo):
        self.command = command
        self.response = response
        self.cooldown = cooldown
        self.tipo = tipo

    def getName(self):
        return self.command

    def getResponse(self):
        return self.response

    def getCooldown(self):
        return self.cooldown

    def getTipo(self):
        return self.tipo

    def isMod(self):
        if self.tipo == "mod":
            return True
        elif self.tipo == "pleb":
            return False
