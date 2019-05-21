class Level:
    def __init__(self, curr_lvl=1, curr_xp=0, xp_skill=1):
        self.curr_lvl = curr_lvl
        self.curr_xp = curr_xp
        self.xp_skill = xp_skill

    def xp_skill_modifier(self):
        if self.xp_skill == 1:
            return 0.75
        elif self.xp_skill == 0:
            return 1.0
        elif self.xp_skill == -1:
            return 1.25

    @property
    def next_level_xp(self):
        return int(((self.curr_lvl**2) * 100) * self.xp_skill_modifier())

    def add_xp(self, xp):
        self.curr_xp += xp
        if self.curr_xp > self.next_level_xp:
            self.curr_xp -= self.next_level_xp
            self.curr_lvl += 1
            return True
        return False
