class Sound(object):

    def __init__(self, sound, game=""):
        self.sound = sound
        self.game = game

    def get_name(self):
        return self.sound

    def get_game(self):
        return self.game

    def is_for_specific_game(self):
        return self.game != ""
