# -*- coding: utf-8 -*-

# python imports
import random
import copy
from operator import indexOf

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


def get_d_cords(dir_to_take):
    if dir_to_take == EDirection.Left:
        return -1, 0
    elif dir_to_take == EDirection.Right:
        return 1, 0
    elif dir_to_take == EDirection.Up:
        return 0, -1
    elif dir_to_take == EDirection.Down:
        return 0, 1


def reproduction(move_list1, move_list2):
    idx = random.randint(0, len(move_list1))
    return move_list1[:idx] + move_list2[idx:]


def invert_move(move):
    if move == EDirection.Up:
        return EDirection.Down
    if move == EDirection.Down:
        return EDirection.Up
    if move == EDirection.Left:
        return EDirection.Right
    if move == EDirection.Right:
        return EDirection.Left


def get_new_pos(cur_pos, d):
    return cur_pos[0] + d[0], cur_pos[1] + d[1]


def mutation(move_list):
    mutation_rate = 0.1
    for i in range(len(move_list)):
        if random.random() < mutation_rate:
            move_list[i] = random.randint(0, 4)
    return move_list


def get_move_options(cur_world, side, enemy_side):
    move_options = []
    cur_agent = cur_world.agents[side]
    enemy_agent = cur_world.agents[enemy_side]
    cur_pos = cur_agent.position.x, cur_agent.position.y
    enemy_pos = enemy_agent.position.x, enemy_agent.position.y
    for move_option in [EDirection.Left, EDirection.Down, EDirection.Right, EDirection.Up]:
        new_pos = get_new_pos(cur_pos, get_d_cords(move_option))
        if invert_move(cur_agent.direction) != move_option and 0 <= new_pos[0] < len(cur_world.board[0]) and 0 <= \
                new_pos[
                    1] < len(cur_world.board) and new_pos != enemy_pos and cur_world.board[new_pos[1]][new_pos[0]] != ECell.AreaWall:
            move_options.append([move_option, False])
        if cur_agent.direction != move_option and 0 <= new_pos[0] < len(cur_world.board[0]) and 0 <= new_pos[
            1] < len(
            cur_world.board) and new_pos != enemy_pos and not cur_agent.wall_breaker_is_on() and cur_agent.wall_breaker_cooldown == 0:
            move_options.append([move_option, True])
    return move_options


def fitness(move_list, start_world):
    best_score_dif = 10000
    n = len(move_list)
    for way in range(int(pow(4, n))):
        this_score = 10000
        other_move_list = []
        num = way
        for i in range(n):
            other_move_list.append(num % 4)
            num //= 4
        cur_world = copy.deepcopy(start_world)
        for i in range(n):
            move_options = get_move_options(cur_world, cur_world.my_side, cur_world.other_side)
            if move_list[i] >= len(move_options):
                break
            cur_world.change_board(cur_world.my_side, cur_world.other_side, move_options[move_list[i]])
            if cur_world.is_game_finished():
                this_score = cur_world.score_difference(cur_world.my_side, cur_world.other_side)
                break
            other_move_options = get_move_options(cur_world, cur_world.other_side, cur_world.my_side)
            if other_move_list[i] >= len(other_move_options):
                break
            cur_world.change_board(cur_world.other_side, cur_world.my_side, other_move_options[other_move_list[i]])
            if cur_world.is_game_finished():
                this_score = cur_world.score_difference(cur_world.my_side, cur_world.other_side)
                break
            if i == n - 1:
                this_score = cur_world.score_difference(cur_world.my_side, cur_world.other_side)
                break
        best_score_dif = min(best_score_dif, this_score)
    return best_score_dif


def genetics(start_world, number_of_generations, number_of_chromosomes, prediction_number):
    chromosomes = []
    for i in range(number_of_chromosomes):
        chromosome = []
        for j in range(prediction_number):
            chromosome.append(random.randint(0, 3))
        chromosomes.append(chromosome)
    for gen_num in range(number_of_generations):
        new_population = []
        sorted_population = []
        probabilities = []
        for chromosome in chromosomes:
            f = fitness(chromosome, start_world)
            probabilities.append(f)
            sorted_population.append([f, chromosome])

        sorted_population.sort(reverse=True)

        new_population.append(sorted_population[0][1])  # the best gen
        new_population.append(sorted_population[-1][1])  # the worst gen

        for i in range((len(chromosomes) - 2)):
            chromosome_1, chromosome_2 = random.choices(chromosomes, weights=probabilities, k=2)

            # Creating two new chromosomes from 2 chromosomes
            child = reproduction(chromosome_1, chromosome_2)
            mutation(child)

            new_population.append(child)
        chromosomes = new_population

    fitnessOfChromosomes = [fitness(chrom, start_world) for chrom in chromosomes]

    bestChromosomes = chromosomes[
        indexOf(fitnessOfChromosomes, max(fitnessOfChromosomes))
    ]

    move_option = get_move_options(start_world, start_world.my_side, start_world.other_side)
    return move_option[bestChromosomes[0]]


class AI(RealtimeAI):

    def __init__(self, world):
        super(AI, self).__init__(world)

    def initialize(self):
        print('initialize')

    def decide(self):
        print('decide')
        self.client1()

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

        start_world = self.update_world_and_agents()

        result = genetics(start_world, 6, 10, 3)

        print(result)

        if not result[1]:
            self.send_command(ChangeDirection(result[0]))
        else:
            self.send_command(ActivateWallBreaker())
