from ks.models import EDirection


class Agents:
    def __init__(self, health, position, direction, wall_breaker_cooldown, wall_breaker_rem_time, score, color, constants):
        self.health = health
        self.position = position
        self.direction = direction
        self.wall_breaker_cooldown = wall_breaker_cooldown
        self.wall_breaker_rem_time = wall_breaker_rem_time
        self.score = score
        self.color = color
        self.constants = constants

    def decrease_health(self):
        self.health -= 1

    def change_position(self, d):
        self.position.x += d[0]
        self.position.y += d[1]

    def activate_wall_breaker(self):
        if not self.wall_breaker_is_on() and self.wall_breaker_cooldown == 0:
            self.wall_breaker_rem_time = self.constants.wall_breaker_duration

    def change_direction(self, new_direction):
        if new_direction in [EDirection.Up, EDirection.Down, EDirection.Left, EDirection.Right]:
            self.direction = new_direction

    def tick_wall_breaker(self):
        if self.wall_breaker_rem_time > 0:
            self.wall_breaker_rem_time -= 1

        if self.wall_breaker_cooldown > 0:
            self.wall_breaker_cooldown -= 1

    def change_score(self, new_score):
        self.score = new_score

    def wall_breaker_is_on(self):
        if self.wall_breaker_rem_time != 0:
            return True
        return False


