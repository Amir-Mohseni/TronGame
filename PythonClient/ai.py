# -*- coding: utf-8 -*-

# python imports
import random
import copy

from Classes.Agents import Agents
from Classes.Worlds import Worlds
from ks.models import *

# chillin imports
from chillin_client import RealtimeAI

# project imports
from ks.models import ECell, EDirection, Position
from ks.commands import ChangeDirection, ActivateWallBreaker

MN = -10000
MX = +10000


class AI(RealtimeAI):

    def __init__(self, world):
        super(AI, self).__init__(world)

    def initialize(self):
        print('initialize')

    def decide(self):
        print('decide')
        self.client1()
        # self.send_command(ChangeDirection(random.choice(list(EDirection))))
        # if self.world.agents[self.my_side].wall_breaker_cooldown == 0:
        #     self.send_command(ActivateWallBreaker())

    def get_next_nodes(self, current_world, neighbors, wallbreaker, move_list, depth):
        best_answer = MN, []

        for move in neighbors:
            new_world = copy.deepcopy(current_world)

            # Change Direction
            new_world.change_board(new_world.my_side, new_world.other_side, [move, wallbreaker])
            new_world.change_sides()
            new_move_list = copy.deepcopy(move_list)
            new_move_list.append([move, wallbreaker])
            ret = self.minimax(new_world, new_move_list, depth + 1)
            if ret[0] * -1 > best_answer[0]:
                best_answer = ret[0] * -1, ret[1]
        return best_answer

    def minimax(self, current_world, move_list, depth):
        if depth == 6:
            return current_world.score_difference(current_world.my_side, current_world.other_side), move_list
        if current_world.is_game_finished():
            return current_world.score_difference(current_world.my_side, current_world.other_side), move_list
        if depth % 2 == 0 and current_world.get_our_agent_position() == current_world.get_enemy_agent_position():
            current_world.scores["Blue"] -= current_world.agents["Blue"].health * 150
            current_world.scores["Yellow"] -= current_world.agents["Yellow"].health * 150
            return current_world.score_difference(current_world.my_side, current_world.other_side), move_list
        my_team = current_world.my_side
        my_enemy = current_world.other_side
        empty_neighbors = current_world.get_our_agent_empty_neighbors()
        blue_walls = current_world.get_our_agent_blue_wall_neighbors()
        yellow_walls = current_world.get_our_agent_yellow_wall_neighbors()
        area_walls = current_world.get_our_agent_Area_wall_neighbors()

        best_answer = MN, move_list

        if current_world.agents[my_team].wall_breaker_is_on():
            # wall breaker is on
            ret = MN, move_list
            if my_team == "Yellow":
                if current_world.agents[my_team].wall_breaker_rem_time > 1 and blue_walls:
                    ret = self.get_next_nodes(current_world, blue_walls, False, move_list, depth)
                    if ret[0] > best_answer[0]:
                        best_answer = ret
                if empty_neighbors:
                    ret = self.get_next_nodes(current_world, empty_neighbors, False, move_list, depth)
                    if ret[0] > best_answer[0]:
                        best_answer = ret
                if yellow_walls:
                    ret = self.get_next_nodes(current_world, yellow_walls, False, move_list, depth)
                    if ret[0] > best_answer[0]:
                        best_answer = ret
            else:
                if current_world.agents[my_team].wall_breaker_rem_time > 1 and yellow_walls:
                    ret = self.get_next_nodes(current_world, yellow_walls, False, move_list, depth)
                    if ret[0] > best_answer[0]:
                        best_answer = ret
                elif empty_neighbors:
                    ret = self.get_next_nodes(current_world, empty_neighbors, False, move_list, depth)
                    if ret[0] > best_answer[0]:
                        best_answer = ret
                elif blue_walls:
                    ret = self.get_next_nodes(current_world, blue_walls, False, move_list, depth)
                    if ret[0] > best_answer[0]:
                        best_answer = ret

        else:
            # wall breaker is off
            if empty_neighbors:
                ret = self.get_next_nodes(current_world, empty_neighbors, False, move_list, depth)
                if ret[0] > best_answer[0]:
                    best_answer = ret
            else:
                if current_world.agents[my_team].wall_breaker_cooldown == 0 and not (
                        current_world.agents[my_team].direction in area_walls):
                    only_move = [current_world.agents[my_team].direction]
                    ret = self.get_next_nodes(current_world, only_move, True, move_list, depth)
                    if ret[0] > best_answer[0]:
                        best_answer = ret
                else:
                    if my_team == "Yellow":
                        if blue_walls:
                            ret = self.get_next_nodes(current_world, blue_walls, False, move_list, depth)
                            if ret[0] > best_answer[0]:
                                best_answer = ret
                        if yellow_walls:
                            ret = self.get_next_nodes(current_world, yellow_walls, False, move_list, depth)
                            if ret[0] > best_answer[0]:
                                best_answer = ret
                    else:
                        if yellow_walls:
                            ret = self.get_next_nodes(current_world, yellow_walls, False, move_list, depth)
                            if ret[0] > best_answer[0]:
                                best_answer = ret
                        if blue_walls:
                            ret = self.get_next_nodes(current_world, blue_walls, False, move_list, depth)
                            if ret[0] > best_answer[0]:
                                best_answer = ret
        return best_answer

    def update_world_and_agents(self):
        temp_our_agent = self.world.agents[self.my_side]
        temp_enemy_agent = self.world.agents[self.other_side]

        our_agent = Agents(temp_our_agent.health, temp_our_agent.position, temp_our_agent.direction,
                           temp_our_agent.wall_breaker_cooldown, temp_our_agent.wall_breaker_rem_time,
                           self.world.scores[self.my_side], self.my_side, self.world.constants)

        enemy_agent = Agents(temp_enemy_agent.health, temp_enemy_agent.position, temp_enemy_agent.direction,
                             temp_enemy_agent.wall_breaker_cooldown, temp_enemy_agent.wall_breaker_rem_time,
                             self.world.scores[self.other_side], self.other_side, self.world.constants)

        agent_dict = {self.my_side: our_agent, self.other_side: enemy_agent}

        start_world = Worlds(self.my_side, self.other_side, self.world.board, agent_dict, self.world.scores,
                             self.world.constants)
        return start_world

    def client1(self):
        #        my_team = self.my_side

        start_world = self.update_world_and_agents()

        #        empty_neighbors = start_world.get_our_agent_empty_neighbors()
        #        blue_walls = start_world.get_our_agent_blue_wall_neighbors()
        #        yellow_walls = start_world.get_our_agent_yellow_wall_neighbors()
        #        area_walls = start_world.get_our_agent_Area_wall_neighbors()

        result = self.minimax(start_world, [], 0)
        if not result[1][0][1]:
            self.send_command(ChangeDirection(result[1][0][0]))
        else:
            self.send_command(ActivateWallBreaker())

    """
        if self.world.agents[self.my_side].wall_breaker_rem_time > 1:
            # wall breaker is on
            if my_team == "Yellow":
                if blue_walls:
                    self.send_command(ChangeDirection(random.choice(blue_walls)))
                elif empty_neighbors:
                    self.send_command(ChangeDirection(random.choice(empty_neighbors)))
                elif yellow_walls:
                    self.send_command(ChangeDirection(random.choice(yellow_walls)))
                else:
                    self.send_command(ChangeDirection(random.choice(list(EDirection))))
            else:
                if yellow_walls:
                    self.send_command(ChangeDirection(random.choice(yellow_walls)))
                elif empty_neighbors:
                    self.send_command(ChangeDirection(random.choice(empty_neighbors)))
                elif blue_walls:
                    self.send_command(ChangeDirection(random.choice(blue_walls)))
                else:
                    self.send_command(ChangeDirection(random.choice(list(EDirection))))

        else:
            # wall breaker is off
            if empty_neighbors:
                self.send_command(ChangeDirection(random.choice(empty_neighbors)))
            else:
                if self.world.agents[my_team].wall_breaker_cooldown == 0 and not (
                        self.world.agents[my_team].direction in area_walls):
                    self.send_command(ActivateWallBreaker())
                else:
                    if my_team == "Yellow":
                        if blue_walls:
                            self.send_command(ChangeDirection(random.choice(blue_walls)))
                        elif yellow_walls:
                            self.send_command(ChangeDirection(random.choice(yellow_walls)))
                        else:
                            self.send_command(ChangeDirection(random.choice(list(EDirection))))
                    else:
                        if yellow_walls:
                            self.send_command(ChangeDirection(random.choice(yellow_walls)))
                        elif blue_walls:
                            self.send_command(ChangeDirection(random.choice(blue_walls)))
                        else:
                            self.send_command(ChangeDirection(random.choice(list(EDirection))))
                            

    def _get_our_agent_empty_neighbors(self, world):
        empty_neighbors = []

        our_position = world.get_our_agent_position()

        their_position = world.get_enemy_agent_position()

        if our_position.x + 1 < len(world.board):
            if world.board[our_position.y][our_position.x + 1] == ECell.Empty and \
                    not (our_position.x + 1 == their_position.x and our_position.y == their_position.y):
                empty_neighbors.append(EDirection.Right)
        if our_position.x - 1 >= 0:
            if world.board[our_position.y][our_position.x - 1] == ECell.Empty and \
                    not (our_position.x - 1 == their_position.x and our_position.y == their_position.y):
                empty_neighbors.append(EDirection.Left)
        if our_position.y + 1 < len(world.board):
            if world.board[our_position.y + 1][our_position.x] == ECell.Empty and \
                    not (our_position.x == their_position.x and our_position.y + 1 == their_position.y):
                empty_neighbors.append(EDirection.Down)
        if our_position.y - 1 >= 0:
            if world.board[our_position.y - 1][our_position.x] == ECell.Empty and \
                    not (our_position.x == their_position.x and our_position.y - 1 == their_position.y):
                empty_neighbors.append(EDirection.Up)
        return empty_neighbors

    def _get_our_agent_blue_wall_neighbors(self, world):
        blue_walls = []
        our_position = world.get_our_agent_position()

        their_position = world.get_enemy_agent_position()

        if our_position.x + 1 < len(world.board):
            if world.board[our_position.y][our_position.x + 1] == ECell.BlueWall and \
                    not (our_position.x + 1 == their_position.x and our_position.y == their_position.y):
                blue_walls.append(EDirection.Right)
        if our_position.x - 1 >= 0:
            if world.board[our_position.y][our_position.x - 1] == ECell.BlueWall and \
                    not (our_position.x - 1 == their_position.x and our_position.y == their_position.y):
                blue_walls.append(EDirection.Left)
        if our_position.y + 1 < len(world.board):
            if world.board[our_position.y + 1][our_position.x] == ECell.BlueWall and \
                    not (our_position.x == their_position.x and our_position.y + 1 == their_position.y):
                blue_walls.append(EDirection.Down)
        if our_position.y - 1 >= 0:
            if world.board[our_position.y - 1][our_position.x] == ECell.BlueWall and \
                    not (our_position.x == their_position.x and our_position.y - 1 == their_position.y):
                blue_walls.append(EDirection.Up)
        return blue_walls

    def _get_our_agent_yellow_wall_neighbors(self, world):
        yellow_walls = []

        our_position = world.get_our_agent_position()

        their_position = world.get_enemy_agent_position()

        if our_position.x + 1 < len(world.board[0]):
            if world.board[our_position.y][our_position.x + 1] == ECell.YellowWall and \
                    not (our_position.x + 1 == their_position.x and our_position.y == their_position.y):
                yellow_walls.append(EDirection.Right)
        if our_position.x - 1 >= 0:
            if world.board[our_position.y][our_position.x - 1] == ECell.YellowWall and \
                    not (our_position.x - 1 == their_position.x and our_position.y == their_position.y):
                yellow_walls.append(EDirection.Left)
        if our_position.y + 1 < len(world.board):
            if world.board[our_position.y + 1][our_position.x] == ECell.YellowWall and \
                    not (our_position.x == their_position.x and our_position.y + 1 == their_position.y):
                yellow_walls.append(EDirection.Down)
        if our_position.y - 1 >= 0:
            if world.board[our_position.y - 1][our_position.x] == ECell.YellowWall and \
                    not (our_position.x == their_position.x and our_position.y - 1 == their_position.y):
                yellow_walls.append(EDirection.Up)
        return yellow_walls

    def _get_our_agent_Area_wall_neighbors(self, world):
        area_walls = []

        our_position = world.get_our_agent_position()

        their_position = world.get_enemy_agent_position()

        if our_position.x + 1 < len(world.board[0]):
            if world.board[our_position.y][our_position.x + 1] == ECell.AreaWall and \
                    not (our_position.x + 1 == their_position.x and our_position.y == their_position.y):
                area_walls.append(EDirection.Right)
        if our_position.x - 1 >= 0:
            if world.board[our_position.y][our_position.x - 1] == ECell.AreaWall and \
                    not (our_position.x - 1 == their_position.x and our_position.y == their_position.y):
                area_walls.append(EDirection.Left)
        if our_position.y + 1 < len(world.board):
            if world.board[our_position.y + 1][our_position.x] == ECell.AreaWall and \
                    not (our_position.x == their_position.x and our_position.y + 1 == their_position.y):
                area_walls.append(EDirection.Down)
        if our_position.y - 1 >= 0:
            if world.board[our_position.y - 1][our_position.x] == ECell.AreaWall and \
                    not (our_position.x == their_position.x and our_position.y - 1 == their_position.y):
                area_walls.append(EDirection.Up)
        return area_walls

    """
