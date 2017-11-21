class Image(object):

    def __init__(self, sound, message, cooldown, game=""):
        self.sound = sound
        self.message = message
        self.cooldown = cooldown
        self.game = game

    def get_name(self):
        return self.sound

    def get_cooldown(self):
        return self.cooldown

    def get_message(self):
    	return self.message

    def get_game(self):
        return self.game

    def is_for_specific_game(self):
        return self.game != ""
