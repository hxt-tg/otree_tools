import numpy
import sys, os

def get_attr(info, default=None, isBoolean=False):
    value = input(info + ('' if default is None \
                  else '(default: {})'.format(default)) + ': ').strip()
    if value == '' and default is not None: value = default
    if isBoolean: value = True if value[0] in 'yY' else False
    return value

def get_cd_matrix(datafile, layoutfile, W, H):
    with open(layoutfile) as f:
        layout_str = f.read().replace('\n', '').replace('\t', '')
    with open(datafile) as f:
        player_str = f.read().replace('C', '1').replace('D', '0').split('\n')
    data_str = ''
    n_players = layout_str.count('_')
    cnt = 0
    if len(player_str) % n_players != 0:
        print('It seems that you have choosen a wrong layout file, please check it.')
        os.system('pause')
        exit(1)
    for i in range(int(len(player_str)/layout_str.count('_'))):
        for p in layout_str:
            if p == '_':
                data_str += player_str[cnt]
                cnt += 1
            else:
                data_str += p
    matrix = list(numpy.array(list(data_str)).reshape((-1, W, H)))
    return matrix

def get_pd_payoff(pm: "Payoff Matrix", stra):
    h = len(stra)
    w = len(stra[0])
    payoff = [[0 for i in range(w)] for i in range(h)]
    s = stra[:]
    for i in range(h):
        for j in range(w):
            s[i][j] = 'D' if s[i][j]=='0' else ('C' if s[i][j]=='1' else s[i][j])
    for i in s:
        print(i)
    for i in range(h):
        for j in range(w):
            # C = 1, D = 0
            ss = s[i][j]
            sl = s[i][(j-1)%w]
            su = s[(i-1)%h][j]
            payoff[i][j] += pm[ss][su]
            payoff[i][j] += pm[ss][sl]
            payoff[i][(j-1)%w] += pm[sl][ss]
            payoff[(i-1)%h][j] += pm[su][ss]
##    p = []
##    for l in payoff:
##        p += l
##    return p
    return payoff
            
    
if __name__ == '__main__':
    print('This file is a library. You should find other files.')

