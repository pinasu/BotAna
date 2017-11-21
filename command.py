class Command(object):

    def __init__(self,command, response, cooldown, tipo, game=""):
        self.command = command
        self.response = response
        self.cooldown = cooldown
        self.tipo = tipo
        self.game = game

    def get_name(self):
        return self.command

    def get_response(self):
        return self.response

    def get_cooldown(self):
        return self.cooldown

    def get_tipo(self):
        return self.tipo

    def is_simple_command(self):
        if self.response == "":
            return False
        return True

    def is_mod(self):
        if self.tipo == "mod":
            return True
        return False

    def get_game(self):
        return self.game

    def is_for_specific_game(self):
        return self.game != ""
