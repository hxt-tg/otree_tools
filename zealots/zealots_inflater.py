import numpy
import sys, os
from zealots_strategies import *

def process():
    name = get_attr('Data file (without ".txt")')
    layout = get_attr('Layout file (without ".txt")')
    W = int(get_attr('Grid width'))
    H = int(get_attr('Grid height'))
    pass
    
def process_sequence(fname):
    pass
if __name__ == '__main__':
    pm = {
        'C': { 'C': 2, 'D': -2},
        'D': { 'C': 4, 'D': 0}
    }
    matrix = get_cd_matrix('data/z2_2.txt', 'data/layout2.txt', 7, 7)
    print(matrix[0])
    p = get_pd_payoff(pm, matrix[0])
    print(p)
##    if len(sys.argv) > 1:
##        process_sequence(sys.argv[1])
##    else:
##        process()
    with open('data/z6_1.txt') as f:
        print(f.read().count('C'))
        
