class Sound(object):

    def __init__(self, sound, cooldown):
        self.sound = sound
        self.cooldown = cooldown

    def getName(self):
        return self.sound

    def getCooldown(self):
        return self.cooldown
