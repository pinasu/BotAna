class Image(object):

    def __init__(self, sound, message, cooldown):
        self.sound = sound
        self.message = message
        self.cooldown = cooldown

    def getName(self):
        return self.sound

    def getCooldown(self):
        return self.cooldown

    def getMessage(self):
    	return self.message
