from random import random, randint

# Game part

def fill_empty_node(stra, choices):
    for i in enumerate(stra):
        if stra[i] not in choices:
            stra[i] = choices[randint(0, len(choices)-1)]


def pd_game_node(nei_matrix, stra, pay_gain):    # stra contains C & D
    CP, CG, DP, DG = list(map(int, pay_gain.replace(' ', '').split(',')))
    payoff_matrix = {'C': {'C': CP + CG, 'D': CP + DG},
                     'D': {'C': DP + CG, 'D': DP + DG}}
    pm = [0]*len(stra)
    for x, nei in enumerate(nei_matrix):
        for y in nei:
            pm[x] += payoff_matrix[stra[x]][stra[y-1]]
    return pm


def pgg_game_control_total_cost_node(nei_matrix, stra, total_cost, multiplier):   # stra contains C & D
    pool = [0]*len(stra)
    for x, s in enumerate(stra):
        if s == 'D': continue
        cost = total_cost/(len(nei_matrix[x])+1)
        pool[x] += cost * multiplier
        for y in nei_matrix[x]:
            pool[y-1] += cost * multiplier
    pm = [0]*len(stra)
    for x, nei in enumerate(nei_matrix):             # x is its id-1
        pm[x] += pool[x]/(len(nei_matrix[x])+1)
        for y in nei_matrix[x]:
            pm[x] += pool[y-1]/(len(nei_matrix[y-1])+1)
        pm[x] -= total_cost if stra[x] == 'C' else 0
    return pool, pm


def pgg_game_control_group_cost_node(nei_matrix, stra, cost, multiplier):   # stra contains C & D
    pool = [0]*len(stra)
    for x, s in enumerate(stra):
        if s == 'D': continue
        pool[x] += cost * multiplier
        for y in nei_matrix[x]:
            pool[y-1] += cost * multiplier
    pm = [0]*len(stra)
    for x, nei in enumerate(nei_matrix):             # x is its id-1
        pm[x] += pool[x]/(len(nei_matrix[x])+1)
        for y in nei_matrix[x]:
            pm[x] += pool[y-1]/(len(nei_matrix[y-1])+1)
        pm[x] -= cost*(len(nei_matrix[x])+1) if stra[x] == 'C' else 0
    return pool, pm

