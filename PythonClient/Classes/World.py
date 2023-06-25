from ks.models import Constants, EDirection, ECell


def get_d_cords(dir_to_take):
    if dir_to_take == EDirection.Left:
        return -1, 0
    if dir_to_take == EDirection.Right:
        return 1, 0
    if dir_to_take == EDirection.Up:
        return 0, -1
    if dir_to_take == EDirection.Down:
        return 0, 1


class Worlds:
    def __init__(self, my_side, other_side, board, agents, scores, constants):
        self.my_side = my_side
        self.other_side = other_side
        self.board = board
        self.agents = agents
        self.scores = scores
        self.constants = constants

    def change_sides(self):
        temp_side = self.my_side
        self.my_side = self.other_side
        self.other_side = temp_side

    def change_board(self, our_agent_side, enemy_agent_side, move):
        cur_agent = self.agents[our_agent_side]
        enemy_agent = self.agents[enemy_agent_side]
        if move is not None:
            cur_agent.direction = move
            if move in [EDirection.Up, EDirection.Down, EDirection.Left, EDirection.Right]:
                next_dir = get_d_cords(move)
                cur_agent.change_position(next_dir)
            else:
                cur_agent.activate_wall_breaker()
                cur_agent.change_position(cur_agent.direction)
        if self.board[cur_agent.position.y][cur_agent.position.x] == ECell.Empty:
            cur_agent.score += self.constants.wall_score_coefficient
            if cur_agent.color == "Blue":
                self.board[cur_agent.position.y][cur_agent.position.x] = ECell.BlueWall
            else:
                self.board[cur_agent.position.y][cur_agent.position.x] = ECell.YellowWall
        elif self.board[cur_agent.position.y][cur_agent.position.x] == ECell.AreaWall:
            cur_agent.health = 0
            cur_agent.score -= self.constants.area_wall_crash_score
        elif self.board[cur_agent.position.y][cur_agent.position.x] == ECell.BlueWall:
            if cur_agent.color == "Blue":
                cur_agent.score += self.constants.wall_score_coefficient - self.constants.my_wall_crash_score
                if not cur_agent.wall_breaker_is_on():
                    cur_agent.health -= 1
                    cur_agent.score -= 100
            else:
                if cur_agent.wall_breaker_is_on():
                    enemy_agent.score -= self.constants.wall_score_coefficient
                    cur_agent.score += self.constants.wall_score_coefficient
                else:
                    cur_agent.health -= 1
                    cur_agent.score -= 100
                    enemy_agent.score -= self.constants.wall_score_coefficient
                    cur_agent.score += self.constants.wall_score_coefficient
                    if cur_agent.health == 0:
                        cur_agent.score -= self.constants.enemy_wall_crash_score
                self.board[cur_agent.position.y][cur_agent.position.x] = ECell.YellowWall
        else:
            if cur_agent.color == "Yellow":
                cur_agent.score += self.constants.wall_score_coefficient - self.constants.my_wall_crash_score
                if not cur_agent.wall_breaker_is_on():
                    cur_agent.health -= 1
                    cur_agent.score -= 100
            else:
                if cur_agent.wall_breaker_is_on():
                    enemy_agent.score -= self.constants.wall_score_coefficient
                    cur_agent.score += self.constants.wall_score_coefficient
                else:
                    cur_agent.health -= 1
                    cur_agent.score -= 100
                    enemy_agent.score -= self.constants.wall_score_coefficient
                    cur_agent.score += self.constants.wall_score_coefficient
                    if cur_agent.health == 0:
                        cur_agent.score -= self.constants.enemy_wall_crash_score
                self.board[cur_agent.position.y][cur_agent.position.x] = ECell.BlueWall
        self.scores[our_agent_side] = cur_agent.score
        self.scores[enemy_agent_side] = enemy_agent.score
        cur_agent.tick_wall_breaker()

    def score_difference(self, my_side, enemy_side):
        return self.agents[my_side].score - self.agents[enemy_side].score

    def get_our_agent_position(self):
        return self.agents[self.my_side].position

    def get_enemy_agent_position(self):
        return self.agents[self.other_side].position

    def get_our_agent_empty_neighbors(self):
        empty_neighbors = []

        our_position = self.get_our_agent_position()

        their_position = self.get_enemy_agent_position()

        if our_position.x + 1 < len(self.board):
            if self.board[our_position.y][our_position.x + 1] == ECell.Empty and \
                    not (our_position.x + 1 == their_position.x and our_position.y == their_position.y):
                empty_neighbors.append(EDirection.Right)
        if our_position.x - 1 >= 0:
            if self.board[our_position.y][our_position.x - 1] == ECell.Empty and \
                    not (our_position.x - 1 == their_position.x and our_position.y == their_position.y):
                empty_neighbors.append(EDirection.Left)
        if our_position.y + 1 < len(self.board):
            if self.board[our_position.y + 1][our_position.x] == ECell.Empty and \
                    not (our_position.x == their_position.x and our_position.y + 1 == their_position.y):
                empty_neighbors.append(EDirection.Down)
        if our_position.y - 1 >= 0:
            if self.board[our_position.y - 1][our_position.x] == ECell.Empty and \
                    not (our_position.x == their_position.x and our_position.y - 1 == their_position.y):
                empty_neighbors.append(EDirection.Up)
        return empty_neighbors
    def get_our_agent_blue_wall_neighbors(self):
        blue_walls = []
        our_position = self.get_our_agent_position()

        their_position = self.get_enemy_agent_position()

        if our_position.x + 1 < len(self.board):
            if self.board[our_position.y][our_position.x + 1] == ECell.BlueWall and \
                    not (our_position.x + 1 == their_position.x and our_position.y == their_position.y):
                blue_walls.append(EDirection.Right)
        if our_position.x - 1 >= 0:
            if self.board[our_position.y][our_position.x - 1] == ECell.BlueWall and \
                    not (our_position.x - 1 == their_position.x and our_position.y == their_position.y):
                blue_walls.append(EDirection.Left)
        if our_position.y + 1 < len(self.board):
            if self.board[our_position.y + 1][our_position.x] == ECell.BlueWall and \
                    not (our_position.x == their_position.x and our_position.y + 1 == their_position.y):
                blue_walls.append(EDirection.Down)
        if our_position.y - 1 >= 0:
            if self.board[our_position.y - 1][our_position.x] == ECell.BlueWall and \
                    not (our_position.x == their_position.x and our_position.y - 1 == their_position.y):
                blue_walls.append(EDirection.Up)
        return blue_walls

    def get_our_agent_Area_wall_neighbors(self):
        area_walls = []

        our_position = self.get_our_agent_position()

        their_position = self.get_enemy_agent_position()

        if our_position.x + 1 < len(self.board[0]):
            if self.board[our_position.y][our_position.x + 1] == ECell.AreaWall and \
                    not (our_position.x + 1 == their_position.x and our_position.y == their_position.y):
                area_walls.append(EDirection.Right)
        if our_position.x - 1 >= 0:
            if self.board[our_position.y][our_position.x - 1] == ECell.AreaWall and \
                    not (our_position.x - 1 == their_position.x and our_position.y == their_position.y):
                area_walls.append(EDirection.Left)
        if our_position.y + 1 < len(self.board):
            if self.board[our_position.y + 1][our_position.x] == ECell.AreaWall and \
                    not (our_position.x == their_position.x and our_position.y + 1 == their_position.y):
                area_walls.append(EDirection.Down)
        if our_position.y - 1 >= 0:
            if self.board[our_position.y - 1][our_position.x] == ECell.AreaWall and \
                    not (our_position.x == their_position.x and our_position.y - 1 == their_position.y):
                area_walls.append(EDirection.Up)
        return area_walls

    def get_our_agent_yellow_wall_neighbors(self):
        yellow_walls = []

        our_position = self.get_our_agent_position()

        their_position = self.get_enemy_agent_position()

        if our_position.x + 1 < len(self.board[0]):
            if self.board[our_position.y][our_position.x + 1] == ECell.YellowWall and \
                    not (our_position.x + 1 == their_position.x and our_position.y == their_position.y):
                yellow_walls.append(EDirection.Right)
        if our_position.x - 1 >= 0:
            if self.board[our_position.y][our_position.x - 1] == ECell.YellowWall and \
                    not (our_position.x - 1 == their_position.x and our_position.y == their_position.y):
                yellow_walls.append(EDirection.Left)
        if our_position.y + 1 < len(self.board):
            if self.board[our_position.y + 1][our_position.x] == ECell.YellowWall and \
                    not (our_position.x == their_position.x and our_position.y + 1 == their_position.y):
                yellow_walls.append(EDirection.Down)
        if our_position.y - 1 >= 0:
            if self.board[our_position.y - 1][our_position.x] == ECell.YellowWall and \
                    not (our_position.x == their_position.x and our_position.y - 1 == their_position.y):
                yellow_walls.append(EDirection.Up)
        return yellow_walls
