def get_neighbor_array(h, w):
    neighbor = []
    for i in range(h):
        for j in range(w):
            # x = i * w + j
            neighbor.append({
                'left': i * w + (j + w - 1) % w,
                'up': (i + h - 1) % h * w + j,
                'right': i * w + (j + 1) % w,
                'down': (i + 1) % h * w + j
            })
    return neighbor

def round_pay(h, w):
    with open('input.txt') as f:
        data = list(filter(lambda x: x != '', f.read().split('\n')))
        data = list(map(lambda x: x.split('\t'), data))
    n_rounds = int(len(data)/(h*w))
    r_data = []
    for i in range(n_rounds):
        r_data.append(data[:h*w])
        data = data[h*w:]
    return(r_data)

def group_payoffs(multi, stras, h, w):
    payoffs = []
    na = get_neighbor_array(h, w)
    for stra in stras:
        pool = [0]*len(stra)
        for i, s in enumerate(stra):
            pool[na[i]['left']] += float(s[0]) * multi
            pool[na[i]['up']] += float(s[1]) * multi
            pool[na[i]['right']] += float(s[2]) * multi
            pool[na[i]['down']] += float(s[3]) * multi
            pool[i] += float(s[4]) * multi
        payoffs.append(pool)
    return payoffs
        
def avg(one_row):
    return sum(one_row)/len(one_row)

if __name__=='__main__':
    print('使用：去掉第一行标题的一列【策略】存入input.txt，和该程序放在一起。')
    w = int(input('网络的宽：'))
    h = int(input('网络的高：'))
    multi = float(input('收益因子：'))
    stras = round_pay(h, w)
    payoffs = group_payoffs(multi, stras, h, w)
    with open('group_payoff.csv', 'w') as f:
        f.write('Rounds,')
        for i in range(len(payoffs[0])):
            f.write('Pool '+str(i+1)+',')
        f.write('Average\n')
        for i, r in enumerate(payoffs):
            f.write('Round '+str(i+1)+','+','.join(list(map(str, r)))+','+str(avg(r))+'\n')

