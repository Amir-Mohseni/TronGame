# -*- coding: utf-8 -*-

# python imports
import random

# chillin imports
from chillin_client import RealtimeAI

# project imports
from ks.models import ECell, EDirection, Position
from ks.commands import ChangeDirection, ActivateWallBreaker

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

    def client1(self):
        my_team = self.my_side
        empty_neighbors = self._get_our_agent_empty_neighbors()
        blue_walls = self._get_our_agent_blue_wall_neighbors()
        yellow_walls = self._get_our_agent_yellow_wall_neighbors()
        area_walls = self._get_our_agent_Area_wall_neighbors()
        # print(f"empty_neighbors : {empty_neighbors}")
        # print(f"blue_walls : {blue_walls}")
        # print(f"yellow_walls : {yellow_walls}")
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

    def _get_our_agent_empty_neighbors(self):
        empty_neighbors = []

        our_position = self._get_our_agent_position()

        their_position = self._get_their_agent_position()

        if our_position.x + 1 < len(self.world.board):
            if self.world.board[our_position.y][our_position.x + 1] == ECell.Empty and \
                    not (our_position.x + 1 == their_position.x and our_position.y == their_position.y):
                empty_neighbors.append(EDirection.Right)
        if our_position.x - 1 >= 0:
            if self.world.board[our_position.y][our_position.x - 1] == ECell.Empty and \
                    not (our_position.x - 1 == their_position.x and our_position.y == their_position.y):
                empty_neighbors.append(EDirection.Left)
        if our_position.y + 1 < len(self.world.board):
            if self.world.board[our_position.y + 1][our_position.x] == ECell.Empty and \
                    not (our_position.x == their_position.x and our_position.y + 1 == their_position.y):
                empty_neighbors.append(EDirection.Down)
        if our_position.y - 1 >= 0:
            if self.world.board[our_position.y - 1][our_position.x] == ECell.Empty and \
                    not (our_position.x == their_position.x and our_position.y - 1 == their_position.y):
                empty_neighbors.append(EDirection.Up)
        return empty_neighbors

    def _get_our_agent_blue_wall_neighbors(self):
        blue_walls = []
        our_position = self._get_our_agent_position()
        their_position = self._get_their_agent_position()
        if our_position.x + 1 < len(self.world.board):
            if self.world.board[our_position.y][our_position.x + 1] == ECell.BlueWall and \
                    not (our_position.x + 1 == their_position.x and our_position.y == their_position.y):
                blue_walls.append(EDirection.Right)
        if our_position.x - 1 >= 0:
            if self.world.board[our_position.y][our_position.x - 1] == ECell.BlueWall and \
                    not (our_position.x - 1 == their_position.x and our_position.y == their_position.y):
                blue_walls.append(EDirection.Left)
        if our_position.y + 1 < len(self.world.board):
            if self.world.board[our_position.y + 1][our_position.x] == ECell.BlueWall and \
                    not (our_position.x == their_position.x and our_position.y + 1 == their_position.y):
                blue_walls.append(EDirection.Down)
        if our_position.y - 1 >= 0:
            if self.world.board[our_position.y - 1][our_position.x] == ECell.BlueWall and \
                    not (our_position.x == their_position.x and our_position.y - 1 == their_position.y):
                blue_walls.append(EDirection.Up)
        return blue_walls

    def _get_our_agent_yellow_wall_neighbors(self):
        yellow_walls = []
        our_position = self._get_our_agent_position()
        their_position = self._get_their_agent_position()
        if our_position.x + 1 < len(self.world.board[0]):
            if self.world.board[our_position.y][our_position.x + 1] == ECell.YellowWall and \
                    not (our_position.x + 1 == their_position.x and our_position.y == their_position.y):
                yellow_walls.append(EDirection.Right)
        if our_position.x - 1 >= 0:
            if self.world.board[our_position.y][our_position.x - 1] == ECell.YellowWall and \
                    not (our_position.x - 1 == their_position.x and our_position.y == their_position.y):
                yellow_walls.append(EDirection.Left)
        if our_position.y + 1 < len(self.world.board):
            if self.world.board[our_position.y + 1][our_position.x] == ECell.YellowWall and \
                    not (our_position.x == their_position.x and our_position.y + 1 == their_position.y):
                yellow_walls.append(EDirection.Down)
        if our_position.y - 1 >= 0:
            if self.world.board[our_position.y - 1][our_position.x] == ECell.YellowWall and \
                    not (our_position.x == their_position.x and our_position.y - 1 == their_position.y):
                yellow_walls.append(EDirection.Up)
        return yellow_walls

    def _get_our_agent_Area_wall_neighbors(self):
        area_walls = []
        our_position = self._get_our_agent_position()
        their_position = self._get_their_agent_position()
        if our_position.x + 1 < len(self.world.board[0]):
            if self.world.board[our_position.y][our_position.x + 1] == ECell.AreaWall and \
                    not (our_position.x + 1 == their_position.x and our_position.y == their_position.y):
                area_walls.append(EDirection.Right)
        if our_position.x - 1 >= 0:
            if self.world.board[our_position.y][our_position.x - 1] == ECell.AreaWall and \
                    not (our_position.x - 1 == their_position.x and our_position.y == their_position.y):
                area_walls.append(EDirection.Left)
        if our_position.y + 1 < len(self.world.board):
            if self.world.board[our_position.y + 1][our_position.x] == ECell.AreaWall and \
                    not (our_position.x == their_position.x and our_position.y + 1 == their_position.y):
                area_walls.append(EDirection.Down)
        if our_position.y - 1 >= 0:
            if self.world.board[our_position.y - 1][our_position.x] == ECell.AreaWall and \
                    not (our_position.x == their_position.x and our_position.y - 1 == their_position.y):
                area_walls.append(EDirection.Up)
        return area_walls

    def _get_our_agent_position(self):
        return self.world.agents[self.my_side].position

    def _get_their_agent_position(self):
        return self.world.agents[self.other_side].position
