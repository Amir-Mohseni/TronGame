from ks.models import Constants, EDirection, ECell


def get_d_cords(dir_to_take):
    if dir_to_take == EDirection.Left:
        return -1, 0
    elif dir_to_take == EDirection.Right:
        return 1, 0
    elif dir_to_take == EDirection.Up:
        return 0, -1
    elif dir_to_take == EDirection.Down:
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
            cur_agent.direction = move[0]
            if not move[1]:
                next_dir = get_d_cords(move[0])
                cur_agent.change_position(next_dir)
                cur_agent.change_direction(move[0])
            else:
                cur_agent.activate_wall_breaker()
                next_dir = get_d_cords(cur_agent.direction)
                cur_agent.change_position(next_dir)
            if self.board[cur_agent.position.y][cur_agent.position.x] == ECell.Empty:
                cur_agent.score += self.constants.wall_score_coefficient
                if cur_agent.color == "Blue":
                    self.board[cur_agent.position.y][cur_agent.position.x] = ECell.BlueWall
                else:
                    self.board[cur_agent.position.y][cur_agent.position.x] = ECell.YellowWall
            elif self.board[cur_agent.position.y][cur_agent.position.x] == ECell.AreaWall:
                cur_agent.score -= cur_agent.health * 150
                cur_agent.health = 0
                cur_agent.score -= self.constants.area_wall_crash_score
            elif self.board[cur_agent.position.y][cur_agent.position.x] == ECell.BlueWall:
                if cur_agent.color == "Blue":
                    cur_agent.score += self.constants.wall_score_coefficient - self.constants.my_wall_crash_score
                    if not cur_agent.wall_breaker_is_on():
                        cur_agent.health -= 1
                        cur_agent.score -= 150
                else:
                    if cur_agent.wall_breaker_is_on():
                        enemy_agent.score -= self.constants.wall_score_coefficient
                        cur_agent.score += self.constants.wall_score_coefficient
                    else:
                        cur_agent.health -= 1
                        cur_agent.score -= 150
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
                        cur_agent.score -= 150
                else:
                    if cur_agent.wall_breaker_is_on():
                        enemy_agent.score -= self.constants.wall_score_coefficient
                        cur_agent.score += self.constants.wall_score_coefficient
                    else:
                        cur_agent.health -= 1
                        cur_agent.score -= 150
                        enemy_agent.score -= self.constants.wall_score_coefficient
                        cur_agent.score += self.constants.wall_score_coefficient
                        if cur_agent.health == 0:
                            cur_agent.score -= self.constants.enemy_wall_crash_score
                    self.board[cur_agent.position.y][cur_agent.position.x] = ECell.BlueWall
            self.scores[our_agent_side] = cur_agent.score
            self.scores[enemy_agent_side] = enemy_agent.score
            cur_agent.tick_wall_breaker()

    def is_game_finished(self):
        if self.agents[self.my_side].health == 0 or self.agents[self.other_side].health == 0:
            return True
        return False

    def score_difference(self, my_side, enemy_side):
        result_score = self.agents[my_side].score - self.agents[enemy_side].score
        return result_score

    def get_blue_yellow_score_difference(self):
        return self.agents["Blue"].score - self.agents["Yellow"].score

    def get_our_agent_position(self):
        return self.agents[self.my_side].position

    def get_our_agent_direction(self):
        return self.agents[self.my_side].direction

    def get_enemy_agent_position(self):
        return self.agents[self.other_side].position

    def get_enemy_agent_direction(self):
        return self.agents[self.other_side].direction

    def get_our_agent_empty_neighbors(self):
        empty_neighbors = []

        our_position = self.get_our_agent_position()

        their_position = self.get_enemy_agent_position()

        if our_position.x + 1 < len(self.board[0]) and EDirection.Left != self.get_our_agent_direction():
            if self.board[our_position.y][our_position.x + 1] == ECell.Empty and EDirection.Left != self.get_our_agent_direction():
                empty_neighbors.append(EDirection.Right)
        if our_position.x - 1 >= 0:
            if self.board[our_position.y][our_position.x - 1] == ECell.Empty and EDirection.Right != self.get_our_agent_direction():
                empty_neighbors.append(EDirection.Left)
        if our_position.y + 1 < len(self.board):
            if self.board[our_position.y + 1][our_position.x] == ECell.Empty and EDirection.Up != self.get_our_agent_direction():
                empty_neighbors.append(EDirection.Down)
        if our_position.y - 1 >= 0:
            if self.board[our_position.y - 1][our_position.x] == ECell.Empty and EDirection.Down != self.get_our_agent_direction():
                empty_neighbors.append(EDirection.Up)
        return empty_neighbors
    def get_our_agent_blue_wall_neighbors(self):
        blue_walls = []
        our_position = self.get_our_agent_position()

        their_position = self.get_enemy_agent_position()

        if our_position.x + 1 < len(self.board[0]):
            if self.board[our_position.y][our_position.x + 1] == ECell.BlueWall and EDirection.Left != self.get_our_agent_direction():
                blue_walls.append(EDirection.Right)
        if our_position.x - 1 >= 0:
            if self.board[our_position.y][our_position.x - 1] == ECell.BlueWall and EDirection.Right != self.get_our_agent_direction():
                blue_walls.append(EDirection.Left)
        if our_position.y + 1 < len(self.board):
            if self.board[our_position.y + 1][our_position.x] == ECell.BlueWall and EDirection.Up != self.get_our_agent_direction():
                blue_walls.append(EDirection.Down)
        if our_position.y - 1 >= 0:
            if self.board[our_position.y - 1][our_position.x] == ECell.BlueWall and EDirection.Down != self.get_our_agent_direction():
                blue_walls.append(EDirection.Up)
        return blue_walls

    def get_our_agent_Area_wall_neighbors(self):
        area_walls = []

        our_position = self.get_our_agent_position()

        their_position = self.get_enemy_agent_position()

        if our_position.x + 1 < len(self.board[0]):
            if self.board[our_position.y][our_position.x + 1] == ECell.AreaWall and EDirection.Left != self.get_our_agent_direction():
                area_walls.append(EDirection.Right)
        if our_position.x - 1 >= 0:
            if self.board[our_position.y][our_position.x - 1] == ECell.AreaWall and EDirection.Right != self.get_our_agent_direction():
                area_walls.append(EDirection.Left)
        if our_position.y + 1 < len(self.board):
            if self.board[our_position.y + 1][our_position.x] == ECell.AreaWall and EDirection.Up != self.get_our_agent_direction():
                area_walls.append(EDirection.Down)
        if our_position.y - 1 >= 0:
            if self.board[our_position.y - 1][our_position.x] == ECell.AreaWall and EDirection.Down != self.get_our_agent_direction():
                area_walls.append(EDirection.Up)
        return area_walls

    def get_our_agent_yellow_wall_neighbors(self):
        yellow_walls = []

        our_position = self.get_our_agent_position()

        their_position = self.get_enemy_agent_position()

        if our_position.x + 1 < len(self.board[0]):
            if self.board[our_position.y][our_position.x + 1] == ECell.YellowWall and EDirection.Left != self.get_our_agent_direction():
                yellow_walls.append(EDirection.Right)
        if our_position.x - 1 >= 0:
            if self.board[our_position.y][our_position.x - 1] == ECell.YellowWall and EDirection.Right != self.get_our_agent_direction():
                yellow_walls.append(EDirection.Left)
        if our_position.y + 1 < len(self.board):
            if self.board[our_position.y + 1][our_position.x] == ECell.YellowWall and EDirection.Up != self.get_our_agent_direction():
                yellow_walls.append(EDirection.Down)
        if our_position.y - 1 >= 0:
            if self.board[our_position.y - 1][our_position.x] == ECell.YellowWall and EDirection.Down != self.get_our_agent_direction():
                yellow_walls.append(EDirection.Up)
        return yellow_walls
